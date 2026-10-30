---
title: Human Agreement Ceiling Protocol
tags: [eval, pattern, conflict]
summary: Before trusting any LLM-judge score on a subjective dimension, measure how well humans agree with each other on the same items (κ_HH) — the judge target is κ_judge ≥ 0.8 × κ_HH, not an absolute number — using quadratic-weighted κ for ordinal scales, Krippendorff's α with MASI distance for multi-select tags, per-tag binary κ, bootstrap 95% CIs, ~100 items (±0.1 CI), and 3–5 scene-literate raters recruited by name before the rating sheet is designed.
updated: 2026-10-30
sources:
  - data/raw/claude-docs/playground/docs/open-questions.md
  - data/raw/claude-docs/akira/docs/research/2026-08-27-b15-kappa-protocol.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-08-27-b15-kappa-protocol.md
  - data/raw/claude-docs/akira/docs/open-questions.md
  - data/raw/claude-docs/kiez-archive/docs/open-questions.md
  - data/raw/claude-docs/akira/docs/onboarding-comments.md
  - data/raw/claude-docs/kiez-archive/docs/onboarding-comments.md
  - data/raw/claude-docs/diskoe/docs/research/2026-08-27-b15-kappa-protocol.md
  - data/raw/claude-docs/playground/docs/research/2026-08-27-b15-kappa-protocol.md
  - data/raw/claude-docs/diskoe/docs/open-questions.md
  - data/raw/claude-docs/diskoe/docs/onboarding-comments.md
  - data/raw/claude-docs/playground/docs/onboarding-comments.md
  - data/raw/claude-docs/akira/docs/technical-feasibility.md
  - data/raw/claude-docs/diskoe/docs/technical-feasibility.md
  - data/raw/claude-docs/playground/docs/technical-feasibility.md
  - data/raw/claude-docs/kiez-archive/docs/technical-feasibility.md
  - data/raw/claude-docs/akira/docs/plans/2026-08-27-3c2-scene-positioning.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-08-27-3c2-scene-positioning.md
  - data/raw/repos/akira/.claude--docs--plans--2026-08-27-3c2-scene-positioning.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-08-27-3c2-scene-positioning.md
  - data/raw/claude-docs/playground/docs/plans/2026-08-27-3c2-scene-positioning.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-08-27-3c2-scene-positioning.md
  - data/raw/repos/playground/.claude--docs--plans--2026-08-27-3c2-scene-positioning.md
  - data/raw/claude-docs/akira/docs/plans/2026-08-27-b15-kappa-protocol.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-08-27-b15-kappa-protocol.md
  - data/raw/repos/akira/.claude--docs--plans--2026-08-27-b15-kappa-protocol.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-08-27-b15-kappa-protocol.md
  - data/raw/claude-docs/playground/docs/plans/2026-08-27-b15-kappa-protocol.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-08-27-b15-kappa-protocol.md
  - data/raw/repos/playground/.claude--docs--plans--2026-08-27-b15-kappa-protocol.md
  - data/raw/claude-docs/akira/docs/plans/2026-08-27-b25-rater-ui.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-08-27-b25-rater-ui.md
  - data/raw/repos/akira/.claude--docs--plans--2026-08-27-b25-rater-ui.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-08-27-b25-rater-ui.md
  - data/raw/claude-docs/playground/docs/plans/2026-08-27-b25-rater-ui.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-08-27-b25-rater-ui.md
  - data/raw/repos/playground/.claude--docs--plans--2026-08-27-b25-rater-ui.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-03-dis28-kappa-rater-study.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-03-dis28-kappa-rater-study.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-03-dis28-kappa-rater-study.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-03-dis28-kappa-rater-study.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-03-dis28-kappa-rater-study.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-03-dis28-kappa-rater-study.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-03-dis28-kappa-rater-study.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-24-dis274-judge-kappa-vocab-phase2.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-24-dis274-judge-kappa-vocab-phase2.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-24-dis274-judge-kappa-vocab-phase2.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-24-dis274-judge-kappa-vocab-phase2.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-24-dis274-judge-kappa-vocab-phase2.md
  - data/raw/repos/nonprofit-success-ai/.claude--docs--plans--2026-10-07-r10-eval-metrics.md
---

# Human Agreement Ceiling Protocol

