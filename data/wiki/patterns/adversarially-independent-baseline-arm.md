---
title: Adversarially Independent Baseline Arm
tags: [eval, pattern]
summary: "A baseline ranker is only a floor if it could plausibly have won: share the production ranker's data contract exactly (same dimension functions, same tie-break, same output shape and version stamp) and differ only at the one decision the experiment tests — so any divergence is attributable — and read its insensitivity to weight changes as weight-blindness, not robustness."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-08-27-b26-kairo-baseline.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-08-27-b26-kairo-baseline.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-08-27-b26-kairo-baseline.md
  - data/raw/claude-docs/playground/docs/plans/2026-08-27-b26-kairo-baseline.md
  - data/raw/repos/akira/.claude--docs--plans--2026-08-27-b26-kairo-baseline.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-08-27-b26-kairo-baseline.md
  - data/raw/repos/playground/.claude--docs--plans--2026-08-27-b26-kairo-baseline.md
  - data/raw/claude-docs/akira/docs/plans/2026-08-27-b27-sensitivity-sweeps.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-08-27-b27-sensitivity-sweeps.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-08-27-b27-sensitivity-sweeps.md
  - data/raw/claude-docs/playground/docs/plans/2026-08-27-b27-sensitivity-sweeps.md
  - data/raw/repos/akira/.claude--docs--plans--2026-08-27-b27-sensitivity-sweeps.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-08-27-b27-sensitivity-sweeps.md
  - data/raw/repos/playground/.claude--docs--plans--2026-08-27-b27-sensitivity-sweeps.md
---

# Adversarially Independent Baseline Arm

An events recommender (repo akira) had to answer "does context-sensitive ranking beat the
incumbent, measurably?" Comparing the new ranker with a relationship-aware variant has no
floor: you learn that B beats C, not whether either beats something simple. The gate
asked for a **named, adversarially independent A arm**, meaning a real alternative that
could plausibly have won, not a strawman.

## How the arm was built

The baseline ("Kairo") is a flat additive ranker:

- **Same inputs.** It calls the same seven dimension-scoring functions as production. It
  reuses their scores and changes only the aggregation.
- **One difference.** Equal weights (1/7 each) whatever the context. No specificity
  profiles, no boosts, no penalties, no composition roles. The base sum is the final
  score.
- **Same contract.** It returns the production `RankResult` shape so a comparison script
  can treat both arms as interchangeable. Zeroed boost, penalty and signal fields are
  there to satisfy the type, not because the arm uses them. Its own `ranker_version`
  stamp lets serve-time logs attribute which arm ran.
- **Same tie-break.** It reuses the production comparator, because the paired ablation
  design needs both arms replayable on the same input.

It disagrees with production at exactly the decision the experiment cares about (does
context-sensitive weighting matter?). It shares enough plumbing that a divergence can
only come from that choice, not from a different data contract.

## Guards that keep it independent

- **Non-regression on the shared part.** A test asserts that production scoring and
  baseline scoring return *identical* per-dimension maps on the same input. That catches
  the quiet copy-paste fork, where the "baseline" starts to differ in places nobody chose.
- **Divergence tests on designed candidates.** On thin pools, score ranges compress and
  the two arms can converge by accident. Synthetic candidates built to expose the weight
  difference prove the arms *can* disagree before the live catalogue is asked whether
  they *do*.
- **Label the pool size.** Spearman ρ on a 9-item live pool is close to 1.0 for almost
  any ordering. The comparison script prints `pool_size` and marks low-n results.

## Insensitive is not superior

A later sensitivity sweep perturbed each weight by ±10% (see
[[Ranker Weight Sensitivity Sweep]]). The equal-weight arm's top-5 barely moved. The
plan required the write-up to say explicitly that ρ = 1.0 for the baseline means it is
*insensitive*, not better: **weight-insensitivity is also weight-blindness.** A ranker
that no weight change can move also cannot be tuned toward what users mean.

## See Also
- [[Ship Logging Before Features]] — extends (why the current system is kept as an arm at all)
- [[Ranker Weight Sensitivity Sweep]] — prerequisite-for (the sweep runs against both arms)
- [[Frozen Ranking Baseline from a Pure Ranker]] — related (the offline replay apparatus the arms run in)
- [[Specificity-Adaptive Ranking and Slate Composition]] — alternative-to (the production design the baseline strips down)
- [[Data Sufficiency Refusal]] — related (a comparison nobody could lose is the same strawman)
