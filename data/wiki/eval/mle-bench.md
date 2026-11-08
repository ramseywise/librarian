---
title: MLE-bench
tags: [eval, reference]
summary: "OpenAI's benchmark of 75 Kaggle competitions that an agent must solve end to end, scored by the share of attempts that would have won any medal on the private leaderboard; o1-preview with the AIDE scaffold medalled in 16.9% of attempts at pass@1 (self-reported), and changing the scaffold moved the score more than changing the hardware."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-05-chan-2024-mle-bench.md
---

# MLE-bench

MLE-bench (Chan et al., arXiv 2410.07095, 2024) tests whether an agent can do applied
machine-learning engineering: read a Kaggle competition, prepare the data, train models and
submit predictions. Each of its 75 competitions is graded locally against the private
leaderboard of the original competition, and the headline metric is the **medal rate**: the
percentage of attempts awarded any medal, bronze or above.

## Setup

Each run gets 24 hours, one GPU and a sandbox with the competition data. The train/test
splits and grading code are re-implemented, so scores only approximate the real leaderboard.

## Headline results (self-reported)

All rows use the AIDE scaffold; ± is one standard error over seeds.

| Configuration | Medal rate |
|---|---|
| o1-preview, pass@1, 16 seeds | 16.9% ± 1.1 |
| Same, pass@8 | 34.1% |
| GPT-4o, 36 seeds | 8.7% ± 0.5 |
| GPT-4o, 24 h → 100 h (seed count not stated) | 8.7% → 11.8% |

## What moved the score

- **The scaffold.** With GPT-4o, AIDE (built for Kaggle) scored 8.7%, OpenHands 4.4% and MLAB
  0.8% (3 seeds each for the last two). The harness around the model is a first-order variable.
- **Attempts**, much more than time: see [[Best-of-k Headline Inflation]].
- **Not hardware.** GPT-4o with AIDE scored 9.1% ± 1.0 on CPU only (3 seeds), 8.7% ± 0.5 on
  the standard single GPU (36 seeds) and 10.2% ± 2.0 on two GPUs (3 seeds); the logs the
  authors inspected show no attempt to put the extra GPU to work.

## Contamination checks

The authors found no link between a model's familiarity with a competition and its score,
saw no drop when competition descriptions were reworded, and found no plagiarism of public
notebooks with a code-similarity tool (all self-reported). The familiarity correlation was in
fact −0.24 (p = 0.04), weak but not zero. These checks ran on GPT-4o, not on o1-preview, the
headline model, and the plagiarism check covered medal-winning runs only. See
[[Eval Contamination Defenses]].

## Limits

Grading is outcome-only, so a medal says nothing about whether the process was sound
([[Trajectory Over Outcome]]). One seed of the full benchmark costs about 1,800 GPU-hours,
which makes repeated runs expensive. How the standard error combines seeds and competitions is not
explained.

## See Also
- [[SWE-Lancer]] — related (another outcome-graded benchmark of real engineering work)
- [[PaperBench]] — related
- [[ALE-Bench]] — related
- [[Best-of-k Headline Inflation]] — related
- [[ScienceAgentBench]] — alternative-to (another agent benchmark for data-driven science and ML work)
- [[Eval Contamination Defenses]] — related
- [[Holistic Agent Leaderboard (HAL)]] — related (scaffold and cost effects across nine benchmarks)
- [[Agents' Last Exam (ALE)]] — related (another end-to-end benchmark graded on output artifacts)