A model-enriched events catalogue (repo akira) scored items on subjective dimensions —
vibe, energy, audience fit — with an LLM judge, and reported "98.8% agreement" with
humans. The protocol asks the prior question: **how much do humans agree with each
other?** Without that number every subjective metric for the next year is
uninterpretable, and a team can spend months optimising toward a target that does not
exist. The planning doc ranked this the highest information-per-euro item available:
~33 rater-hours, no pipeline, no traffic.

## The ceiling rule

The judge is not scored against 1.0. It is scored against the human-human agreement on
the same items:

```
κ_judge ≥ 0.8 × κ_HH        → judge is usable on this dimension
κ_HH itself < 0.4            → the dimension is not reliably ratable; fix the rubric or drop it
```

A judge at κ = 0.55 on a dimension where humans reach 0.6 is excellent; the same judge at
0.55 where humans reach 0.9 is weak. Reporting the judge number alone hides which.

## Statistic per scale type

| Dimension shape | Statistic | Why |
|---|---|---|
| Ordinal (low/medium/high) | Cohen's κ, **quadratic weights** | adjacent disagreement costs less than distant |
| Multi-select tags | **Krippendorff's α with MASI distance** | partial set overlap is partial agreement; plain κ treats {a,b} vs {a} as total disagreement |
| Each tag in isolation | per-tag binary κ | shows which tags drive a low α |
| Nominal single choice | Cohen's κ (unweighted) or Fleiss for >2 raters | |

