---
title: Length Limits Are a Fit Layer, Not a Prompt
tags: [prompting, pattern]
summary: Word and character limits for layout-bound generation are a deterministic problem — let the model write, enforce `maxLength` (characters, not words) in the schema, truncate or reflow in code after generation, and cap the validate-and-retry loop at 2–3 attempts before falling back to deterministic repair, because prompt-stated limits fail 5–20% of the time and retry error messages drift.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/sisyphus/docs/research/2026-08-08_ml6-prototyping_io-boundary.md
  - data/raw/claude-docs/sisyphus/docs/research/2026-08-08_ml6-prototyping_orchestration.md
  - data/raw/claude-docs/sisyphus/docs/research/2026-08-08_ml6-prototyping_loop-and-presentation.md
  - data/raw/repos/galactus/CLAUDE.md
  - data/raw/repos/galactus/README.md
---

# Length Limits Are a Fit Layer, Not a Prompt

Research for a take-home that turns source PDFs into a templated marketing document (fixed
fields, word limits, image placeholders, theme colours) concluded that the most important
design decision was *not* in the prompt: **fitting content into a layout is deterministic
work, and belongs in code after generation.** Medium-confidence web research; the
mechanism is the durable part.

## Why the prompt can't own the limit

- Models learn output length during fine-tuning; a stated maximum is a soft learned
  tendency, not a boundary. Exact word/character limits fail roughly 5–20% of the time.
- When a model hits a token cap mid-generation it stops rather than finishing gracefully.
- Reliability tiers: prompt-only limits ~80–95% compliance; forced tool-use ~95–99%;
  native constrained decoding (JSON-Schema mode) ~100% *structural* compliance.
- Even constrained decoding cannot enforce semantic compliance — "factually correct about
  the source" is a grounding problem, not a structure problem.

## The two-stage shape

1. **Generate** — ask for each field without obsessing over the limit; the schema is visible
   so the model self-regulates somewhat.
2. **Fit** — deterministic post-processing: character-level truncation at a sentence
   boundary, reflow, placeholder resolution. 100% reliable.

Express limits as **`maxLength` in characters**: JSON Schema has no word-count keyword, so
convert (~5 chars/word; 150 words ≈ 750 chars). Constrained-decoding engines enforce
`maxLength` at the token level. For nested sections, FSM-based engines struggle with deep
recursion; CFG-based ones handle it.

## Bounded repair

Validation failure → retry with the validation error as context, but:

- **Cap at 2–3 retries.** Each is a full inference call; budget 2–3× cost if retries are
  common. Past 3, failures are effectively deterministic.
- **Error-message drift:** repeated "fix this" rounds degrade the error context and the
  model diverges further. After 2, switch to deterministic repair (placeholders, defaults).
- **Valid-but-useless output:** a string field padded with `\n\n\n…` to the token limit is
  schema-valid. Add semantic validators that reject empty/whitespace-only fields.

## Provider portability leaks at the edges

A single Pydantic model can emit JSON Schema for every provider, but the abstraction leaks:
one provider wraps the schema as a forced tool call (and streams the tool block only at the
end), others take a response-format schema directly and stream natively; errors surface
differently. A validate-and-retry wrapper library is the minimal portable tool for a single
extraction call; a full agent framework is overkill for it.

## See Also
- [[Structured Output]] — extends (the fit layer is what structured output cannot do on its own)
- [[Evidence-Labelled Generation with Deterministic QC]] — extends (same split: model generates, pure code decides)
- [[Canonical Document IR for Ingest]] — prerequisite-for (the typed payload the generator consumes)
- [[Loop Detection and the Two-Retry Rule]] — extends (bounded retries, same ceiling)
