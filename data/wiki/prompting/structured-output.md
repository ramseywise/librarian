---
title: Structured Output
tags: [prompting, llm, concept]
summary: Getting machine-parseable output via a six-rung ladder (ask, show, fence, prefill, constrain, route through a tool) — a schema guarantees shape not truth, so pair it with content validation, and beware that a strict template can lower accuracy.
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt--prompt-engineering.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--04-controlling-output.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--06-chaining-and-workflows.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--09-evaluating-prompts.md
---

# Structured Output

## What It Is

Ask the model to return its answer in a machine-parseable shape — usually JSON, sometimes
XML tags or a fixed line format — so downstream code can consume it without a parsing
heuristic:

```
Return your answer as JSON with keys: "summary", "confidence", "next_steps".
```

## The Validation Requirement

**A structured-output prompt is a request, not a guarantee.** Always pair it with schema
validation in the harness. The prompt raises the probability of a conformant response; the
validator is what makes the pipeline reliable. Without one, a single malformed response
propagates a parse error into whatever consumes it.

Where the provider offers constrained decoding or a native schema parameter, prefer that
over prompt-level requests — it moves the guarantee from probabilistic to structural.

## The Guarantee Ladder

From weakest to strongest:

1. **Ask** — "Return JSON with keys…". Fine for prototypes, breaks at scale.
2. **Show** — a schema or one complete example; also match the prompt's format to the
   wanted output (markdown in, markdown out).
3. **Fence** — XML tags give an unambiguous parse target even inside a chatty reply.
4. **Prefill** — start the assistant turn with `{` or `<answer>` so the model can only
   continue the structure. **Some newer models no longer accept a prefilled final
   assistant turn** — check the docs and use rungs 5–6.
5. **Constrain** — JSON mode or schema-constrained decoding; the decoder cannot emit
   schema-breaking tokens.
6. **Route through a tool** — a tool whose parameters *are* the output schema, forced via
   `tool_choice` ([[Tool Definitions as Prompts]]).

A schema guarantees **shape, not truth**: a valid object can still hold hallucinated values,
so validate content too ([[Evaluating Prompts]]). Give the empty case an explicit
representation ("If there are no relevant quotes, respond 'No relevant quotes found!'")
so absence is distinguishable from failure. Recognizable ends double as stop sequences
([[Stop Sequences and Completion Anatomy]]).

**Strictness has a cost.** In Clavié et al. (2023), adding a strict output template raised
template adherence to 98% but *lowered* F1 (89.3 → 86.3). Parse loosely, or constrain the
format in a separate step.

## Format Choice

- **JSON** — the default for anything a program consumes.
- **XML tags** — better when the payload is prose that happens to need sectioning
  (`"Write your analysis in <analysis> tags"`); avoids escaping newlines and quotes. See
  [[XML Prompt Structuring]].

## See Also
- [[Prompt Engineering]] — related (part of)
- [[Stop Sequences and Completion Anatomy]] — extends
- [[Tool Definitions as Prompts]] — extends
- [[XML Prompt Structuring]] — alternative-to
- [[Graded-Uncertainty Enrichment Contract]] — extends (how a schema represents what the model could not determine)
- [[Length Limits Are a Fit Layer, Not a Prompt]] — extends (length and layout limits enforced in code after generation)
- [[Free Text With Deterministic Repair Over SDK-Enforced Schema]] — alternative-to (a decision to keep text generation plus a deterministic repair chain)