Every statistic ships with a **bootstrap 95% CI (2000 resamples)**. The gate is on the
lower bound, not the point estimate — the same move the product metrics made ("95% lower
bound exceeds 0.60", not "wins ≥70%").

## Sample and raters

- **n ≈ 100 items** gives a CI of roughly ±0.1 on κ, enough to tell 0.4 from 0.6 but not
  0.6 from 0.65. Sampling is stratified across the rubric's categories so sparse
  categories are represented.
- **3–5 raters, scene-literate**, recruited *by name* before the sheet is designed. Random
  raters cannot judge a niche basement show; the validity of the whole exercise is a
  sourcing decision, not an analysis one.
- **Spreadsheet first.** One sheet, items as rows, raters as tabs, a short rubric per
  column. No tooling until the first pass shows the rubric holds.
- **Do not block the eval harness on it.** The harness runs with deterministic graders
  at 1.0 and the judged dimensions marked ungated until κ_HH arrives; the ceiling study
  sets their gates, it does not delay everything else.

## What "agreement" numbers often hide

The product's headline 77.8% Top-5 hit rate came from **human-curated** sets, N=6, three
clustered tasks each, **with a pre-specified answer key**. That is a ceiling for curation
with the rubric in hand, not a measurement of the automated system — see
[[Validated Concept vs Unmeasured System]]. The same scrutiny applies to any judge
agreement figure: agreement with whom, on what sample, with what key.

## Stopping, anchoring and weight caps (feasibility study, 2026-10)

- Track **ρ = κ_machine-human / κ_human-human**; stop optimizing the judge at ρ ≥ 0.9.
- **Anchored rubrics** — scale-use variance between raters inflates apparent subjectivity.
- Record each rater's position in the domain (e.g. scene insider vs outsider) as a
  covariate; two distinct ceilings across rater groups is a product finding, not noise.
- Below κ_HH ≈ 0.3 there is no construct; **cap each dimension's ranking weight by its κ_HH**
  and decompose it (see [[Decompose Low-Ceiling Dimensions into Checkable Sub-Signals]]).

## Agreement as a Build Gate for a New Dimension (akira scene positioning, 2026-08)

A plan to add an LLM-judged "scene positioning" dimension put the human-agreement check
*before* any engineering:

- **The gate is κ_HH ≥ 0.4 over ≥ 80 items.** If two humans cannot agree at that level, suspend
  the dimension and document why. Don't build an enrichment the humans cannot ground.
- **Start narrow on the scale.** A 3-band ordinal was preferred over a 5-point scale. You can
  widen a scale later by splitting bands, but you cannot narrow one without collapsing history.
  Once enrichment rows exist under the scale, it is final.
- **Two different empties.** `null` means "not enriched under this schema". `unknown` means
  "enriched, insufficient evidence". If they are merged, re-enrichment cannot tell where it
  still has work to do.
- **A new dimension means rebalancing weights,** which risks behavioural drift in ranking that
  would otherwise go unexamined. Budget that as part of the work.

## Running the study (akira B-15 and B-25 plans, 2026-08)

The execution plan for the ceiling study added lessons the research did not have:

- **The instrument decides which statistic you can compute.** A pairwise forced-choice
  rater UI (A vs B vs tie) was built alongside the plan, while the plan still said "spreadsheet,
  UI deferred". The two collect different data. Pairwise output cannot produce
  Krippendorff's α on an ordinal scale or per-tag κ, because raters never assign labels.
  Only absolute ratings give κ_HH. The κ script had been written for absolute ratings and
  would not run on pairwise exports. Resolution: run **both** with the same raters and
  corpus. Absolute ratings come first and gate the judge thresholds. Pairwise comes second:
  it is faster per item, gives Bradley-Terry win rates and percent agreement for model
  comparison, and is logged but does not gate.
- **Tie is load-bearing in forced choice.** Without a tie option, genuinely equivalent
  pairs become coin flips and pull win rates toward 50%.
- **Derived numbers are not observed numbers.** The corpus-export scripts were written and
  tested (24 green tests) but never run. "100 items" was a cap constant, not a count. A
  pre-flight step turns every derived input (item count, pair count) into an observed one
  before compensation is calculated.
- **Rater burden was under-quoted 2.4×.** The "~33 rater-hours" carried in the roadmap
  traced back to a 2-rater, partial-overlap design the plan did not use. At full overlap
  the real figures are 48 h (3 raters), 64 h (4) and **80 h (5, the target)**. "Under-quoting the
  burden is exactly how a study gets approved and then stalls at recruitment."
- **Keep model labels out of the rater export.** They go in a separate file, used only
  after collection to compute judge agreement. This prevents anchoring.
- **Screener became intake.** With friends as an unpaid first cohort, the pass/fail
  screener turned into demographic intake fields (neighbourhood, event frequency, years
  in the city, language). Exclusion was replaced by **per-cohort κ** (do residents agree
  more than newcomers?), and people outside the original "scene-literate" profile stay
  in as a contrast cohort.
- **Mid-collection check, before block 2.** If one rater marks more than 20% of items
  `unknown`, they are under-reading. If `unknown` clusters on the same items for every
  rater, the corpus description is thin (note it, don't drop the items). If every rater
  is confused by one venue, the description is the problem, not real ambiguity.
- **Never substitute a rater mid-study.** α assumes full overlap, so a replacement rating a
  different subset breaks it. Recruit 6, confirm 5, expect 4 completers. Any clarification
  goes to every rater at once, dated. Guidance given to one rater is a confound.
- **A low ceiling is a result.** If α < 0.25, record it and set the judge threshold at
  0.8 × observed. Do not widen the corpus or re-run to get a better number.
- **Unpersisted ratings are one reload from gone.** The in-memory rater UI had no storage
  layer, so the rule was to export every ~20 pairs.

## Pipeline hazards between collection and κ (akira DIS-28 execution wrapper, 2026-09)

A thin execution plan written over the protocol plan found defects in the handoff between
the rating sheet and the κ script. None of them showed up in the protocol itself:

- **Resolved decisions had not reached the body text.** The protocol's open questions
  were marked RESOLVED, but the brief, screener and compensation sections still
  described a paid, hard-gated study. Running from the body text would have run the wrong
  study. The wrapper superseded those sections for execution instead of editing them in
  place.
- **Two copies of the tag vocabulary shared 12 of 26 tags.** The sheet generator used the
  canonical list. The κ script carried its own hand-typed list. The aggregate MASI α was
  unaffected because it reads raw tag sets. The **per-tag report** was not: it would
  never compute κ for tags raters actually used, and its "most ambiguous tags" would
  surface tags raters *could not assign*. Those tags score **κ = 1.0**, because both
  raters always give 0 and the degenerate case counts as perfect agreement. That looks
  reassuring for a tag that was never in play. The fix is to import one shared constant.
  See [[The Untested Copy Wins]].
- **Gate the cheap engineering fix ahead of the slow human step.** The vocabulary fix
  takes ~30 minutes and depends on nothing human, so it gates sending the recruiting
  brief, not just running the κ script. Otherwise the wrong per-tag report is a live
  footgun for the whole collection window, and it is the output most likely to be pasted
  into a pruning decision.
- **Per-rater sheet copies need a specified merge.** Each rater got an independent copy
  with the other raters' columns deleted, which protects independence. At close-out that
  means five files, and nothing said how to merge them. Merge steps: strip the frozen
  valid-values comment row, which otherwise downloads as data and parses to `NaN` in every
  rater's first item. Diff the `event_id` column across all files, because a rater
  sorting their own copy breaks alignment invisibly. Check the merged header against the
  script's suffix-matched column pattern and `wc -l` before computing anything.
- **Invalid cells drop silently.** Any ordinal value outside the map parses to `NaN` and
  quietly removes that rater-item pair from α. Spot-check the cells, not only the header.
- **Keep raw per-rater labels.** Archive the per-rater sheets and the merged CSV outside
  the repo, not just the computed summary.
- **Under time pressure, cut raters before items.** Item count drives corpus
  representativeness. Rater count drives CI width. A wider CI on the gate costs less
  downstream than a corpus that does not represent the catalogue.
- **Keep new gate keys commented until their graders are registered.** The target checker
  silently no-ops on a key with no matching registered metric.


## Single-Operator κ_MH Against a Test-Retest Ceiling (akira, 2026-09-24)

When the only human labels come from one operator, there is no κ_HH yet. A later plan
measured judge-vs-human agreement against that operator's own binary right/wrong verdicts:

- **Pick the instrument by the label shape.** The labels were binary verdicts on a stored
  value, the same question the judges answer. So the judge as second rater gives a
  two-rater binary Cohen's κ (κ_MH), reusing the existing TypeScript function. Extending the
  Krippendorff-α script would have been wrong: that is a different instrument, over
  rater-assigned tags.
- **The ceiling is the operator's own consistency.** ρ = κ_MH / κ_retest, where κ_retest
  comes from the operator relabelling the same items later. ρ is `null` with a reason until
  retest pairs exist. It is never reported over zero pairs.
- **Score the judge on what the human saw.** The label row snapshots the value shown at seed
  time. The judge is scored on that snapshot, never on the row's current value, so a
  re-enrichment since labelling cannot change what is being compared.
- **Count the exclusions out loud.** `judge_unavailable` (the judge returned null) and
  `evidence_missing` (content row gone) are excluded from κ but counted and printed.
- **Hand-compute the tests.** Every κ in the tests is worked out in a comment: perfect, chance,
  all-one-class, and retest-row exclusion. The function is never its own oracle.
- **What the first dry run found.** There were 14 labelled rows (8 energy, 6 vibe), **all
  "right"**. An all-one-class sample makes κ undefined (`null`), so a correct tool printed
  no number. Before you schedule the judge run, check the class balance of the label queue.

## Variant: trust bar at the full inter-rater κ (nonprofit-success-ai)

One project's κ protocol for a narrative-draft judge uses a stricter bar than 0.8 × κ_HH:
20 cases × the model path, each dimension binary, Cohen's κ per dimension, and **the judge
is trusted only when judge-vs-rater agreement ≥ the inter-rater κ**. The rater-sheet
location is recorded in the harness spec, and the judge metric stays UNGATED until a keyed
run completes the protocol. This is a threshold choice, not a contradiction: both treat
human-human agreement as the ceiling, and they differ only in how much of it the judge
must reach.

## See Also
- [[HITL Annotation Pipeline]] — extends (adds the ceiling to its inter-annotator-agreement gate)
- [[LLM-as-Judge Evaluation]] — prerequisite-for (the judge is calibrated against κ_HH)
- [[Golden Set Mechanics]] — related (the rated items become the golden set)
- [[Validated Concept vs Unmeasured System]] — complements
- [[One Check Shape for Quality Verdicts]] — related (where UNGATED-until-κ lives in the check registry)
- [[Graded-Uncertainty Enrichment Contract]] — related (the enrichment vocabulary the rater instrument must import, not copy)
- [[Decompose Low-Ceiling Dimensions into Checkable Sub-Signals]] — prerequisite-for (what to do with a low ceiling)
- [[Publish Automatically, Sample for Review]] — related (an operator-graded sample as a source of labels)
- [[Blind Labels Judge No Prompt]] — extends (schema-enforced blinding for the absolute instrument that measures κ_HH)
- [[Closed Judge Vocabulary, Tolerant Parse]] — related (judge-output design in the same lane)
- [[Demote Judge Findings to Keyless Gates]] — extends (the 10-label calibration floor that precedes a κ run)
- [[Error Analysis (Open and Axial Coding)]] — extends
- [[Judge Calibration (TPR, TNR and Corrected Pass Rate)]] — extends
