---
title: PIE Performance-Improving Edits Benchmark
tags: [eval, project]
summary: PIE is a dataset of more than 77K pairs of slow and fast C++ programs timed in the gem5 simulator; the paper reports that fine-tuned and retrieval-prompted models reach multi-fold speedups, that chain-of-thought prompting adds little, and that conditioning on speed lowers correctness.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-07-shypula-2023-learning-performance-improving-code-edits.md
---

# PIE Performance-Improving Edits Benchmark

PIE holds more than 77K pairs of C++ programs, a slower and a faster solution to the same problem, with runtime measured in the gem5 simulator, in place of wall-clock timing. The task is to rewrite a slow program so it runs faster while staying correct.

## Reported results

All figures are (self-reported); the metric is the best speedup over eight samples (Best@8) unless stated.

- GPT-3.5 fine-tuned on high-quality pairs plus self-play: 6.86x, with 87.63% of programs optimized, against 3.66x for human programmers.
- CodeLlama 13B fine-tuned with performance conditioning: 5.65x.
- GPT-4 with retrieved examples (K=4): 3.93x. Chain-of-thought prompting: 1.60x.
- Performance conditioning lowers correctness, 70.96 against 85.07.
- The extraction records a phantom speedup of 1.12x when timing with hyperfine, and 42.8M gem5 simulations to build the measurements.

## Limits

- C++ competitive-programming programs only; results may not carry to production code.
- Best@8 selects the best of several samples, which inflates headline numbers relative to a single try.
- Numbers come from the paper's own fine-tuning and prompt setups, which differ across rows.

## See Also
- [[Code Generation Prompting]] — prerequisite-for
- [[Best-of-k Headline Inflation]] — related (Best@8 reports the best sample)
