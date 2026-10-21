---
title: Spend Gate Before the Model Call
tags: [llm, infra, pattern]
summary: A pure, deterministic gate that decides whether a model call is worth making before a token is spent — skip on an unchanged input hash (which includes the prompt and vocabulary versions), skip when the evidence is too thin to support an answer, write a rules-only row for what deterministic mapping can already say — with every outcome counted so the cost of a run is one number.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/kiez/docs/enrichment.md
  - data/raw/claude-docs/kiez/docs/env.md
  - data/raw/claude-docs/akira/docs/plans/2026-08-26-b14a-index-page-filter.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-08-26-b14a-index-page-filter.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-08-26-b14a-index-page-filter.md
  - data/raw/claude-docs/playground/docs/plans/2026-08-26-b14a-index-page-filter.md
  - data/raw/repos/akira/.claude--docs--plans--2026-08-26-b14a-index-page-filter.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-08-26-b14a-index-page-filter.md
  - data/raw/repos/playground/.claude--docs--plans--2026-08-26-b14a-index-page-filter.md
  - data/raw/claude-docs/akira/docs/plans/2026-08-26-b23-content-hash-gate.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-08-26-b23-content-hash-gate.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-08-26-b23-content-hash-gate.md
  - data/raw/claude-docs/playground/docs/plans/2026-08-26-b23-content-hash-gate.md
  - data/raw/repos/akira/.claude--docs--plans--2026-08-26-b23-content-hash-gate.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-08-26-b23-content-hash-gate.md
  - data/raw/repos/playground/.claude--docs--plans--2026-08-26-b23-content-hash-gate.md
  - data/raw/claude-docs/akira/docs/reviews/2026-08-26-b23-content-hash-gate.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-08-26-b23-content-hash-gate.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-08-26-b23-content-hash-gate.md
  - data/raw/claude-docs/playground/docs/reviews/2026-08-26-b23-content-hash-gate.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-08-26-b23-content-hash-gate.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-08-26-b23-content-hash-gate.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-08-26-b23-content-hash-gate.md
  - data/raw/claude-docs/akira/docs/plans/2026-08-27-b50-spend-ledger.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-08-27-b50-spend-ledger.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-08-27-b50-spend-ledger.md
  - data/raw/claude-docs/playground/docs/plans/2026-08-27-b50-spend-ledger.md
  - data/raw/repos/akira/.claude--docs--plans--2026-08-27-b50-spend-ledger.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-08-27-b50-spend-ledger.md
  - data/raw/repos/playground/.claude--docs--plans--2026-08-27-b50-spend-ledger.md
  - data/raw/claude-docs/akira/docs/plans/2026-08-27-b63-spend-observability.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-08-27-b63-spend-observability.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-08-27-b63-spend-observability.md
  - data/raw/claude-docs/playground/docs/plans/2026-08-27-b63-spend-observability.md
  - data/raw/repos/akira/.claude--docs--plans--2026-08-27-b63-spend-observability.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-08-27-b63-spend-observability.md
  - data/raw/repos/playground/.claude--docs--plans--2026-08-27-b63-spend-observability.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-30-dis438-enrichment-queue-e2e.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-30-dis438-enrichment-queue-e2e.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-30-dis438-enrichment-queue-e2e.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-30-dis438-enrichment-queue-e2e.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-30-dis438-enrichment-queue-e2e.md
---

# Spend Gate Before the Model Call

In the kiez venue-enrichment graph, `gate.py` is a pure function that runs after evidence
has been collected and shaped and before anything is sent to a model. It exists so that
the expensive step is only taken when it can produce something new and defensible.

## The gate, in order

1. **Unchanged.** `input_hash = content_hash({shaped input, PROMPT_VERSION, TAGS_VERSION})`.
   If the current row's hash equals the new one, skip. Because the hash covers the prompt
   and the tag-vocabulary version, bumping either re-enriches *everything*, while
   unchanged evidence never does. The same idea is applied again downstream: the
   embedding carries its own hash over its text plus the embedding model, so an unchanged
   text is not re-embedded.
