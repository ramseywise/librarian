# simple_router — Claude Code Guidelines

## Multilingual requirement

Every agent in this system **must respond in the same language the user wrote in**.
This is a hard product requirement across all supported markets (EN / DA / DE / FR).

### How it is enforced today

| Layer | Mechanism | File |
| --- | --- | --- |
| Out-of-scope detection | `OOS_BY_LANG` holds keyword lists per language; `detect_out_of_scope` checks DA → DE → FR → EN so language-specific terms win over shared words (e.g. "budget") | `oos_detection.py` |
| Out-of-scope response | `apply_out_of_scope_instruction` overrides the system instruction with `OUT_OF_SCOPE_INSTRUCTION`, which explicitly tells the LLM to reply in the user's language | `oos_detection.py` |
| Follow-up detection | `NEW_REQUEST_STARTS` covers imperative/question openers in EN, DA, DE, FR so the follow-up shortcut does not misfire on non-English commands | `follow_up_detection.py` |
| Agent prompts | Each prompt must include a language-matching rule (see below) | `prompts/*.txt` |

### Rule to add to every agent prompt

When writing or editing a prompt in `prompts/`, include this line (or equivalent) in the response rules section:

```text
- Language: always reply in the same language the user wrote in. Do not switch languages mid-conversation.
```

The best place is `prompts/shared_rules.txt` so it applies to all experts automatically via the `{shared_rules}` placeholder.

### When adding a new language market

1. Add out-of-scope keywords to `OOS_BY_LANG` in `oos_detection.py` under a new language key.
2. Add the new language's imperative/question openers to `NEW_REQUEST_STARTS` in `follow_up_detection.py`.
3. Verify that `OUT_OF_SCOPE_INSTRUCTION` still instructs the LLM to match language (it uses a generic directive — no change usually needed).
4. Add a response eval case in `eval/response_evalset.json` that sends an out-of-scope message in the new language and expects a decline in that same language.

### When adding a new out-of-scope topic

Add the terms (in all supported languages) to the appropriate language group in `OOS_BY_LANG` in `oos_detection.py`. Do not add only English terms.

---

## Design constraints for specs and implementation suggestions

Every spec and implementation suggestion must optimize for these three constraints.
Explicitly evaluate each one before finalizing any proposal.

1. **Prefix caching** — keep request fingerprints stable across turns so Gemini can cache
   the `[SI + conversation prefix]` consistently. Concretely:
   - Never inject dynamic data into the system instruction at runtime; use `inject_facts_callback` to append to `contents` instead
   - Strip noise from prior turns (tool calls, thought parts) so the history prefix is uniform
   - Place dynamic tail content (facts, current-turn tool results) *after* the stable prefix, not before it

2. **Minimize LLM calls per turn** — the baseline single-domain path is 2 calls (router → expert). Prefer shortcuts, synthetic `LlmResponse` returns from callbacks, or pre-execution over adding real LLM calls. Every additional call must be justified.

3. **Clear and concise conversation history** — structured data belongs in `public:session_facts` (delivered via `inject_facts_callback`), not in the conversation thread. Prior tool-call chains must be stripped before each LLM call. The history seen by any expert at any turn should be: user messages + agent text replies + current facts snapshot — nothing else.

Every spec must also include an **evalset review**: check whether existing routing and response eval cases cover the changed behavior, and explicitly add or fix cases where they don't. A spec is not complete without this step.

---

## After every refactor or code improvement

### Development loop (fast feedback first)

Always follow this order — do NOT run the full suite until the targeted cases pass:

**Step 1 — Run only the directly affected or newly added cases:**

```bash
# Comma-separated eval IDs for the cases you changed or added
make -C agents/simple_router eval-response CASES=generic_request_after_history_recall_asks_for_id,follow_up_field_question_answers_concisely
make -C agents/simple_router eval-routing CASES=follow_up_shortcut_fires
make -C agents/simple_router eval-behavior CASES=behavior_oos_decline_danish
```

If a targeted case fails: read `eval/.last_thoughts.log` to understand the model's reasoning,
fix the issue, and re-run the targeted cases. Repeat until they pass.

**Step 2 — Only after targeted cases pass, run the full suite:**

```bash
# 1. Unit tests — must pass with zero failures
make -C agents/simple_router test

# 2. Routing eval — tool_trajectory_avg_score must be 1.0
make -C agents/simple_router eval-routing

# 3. Response eval — final_response_match_v2 must meet threshold (1.0)
make -C agents/simple_router eval-response

# 4. Behavior eval — rubric_based_final_response_quality_v1, threshold 0.8
make -C agents/simple_router eval-behavior

# 5. Error eval — rubric_based_final_response_quality_v1, threshold 0.8
make -C agents/simple_router eval-error
```

If the full suite reveals regressions in unrelated cases, fix those before finishing.

### Debugging failing eval cases

When a case fails, run it in isolation and read the thoughts log:

