---
title: LegalBench
tags: [eval, reference]
summary: "A benchmark of 162 legal-reasoning tasks from 36 sources, built by a call for tasks and grouped into six reasoning types; GPT-4 led the category averages of 20 models (self-reported), rule recall was the weakest category for every model, and the choice of in-context demonstrations moved scores by over 20 points."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-05-guha-2023-legalbench.md
---

# LegalBench

LegalBench (Guha et al., Stanford, arXiv 2308.11462, 2023) is a benchmark for legal reasoning
in language models, built collaboratively: a call for tasks went out in August 2022 and
legal scholars and the paper's authors contributed. Tasks come in three kinds: public datasets reused after reformatting,
unreleased datasets coded by hand by legal scholars, and tasks written for the
benchmark; submissions were vetted for legal correctness. Version 1 (August 2023) has 162
tasks from 36 sources, English only.

## Structure

Tasks fall into six reasoning types, four taken from the IRAC method (issue, rule,
application, conclusion) plus interpretation and rhetorical understanding. IRAC serves only
as a grouping principle and each task tests one type. By the paper's Section 4.2 counts the
mix is 5 rule-recall, 16 issue-spotting, 16 rule-application, 16 rule-conclusion, 119
interpretation and 10 rhetorical-understanding tasks. Tasks have at least 50 samples (mean
563) and train splits of 2 to 8 examples. Classification uses exact match, reported as balanced
accuracy, multi-answer tasks are scored by F1, and rule-application answers are graded by hand against
a released guide for correctness and for analysis.

## Results (self-reported)

Setup: 20 models, 0 to 8 hand-picked demonstrations, temperature 0, one prompt per task shared
across models.

- GPT-4 led. Its category averages were 82.9 for issue-spotting, 59.2 for rule-recall, 89.9
  for rule-conclusion, 75.2 for interpretation and 79.4 for rhetorical understanding.
  GPT-3.5 and Claude-1 averaged 60.9 and 58.1 on issue-spotting, and 46.3 and 57.7 on
  rule-recall. Rule recall was the weakest category for every model.
- On rule-application (12 tasks, one law-trained grader), correctness against analysis
  scored 82.2 and 79.7 for GPT-4, 58.5 and 44.2 for GPT-3.5, and 61.4 and 59.0 for Claude.
- Demonstration sensitivity (eight binary tasks, five random sets of four demonstrations, run on GPT-3.5
  and a 7B open model): for the open model the best prompt beat the worst by over 20
  balanced-accuracy points (permutation test p < 0.01).
- For GPT-3.5, a plain-language prompt outperformed a technical-language one on four of five
  tasks, by up to 21 points; one task went the other way.

## Contamination

The authors concede some tasks may have leaked into pretraining data, and sort tasks by prior web
availability instead of testing. Two tasks use post-cutoff material.

## Limits

- Stated: the tasks exclude long documents and any question without an objectively correct
  answer, are in English, and lean toward US law and contracts; the IRAC steps are
  never chained, each being tested on its own; scores are a lower bound because prompts were untuned; no open
  model above 13B was run. One source supplies 16 of the 17 issue-spotting tasks.
- Unstated: no human baseline, one manual grader with no agreement figure, no confidence
  intervals on the category table, no contamination experiment; manual slices have n = 12-29.
- Section 4.2 and 4.3 disagree on task counts (16/16/119 vs 17/12/118).
- Two tasks used ChatGPT during construction. The models tested (GPT-4, GPT-3.5, Claude-1) were queried
  between May and August 2023.

## See Also
- [[Benchmark Prompt Format Sensitivity]] — related (demonstration choice and prompt wording moved scores)
- [[Eval Contamination Defenses]] — related
- [[AGIEval]] — related (another human-domain exam benchmark, with a law component)
- [[Eval Error Bars and Sample Size]] — related (small tasks, no intervals)
