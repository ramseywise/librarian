---
title: TruthfulQA
tags: [eval, reference]
summary: "An 817-question benchmark written to elicit imitative falsehoods; in 2021-era models the best, GPT-3-175B with a helpful prompt, was truthful on 58% of questions against 94% for a human baseline (self-reported), and larger models within a family were generally less truthful."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-lin-2021-truthfulqa.md
---

# TruthfulQA

Lin, Hilton and Evans (arXiv v2, May 2022) ask whether language models produce truthful answers or mimic common human falsehoods learned from their training text. Their hypothesis is that, because training rewards imitating human text, bigger models will give more **imitative falsehoods** (false answers that are likely under the training distribution) on questions built to elicit them, a pattern they call inverse scaling.

## The benchmark

The authors wrote 817 questions in 38 categories, each paired with true answers, false answers and a source. Adversarial filtering against GPT-3-175B shaped 437 of the 817. There is a generation task, scored by blinded human labels (13 labels mapped to a scalar, thresholded at 0.5), and a multiple-choice variant scored by likelihood. An answer is truthful if it avoids asserting a false statement, so a refusal, an expression of uncertainty or a true but off-topic reply all qualify. Evaluation is "true zero-shot": no gradient updates, no benchmark examples in the prompt, and no prompt tuning on the benchmark.

**GPT-judge** is a finetuned GPT-3-6.7B classifier of answers as true or false. It predicted human truthfulness labels with accuracy of 90 to 96% when validated on a model family left out of its training, and reached 89.5% on the human baseline's answers, which it had not trained on (self-reported). GPT-info, a judge for informativeness, reached 86.3% on UnifiedQA.

## Results (self-reported)

Setup unless stated: the generation task, scored by humans, with greedy decoding and no examples in the prompt.

- With the helpful prompt, GPT-3-175B was truthful on 58% of questions, and the human baseline on 94% (one participant, 250 questions). It was true and informative on 21% against 87%, and false and informative on 42% against 6%.
- The prompt matters: GPT-3-175B scored 58.1% true with the helpful prompt and 12.5% with the harmful one.
- Inverse scaling: with the default QA prompt, GPT-3 fell from 37.0% truthful at 350M parameters to 20.4% at 175B. GPT-Neo/J at 6B was 17% less truthful than the 125M model. On multiple choice, GPT-Neo/J at 6B was 12% less truthful than at 125M, and none of the models did significantly better than chance.
- For over 80% of questions, a false, informative answer came from at least half of four models (UnifiedQA 2.8B, GPT-2 1.5B, GPT-J 6B and GPT-3 175B), described as the four largest.
- Newer training methods (context distillation, InstructGPT, WebGPT, Gopher) restore positive scaling but slowly; a linear extrapolation from three points per model puts InstructGPT at 48% against 95% human on multiple choice at 10^20 parameters.
- On control questions edited by one to three words, truthfulness improved with model size, which the authors read as counting against a non-imitative explanation.

## Limits

Because 437 of 817 questions were filtered against GPT-3-175B, its results are biased; the unfiltered subset is reported separately. The authors concede that non-imitative weaknesses may be exploited by some questions, and that reference answers are incomplete, especially for small models. They estimate 2 to 6% disagreement with their labels, so tiny score differences may be noise. The human baseline is one participant, and the validator and participant spent under two minutes per question. Long-form generation and interactive chat are outside its scope. GPT-judge struggles with long or qualified answers, so human evaluation remains the gold standard. It is not designed for few-shot use, which would likely overstate truthfulness, and "No comment" counts as truthful, so read it with informativeness. The results are from 2021-era models, and the paper notes newer ones close part of the gap.

## See Also
- [[FActScore]] — alternative-to (scores long-form factual precision rather than short-answer truthfulness)
- [[FreshQA]] — alternative-to (another factuality benchmark, built around whether answers are current)
- [[Benchmark Prompt Format Sensitivity]] — related (the prompt moved GPT-3's score from 12.5% to 58.1% here)
- [[Language Model Self-Knowledge]] — related (uses TruthfulQA among its calibration tasks)
- [[ETHICS Benchmark]] — related (another alignment-flavoured benchmark, filtered adversarially)
- [[HELM Holistic Evaluation]] — related (runs TruthfulQA as one of its core scenarios)
- [[ETHICS Benchmark]] — related (another alignment-flavoured benchmark, filtered adversarially)
- [[HELM Holistic Evaluation]] — related (runs TruthfulQA as one of its core scenarios)
- [[Evaluation-Driven Model Selection]] — related (a textbook chapter that uses it as a factual-consistency example)
- [[Intrinsic vs Extrinsic Hallucination]] — related
- [[LLM Hallucination Surveys]] — related (surveys that describe this benchmark)
- [[Model-Written Evaluations]] — related (its sandbagging test reuses these questions)
