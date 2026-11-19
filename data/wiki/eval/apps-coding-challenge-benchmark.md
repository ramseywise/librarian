---
title: APPS Coding Challenge Benchmark
tags: [eval, code, benchmark]
summary: "APPS has 10,000 Python problems from introductory to competition level with 131,777 test cases; fine-tuned GPT-Neo 2.7B reached about 1.12% strict accuracy overall and the few-shot GPT-3 solved 3 of 5,000 test problems (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-hendrycks-2021-measuring-coding-challenge-competence-apps.md
---

# APPS Coding Challenge Benchmark

Hendrycks and colleagues ask how well language models write Python from arbitrary natural-language problem specifications when scored by test cases rather than text overlap.

## Construction

- 10,000 problems (the test split holds 5,000) from Codewars, AtCoder, Kattis and Codeforces, plus CodeChef, HackerRank and LeetCode, parsed with custom parsers, deduplicated and run under one judge.
- Three difficulty levels: introductory, interview and competition.
- The set carries 131,777 test cases plus 232,421 solutions written by people.
- Two metrics: **test case average** (mean fraction of test cases passed per problem) and **strict accuracy** (fraction of problems passing every test case).

## Results (self-reported)

Setup: APPS test split; GPT-2 and GPT-Neo fine-tuned on the APPS train set, beam search size 5, top-1 unless stated.

- GPT-Neo 2.7B: on introductory problems roughly 15% test case average and 4% strict accuracy, and across all levels about 1.12% strict accuracy. GPT-2 1.5B reaches 0.68% overall, and no fine-tuned model solves any competition-level problem under strict accuracy (0.00).
- Judging the best of five beams instead of one improves GPT-Neo on introductory problems, taking strict accuracy from 3.9% up to 5.5% and the test case average from 14.7% up to 19.9%. GPT-2 0.1B at top-5 (test case average 10.75) beats GPT-2 1.5B at top-1 (7.96), so sampling several candidates helps.
- Few-shot GPT-3 175B (davinci instruct, two examples per format) solves 3 of 5,000 problems (strict accuracy 0.06%); about 59% of its introductory solutions have syntax errors against about 3% for GPT-Neo.
- BLEU is anticorrelated with accuracy: it rises with difficulty while accuracy falls, and on introductory problems the small GPT-2 0.1B (BLEU 26.8) is almost level with GPT-Neo 2.7B (27.1).
- Codex 12B, with figures taken from Chen et al. (2021): introductory accuracy 4.14% at top-1, 9.65% at top-5 and 25% at top-1000.
- Checking by hand the problems that have just 2 test cases, the authors found false positives in under 1% of problems (8 of the 12 solved ones).

## Later uses

[[CodeT Generated-Test Reranking]] and [[Planning-Guided Transformer Decoding (PG-TD)]] both evaluate on APPS.

## Limits

- Some Kattis problems have as few as 2 test cases, which can give false positives.
- GPT-Neo pretraining data is not decontaminated against APPS; the authors reason that memorisation is unlikely since scores follow difficulty, but run no direct test.
- GPT-3 was run few-shot only with two examples, so the 3 problems it solved could be memorised or chance.
- The source of GPT-Neo's advantage over GPT-2 (more code, scale or architecture) is not separated.
- Python only; fine-tuning hyperparameters are not given; single run with no seeds or intervals.
- The models are from 2021 and later systems score far higher; the test cases cover only some of the possible inputs.

## See Also
- [[HumanEval and pass@k]] — alternative-to
- [[CodeXGLUE Code Understanding and Generation Benchmark]] — alternative-to
- [[SPoC Pseudocode-to-Code]] — related
- [[CodeT Generated-Test Reranking]] — extends
- [[Planning-Guided Transformer Decoding (PG-TD)]] — extends
