---
title: LILA Math Reasoning Benchmark
tags: [eval, benchmark]
summary: "LILA unifies 20 math datasets into 23 tasks with Python program solutions, plus out-of-distribution and robustness splits; multi-task fine-tuning of GPT-Neo-2.7B beat single-task training and few-shot Codex scored only 60.40% F1 (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-mishra-2022-lila.md
---

# LILA Math Reasoning Benchmark

Mishra and colleagues (EMNLP 2022) ask whether one unified math benchmark, with program solutions and out-of-distribution and robustness splits, can both measure and improve general mathematical reasoning. The benchmark spans 23 tasks in four categories, with 133,815 questions and 358,769 programs. It comes from 20 existing datasets, to which the authors added Python programs and instructions.

## Splits and models

- **IID**: a random 70/10/20 train, dev and test split within each task. **LILA-OOD**: whole datasets of a task held out from training; a task backed by only one dataset has no OOD set. **LILA-ROBUST**: 20 sampled questions per dataset rewritten through nine perturbation templates by crowd workers.
- BHASKARA is GPT-Neo-2.7B fine-tuned multi-task. GPT-3 and Codex are prompted few-shot on 100 examples per task for cost.

## Results (self-reported)

Setup: average F1 over 23 tasks, program-synthesis output unless noted.

- IID: multi-task Neo-Multi-P 0.480 against single-task Neo-P 0.394. OOD: 0.448 against 0.238. The abstract gives an average relative improvement of 21.83% F1.
- Asking for a program roughly doubles the multi-task F1 compared with asking for the answer directly (0.480 against 0.252).
- Few-shot Codex scores 0.604 IID and 0.586 OOD (the 60.40% headline) and stays under 0.5 on geometry, number theory, advanced math, computer science and several other categories.
- Roughly one in ten Neo-Multi IID programs does not run, and 86% of those failures are syntax errors. On perturbed IID examples the multi-task model did not get worse.
- Instructions helped GPT-3 only zero-shot (IID 0.148 without, 0.156 with). Starting from Neo-Multi improved a direct-answer model on held-out OOD data from 30.1% to 37.6% F1.

## Limits

- The source says 20 existing datasets in one place and "23 tasks, 44 datasets" in Table 2.
- F1 likely overestimates performance: a gold answer of "2 apples" scores the same for "2" and "apples".
- Codex and GPT-3 were scored on only 100 examples per task, which makes their numbers noisy and puts them on a different footing from fine-tuned scores on the full test set.
- OOD difficulty depends on which datasets land in the OOD split. No hyperparameters or seeds are reported; Codex training data is unknown so contamination cannot be ruled out.
- The extraction notes that several example tables repeat the same generated program for unrelated examples, which it takes to be a typesetting error.

## See Also
- [[Math Word Problem Benchmarks]] — related (earlier datasets, some of which LILA absorbs)
- [[SciBench]] — related
- [[Code Generation Prompting]] — related
