---
title: SPoC Pseudocode-to-Code
tags: [eval, benchmark]
summary: "SPoC pairs 18,356 C++ programs with line-level human pseudocode and about 38.6 tests each, and searches over per-line translations under a compilation budget; the paper reports error localization lifting success to 44.7% at 100 compilations, though its abstract and introduction disagree on the top-one baseline (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-kulal-2019-spoc.md
---

# SPoC Pseudocode-to-Code

Kulal and colleagues (NeurIPS 2019) ask whether long programs that behave correctly can be built from pseudocode given line by line, together with test cases, by searching among candidate translations, and whether blaming a line for a compiler error makes the search cheaper. The dataset has 18,356 C++ programs from 677 Codeforces problems, written up by 59 crowdworkers, with about 38.6 test cases per program.

## Mechanism

- For each pseudocode line a seq2seq model proposes 100 candidate lines of code. A best-first search then combines them, compiling each program and running the public tests until a program passes or the budget is spent.
- **Success rate at B** is the fraction of test examples where an accepted program is found within B **synthesis trials**, each a compiler call plus execution on public tests; hidden tests judge the final program.
- Two localizers down-weight or blacklist the candidate that caused a compile error: a neural multiclass predictor of the offending line, and prefix-based pruning that spends extra compiles to find the shortest failing prefix.

## Results (self-reported)

- Best-first search with error localization reaches 44.7% success under 100 compilations (abstract figure); the abstract gives a top-one success rate of 25.6% while the introduction says 24.6%.
- Accuracy per line does not translate into accuracy per program: a minority of programs have every line correct in the top-one translation.
- The line number the compiler reports is wrong about one time in five, and down-weighting it makes the search worse than none at large budgets.
- The multiclass localizer helps most at B = 100; prefix-based pruning is better at large budgets but worse at B = 10, since the extra compiles it spends count against the budget.
- With the multiclass localizer, 13.5% of examples need fewer trials (median 26 fewer), but 1.6% of successes become failures; pruning worsens the trial count for 15.7% and improves it for 4.1%.

## Limits

- Credit assignment uses only compile errors, which make up 88.7% of failures. The oracle ceilings (55.2% and 71.4%) assume incorrect candidates never combine into correct behaviour.
- The problems are the easiest on Codeforces, the language is C++ only, and pseudocode must be aligned to lines.
- Training hyperparameters and seeds are not given; single runs. The source gives both 13.5% and 15.5% for the same localizer's reduced trials. According to the extraction notes, the 44.7% headline cannot be read straight off the figure cells.
- The paper gives no rate for programs that pass the public tests but fail the hidden ones.

## See Also
- [[Code Generation Prompting]] — related
- [[DS-1000]] — related (execution-based code benchmark)
- [[Eval Metric Interpretation Pitfalls]] — related
