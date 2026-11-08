---
title: AGIEval
tags: [eval, reference]
summary: "A benchmark of 8,062 objective questions from 20 human exams (Gaokao, SAT, law, LSAT, civil service, GRE/GMAT, AMC/AIME) in English and Chinese; GPT-4 averaged 58.4 under zero-shot chain of thought against a human average of 67 (self-reported), but the human figures are not measured on the same items."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-05-zhong-2023-agieval.md
---

# AGIEval

AGIEval (Zhong et al., Microsoft, arXiv 2304.06364, 2023) evaluates models on questions
written for people sitting admission and qualification exams. It has 8,062 objective
questions across 20 tasks. By source: Gaokao supplies nine tasks (2,080 items); the SAT two
(426); the Chinese lawyer qualification, through JEC-QA, two (2,000); the LSAT three (1,000);
the civil service exam, through LogiQA in English and in Chinese, 651 items each; GRE and GMAT
questions, through AQuA-RAT, 254; and AMC and AIME problems, through MATH, 1,000. Open-ended
questions were dropped. Only the Gaokao and SAT items are new; everything else is a public
dataset reused.

## Human baselines

The paper did not measure people on these items. It took figures from the source datasets'
papers, or scaled exam scores to a 100-point range, treating "average" as the 50th percentile
and "top" as the top 1% (the lawyer test uses the top 10%, per Fig. 1). One pair is applied
to every section of a test: the three LSAT parts all use 56 and 91.

## Results (self-reported)

Setup: GPT-4 called via the Azure chat API at temperature 0; the few-shot condition used
five demonstrations.

- GPT-4 averaged 58.4 with zero-shot chain of thought and 61.3 with few-shot chain of thought,
  against a human average of 67 and a top score of 91.
- Against the human average it was ahead on some tasks, such as SAT-Math (95.0 against 66),
  LSAT-LR (80.6 against 56), LSAT-RC (85.1 against 56), MATH (47.7 against 40) and
  Gaokao-English (92.5 against 69), and behind on others: LSAT-AR scored 34.4 against 56,
  JEC-QA-KD 31.9 against 71, AQuA-RAT 73.2 against 85 and Gaokao-physics 45.5 against 71.
- Few-shot added little to zero-shot (GPT-4 average 56.4 zero-shot against 59.2
  few-shot). Chain of thought was uneven: SAT-Math rose from 64.6 to 95.0, while Gaokao Chinese
  fell from 53.3 to 44.7.
- Contamination check (GPT-4 zero-shot, six Gaokao subjects): the authors set the whole
  subject against its 2022 items, which come after GPT-4's September 2021 cutoff. Math QA
  went from 47% down to 29.8% (n=47), math cloze from 16.1% to 4% (n=25), and chemistry from
  51.7% to 42.2% on 64 items;
  geography, biology and physics barely moved. The authors call the drops outside mathematics
  minor.
- Error analysis: researchers scored 100 wrong ChatGPT answers per task (zero-shot chain of
  thought) on understanding, knowledge, reasoning and calculation. Reasoning was the weakest
  dimension, with failures such as ignoring premises and confusing sufficient with necessary
  conditions.

## Limits

- Conceded: the authors call human accuracy "a useful approximation", say AGIEval may itself be
  contaminated, and it covers only objective, text-only questions.
- Not like for like: the human figures are scaled whole-exam scores, which count the
  removed open-ended questions, while the model figures are accuracy on the objective
  subset. The test-takers behind MATH, LogiQA and JEC-QA are not identified.
- Contamination is untested for the LSAT, the SAT and the reused datasets. The contamination
  table has no confidence intervals and small n. The error analysis reports no inter-annotator
  agreement. The JEC-QA "test" items are simply the first 1,000 of its training examples.
- GPT-4 reaches 51.0 zero-shot on SAT-English even when the passage is removed, a result the
  paper leaves undiscussed; it also gives two figures for Gaokao-English (92.5 and 93.8).
- Models are from 2023 (GPT-4, ChatGPT, Text-Davinci-003, Vicuna-13B).

## See Also
- [[LegalBench]] — related (another professional-domain benchmark)
- [[Eval Contamination Defenses]] — related
- [[Benchmark Prompt Format Sensitivity]] — related
- [[Eval Error Bars and Sample Size]] — related