2. **Enough prose.** Send only if a long-form source has ≥ 200 chars of prose, or a short
   structured description plus a shorter own-site snippet both exist. Otherwise skip with
   a named reason (`no_prose` vs `prose_too_thin`) — two reasons, because they call for
   different fixes.

## Rules-only rows

A venue the gate turns away still gets a row when deterministic mapping from its source
tags yields facet values: `model = 'rules'`, no summary, QC verdict `pass` with reason
`rules_only`. It carries an `input_hash`, so the next run skips it as unchanged until new
evidence arrives. Nothing is sent to a model for it. The gate therefore separates "what
we can say without a model" from "what a model could add," and only pays for the second.

## Evidence score a reader can recompute

`evidence_score` is the share of five plain checks that hold (a long prose item; prose
from two sources; a structured-data item; an own-site item; enough source tags). It is
deliberately not learned so that anyone can recompute it by hand from the row.

## Spend is an explicit switch

Billable calls are refused unless `KIEZ_ALLOW_SPEND=1` is set — on both the pipeline and
the web model seams. `--dry-run` calls no model and prints each venue's gate verdict and
the prompt that *would* be sent; `--fake` substitutes a canned responder for local
end-to-end runs. The run logs one count per outcome (`selected`, `sent`,
`gated_unchanged`, `gated_no_prose`, `gated_prose_too_thin`, `rules_only`,
`written_pass|review|fail`, …) and **the cost of a run is `sent`**.

## A Review Flag Is Not a Spend Gate (akira, 2026-08)

In akira's event pipeline, an index-page detector flagged rows for review. The paid enrichment
handoff was still sent unconditionally, before any human saw the flag. The plan's placement
rules:

- **Gate at the call site where the verdict is consumed.** Not inside the classifier, which
  stays pure and I/O-free. Not at persistence either, because by then the call has been billed.
- **Key the gate on the specific verdict (`isIndexPage`), not the broad `needsReview` flag.**
  The broad flag also covers thin but real events, so gating on it would quietly stop
  enrichment for legitimate rows.
- Record "skipped because not useful" separately from "skipped because not possible".
- The gate and the cleanup script share one heuristic. Cleanup rejects rather than deletes and
  defaults to dry-run.

## Input-Only Hash Variant (akira content-hash gate, 2026-08)

A second gate skips re-enrichment when the scraped input has not changed. It computes SHA-256
over the handoff payload with sorted keys, excluding volatile fields (`content_id`,
`raw.scraped_at`):

- **The hash covers the input only, not the prompt or model.** A prompt or model change
  therefore leaves stale enrichments in place. The plan records this as a known limitation.
  This differs from designs that fold a prompt version into the key (above). It is a narrower
  variant, not a contradiction.
- **Legacy rows bootstrap once.** A null stored hash never matches, so each legacy row is
  enriched once and then gated.
- **A skip is not a failure.** The result is `handoff_skipped` with `errorType: 'hash_match'`,
  so skips do not inflate the failure rate that source-health monitoring reads.
- **A failed hash lookup falls through to re-enrichment** (from the review). If the gate's own
  DB read errors, the safe default is to pay for the call, not to skip work silently.

## Ledger Coverage Is a Per-Call-Site Table, Not a Docstring (akira, 2026-08)

A model-bounds module's docstring said "both model call sites" were covered by the spend
ceiling. That was half true. Writing it out as a table (call site × timeout × retry cap ×
ledger) showed that the QC evaluator had a timeout and retries but no ledger, and that the
LLM-judge base class had none of the three. Rules from the fix and its review:

- **Fix latent gaps before promotion.** Both uncovered sites were reached only from manual
  scripts. The risk was promoting either one to a per-event pipeline stage *while the gap
  was open*, where a runaway bills the whole batch before the ceiling fires.
- **Credit the ledger even when the model errors.** Record usage before branching on
  success, because the provider bills failed calls.
