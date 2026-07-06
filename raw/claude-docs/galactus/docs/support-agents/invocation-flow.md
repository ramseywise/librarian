# Support Agents — Invocation Flow

Three agents (`hc_adk`, `hc_lg`, `hc_rag`) share a common guardrail layer. This document describes the full request pipeline for each agent, the shared guardrail architecture, and the key architectural decisions with their rationale.

---

## Three-agent overview

| Agent | Framework | Retrieval | Layer 1 | Layer 4 |
|---|---|---|---|---|
| `hc_adk` | Google ADK | Bedrock KB or hc_rag | `run_input_guard()` in `main.py` | `run_output_guard()` in `main.py` |
| `hc_lg` | LangGraph | Bedrock KB or hc_rag | `run_input_guard()` in `main.py` | `run_output_guard()` in `agent.py:grounding_node` |
| `hc_rag` | FastAPI + RAG | Vector DB + reranker | `_GuardrailMiddleware` in `main.py` | not implemented |

The three agents are intentionally self-contained for apples-to-apples eval comparison. See Decision 7 for why cross-agent routing is disallowed during evals.

---

## Shared guardrail pipeline

Both pipelines are imported from `src/support_agents/guardrails/`:

```python
from guardrails import run_input_guard, run_output_guard
```

### Layer 1 — Input pipeline (`guardrails/input_pipeline.py`)

Runs synchronously **before any LLM or retrieval call**. Zero external I/O. Total cost: <1ms.

```
message
  → unicode_sanitize       # normalize homoglyphs, strip zero-width chars
  → detect_and_redact      # replace CPR/email/phone/IBAN with [REDACTED]
  → looks_like_injection   # regex: ignore-previous, role-play, jailbreak patterns
  → InputGuardResult
```

| Field | Type | Meaning |
|---|---|---|
| `message` | `str` | cleaned message to pass downstream |
| `blocked` | `bool` | True → return error, do not call LLM |
| `failure_reason` | `str \| None` | "injection_blocked" if blocked |
| `pii_found` | `bool` | True → log warning, message is redacted |
| `sanitize_warnings` | `list[str]` | non-blocking normalization notes |

### Layer 4 — Output pipeline (`guardrails/output_pipeline.py`)

Runs **after the LLM generates a response**, before returning to the caller. Zero I/O.

```
(response: AssistantResponse, retrieved_urls: set[str])
  → enforce_grounding()    # Tier 1–4 citation + quote checks
  → OutputGuardResult
```

| Field | Type | Meaning |
|---|---|---|
| `response` | `AssistantResponse` | safe to use — may be rewritten on violation |
| `passed` | `bool` | False → response was rewritten to escalation |
| `violation_type` | `"hard" \| "soft" \| None` | hard = model actively fabricated; soft = KB gap |
| `reason` | `str \| None` | "hallucination", "fabricated_claims", "answered_from_training_memory", etc. |

---

## hc_adk pipeline (Google ADK)

`hc_adk` uses the ADK `Runner` + `LlmAgent` callback pattern. One ADK "step" = one `before_model → LLM call → (optional tool call) → after_model` cycle.

```
POST /chat
  │
  ├─ run_input_guard(message)              # Layer 1 — sync, <1ms
  │    blocked? → return 400
  │    pii_found? → log warning
  │    message = guard.message            # cleaned
  │
  └─ Runner.run_async()
       │
       ├─ [step 1+] before_model_callback()          src: hc_adk/callbacks.py
       │    ├─ check_step_limit()          hard-stop at MAX_STEPS+1; warn at MAX_STEPS
       │    ├─ inject_kb_error_guard()     force escalation if tool threw system error
       │    ├─ inject_retry_stop()         bail if retry search had no score improvement
       │    └─ prune_old_passages()        strip stale KB text from context window
       │
       ├─ [LLM generates → may call fetch_support_knowledge tool]
       │    before_tool: record _kbCallStart timestamp
       │    after_tool:  update _kbTopScore, record call in _kb_calls
       │
       └─ [final step] after_model_callback()
            └─ enforce_grounding()         Tier 1–4 citation checks
                 → rewrite response if violation detected
       │
  └─ run_output_guard(response_obj, retrieved_urls)   # Layer 4 — normalizes result
       not out.passed? → use out.response (rewritten escalation)
```