```bash
make -C agents/simple_router eval-response CASES=follow_up_field_question_answers_concisely
# eval/.last_thoughts.log is overwritten on each run — always reflects the last execution
```

The thoughts log (`eval/.last_thoughts.log`) captures the model's internal reasoning for every
LLM call made by expert agents. Each entry is prefixed with the runtime `invocation_id` and
agent name. Running a single case keeps the log focused and readable.

### When to run which eval

| Change made                                    | Eval targets to run                                  |
|------------------------------------------------|------------------------------------------------------|
| Any `prompts/*.txt` change                     | `eval-routing` + `eval-response` + `eval-behavior`   |
| Cases added to `eval/routing_evalset.json`     | `eval-routing`                                       |
| Cases added to `eval/response_evalset.json`    | `eval-response`                                      |
| Cases added to `eval/behavior_evalset.json`    | `eval-behavior`                                      |
| Cases added to `eval/error_evalset.json`       | `eval-error`                                         |

When adding cases to **any** evalset, also update `eval/README.md` — add the new case ID and a one-line description to the appropriate cases table.
| Cases added to `eval_apps/receptionist_agent/`  | `eval-receptionist-agent`                            |
| Cases added to `eval_apps/support_agent/`       | `eval-support-agent`                                 |
| Cases added to `eval_apps/invoice_agent/`       | `eval-invoice-agent`                                 |
| Cases added to `eval_apps/orchestrator_agent/`  | `eval-orchestrator-agent`                            |

If any eval case regresses, fix the code (or update the evalset expected response if the new behaviour is intentionally different) before finishing.

---

## Key files

| File | Purpose |
|------|---------|
| `agent.py` | Root agent — router wiring and sub-agent list |
| `expert_registry.py` | Single source of truth for domain experts; builds `direct_agent` and `helper_agent` variants; loads prompts |
| `callbacks.py` | Router `before_model_callback` chain — circuit breaker, reroute guard, OOS shortcut, follow-up shortcut, static routing, context prefetch |
| `_facts_callbacks.py` | `inject_facts_callback`, `persist_facts_callback`, `router_force_context_callback` — fact lifecycle |
| `_history.py` | `strip_tool_history_callback` — purges prior tool call/response/thought parts; no local imports (avoids circular dep) |
| `routing.py` | Deterministic keyword scorer (`RoutingDecision`, `decide_route`) — no LLM |
| `oos_detection.py` | OOS keyword vocabulary (`OOS_BY_LANG`) and `detect_out_of_scope` / `apply_out_of_scope_instruction` |
| `follow_up_detection.py` | Follow-up classifier (`NEW_REQUEST_STARTS`, `is_follow_up_answer`) — multilingual, no LLM |
| `tools/context_tools.py` | `get_conversation_context`, `signal_follow_up`, `signal_reroute`, `set_fact`, session state keys |
| `prompts/shared_rules.txt` | Rules injected into every expert prompt via `{shared_rules}` |
| `prompts/*.txt` | Per-agent prompts — load via `load_prompt(name)` in `expert_registry.py` |
| `SPEC.md` | Full system specification — routing rules, agent contracts, tool contracts |

## Static routing

The keyword-based routing shortcut (`static_route_shortcut`) is **disabled by default** (`_STATIC_ROUTING_DEFAULT = "0"`). Enable with `SIMPLE_ROUTER_STATIC=1`. Tests that exercise the enabled path must patch `_STATIC_ROUTING_ENABLED = True` explicitly. A dedicated test (`test_static_routing_disabled_by_default`) asserts the default is off — it will fail if the default is reverted to `"1"`.

## Context prefetch

`context_prefetch_shortcut` is always active and fires as the last step in
`router_before_model_callback` when no other shortcut fires. It pre-executes
`get_conversation_context` via a synthetic `LlmResponse`, reducing the LLM-path
from 2 calls to 1.

Two-pass design:

- **Pass 1** (synthetic LlmResponse): `_emit_prefetch_label_span` emits an OTel span with
  `gcp.vertex.agent.invocation_id` + `gcp.vertex.agent.llm_request` (just the user's text).
  This span has an earlier `start_time` than the pass-2 LLM span, so the ADK web Trace tab's
  `findUserMsgFromInvocGroup` picks it first and shows the user's text instead of `[attachment]`.
- **Pass 2** (`_patch_prefetch_thought_signature`): injects `b"skip_thought_signature_validator"`
  directly into `llm_request.contents` before the real LLM call so the Gemini API accepts the
  synthetic Part in history. This value is the official Gemini API bypass for injecting synthetic
  tool calls into conversation history (intended for migration from stateless models).

Why `[attachment]` appeared without the label span: pass 1 returns a synthetic `LlmResponse`
early (line 887 of `base_llm_flow.py`) — ADK tracing never fires for synthetic responses. The
only span created is the pass-2 LLM call, whose `llm_request.contents` end with a
`function_response` part (no text) → `text ?? "[attachment]"` in the JS.

Disable by returning `None` early from `context_prefetch_shortcut` (no env var gate).