- **Count billed-but-unknown attempts.** `record()` returned early when `usage` was falsy,
  which is correct for token counts (they can't be guessed) but wrong for the *calls*
  counter. A timeout therefore left `calls` unchanged, inflated the per-call average, and
  hid the attempt from the ceiling. Count the attempt even with empty usage.
- **Track cached tokens separately from the ceiling input.** They are billed differently,
  and folding them in misstates both spend and cache effectiveness.
- **Check the test's assertion against the plan.** The shipped ceiling test asserted
  `spent === 0` where the plan specified 7. It was inverted, so it would have passed with the
  ledger credit missing.

## One Pre-Spend Queue Table Before a Batch Move (akira #438, 2026-09-30)

A 4,529-row batch had been submitted in which only 16 rows carried homepage text. Every
request was about 3,800 tokens, roughly 93% of it the fixed system prompt, and the output
would have been low-confidence rows that the load floor drops anyway. Before the next batch
move, the plan built **one table** with a row per entity across all four verticals. Each row
says what source data is held, how complete and relevant it is, which pre-spend gates pass
and why not, the verdict (enrich or skip), and the **exact model request** it would send.

- **An evidence gate with an ordered first-failing reason.** For venues, a row passes on
  site text of at least 400 chars, or else on a description of at least 200 chars, since the
  probe verifies quotes against both. Otherwise it fails with the first reason that applies:
  `no_website`, `site_not_probed`, `rights_withheld`, `site_no_text`, `thin_text`. The eval
  fixtures were hand-written from the rule text and never produced by running the function,
  and the metric was gated at 1.0. The gate is advisory at first: the queue builder reads it,
  and wiring it into the batch path is a follow-up.
- **Gates are marked blocking or informational.** Having a website and the relevancy phase
  are informational. Evidence and not-already-enriched are blocking.
- **The payload is the real request.** The queue row's payload is built by the production
  prompt builder. Its token estimate is labelled as the chars/4 proxy, and the e2e run
  records measured usage beside it so the two can be calibrated against each other.
- **The e2e run writes nothing to the database.** It calls `generate()` and the pure
  pipeline, never the writing runner, and it is a dry run unless explicitly confirmed. All
  418 content rows were skipped for real reasons, so the run got an `--include-enriched`
  flag that samples rows blocked *only* by the already-enriched gate.
- **The first live read surfaced four read-path defects.** These were: an `.in()` over
  about 9k ids returned HTTP 414 (fixed by chunking at 200); external OSM ids were sent to a
  uuid column; a column name was wrong; and two verticals read `title` where they store
  `name`, so every row failed `missing_title`. Separately, QC received only `{id}`, so the
  deterministic precheck rejected every event before any model call. **A summary-shaped
  synthetic input always fails the precheck**, so payloads have to carry the source row.
  The tests were changed to assert this real behaviour, not to fake fields to force a pass.
- **Report a lever against the right denominator.** The gate's effect was first computed
  as more than 100% and then re-based on the ungated queue (58.4%).

## See Also
- [[Evidence-Labelled Generation with Deterministic QC]] — prerequisite-for (what happens to the calls that pass the gate)
- [[Kiez Project]] — instance-of
- [[Webhook Handler Idempotency]] — related (idempotency by content identity, applied to inbound events)
- [[Prefix Caching]] — related (another lever on the same cost)
- [[CRAG Retry Logic]] — related (a confidence gate after retrieval, rather than before generation)
- [[Shadow Signal Before Gate Change]] — extends (how to change the hash the gate keys on with evidence)
- [[Sanitize Never Fails, Validate Never Mutates]] — related (the stages after the gate in the same chain)
- [[Offline Annotation over Online Inference]] — related (the decision that makes this gate the smaller of two cost levers)
- [[Budget Without a Meter Is a Preference]] — related (the meter that tells you a gate saved money)
- [[Model Gateway Is Transport, Call Site Owns Meaning]] — related (why the gate is not inside the gateway)
- [[A Capped Run Is Not a Clean Run]] — extends (the run-level signal when the gate starts refusing)
