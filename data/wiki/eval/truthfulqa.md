---
title: TruthfulQA
tags: [eval, reference]
summary: "An 817-question benchmark written to elicit imitative falsehoods; in 2021-era models the best, GPT-3-175B with a helpful prompt, was truthful on 58% of questions against 94% for a human baseline (self-reported), and larger models within a family were generally less truthful."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-07-lin-2021-truthfulqa.md
---

# TruthfulQA

Lin, Hilton and Evans (arXiv v2, May 2022) ask whether language models produce truthful answers or mimic common human falsehoods learned from their training text. Their hypothesis is that, because training rewards imitating human text, bigger models will give more **imitative falsehoods** (false answers that are likely under the training distribution) on questions built to elicit them, a pattern they call inverse scaling.

## The benchmark

The authors wrote 817 questions in 38 categories, each with sets of true and false reference answers and a source. For 437 of the 817 the questions were adversarially filtered against GPT-3-175B. There is a generation task, scored by blinded human labels (13 labels mapped to a scalar, thresholded at 0.5), and a multiple-choice variant scored by likelihood. An answer is truthful if it avoids asserting a false statement, so refusing, voicing uncertainty or giving a true but irrelevant answer all count. Evaluation is "true zero-shot": no gradient updates, no benchmark examples in the prompt, and no prompt tuning on the benchmark.

**GPT-judge** is a GPT-3-6.7B model finetuned to label answers true or false. It predicted human truthfulness labels with 90 to 96% validation accuracy on held-out model families, and reached 89.5% on the human baseline's answers, which it had not trained on (self-reported). GPT-info, a judge for informativeness, reached 86.3% on UnifiedQA.

## Results (self-reported)

Setup: generation task, zero-shot, greedy decoding, human evaluation, unless stated.

- GPT-3-175B with the helpful prompt was truthful on 58% of questions against 94% for the human baseline (one participant, 250 questions). It was true and informative on 21% against 87%, and false and informative on 42% against 6%.
- The prompt matters: GPT-3-175B scored 58.1% true with the helpful prompt and 12.5% with the harmful one.
- Inverse scaling: with the default QA prompt, GPT-3 fell from 37.0% truthful at 350M parameters to 20.4% at 175B. GPT-Neo/J at 6B was 17% less truthful than the 125M model. On multiple choice, GPT-Neo/J 6B was 12% less truthful than 125M and no model beat random guessing significantly.
- On over 80% of questions, at least half of the four largest models (GPT-3 175B, GPT-J 6B, GPT-2 1.5B, UnifiedQA 2.8B) returned a false, informative answer.
- Newer training methods (context distillation, InstructGPT, WebGPT, Gopher) restore positive scaling but slowly; a linear extrapolation from three points per model puts InstructGPT at 48% against 95% human on multiple choice at 10^20 parameters.
- On control questions edited by one to three words, truthfulness improved with model size, which the authors read as counting against a non-imitative explanation.

## Limits

Because 437 of 817 questions were filtered against GPT-3-175B, its results are biased; the unfiltered subset is reported separately. The authors concede some questions may exploit non-imitative weaknesses and that reference answers are incomplete, especially for small models. They estimate 2 to 6% disagreement with their labels, so tiny score differences may be noise. The human baseline is one participant, and the validator and participant spent under two minutes per question. It does not cover long-form generation or interactive chat. GPT-judge struggles with long or qualified answers, so human evaluation remains the gold standard. It is not designed for few-shot use, which would likely overstate truthfulness, and "No comment" counts as truthful, so read it with informativeness. The results are from 2021-era models, and the paper notes newer ones close part of the gap.

## See Also
- [[FActScore]] — alternative-to (scores long-form factual precision rather than short-answer truthfulness)
- [[FreshQA]] — alternative-to (another factuality benchmark, built around whether answers are current)
- [[Benchmark Prompt Format Sensitivity]] — related (the prompt moved GPT-3's score from 12.5% to 58.1% here)
- [[Language Model Self-Knowledge]] — related (uses TruthfulQA among its calibration tasks)
