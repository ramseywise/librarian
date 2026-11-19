---
title: Adversarial Filtering and AFLite
tags: [eval, datasets-and-contamination, concept]
summary: "Adversarial Filtering (SWAG, HellaSwag) and AFLite (WinoGrande, PIQA) build multiple-choice sets by removing or replacing items a weak model can already answer from artifacts; the papers show large drops for the filter model, and also that the filter bakes in a ceiling and a bias against the filter model."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-zellers-2018-swag.md
  - data/raw/papers/2026-11-07-zellers-2019-hellaswag.md
  - data/raw/papers/2026-11-08-sakaguchi-2020-winogrande.md
  - data/raw/papers/2026-11-07-bisk-2020-piqa.md
  - data/raw/papers/2026-11-07-clark-2018-think-you-have-solved-question.md
  - data/raw/papers/2026-11-08-mihaylov-2018-can-suit-armor-conduct-electricity.md
---

# Adversarial Filtering and AFLite

SWAG's and WinoGrande's authors hypothesise that style or word-association artifacts let a model answer without the intended skill. The papers here respond by running a model over the candidate data and keeping what it gets wrong. [[Commonsense Multiple-Choice Benchmarks]] lists the datasets; this page is the construction mechanism.

## Adversarial Filtering (AF)

Zellers et al. define AF as iterative refinement of the set of negative endings to raise the entropy under a chosen model family: negatives the model already ranks below the true ending ("easy") are replaced with new candidates the model scores above them. SWAG starts from two consecutive video captions (ActivityNet Captions, LSMDC); an LSTM language model oversamples 1,023 wrong endings per context, AF retains the 9 hardest for a stylistic ensemble, and Mechanical Turk validates the result. AF drives the stylistic ensemble's accuracy from about 60% to near random (self-reported). SWAG has 113k questions (73k train, 20k val, 20k test); ESIM+ELMo reaches 59.2% on test against 88.0% for five-Turker majority vote on 100 sampled questions.

HellaSwag repeats AF over ActivityNet Captions and WikiHow, with GPT writing the endings and BERT-Large as discriminator, then adds crowd validation. The authors call the target the "Goldilocks zone": generations nonsensical to humans yet indistinguishable to state-of-the-art discriminators. Reported effects (self-reported):

- With SWAG's original LSTM generator AF converges at roughly 75% BERT-Large accuracy; GPT generations push it below 30%.
- On WikiHow, AF using GPT settles near 35%, 40% and 50% accuracy for endings of one, two and three sentences; the authors picked two. A discriminator with three times the parameters of the filter (BERT-Large against BERT-Base) still reaches only 63%.
- BERT-Large trained on SWAG scores 34.6% on HellaSwag; transfer in either direction costs 12% to 15%. BERT-Large overall test accuracy is 47.3% against more than 95% for humans.

## AFLite

WinoGrande removes instances whose precomputed RoBERTa embeddings let ensembles of linear classifiers predict the label. AFLite leaves 12,282 debiased items from the crowdsourced twin questions (53k passed validation). The authors report that the KL divergence between the label classes falls from 2.53 to 0.12 under AFLite, against 2.51 for random removal and 2.42 for PMI-based filtering. RoBERTa with local context only is at chance on the debiased items. PIQA uses AFLite with BERT-Large as the filter model, and BERT is the worst of its three models; the authors explain this by the dataset having been built against BERT.

## Other filters by weak solvers

ARC's Challenge Set is the questions both a retrieval solver and a word co-occurrence solver answered wrongly. OpenBookQA keeps questions that fail IR and word-association solvers and that 4 of 5 other crowd workers answer correctly. Both papers note the solvers define the split: IR scores 1.02% on ARC Challenge but 74.48% on Easy by design, and OpenBookQA's IR baseline scores 0% by construction.

## Limits

- The filter model biases the result against itself: HellaSwag is filtered against BERT-Large, so ranking models against the filter is biased; PIQA's low BERT score is partly by construction; ARC and OpenBookQA solver scores are biased by design.
- SWAG's AF is purely stylistic and looks only at the second sentence; the authors concede subtler artifacts remain and semantic implausibility was not filtered. HellaSwag's authors say the aim is the task rather than the dataset, and admit later models may find new spurious patterns.
- Filtered data can be unusable alone: training on WinoGrande's debiased set alone leaves BERT and RoBERTa at chance, so strong results need the 40,938-item full train set.
- Hyperparameters and AF details are in supplements not in these extractions. No seeds or significance tests. Models are 2018-2020 era; HellaSwag's extraction adds that GPT-4-class models later passed 90%, and WinoGrande's that 2020+ models saturated it.

## See Also
- [[Commonsense Multiple-Choice Benchmarks]] — related (the datasets built this way)
- [[Eval Contamination Defenses]] — related
- [[Visual Commonsense Reasoning and Adversarial Matching]] — related (the multimodal analogue of the same idea)
- [[TruthfulQA]] — related (also filters questions adversarially)
