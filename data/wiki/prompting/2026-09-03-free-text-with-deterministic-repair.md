---
title: Free Text With Deterministic Repair Over SDK-Enforced Schema
tags: [prompting, llm, decision]
summary: "Decision (akira, 2026-09): keep enrichment on plain text generation plus a deterministic sanitize/validate chain instead of SDK-enforced structured output, and amend the requirement that claimed API-layer enforcement. None of the three deciding criteria was measured, measuring token cost would mean half-building the alternative, and the rewording itself had to name each path's real mechanism, because every uniform claim (including the corrections) turned out false."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-03-dis126-ratify-dc2.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-03-dis126-ratify-dc2.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-03-dis126-ratify-dc2.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-03-dis126-ratify-dc2.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-03-dis126-ratify-dc2.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-03-dis126-ratify-dc2.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-03-dis126-ratify-dc2.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-03-dis126-ratify-dc2.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-03-dis126-ratify-dc2.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-03-dis126-ratify-dc2.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-03-dis126-ratify-dc2.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-03-dis126-ratify-dc2.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-03-dis126-ratify-dc2.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-03-dis126-ratify-dc2.md
---

# Free Text With Deterministic Repair Over SDK-Enforced Schema

## Context

A requirement row in akira's design registry claimed that enrichment output was
"structured output enforced at the API layer (tool-use schema), not by prompt". The code
called plain text generation and then ran a deterministic chain: sanitize (filter or coerce
to the vocabulary), then validate (flag), then review gate, then write. The registry's own
contradictions table recorded the mismatch. A comment in the enrichment module gave the only
argument on record:

> An SDK schema call would make the SDK responsible for enforcing shape, silently
> duplicating what the validator already does — and doing it differently. The chain
> expects raw model output so sanitize can repair it and validate can report what it could
> not.

## Decision

**Option A, ratified: reword the requirement to match the code** at all 19 sites across
four spec files (not the 13 first named). The contradiction row is deleted, not marked
resolved, because a wording contradiction has no fix to point at once the wording is
correct. Code-change contradictions keep a `FIXED` row because they have a migration to
cite.

**Option B, specified but not ratified: move to SDK structured output.** It stays executable
only if someone brings the missing measurement. Even then the repair chain would shrink, not
disappear. A schema constrains shape. It does not constrain business rules like "backfill
the plan role", cardinality caps, or per-vertical divergence. Every sanitize/validate rule
has to be checked against what the schema actually enforces before calling it redundant.

## The evidence rule

The issue's decision rule was "B only with measured evidence". All three criteria came back
unmeasured:

| Criterion | What existed | Verdict |
|---|---|---|
| Token cost | One baseline for text generation alone, flagged by its own doc as likely 6–10× too high | No comparison |
| Conformance rate | Pass-rate metrics gated at 1.0, but they test fixture correctness, not how often real output needs repair | No production rate |
| Quality delta | Judge metrics blocked on human inter-rater agreement | None |

The cost of closing each gap differs, and that difference is why the rule exists.
Conformance rate is cheap: a counter on the existing per-record run. Token cost is
**circular**: measuring it honestly means running the alternative on a comparable sample,
which is partially building B to get the evidence that would justify building B. Without
evidence, the default goes to the status quo.

## Every uniform claim was false

The reword went through two refine passes and two review rounds. Each pass replaced one
uniform claim with another, and each one was wrong:

1. The original claim: "closed enum enforced at the API layer". False for every vertical.
2. First refine: the repair chain "blocks the write outright, stronger than a schema". False
   for one vertical. Arrays are filtered and two verticals coerce scalars, but the third
   vertical's scalars pass through to storage and are only flagged.
3. Second refine: "written, but kept off the public surface by the review flag". A later
   trace found the publish script never read that flag. See
   [[Sanitize Never Fails, Validate Never Mutates]].
4. Review round 1 blocker: the new wording said "a parse failure reaches the review gate as
   `validation_failed`". In fact unparseable output returns before the gate, with no gate
   row. Out-of-vocabulary *values* inside parseable output do reach the gate. The two failure
   modes had been merged into one.

The lesson for spec text about an enforcement chain: **name the mechanism per path (field
kind × vertical × failure mode) and trace each one to its final consumer.** Keep the odd
case's clause deliberately verbose. If it reads like its siblings, a later editor will
"simplify" it back into the uniform claim. This decision changes enforcement wording, not
enforcement layer. A schema would face the same question for the vertical whose scalars
went unchecked.

## See Also
- [[Structured Output]] — alternative-to (the API-layer enforcement this decision declined)
- [[Sanitize Never Fails, Validate Never Mutates]] — extends (the repair chain and the escape the trace found)
- [[Length Limits Are a Fit Layer, Not a Prompt]] — related (the same "let the model write, enforce in code" stance)
- [[Evidence-Labelled Generation with Deterministic QC]] — related
- [[Stage-Scoped Scout Agents]] — related (the fix stage that refused a relayed blocker approval on this plan)