### before_model_callback — four concerns (hc_adk/callbacks.py)

Each function is independently testable and early-returns without touching the others.

| Function | Fires when | Action |
|---|---|---|
| `check_step_limit` | Every step | Warn at `MAX_STEPS-1`; return hard-stop `LlmResponse` at `MAX_STEPS+1` |
| `inject_kb_error_guard` | `state._kb_system_error == True` | Append "do not retry, set contact_support: true" to contents |
| `inject_retry_stop` | After retry KB call | Append stop message if `curr_score ≤ prev_score + ε` |
| `prune_old_passages` | Every step | Strip passage text from all-but-last KB tool response |

### Score delta guard — inject_retry_stop

```python
_SCORE_DELTA_EPSILON = 0.05

kb_calls = state.get("_kb_calls") or []
if len(kb_calls) >= 2:
    prev = kb_calls[-2].get("top_score")
    curr = kb_calls[-1].get("top_score")
    if curr <= prev + _SCORE_DELTA_EPSILON:
        → inject stop message
```

Without this guard: a query with no KB match triggers a retry, then the LLM confirms the same negative result — one wasted LLM call. Expected saving: ~1–2s on dead-end queries.

*Con (known):* The threshold is fixed at 0.05. A retry improving by 0.04 is declared futile even if it would have produced a better answer. Monitored via LangSmith traces on `hc_adk_turn`.

---

## hc_lg pipeline (LangGraph CRAG)

`hc_lg` uses a `StateGraph` with a CRAG retrieval subgraph embedded inside an answer graph.

```
POST /chat
  │
  ├─ run_input_guard(message)              # Layer 1
  │
  └─ run(message, session_id, history)
       │
       └─ retrieval subgraph  (hc_lg/subgraphs/retrieval.py)
            │
            ├─ fetch_node()               Bedrock or hc_rag, captures prev_top_score
            ├─ confidence_gate()          skip grading if top_score ≥ HIGH_CONFIDENCE_THRESHOLD
            ├─ grade_node()               batched YES/NO passage grading (one LLM call)
            └─ decision_node()            → "end" | "rewrite"
                 ├─ MAX_RETRIES exceeded?           → end
                 ├─ curr_top ≤ prev_top + ε?        → end (score delta guard)
                 ├─ len(good_passages) sufficient?  → end
                 └─ otherwise                       → rewrite
            └─ rewrite_node()             query reformulation (or HyDE if enabled)
            └─ [back to fetch_node]
       │
       ├─ answer_node()                   LLM generates AssistantResponse
       │
       └─ grounding_node()               run_output_guard(response, retrieved_urls)
            not guard.passed? → state.response = guard.response
       │
  └─ low-confidence structural override  force contact_support if conf < 0.35
```

### CRAG decision_node edge routing

| Condition checked (in order) | Edge | Why |
|---|---|---|
| `retrieval_attempts >= MAX_RETRIES` | end | Hard ceiling — prevent infinite loop |
| `attempts >= 2 AND curr_top ≤ prev_top + ε` | end | Score delta guard — extra fetch won't help |
| `len(good_passages) >= HIGH_CONFIDENCE_THRESHOLD` | end | Strong evidence, no reformulation needed |
| otherwise | rewrite | Try a different query formulation |

`prev_top_score` is captured in `fetch_node` *before* overwriting `state.passages`, so `decision_node` always has the two adjacent scores.

---

## Layer 4 grounding checks (`guardrails/grounding/`)

The grounding subpackage is split into single-concern files:

```
grounding/
  citation.py   → Tier 1 + Tier 2
  quote.py      → Tier 3
  audit.py      → Tier 4 (diagnostics, language check)
  __init__.py   → enforce_grounding() dispatcher → GroundingResult
```

### Four-tier pipeline

