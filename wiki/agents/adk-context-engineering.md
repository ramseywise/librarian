---
title: ADK Context Engineering
tags: [adk, context-management, pattern]
summary: How the ADK samples repo manages context — SKILL.md pattern, three skill-loading strategies, static vs dynamic instruction, and history compaction.
updated: 2026-04-24
sources:
  - raw/playground-docs/adk-samples-patterns-analysis.md
  - raw/playground-docs/rag-agent-template-research.md
  - raw/claude-docs/playground/agents/analyzer.md
  - raw/claude-docs/playground/agents/comparator.md
  - raw/claude-docs/playground/agents/grader.md
  - raw/claude-docs/playground/skills/a2ui-workspace/README.md
---

# ADK Context Engineering

## Core Discipline

**`static_instruction=`** is always a string literal or file read — no dynamic data allowed. Dynamic context goes into `instruction=callable` or is injected into conversation history as `function_response` events.

**Why this matters:** static instructions are eligible for [[Prefix Caching]] — the model caches everything up to the first dynamic token. Mixing dynamic data into static instructions breaks caching and inflates costs.

## File Organization

| File | Role |
|---|---|
| `prompts/system.txt` | Static system instruction — never changes per turn (prefix cache) |
| `prompts/summarizer.txt` | History compaction prompt |
| `skills/SKILL.md` | YAML frontmatter (`adk_additional_tools`) + instruction body |
| `CLAUDE.md` | Developer-facing spec (not runtime context) |
| `SPEC.md` | Architecture specification per agent |

## SKILL.md Pattern

See [[SKILL.md Pattern]] for full detail.

```yaml
---
name: invoice-skill
metadata:
  adk_additional_tools:
    - list_invoices
    - get_invoice
    - create_invoice
---
# Invoice Management Instructions

You can create, view, and edit invoices...
```

The frontmatter declares which MCP tools to activate. The body is the instruction text injected when the skill loads. **This separates domain logic from agent orchestration code entirely.**

**Gap in both rag_poc and playground:** no skill-file pattern. Prompts are code, not loadable artifacts.

## Three Skill-Loading Strategies

### Strategy A — Dynamic/Proxy (`dynamic_skill_mcp`)

- Tools list: `[load_skill, execute_mcp_action, _preloaded_toolset]` — static, never changes
- Skill instructions + tool schemas injected into conversation history as `function_response`
- **Prefix cache benefit:** tools list is stable across all turns
- **Trade-off:** schemas in conversation history; **incompatible with voice/BIDI** (VAD interrupts the 2-step chain)

### Strategy B — Native SkillToolset (`native_skill_mcp`) ← most relevant

- Tools: `[_preloaded_toolset, _skill_toolset]`
- `load_skill` returns prose only; schemas live in the `tools` API field
- Tool registry expands dynamically as `activated_skills` state grows
- **Benefits:** voice compatible (single-turn tool calls), smaller `load_skill` responses, clean separation
- **LangGraph mapping:** `activated_skills` state + `get_visible_tools()` + `MultiServerMCPClient`

### Strategy C — All Preloaded (`live_mcp`)

- All tool schemas + all skill instructions in system prompt from turn 1
- **Why:** voice/BIDI agents can't tolerate multi-step `load_skill → domain_tool` chains
- **Trade-off:** large initial context; no lazy loading

**Current state:** rag_poc uses an implicit Strategy C — one tool always bound, no lazy loading. Fine for single-domain RAG but doesn't scale to multi-domain.

## LangGraph Translation of Strategy B

| ADK Concept | LangGraph Implementation |
|---|---|
| `SkillToolset` | `activated_skills` in `TypedDict` state + `get_visible_tools()` |
| `McpToolset` (filtered) | `MultiServerMCPClient` with tool allowlist |
| `load_skill` tool | Async function that appends to `activated_skills` |
| `_preloaded_toolset` | Tools always in tool node (support/FAQ skills) |
| History compaction callback | `before_node` callback in `history_pruning.py` |
| `static_instruction` | System message never rebuilt |
| `instruction=callable` | `SystemMessage` rebuilt each turn from state |

## History Compaction Node

- **Trigger:** 8 messages
- **Overlap:** keep last 4 messages after compaction
- **Model:** Haiku (cost-efficient, not Sonnet)
- **Why:** preserves factual state across compaction; Sonnet is overkill for summarization

```python
# Summarization node pattern
if len(state["messages"]) >= 8:
    summary = await haiku.ainvoke(
        [SystemMessage(SUMMARIZER_PROMPT)] + state["messages"][-8:]
    )
    state["messages"] = [summary] + state["messages"][-4:]
```

## Context Management for Voice/BIDI

Voice agents require Strategy C (all-preloaded) because voice activity detection (VAD) can interrupt mid-sequence, making the 2-step `load_skill → domain_tool` chain unreliable.

