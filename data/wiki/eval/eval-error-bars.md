---
title: Eval Error Bars and Sample Size
tags: [eval, llm, reference]
summary: "Every pass rate is an estimate — SE = √(p(1−p)/n), so on 50 tasks 80% is ±11 points; size the suite from the smallest difference you must detect, average trials within a task before computing SE, cluster SEs for grouped tasks, and correct for multiple comparisons."
updated: 2026-11-08
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--06-eval--notes--09-reading-results.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--06-eval--notes--03-eval-datasets.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--06-eval--README.md
  - data/raw/papers/2026-11-05-ye-2023-comprehensive-capability-analysis-gpt-3.md
  - data/raw/papers/2026-11-05-zhong-2024-evaluation-openai-o1.md
---

# Eval Error Bars and Sample Size

An eval score is an estimate from a sample, not a fact. Most "improvements" on small suites
are noise.

## The error bar on a pass rate

```
SE = √( p(1 − p) / n )          95% CI ≈ p ± 1.96 · SE
```

| n | SE at p = 0.80 | 95% CI |
|---|---|---|
| 20 | 0.089 | 62% – 98% |
| 50 | 0.057 | 69% – 91% |
| 100 | 0.040 | 72% – 88% |
| 300 | 0.023 | 75% – 85% |
| 1,000 | 0.013 | 77% – 83% |

**On 50 tasks, 80% and 72% are indistinguishable.** Report the interval with every headline
number. For small n or p near 0/1, use the **Wilson interval** — it never leaves [0, 1]
(the rule enforced by [[Small-N Reporting Floor]]).

## How many tasks: size from the smallest difference that matters

Rough sizes for a paired comparison (same tasks, 80% power, α = 0.05, pass rates ~70–85%):

| Smallest difference that matters | Tasks needed |
|---|---|
| 15 points | 50–100 |
| 10 points | 100–200 |
| 5 points | 400–800 |
| 2 points | 2,500+ |

The paired range depends on how often the two versions disagree on a task; unpaired needs
noticeably more. Consequence: **a 50-task golden set is a smoke detector for big
regressions** — it cannot show a 3-point prompt gain. Grow the suite or stop deciding on
3-point differences. Dataset stage sizes follow from this (5–20 example suite, 20–50 first
golden set, 100–300 working set for ±5–8 points, 1,000+ for small effects —
[[Golden Set Mechanics]]). For a per-event never-event gate the related question is
detection power ([[Binary Gate Sample Power]]).

## Repeats and clustering

- **Repeated trials** ([[Eval Non-Determinism]]): average trials *within* each task first,
  then compute SE across tasks. 100 tasks × 5 trials is not 500 independent samples.
  Repeats reduce sampling noise within a task, not noise from *which tasks you picked* —
  beyond a few repeats, more tasks beat more repeats.
- **Clustered tasks** (10 questions on one document, 5 turns of one conversation) are not
  independent. Use clustered standard errors; Miller (*Adding Error Bars to Evals*,
  Anthropic 2024) reports they can be several times larger than naive SEs on popular
  benchmarks.

## Multiple comparisons

Slice 20 ways and one slice will look "significant" at α = 0.05 by chance. Testing 6 fixes
at once at 95% each gives 1 − 0.95⁶ ≈ **26%** chance of at least one false positive. Either
tighten the threshold (Bonferroni: α / number of tests) or re-run each positive as an
independent confirmation. Pre-register the slices that gate releases.

**When the difference is smaller than the noise, don't switch.** 100 tasks at 70% → SE ≈
4.6 points, 95% interval ±9; "73% vs 70%" is inside it. Run the paired test first
([[Paired Eval Comparison]]).

## Small samples in capability papers

Two 2023-24 capability studies show how thin the sample behind a headline can be (both
self-reported; how the items were chosen is unstated in one and described inconsistently in
the other). In a GPT-3/3.5 analysis, cross-model
comparisons mixed test sets of 100 items (davinci, code-davinci-002), 1,000 items
(text-davinci-001 and -002) and full datasets (text-davinci-003, gpt-3.5-turbo), the reported
`±` was never defined, and no significance test was given; the authors say the subsampling,
made for API rate limits, does not affect the overall trend. In an evaluation of OpenAI's
o1-preview across 27 tasks, the claimed perfect score in high-school maths covers just 10 items, college maths was
7 correct of 12, and the 83.3% coding figure is 10 of 12 LeetCode problems with three attempts
each. The extractions report no intervals or inter-rater agreement for either, and the o1
paper reports no human baseline despite "human-level" language. A benchmark-side counterpart
is [[GSM-Symbolic]], where the spread across re-instantiated question sets is about what
sampling alone gives at 100 questions per set, by the extraction's estimate.

## See Also
- [[Paired Eval Comparison]] — extends (variance reduction for A vs B)
- [[Eval Metric Interpretation Pitfalls]] — related (what the number means, not just how wide it is)
- [[Small-N Reporting Floor]] — instance-of (Wilson bounds enforced in a report)
- [[Binary Gate Sample Power]] — related (power for never-event gates)
- [[Eval Non-Determinism]] — related (k trials per task)
- [[Confidence Interval Coverage and Wilson]] — related (why Wald fails for rare events)
- [[Multiple Comparisons Corrections]] — related (many metrics or variants compared at once)
- [[Best-of-k Headline Inflation]] — related (a best-of-k headline is not a single-run estimate)
- [[Benchmark Prompt Format Sensitivity]] — related (prompt format can move a score more than its error bar)
- [[GSM-Symbolic]] — related (a score as a draw from a distribution)
- [[GHOSTS Benchmark]] — related (expert grading with no agreement statistic)
- [[AGIEval]] — related (human baselines without intervals)
- [[Private Variant Testing on Arena Leaderboards]] — related (identical checkpoints scoring 17 points apart)
- [[Live Multi-Market Trading Benchmark]] — related (single-run cells, no intervals)
- [[Live Penetration Testing of Agents and Professionals]] — related (one run per agent, no hypothesis tests)
- [[GPQA]] — related (the authors state the effect size needed for 80% power at 448 questions)
