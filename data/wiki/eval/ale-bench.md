---
title: ALE-Bench
tags: [eval, reference]
summary: "Sakana AI's benchmark of 40 AtCoder Heuristic Contest optimisation problems where an agent's score is placed on the human leaderboard and converted to an Elo-like performance; o4-mini-high with 4-hour iterative refinement reached rating 2104 (top 11.8%) but only 1520 average performance (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-05-imajuku-2025-ale-bench.md
---

# ALE-Bench

ALE-Bench (Imajuku et al., Sakana AI, NeurIPS 2025 Datasets and Benchmarks, arXiv 2506.09050) uses 40
AtCoder Heuristic Contest problems, which are score-based contest problems (a 10-problem lite subset also exists).
An agent submits code, receives public-test feedback and can refine it. The hidden-test score is slotted into the
human leaderboard of the real contest to give a rank, which is then mapped to an Elo-like
"performance" of roughly 0 to 3500.

## Rating versus average performance

The authors prefer average performance to rating: rating rewards a single very high result and does not penalise weak ones. For o4-mini-high (C++20, four hours of iterative refinement, all 40 problems, one run) the
two views differ (self-reported): rating 2104 (top 11.8% of humans) against average performance 1520
(top 22.3%). It reached 1600 or more on 32.5% of problems, below the 56.2% human average in that band and
closer to the 33.9% of users rated 1600-1700.

## Results (self-reported)

- **One-shot** (extra generations allowed only to repair errors, at most five): the best model, o3-high, scored 1044 average
  performance against a human average of 1260.
- **Iterative refinement** using public-test feedback lifted all 4 models tested, over 4 hours, by
  more than 400 average points. On the 6 problems where o4-mini-high had already scored 2000 or more, refinement scored about 300 points or more above the top result among 150
  separate one-shot attempts.
- **Scaffolds** (lite subset, Gemini 2.5 Pro, 4 hours, one run): the authors' ALE-Agent went from 1167 (base)
  to 1264 with one addition and 1879 with a best-first tree search, at a cost rising from $7.64 per problem to $100.33. OpenHands scored 903, and the authors note it often exited early.
- **Budget form matters:** DeepSeek-R1 produced about 60 programs in four hours and GPT-4.1-mini about 300,
  so wall-clock and call-count budgets rank models differently.
- The authors saw no notable performance change around model cutoffs and manually reviewed the 12
  programs scoring 2000 or more.

## Limits

Main results are single runs (a five-run check exists only for the one-shot setting). Only 40 problems, with
the iterative and scaffolding results carry no intervals, and the ALE-Agent ablation covers 10 problems and one model.
No budget beyond 4 hours was tested, though humans spend up to hundreds of hours on long contests.
The contamination check is a visual scatter without a statistical test. Ratings depend on the subset: the
same run scored 2104 on the full set and 1386 on lite. The authors note their sandbox differs from AtCoder's,
and the models date from April-May 2025.

## See Also
- [[MLE-bench]] — related (another open-ended engineering benchmark the authors cite)
- [[Best-of-k Headline Inflation]] — related (refinement compared against many one-shot samples)
- [[Long-Horizon Execution]] — related
- [[Eval Contamination Defenses]] — related