```
enforce_grounding(response, retrieved_urls)
  ├─ Tier 1  citation.check_hallucinated_sources()   IDs not in retrieved set
  ├─ Tier 2  citation.check_missing_citations()      claim-level IDs not in top-level set
  ├─ Tier 3  quote.check_claims()                    verbatim quote, prefix+suffix boundary
  └─ Tier 4  audit.log_grounding_diagnostics()       language mismatch, hallucinated suggestion URLs
  → GroundingResult(passed, violation_type, reason, response)
```

### Hard vs soft fail table

| Condition | violation_type | Action |
|---|---|---|
| Top-level citation IDs not in retrieved set (Tier 1) | `hard` | Rewrite → hallucination escalation message, clear sources |
| Claim-level citation IDs not declared at top level (Tier 2) | `hard` | Rewrite |
| Zero-score claims — no shared tokens between quote and passage (Tier 3) | `hard` | Rewrite |
| `insufficient_information` without retry (`kbNetworkCallCount < 2`) | `hard` | Rewrite |
| Answered from training memory (no citations, no `insufficient_information`) | `soft` | Rewrite with model's original message |
| Low `relevance_score` | `soft` | Log warning only — no rewrite |

`violation_type` is the canonical field for monitoring dashboards. Hard violations increment `_grounding_violations` for alerting thresholds.

### Why claims are extracted (Tier 2 rationale)

Tier 1 alone is defeatable: a model that learns which passage IDs were fetched can list only valid IDs at the response level while composing its answer entirely from training memory. The `claims` array forces the model to declare, per assertion, which passage it draws from and provide a verbatim excerpt. Tier 2 then cross-checks that every claim-level citation was already declared in the top-level `citations` array. This catches the model passing Tier 1 by listing only valid IDs, then silently referencing undeclared passages inside individual claims.

### Quote boundary check — all occurrences, prefix + suffix (Tier 3)

`check_claims()` in `grounding/quote.py` searches **all occurrences** of the quote in the passage (not just the first), verifying both prefix AND suffix word boundaries at each position.

The first match often lands mid-word: `"kvartal"` found inside `"kvartalsvis"` fails the suffix check (next char is `"s"`), but a standalone `"kvartal"` at a later offset is valid. A naïve `str.find()` would stop at the first (invalid) match and incorrectly declare `quote_found = False`.

```python
start = 0
while True:
    idx = text_norm.find(quote_norm, start)
    if idx < 0:
        break
    before_char = text_norm[idx - 1] if idx > 0 else ""
    after_idx = idx + len(quote_norm)
    after_char = text_norm[after_idx] if after_idx < len(text_norm) else ""
    if (
        (not before_char or not before_char.isalnum())
        and (not after_char or not after_char.isalnum())
    ):
        quote_found = True
        break
    start = idx + 1
```

---

## Architectural decisions

**D1 — Callbacks decomposed by single concern**
`before_model_callback` was a 70-line waterfall of 4 unrelated checks. Splitting into named functions (`check_step_limit`, `inject_kb_error_guard`, `inject_retry_stop`, `prune_old_passages`) makes each independently testable and early-returnable without affecting the others. `before_model()` is a 7-line dispatcher.

**D2 — Score delta guard (retry early-exit)**
Decision 2 in both agents. A query with no KB match fires a retry, then the LLM confirms the same negative result — one wasted LLM + one wasted retrieval call (~1–2s). Comparing adjacent `top_score` values with ε=0.05 detects futile retries before the model is called. *Con:* fixed threshold — a 0.04-delta retry is skipped even if it would help. Monitored in LangSmith.

**D3 — Pipeline API (`run_input_guard` / `run_output_guard`)**
Before: each of the three agents manually sequenced `sanitize → detect_and_redact → looks_like_injection`. Adding a guardrail required editing 3 files. After: agents call two functions. The guardrail internals are encapsulated in `input_pipeline.py` and `output_pipeline.py`.

**D4 — Grounding subpackage**
`grounding.py` was 257 lines mixing citation checks, quote checks, language detection, and audit logging. Decomposed into `grounding/citation.py`, `grounding/quote.py`, `grounding/audit.py`, `grounding/__init__.py`. `enforce_grounding()` is the only public entry point.

