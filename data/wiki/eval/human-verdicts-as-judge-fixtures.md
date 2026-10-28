---
title: Human Verdicts as Judge Fixtures
tags: [eval, pattern]
summary: "Close the eval loop by exporting human right/wrong verdicts into judge fixtures where the judged value becomes `expected`, the human decision rides in `metadata` the judge never sees, and a `wrong` verdict is as valid a case as a `right` one; score judge-vs-human agreement on a hash-split holdout beside the human retest ceiling, and feed judge/gate disagreements back to humans as a separately tagged sample stream."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-21-dis358-eval-loop.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-21-dis358-eval-loop.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-21-dis358-eval-loop.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-21-dis358-eval-loop.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-21-dis358-eval-loop.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-21-qc-eval-loop.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-21-qc-eval-loop.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-21-qc-eval-loop.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-21-qc-eval-loop.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-21-qc-eval-loop.md
---

# Human Verdicts as Judge Fixtures

From an akira plan that wired five already-built pieces into one loop: a human label queue
(right/wrong per enrichment field), a test-retest κ ceiling over that queue, three LLM
plausibility judges graded only on hand-written fixtures, and a random human-sampling table.
Each piece worked; none fed the next.

## The fixture mapping

A label row holds the value the human judged (`label_value`) and a `decision`. A judge
fixture holds `input` (the evidence) and `expected` (the output to grade). The mapping:

- **`label_value` → `expected.<field>` verbatim.** That is exactly what the pipeline
  produced and what the judge is asked to grade.
- **`decision` → `metadata.human_decision`, never `expected`.** The fixture type's
  `metadata` is open and the judge's prompt builder serialises only `input`/`expected`, so
  the ground truth travels in the file without reaching the prompt. The decision is what
  scores the judge, not something the judge reads.
- **A `wrong` verdict is a valid case.** The judge is asked "is this defensible", not "did
  the human like it", so both kinds of verdict make fixtures. This is what gives the set
  precision as well as recall (contrast [[Positive-Only Judge Fixtures Measure Recall]]).
- **Evidence by live join, not a payload change.** The label payload had no evidence
  fields. Because content rows are never overwritten by a re-crawl and enrichment rows are
  supersede-then-insert, a join at export time rebuilds the evidence. The accepted caveat:
  if the item was re-enriched after judgment, the export reflects the current enrichment,
  not what was on screen. Snapshotting evidence at seed time would close that gap; it was
  rejected while the queue had zero production verdicts to protect, with a named revisit
  trigger ("if the export shows a meaningful re-enrichment collision rate").

## Agreement, beside the ceiling

The agreement report scores `judge.isCorrect` against `metadata.human_decision` on a
**holdout chosen by hashing the content id** (`hash("eval_holdout:" + kind + ":" + id) <
rate`). This reuses the repo's existing deterministic-split helper; see
[[Write-Time Deterministic Holdout]]. The report prints its number *beside* the human retest κ, never
re-deriving it. A judge cannot be held to more agreement than two humans reach with each
other. When the number is big enough to gate on is left as an explicit human call once real
N exists.

## Disagreement as a second sample writer

The human-sampling table already had one writer: a 10% random sample at publish. The plan
added a nullable, CHECK-constrained `sample_reason` (`random` | `qc_judge_disagreement`).
The random writer now stamps `random` explicitly, so every row says why it was sampled
from the day the column lands, with no backfill. A second writer inserts a row when the
production judge sweep disagrees with the row's QC or review-gate verdict. Each disagreement
a human resolves becomes a future fixture, which closes the loop. Keeping the random
stream separate matters: rates estimated from disagreement-sampled rows are biased by
construction, so the reason column decides which rows can feed a population estimate.

## Dependency honesty

The production sweep needed the judge rubrics moved out of the eval package, which the
lint layering forbade other code from importing. The plan shipped the export and
agreement slices inside the eval package. It did not copy the sweep logic there to get
around the wait. The blocked slices shipped later, once the move landed.

## See Also
- [[Positive-Only Judge Fixtures Measure Recall]] — extends (human `wrong` verdicts supply the negatives)
- [[Blind Labels Judge No Prompt]] — prerequisite-for (the blind label rows this exports)
- [[Write-Time Deterministic Holdout]] — instance-of (hash-of-identity split reused for the holdout)
- [[One Check Shape for Quality Verdicts]] — extends (later refactor: fixtures exported from human overturns)
- [[UNGATED Metric Convention]] — related (judges stay ungated until agreement is measured)
- [[HITL Annotation Pipeline]] — instance-of
- [[Snapshot the Judged Value on the Verdict Row]] — extends (the verdict table these fixtures are exported from)
- [[Own-Oracle Fixtures and the Blind Relabel Path]] — alternative-to (the same loop for deterministic functions)
