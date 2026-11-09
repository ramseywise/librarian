---
title: Verbalized Probability Calibration and CalibratedMath
tags: [foundations, concept]
summary: Finetuning GPT-3 to append a stated confidence, as a number or a word, to its arithmetic answers, tested for calibration under distribution shift on a 21-task suite.
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-lin-2022-teaching-models-express-their-uncertainty.md
---

# Verbalized Probability Calibration and CalibratedMath

Lin, Hilton and Evans (a preprint) ask whether a language model can state calibrated confidence in its own answers in words, and whether that holds when the task distribution shifts. They introduce CalibratedMath, a suite of 21 arithmetic tasks.

## Method

The model is GPT-3 davinci (175B). It answers arithmetic questions zero-shot under greedy decoding, and those answers are then held fixed. The model is then finetuned with supervision to append a confidence, expressed as a number or as one of five words. The training label is GPT-3's measured accuracy on the sub-task that the question belongs to. Calibration on held-out task groups is scored by mean squared error (Brier) and mean absolute deviation, and compared with confidences derived from logits and with a constant baseline. The paper contrasts this with "answer logit" (the normalised log-probability of the answer) and "indirect logit" (the log-probability of a True token appended to the answer).

## Reported numbers (self-reported)

Setup: GPT-3 175B, trained on the Add-subtract tasks and evaluated on held-out groups, greedy decoding unless stated; one run.

- On Multi-answer, finetuned verbalized numbers beat the answer logit and the constant baseline in mean squared error.
- When tested on Multiply-divide, verbalized numbers do no better than the constant baseline and are beaten by the zero-shot answer logit. Training on Multiply-divide instead gives much worse Multi-answer calibration, which the authors attribute to larger label shift.
- About 2,700 training examples suffice; more did not improve generalisation. Stochastic 50-shot prompting nearly matched finetuning on 10,000 examples.
- A logistic regression on heuristic features and a linear probe on embeddings did worse than verbalized words on Multi-answer, though the probe was close.
- Across sub-tasks, verbalized-finetune error correlates 0.84 with verbalized words, but only 0.65 with indirect logit and 0.60 with answer logit.
- For verbalized words, Expected Value decoding calibrated somewhat better than greedy decoding did.

## Limits

- One model (GPT-3 175B) and arithmetic only; the authors call for other subjects, chat and long-form formats, forecasting and other models.
- Supervised finetuning on sub-task accuracy, a noisy per-question label, rather than reinforcement learning on a proper scoring rule.
- The model emits a number only if that token appeared in training, so calibration curves are lumpy. It is underconfident on Multi-answer.
- Single run with no seeds or intervals; many finetuning hyperparameters are left at API defaults and unstated. The davinci finetuning API dates from 2022.
- The authors concede calibration does not prove honesty, since a model could imitate a calibrated person.

## See Also
- [[Confidence-Gated Escalation]] — related
