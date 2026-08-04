---
title: Structured Output
tags: [llm, concept]
summary: Requesting JSON or a schema-conformant response so downstream code can parse it — reliable only when paired with harness-side validation.
updated: 2026-08-04
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt--prompt-engineering.md
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

## Format Choice

- **JSON** — the default for anything a program consumes.
- **XML tags** — better when the payload is prose that happens to need sectioning
  (`"Write your analysis in <analysis> tags"`); avoids escaping newlines and quotes. See
  [[XML Prompt Structuring]].

## See Also
- [[Prompt Engineering]] — part-of
- [[XML Prompt Structuring]] — alternative-to
