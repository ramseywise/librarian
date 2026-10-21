---
title: Review Preview Over the Production Pipeline
tags: [eval, pattern]
summary: "To let a human review an unpublished backlog in the shape a user would see it, reuse the production ranker and card behind a sibling candidate source, split the visibility predicate out of the eligibility filter, tag every preview slate with its own log surface and audit every reader of that log, and make \"approve\" write a verdict row rather than a second publish path."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-19-dis337-hitl-review-feed.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-19-dis337-hitl-review-feed.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-19-dis337-hitl-review-feed.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-19-dis337-hitl-review-feed.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-19-dis337-hitl-review-feed.md
---

# Review Preview Over the Production Pipeline

A plan in akira (2026-09-19) for reviewing a 386-row draft backlog. The goal was a
**slate-shaped** review view, with the same ranker, the same result card and the same
alternatives block a consumer sees. The reviewer then judges each row the way it will
actually be served, not as a database row. Two constraints shaped the design. No
unpublished row may reach a production surface. And no preview slate may contaminate the
logged metrics the ranker is measured against.

## The moves

1. **Split the visibility predicate out of the eligibility filter.** The single
   hard-filter function had eleven exclusion reasons. Two of them gated *visibility*
   (not published, needs review). Nine gated *fit to the moment* (expired, wrong district,
   sold out, and so on). The plan split it into `visibilityReason` and `momentFitReason`
   and kept the original as their composition (`visibility ?? momentFit`). All four
   existing callers compile unchanged, rollback is "revert one function", and the preview
   path calls only the fit half. About 30 lines moved and no logic changed.
2. **Add a sibling candidate source; don't fork the pipeline.** The production source
   applied the published-only narrowing **five times** across one 938-line file. The
   preview source copies its shape (columns, chunking, quarantine, joins) with those
   `eq()` calls dropped. The single swap point (`getRecommendations`) needs zero
   changes: only the source passed in and the request's `surface` differ. Shared helpers
   are extracted by literal cut-paste, with the existing test suite green and zero fixture
   edits, *before* any new test is written. The file already carried eight review-round
   corrections, and a careless extraction would reintroduce them.
3. **Give preview slates their own log surface, and audit every reader in the same PR.**
   `ResultSetLog.surface` grows a `'preview'` value. Consumers typed as
   `Record<Surface, …>` fail at compile time, which is good. The dangerous readers are
   the untyped ones:
   - The admin dashboard selected all result sets unconditionally. It gets
     `.neq('surface','preview')`, plus an explicit id-set intersection wherever an
     aggregate reads the interactions table directly instead of through the filtered
     result sets. A child table keyed by `result_set_id` is only excluded if every
     aggregate actually joins through the filtered parent.
   - The retention job archived expired result sets into a **replay corpus**. It now
     deletes preview rows without copying them, so the corpus never absorbs operator
     traffic. Its return value (`v_moved`) still means what its name says.
   - Done-when for each reader: *a fixture-seeded preview row moves none of the rendered
     numbers*.
4. **"Approve" writes a verdict, never a publish.** Publishing stays the one scripted,
   reversible path. An approve button that flipped `needs_review` would be a second
   visibility workflow, which the repo's rules forbid. Verdicts go to a narrow review table.
   The existing graded-rater table was rejected because using it would mean fabricating a
   rater id and a ranker version that don't describe what happened.

## A review render must carry every distinguishing field

Reusing the consumer card brought along a known gap: the card did not render the two
fields that tell one bar from another. On the consumer page that was a missing nicety. On
a review surface it is a **correctness defect**: the verdict written to the HITL table
would be a verdict on an incomplete render. The fix went into the review wrapper, not the
consumer card, so the consumer-side follow-up stayed independently decidable. Threading
the fields also meant adding them to the card-payload builder: the wrapper cannot render
a field the wire response never carries.

## Where it diverges from "never fork"

Alternatives on the production path are computed once, at composition time, and are
similarity-only. The preview surface wanted a similar/nearby toggle, so its route computes
both lists server-side from the already-eligible pool. That doubles the alternatives
compute for low-volume operator traffic. The plan flagged it explicitly so it would not be
copied into the production route later.

## See Also
- [[One-Sided Label Control]] — extends (the same review feed, later scoped to a labelling sample)
- [[Append-Only Human Labels]] — related (where the verdict rows belong)
- [[Frozen Version Stamps on Logged Results]] — related (why fabricated rater or version stamps were refused)
- [[Data Clusters by Writer and Trust]] — related (preview traffic as measurement that must not pollute measurement)
- [[Every Column Names Its Reader]] — related (the "second visibility workflow" rule)
