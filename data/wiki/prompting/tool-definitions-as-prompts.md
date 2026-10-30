---
title: Tool Definitions as Prompts
tags: [prompting, mcp, pattern]
summary: Function calling is still document completion — schemas are rendered into the system message (TypeScript-style in one vendor's format, with some JSON-schema constraints silently dropped), so every name, description and enum is prompt text steering a chain of hierarchical classifiers; validate constraints and gate side effects in code.
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--05-tools-and-function-calling.md
---

# Tool Definitions as Prompts

The model never touches the world: it **proposes** a call, your code **executes** it and
appends the result as a `tool` message. Arguments arrive as a JSON *string*; one reply can
carry several parallel calls, each answered by `tool_call_id` before the next model call.
`tool_choice` can be `auto`, `none`, or a forced tool — forcing is how a tool becomes a
structured-output mechanism ([[Structured Output]]). The observation becomes context for
the next step: [[ReAct Pattern]] with the bookkeeping done by the API.

## Under the hood

Tool calling is fine-tuning plus API sugar ([[Prompts as Document Completion]]). Berryman &
Ziegler's reconstruction of one vendor's internal format:

- Schemas are rendered into the system message as **TypeScript-style declarations** with
  doc comments — a richer type vocabulary, and named arguments make the model write each
  argument name right before its value, reducing mis-assignment.
- A call is just tokens on the assistant turn addressed to `functions.<name>`; results
  return in a dedicated `tool` role.
- As of late 2023, `minimum`, `maximum`, `pattern`, `format`, `minItems` and nested
  descriptions **were not rendered into the prompt** — the model never saw them.
  **Validate constraints in code.**

Token by token the model runs a chain of hierarchical classifiers — tool or text? which
tool? which argument? what value? done? — in 10–20 tokens. **Writing a tool definition is
writing a prompt.**

## Writing definitions

| Rule | Why |
|---|---|
| Few tools that partition the domain | Each extra tool is a distractor; overlapping tools force a coin flip |
| Self-documenting names | Unbroken lowercase tokenizes and reads badly |
| Descriptions say *when* to use it | Simple, not legalese — over-specified definitions overload attention |
| Mirror public APIs the model already knows | A coding assistant found matching known argument names cut errors |
| Few simple arguments, `enum`s | Long parameter lists burn tokens and accuracy |
| Avoid long free text inside JSON | Escaping at length is error-prone; XML-style tool formats cope better |
| Drop arguments the app already knows | The model invents plausible placeholders (`"my-repo"`) for values it can't see |
| Lean outputs of predictable shape | Padding is noise in the next prompt |
| Errors that teach | "`date` must be YYYY-MM-DD", not a stack trace, so the retry is right |

Reinforce routing in the system prompt ("prefer the knowledge base before web search")
when tools are close in purpose.

## Gate in code, not the prompt

"Always confirm before booking" **will eventually be skipped**. Let the model request any
call, then intercept side-effecting calls in the application and require approval showing
the exact arguments (an authorization card in the UI). Tool results are untrusted input
([[Prompt Injection]], [[Execution Boundaries and Guardrails]]).

## Context for a tool-using agent

Preamble (rules, tool definitions, examples) → prior conversation plus attached artifacts →
current exchange and its tool traffic → final response (usually the only part kept
verbatim). Expose only tools relevant to the current state; summarize large artifacts
rather than inlining them; drop stale history when the topic shifts (a small cheap model
can judge relevance). Too much context confuses, too little starves — evaluate.

## Debugging

Log tool, arguments, observation and token counts per step.

| Symptom | Usual fix |
|---|---|
| Wrong tool | Sharpen descriptions, remove overlap, add a routing rule |
| Invented or bad arguments | Enums and examples in parameter descriptions; remove app-known arguments |
| Tool not called | Say *when* in the description; check it is actually passed |
| Observation misread | Simpler output format; return less |

UX: show tool activity distinctly, and let users **edit a call's arguments and resubmit**,
regenerating from that point — a derailed conversation becomes a quick correction.

## See Also
- [[Tool Design as Harness Surface]] — extends (agent-level tool surface)
- [[Structured Output]] — extends
- [[ReAct Pattern]] — instance-of
- [[Prompts as Document Completion]] — prerequisite-for