**Voice-specific constraints:**
- Latency budget: <400ms for first response token
- No multi-step tool chains in the hot path
- All tool schemas in system prompt from turn 1
- Session state must handle text and voice turn structures (spike: verify compatibility)

## Output Schema Placement (Multi-Agent)

`output_schema` belongs on **leaf agents only**. The root router has no schema.

**Risk if set on root:** ADK enforces that the router's routing-decision text conforms to the output schema. It won't, and the call fails with a validation error that looks like a model output problem.

## ContextVar vs session.state (ADK Python)

In ADK Python multi-agent, `asyncio.create_task()` copies a context snapshot — `ContextVar` mutations after creation are invisible to child tasks. **Use `session.state` as the primary auth channel for multi-agent**, not `ContextVar`.

```python
# FastAPI endpoint — write auth into session before runner call
session = await session_service.create_session(
    app_name="copilot-py",
    state={
        "billy_api_token": body.api_token,
        "billy_org_id": body.org_id,
    },
)

# Tool functions — read via ToolContext (multi-agent safe)
async def list_bills(tool_context: ToolContext) -> list[dict]:
    token = tool_context.state["billy_api_token"]
    ...
```

---

## SKILL.md Evaluation Framework

Three agents (Grader → Comparator → Analyzer) form a pipeline for measuring whether a SKILL.md improves Claude's output.

### How the pipeline works

1. **Run** the same eval prompt twice: once with the skill loaded (`with_skill`), once without (`without_skill`). Save outputs and transcripts.
2. **Grader** evaluates each run independently: PASS/FAIL per expectation, plus claims extracted from outputs, plus critique of the eval assertions themselves ("this assertion would also pass for a clearly wrong output").
3. **Comparator** judges which output is better without knowing which skill produced it (blind). Scores on a content + structure rubric, determines winner.
4. **Analyzer** unblins the result: reads both skills + transcripts, identifies what made the winner win, produces improvement suggestions ranked by impact.

### Grader output structure

```json
{
  "expectations": [{"text": "...", "passed": true, "evidence": "..."}],
  "summary": {"passed": 2, "failed": 1, "total": 3, "pass_rate": 0.67},
  "claims": [{"claim": "...", "type": "factual|process|quality", "verified": true}],
  "eval_feedback": {
    "suggestions": [{"assertion": "...", "reason": "would also pass for wrong output"}],
    "overall": "Assertions check presence but not correctness."
  }
}
```

The `eval_feedback` field critiques the eval assertions themselves — a passing grade on a weak assertion creates false confidence. Surface suggestions when an assertion is trivially satisfied or a real outcome goes unchecked.

### Comparator: blind judgment

Comparator receives outputs labeled A and B without knowing which skill produced which. Evaluates on a rubric:
- **Content:** correctness, completeness, accuracy (1–5 each)
- **Structure:** organization, formatting, usability (1–5 each)
- Winner declared by rubric score first, assertion pass rate second.

### Analyzer improvement suggestions

Four suggestion categories: `instructions`, `tools`, `examples`, `error_handling`. Priority levels: `high` (would change the outcome), `medium` (improves quality), `low` (nice to have). Focus on changes that would have changed the win/loss outcome, not cosmetic improvements.

### A2UI benchmark results (3 iterations)

| Iteration | Change | With Skill | Without | Delta |
|---|---|---|---|---|
| 1 | Initial draft, easy evals | 92% | 100% | −8pp |
| 2 | Replaced easy eval with checkout form; fixed debug JSON example | 94% | 22% | +72pp |
| 3 | Added `action` reminder to Button | **100%** | 22% | **+78pp** |

**Key finding:** Without the a2ui skill, Claude hallucinates a fake schema — nested `children` trees, `"type": "card"` shorthand, `bind` fields — none of which exist in the A2UI protocol. The skill prevents this entirely. +78pp gain from a single well-crafted SKILL.md.

**Lesson:** Eval design matters as much as skill design. Iteration 1 used easy evals that the baseline already passed (100%) — they couldn't detect skill value. Only when the eval targeted behavior that actually requires the skill (checkout form, debug blank screen) did the signal emerge.

### Description optimization

The skill `description` field is the only thing Claude reads when deciding whether to load the skill. A skill that under-triggers (user needs it, it doesn't load) or over-triggers (loads on unrelated prompts, wastes context) defeats its purpose. Description optimization runs an automated loop:
1. Evaluate current description against 20 trigger/no-trigger queries (3 runs each)
2. Propose improved description based on failures
3. Re-evaluate on training + held-out test set
4. Iterate up to 5 times

---

## See Also
- [[ADK vs LangGraph Comparison]]
- [[Agent Memory Types]]
- [[LangGraph Advanced Patterns]]
- [[MCP Protocol]]
- [[VA Agent Project]]
