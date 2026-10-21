---
title: Ranker Weight Sensitivity Sweep
tags: [eval, pattern]
summary: "Turn a weight table's design thesis into a measured curve: perturb one weight at a time by ±10% and renormalise the rest (never clamp), score a synthetic pool large enough for rank correlation to mean something (≥ 20; 30 used), and report Spearman ρ, top-5 overlap, top-1 agreement, inverted-pair count and mean score delta per cell — and when adding questions lowers every absolute score, rank agreement, not score, is the metric that transfers."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-08-27-b27-sensitivity-sweeps.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-08-27-b27-sensitivity-sweeps.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-08-27-b27-sensitivity-sweeps.md
  - data/raw/claude-docs/playground/docs/plans/2026-08-27-b27-sensitivity-sweeps.md
  - data/raw/repos/akira/.claude--docs--plans--2026-08-27-b27-sensitivity-sweeps.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-08-27-b27-sensitivity-sweeps.md
  - data/raw/repos/playground/.claude--docs--plans--2026-08-27-b27-sensitivity-sweeps.md
  - data/raw/claude-docs/akira/docs/plans/2026-08-27-b17-real-data-validation.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-08-27-b17-real-data-validation.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-08-27-b17-real-data-validation.md
  - data/raw/claude-docs/playground/docs/plans/2026-08-27-b17-real-data-validation.md
  - data/raw/repos/akira/.claude--docs--plans--2026-08-27-b17-real-data-validation.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-08-27-b17-real-data-validation.md
  - data/raw/repos/playground/.claude--docs--plans--2026-08-27-b17-real-data-validation.md
---

# Ranker Weight Sensitivity Sweep

An events recommender (repo akira) chose weight profiles by how specific a request was.
Vague requests weighted vibe and context; specific requests weighted time and format.
The profiles had been copied from a design doc and never stress-tested. Two measurement
items turned the thesis into numbers without changing a single production weight.

## The sweep

**One-at-a-time (OAT), ±10%, per dimension, per profile.** That is 3 profiles × 7
dimensions × 2 directions = 42 cells. A full factorial would be 2^7 = 128 per profile.
OAT answers the question that matters ("which weight is load-bearing?") without the
combinatorial cost. A two-dimension interaction sweep is a follow-on, not a requirement.

- **Renormalise, don't clamp.** After moving one weight, spread the residual equally over
  the other six so the profile still sums to 1.0. Clamping pushes the base score off the
  0–1 scale, so comparing with the baseline means nothing. Renormalising also models the
  real tuning action: raising one weight means lowering others. ±10% spread across six
  is about 1.7% each, so the distortion is small.
- **Pool size is a precondition, not a detail.** With fewer than ~20 candidates, ρ ≈ 1.0
  for almost any ordering. The live catalogue had 9 events. The primary instrument was a
  **synthetic pool of 30** with designed spread on every dimension. The live pool sits
  behind an opt-in flag and prints `pool_size`, so the low-n warning is automatic. Check
  that the baseline score distribution has visible variance before trusting any ρ.
- **Shim parity.** Re-scoring with injected weights needs a `rankWithWeights` shim. A
  non-regression test asserts that the shim, given the production weights, reproduces
  production order exactly. Otherwise a logic fork in the shim reads as sensitivity.

## Per-cell metrics

| Metric | Why it is there |
|---|---|
| Spearman ρ vs baseline order | summary; 1.0 = no reordering |
| Top-5 overlap | the user-facing measure; a swap outside the top 5 is invisible |
| Top-1 agreement | the highest-stakes single swap |
| Inverted-pair count | churn across the whole pool, not just the top N |
| Mean absolute score delta | tells "weights moved but order held" from "order shuffled" |

Each metric is reported for production and for the equal-weight baseline
([[Adversarially Independent Baseline Arm]]). The action rule: if a ±10% shift drops
top-5 ρ below 0.80, that weight is so load-bearing that any change to it needs a new
weights version stamp. It goes on record as a design risk. (The measured sweep found no
cell below 0.80.)

## The score trap: rank agreement is what transfers

An earlier synthetic replay (60 fabricated events, 4 golden requests) found a mechanism:
**more intake questions lower raw scores.** Each answered question adds a constraint that
neutral defaults no longer cover. So absolute scores from a 3-question path and an
8-question path cannot be compared, and *ranking agreement* between the short and full
variants is the valid metric. The real-data replay's decision rule was written before it
ran:

- Monotonic score fall holds **and** ρ(short, full) ≥ 0.5 on every request → the
  synthetic curves transfer, and the short path is validated. No weight action.
- Fall holds but ρ < 0.5 on some request → that specificity level's profile needs review,
  filed as its own issue before any tuning.
- Fall does not hold → the neutral-default mechanism has changed. Re-read the pinned test
  first.

Known non-discriminating dimensions were written down as *expected* in advance. Every
real event carried the same capped uncertainty penalty, and location was neutral for all
until coordinates landed. That way they were not mistaken for findings. The replay ran
against a committed fixture that turned out to be a placeholder (pool = 0). A pool-size
guard skips the test rather than reporting trivial agreement, and an export date in the
fixture header makes staleness visible.

## See Also
- [[Specificity-Adaptive Ranking and Slate Composition]] — extends (measures the weight profiles that design specifies)
- [[Adversarially Independent Baseline Arm]] — related (the second arm every cell is reported for)
- [[Frozen Ranking Baseline from a Pure Ranker]] — related (pure ranker → offline replay is cheap)
- [[Eval Non-Determinism]] — related (determinism of the ranker is what makes ρ meaningful)
