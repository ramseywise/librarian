---
title: Structured Output
tags: [prompting, llm, concept]
summary: Getting machine-parseable output via a six-rung ladder (ask, show, fence, prefill, constrain, route through a tool) — a schema guarantees shape not truth, so pair it with content validation, and beware that a strict template can lower accuracy.
updated: 2026-11-08
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt--prompt-engineering.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--04-controlling-output.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--06-chaining-and-workflows.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--09-evaluating-prompts.md
  - data/raw/papers/2026-11-07-parikh-2026-structured-output-collapses-answer-diversity.md
  - data/raw/papers/2026-11-08-tang-2023-struc-bench.md
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

## Asking for JSON narrows answer diversity (Parikh)

A July 2026 preprint checked whether simply asking for a JSON reply (with no schema enforcement and no constrained decoding) shifts which answer a model picks when many answers are equally valid ("Name a tree."). Setup: 31 prompts (thirty of the form "Name a[n] X." and one "Pick a word."), 44 models, 4 samples each, requested temperature 1.0, no system prompt, one-word replies matched exactly with no judge, via one gateway; surprisal is measured against the other 43 models. All numbers are the paper's own (self-reported).

- Field-mean answer-choice surprisal fell from 1.80 to 1.58 bits under a JSON request (per-model change -0.22 bits, p=.0002). XML gave -0.23, YAML and CSV -0.09 each, and square brackets +0.13.
- On "Pick a word." the modal word's share rose from 41% to 64% and distinct answers fell from 52 to 36.
- Only 6 of 44 models were individually significant (all compressions; for example deepseek-v3.2 went from 2.63 to 1.32 bits); about 38 were indistinguishable from zero.
- It sharpens the existing preference rather than swapping it: for 28 of 31 categories, the most common JSON answer matched the most common plain-chat answer. Within-category distinctness was flat (plain 0.42, JSON 0.39), so it is not a temperature change.
- Of 144 flagged chat defaults, JSON significantly shifted 76 (53%); 29% reverted to the field mode, and JSON also installed defaults absent from chat (for example 81% of four-of-four JSON-only answers survived a 20-sample re-check).
- Decoder enforcement added almost nothing on a 36-model subset: 1.79 bits plain, 1.56 under the request, 1.53 with a json_schema response format.
- The author's own scope note, not tested: it matters where a task allows many acceptable answers (surveys, brainstorming, tool choice), not where output holds a single correct value such as extraction, classification or routing.
- The author reads the mechanism as mostly tool-use post-training with a corpus-register part; the black-box setup cannot separate them.

Limits: one snapshot through one channel, with requested temperature not honoured uniformly; surprisal is panel-relative; one clause wording per format; single-word answers only, so schemas with several keys, accuracy and reasoning are not covered; no per-model intervals and a mid-table declared uninterpretable; the author co-wrote with models that are also study subjects (disclosed).

## Complex table generation (Struc-Bench)

Tang et al. (2023) built a text-to-table benchmark in raw text, HTML and LaTeX tables from RotoWire and The Stack. On RotoWire, MTurk annotation found just 3% of GPT-3.5 outputs and 9% of GPT-4 outputs fully accurate. They fine-tuned LLaMA-7B on format descriptions that GPT-3.5 wrote for each target table (FormatCoT). It reached SacreBLEU 90.6 on raw-text tables against 68.13 for GPT-4, and 89.13 against 78.15 on LaTeX, while GPT-4 narrowly won on HTML (79.25 against 77.50) (self-reported). The un-finetuned 7B model scored 9.9, so that row cannot separate the effect of FormatCoT from that of ordinary fine-tuning. The GPT-3.5 judged P-Score tracked human content scores at 0.5301 and the heuristic H-Score at 0.1059. Limits: no fine-tuning settings or variance, the FormatCoT ablation is one qualitative example, and model versions are unstated.

## See Also
- [[Prompt Engineering]] — related (part of)
- [[Stop Sequences and Completion Anatomy]] — extends
- [[Tool Definitions as Prompts]] — extends
- [[XML Prompt Structuring]] — alternative-to
- [[Graded-Uncertainty Enrichment Contract]] — extends (how a schema represents what the model could not determine)
- [[Length Limits Are a Fit Layer, Not a Prompt]] — extends (length and layout limits enforced in code after generation)
- [[Free Text With Deterministic Repair Over SDK-Enforced Schema]] — alternative-to (a decision to keep text generation plus a deterministic repair chain)
- [[Python Type Hints and Dataclasses]] — related (Pydantic validation at the boundary for LLM output)
- [[Runtime Validation with Zod]] — related (the code-side parse that pairs with the constrain rung)
- [[TypeScript for AI Apps]] — instance-of (zod output format plus parsed_output null and refusal checks)
- [[Jev Decision Model]] — related (a model whose whole output is schema-restricted)
- [[Outlines Guided Generation]] — instance-of (FSM index and logit mask)
- [[Ctrl-G HMM Logical Control]] — instance-of (HMM and DFA constraint control)
- [[Chain-of-Table]] — related (table-reasoning prompt format)
