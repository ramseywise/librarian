---
title: Graded-Uncertainty Enrichment Contract
tags: [prompting, llm, eval, pattern]
summary: An LLM annotation schema that separates three levels of not-knowing — non-blocking `uncertainty_flags`, a usable-but-incomplete `enrichment_status=partial`, and a blocking `needs_review` with a reason — so sparse input lowers certainty rather than quality scores, enums carry `unknown` while multi-selects use empty arrays, and the downstream gate routes `partial_but_usable` items to production instead of a review backlog.
updated: 2026-10-30
sources:
  - data/raw/claude-docs/diskoe/docs/notion/ai-enrichment.md
  - data/raw/claude-docs/playground/docs/notion/ai-enrichment.md
  - data/raw/claude-docs/diskoe/docs/notion/review-gate.md
  - data/raw/claude-docs/playground/docs/notion/review-gate.md
  - data/raw/claude-docs/diskoe/docs/notion/taxonomy.md
  - data/raw/claude-docs/playground/docs/notion/taxonomy.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-24-dis384-measurement-loop.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-24-dis384-measurement-loop.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-24-dis384-measurement-loop.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-24-dis384-measurement-loop.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-24-dis384-measurement-loop.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-24-dis384-measurement-loop.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-24-dis384-measurement-loop.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-24-dis384-measurement-loop.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-24-dis384-measurement-loop.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-24-dis384-measurement-loop.md
---

# Graded-Uncertainty Enrichment Contract

The output contract for an offline LLM enrichment stage that annotates catalogue items
(events, venues) with a fixed taxonomy, from the diskoe product specs. It is a
[[Structured Output]] schema, but the interesting part is not the field list — it is how
the schema represents *what the model could not determine*, and how a deterministic gate
downstream reads that.

## Field status, not field presence

Every field is declared **Required**, **Expected**, or **Optional**. A missing Required
field is a contract violation (blocking); a missing Expected field is normal and recorded;
Optional fields are bonuses. The distinction lets the gate be strict about the few
fields serving actually depends on without rejecting every thin listing.

## How "unknown" is spelled depends on the type

- Single-value enums carry an explicit `unknown` member. The schema is flat — bare
  enums, no nested confidence objects — because per-field confidence is noise the
  reader cannot act on.
- Multi-selects use the **empty array**, never `["unknown"]`: an `unknown` tag inside a
  set would match a filter as if it were a real tag.
- Uncertainty is recorded at **record level**, not per field.
- There is **no public numeric AI-confidence score**. A 0.73 on a card invites the user
  to calibrate against a number nobody calibrated.

## Three levels of not-knowing

| Level | Field | Blocks publish? | Meaning |
|---|---|---|---|
| 1 | `uncertainty_flags` (set) | No | "I inferred this from weak evidence" — read by the ranker as a mild penalty |
| 2 | `enrichment_status = partial` | No | Usable but incomplete; Expected fields missing |
| 3 | `needs_review = true` + `review_reason` | Yes | Something the model cannot resolve and a human must |

The central rule: **information completeness is not content quality.** A sparse source
must *not* lower the item's fit/value scores or trip `needs_review` on its own. Sparse
input lowers certainty (level 1–2), and the ranker applies a bounded uncertainty penalty
(see [[Specificity-Adaptive Ranking and Slate Composition]]). Conflating the two makes
the catalogue systematically prefer whoever writes the longest listing — the same bias
an uncalibrated judge shows (see [[LLM Grader Calibration Insights]]).

`not_recommended` is a verdict about fit, not a delete: the row stays, with the reason,
so a later taxonomy change can revisit it.

## The gate reads the levels

The review gate maps enrichment output to one of four routes:
`auto_approved` / `partial_but_usable` / `manual_review_required` / `reject_or_exclude`.

- It checks **operational safety** (Required fields present, no contradiction with hard
  source facts, no blocking flag), not attribute correctness — a human cannot review
  every vibe tag, and should not try.
- **`partial_but_usable` is the anti-backlog mechanism.** Without it every level-2 item
  queues for a reviewer, the queue grows faster than anyone reads it, and the catalogue
  stalls. Partial items ship with their uncertainty visible to the ranker.
- **If rejection is uncertain, route to review**, never to reject: a wrong exclusion is
  invisible, a wrong inclusion is reported.
- When the gate itself uses a model, it must come from a **distinct prompt lineage** from
  the enrichment prompt. A gate that shares the enricher's prompt family inherits its
  blind spots and agrees with it by construction.

## Taxonomy hygiene the contract depends on

The schema stays scorable only if the taxonomy keeps `format`, `category`, `vibe`,
`context`, `plan_role` and `audience` as separate axes and splits `decision_signals`
(machine-read) from display copy (human-read). "A tag should earn its place": a value
with no reader is removed, so the model never spends tokens classifying into a bucket
nothing consumes.

## Measured: forbid inference from kind or from absence (akira, 2026-09-24)

A venue-enrichment probe's judge flagged two recurring defects:
`assumed_from_venue_kind`, where a vibe, audience or price was inferred from the venue
*type*, and `casual_from_absence`, where "casual" was inferred from a *lack* of evidence.
One added prompt instruction forbade both. On a pinned 40-venue sample (one probe run and
one judge run against the previous version's stored results, no fresh re-call of the old
version), judge pass rate went from 0.875 to **0.974**. `assumed_from_venue_kind` fell from
23 to 12 and `casual_from_absence` from 6 to 3. Mean tags kept fell slightly in the richest
evidence band while pass rate there reached 1.0. That was read as the instruction correctly
declining weakly grounded tags. The measurement rule was to report pass rate **together
with** yield, so a drop in tag count could not pass as a quality loss, or a rise as a gain.

## See Also
- [[Structured Output]] — extends (what the schema says about absence, not just presence)
- [[HITL Annotation Pipeline]] — related (level 3 is the HITL hand-off; levels 1–2 keep most items out of it)
- [[Evidence-Labelled Generation with Deterministic QC]] — related (the deterministic check that reads this contract)
- [[Specificity-Adaptive Ranking and Slate Composition]] — prerequisite-for
- [[LLM Grader Calibration Insights]] — related (verbosity bias as the failure this rule guards against)
- [[Human Agreement Ceiling Protocol]] — related (the subjective fields here are the ones whose accuracy is a category error)
- [[Confidence That Is Not a Probability]] — extends (why a numeric confidence can't be calibrated or escalated on yet)
- [[One Facet Per Fact]] — extends (one facet per kind of fact, time derived not emitted)
- [[Hide-Unknown Display Contract]] — related (abstention upstream, hidden field downstream)
- [[Capped Tiered Tag Assignment]] — related (how many tag values an item gets)
- [[Fixed-Rule Clusters With a Degeneracy Gate]] — related (`unknown` treated as a value when grouping)
