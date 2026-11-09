---
title: Code-Based Self-Verification and Weighted Voting
tags: [harness, pattern]
summary: Prompting a code-interpreter model to verify its answer with code, then weighting sampled answers by verification state, lifted MATH accuracy where natural-language verification did not.
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-06-zhou-2023-solving-challenging-math-word-problems.md
---

# Code-Based Self-Verification and Weighted Voting

A paper (CUHK MMLab and others, arXiv preprint, August 2023) studies GPT-4 Code Interpreter (GPT4-Code) on math word problems. The authors prompt it to check its answer with code, and then vote over sampled paths weighted by the check's outcome. Numbers are the authors' own.

## Mechanism

- **Prompt:** the verification prompt asks the model to solve step by step and verify its answer using the code interpreter.
- **States:** a verification returns True, False or Uncertain. a False result prompts a fresh solution that is verified again, whereas an Uncertain result is taken as the final answer.
- **Voting:** each sampled answer scores the sum of weights for its verification states. With weights 1 for True, 0.5 for Uncertain and 0.2 for False, an answer with 3 True and 1 Uncertain scores 3.5, beating one with 1 True, 1 Uncertain and 4 False at 2.3, although plain majority picks the second.
- **Self-debugging contrast:** the authors say self-debugging checks code steps but not the reasoning or final answer.

## Reported numbers (self-reported)

Setup: GPT4-Code zero-shot on the MATH test set (size not stated), voting over k=16 sampled paths unless noted.

- Verification alone: 69.69% to 73.54%. With weighted voting at k=16: 84.32%.
- Natural-language verification on the same model gave 69.29%, below the baseline, while code verification rose on all 7 subjects.
- Precision of a True verdict averaged 95.88% against recall 79.11%, over five sampled paths.
- Weights must satisfy True above Uncertain at or above False; inverting them was worse than naive majority voting.
- Baselines as reported by the authors: GPT-4 without code 42.20, chain of thought 50.36, PHP 53.90.
- On other sets, GSM8K improves from 92.9 to 97.0 with 5 paths, MMLU-Math from 87.5 to 89.2 and MMLU-STEM from 86.8 to 87.0. Geometry gains only 0.6 points from verification.
- More code use tracked higher accuracy, more so on harder problems, but the prompts changed, so the link is correlational.

## Limits

- Only GPT4-Code, a closed model with a built-in sandbox from August 2023; no variance, seeds or intervals, and test size is not stated.
- The model grades its own answer, and the paper does not separate verification catching errors from extra code or longer reasoning helping. Voting weights were tuned on the same benchmark.
- The frequency of Uncertain is not reported, an appendix example shows a verification that misled, and transfer beyond tasks with a computable check is not shown.
- The extraction notes an internal inconsistency: for Number Theory, Table 1 shows a gain of +7.6 and Table 4 shows +8.4 although both describe the move from 77.2 to 85.6, where the difference supports 8.4.

## See Also
- [[Verification Loops]] — related
- [[LLM-as-a-Verifier]] — related
- [[Self-MoA Single-Model Aggregation]] — related (aggregating sampled answers)