**D5 — `GroundingResult` typed return**
The old signature was `enforce_grounding() → AssistantResponse | None`. Callers had to infer success from presence. `GroundingResult(passed, violation_type, reason, response)` makes the hard/soft distinction explicit in the type, not just in log levels. `violation_type` is the field monitoring dashboards consume.

**D6 — Context window pruning**
In multi-step turns, each `fetch_support_knowledge` call appends its full passage text to the conversation. By step 4, the context contains 3 full KB result sets. `prune_old_passages` strips text from all-but-last KB tool responses, keeping ID/URL/title/score metadata. Matches `pruneOldKbPassages` in va-agents TypeScript.

**D7 — Eval isolation**
The three agents share `guardrails/` but each owns its retrieval + LLM pipeline. Routing hc_adk through hc_rag contaminates eval comparison: guardrails run twice (both agents' Layer 1), passages are consumed before hc_adk's grounding check sees them, and the step counter is wrong. `VA_RETRIEVAL_MODE=bedrock` is required for clean eval runs on hc_adk.

---

## Comparison with va-agents (TypeScript help-center-assistant)

Post-hardening parity (see `research/guardrail-hardening.md` for what changed and why).

| Feature | galactus (Python) | va-agents (TypeScript) |
|---|---|---|
| Sanitize (HTML strip, control chars, NFC) | ✅ `guardrails/sanitize.py` | ✅ `guardrails/sanitize.ts` |
| PII redaction (21 patterns) | ✅ `guardrails/pii.py` | ✅ `guardrails/pii.ts` |
| Injection detection (11 groups) | ✅ `guardrails/injection.py` | ✅ `guardrails/injection.ts` |
| `sanitize_warnings` in result | ✅ | ✅ |
| Input pipeline entry point | ✅ `run_input_guard()` | ✅ `runInputGuard()` |
| Output pipeline wrapper | ✅ `run_output_guard()` | ✅ `runOutputGuard()` |
| Score delta guard | ✅ `callbacks.py` / `decision_node` | ✅ `help-center-assistant.ts` |
| Word-boundary check (prefix + suffix + all occurrences) | ✅ `grounding/quote.py` | ✅ `grounding/quote.ts` |
| Suggestion URL check (Tier 4c) | ✅ `grounding/audit.py` | ✅ `grounding/audit.ts` |
| Grounding subpackage split | ✅ `grounding/` | ✅ `grounding/` |
| Typed violation result (`violation_type` / `violationType`) | ✅ `GroundingResult` | ✅ `GroundingResult` |
| Context window pruning | ✅ `prune_old_passages` | ✅ `pruneOldKbPassages` |
| Multi-language escalation messages | ✅ DA/EN | ✅ 9 languages |
| History caching (system instruction + tool schemas) | ❌ not implemented | ✅ `cache.ts` 1-hour TTL singleton |
| Input guardrail at route level (multi-agent) | ❌ pending | ❌ pending — wired in `beforeModel` at step 1 |

**Known gap — va-agents Decision 7:** The `contactSupport` pass-through guard (`!hasHallucinations`) does not account for Tier 3 fabrication — a response that correctly sets `contactSupport: true` but contains fabricated quotes with valid citation IDs passes through unrewritten. This is a monitoring gap, not a user-visible defect (the user is already being escalated), but it means `_groundingViolations` can miss some Tier 3 failures. No equivalent gap in galactus Python — `run_output_guard()` always runs all tiers before checking `contact_support`.

**Remaining delta — history caching:** va-agents caches the system instruction (~4 000 tokens) and tool schemas as a Gemini `cachedContent` resource with a 1-hour TTL, refreshed proactively 5 minutes before expiry. galactus does not implement this. At request volume it is the main per-call cost reduction available — the system instruction is the dominant token cost per turn. When the system instruction stabilises, implement as a module-level singleton matching `cache.ts` — cache on first call, refresh in background, strip `system_instruction` + `tools` from the request when cache is active (Gemini rejects the request if both are present alongside a `cachedContent` reference).
