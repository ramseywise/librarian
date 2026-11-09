---
title: Medprompt
tags: [prompting, pattern]
summary: Medprompt combines nearest-neighbour few-shot exemplars, self-generated chain-of-thought and a choice-shuffle ensemble to push GPT-4 past specialist medical models on multiple-choice benchmarks.
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-06-nori-2023-can-generalist-foundation-models-outcompete.md
---

# Medprompt

Nori, Lee, Zhang and colleagues (Microsoft, arXiv 2311.16452 v1, November 2023) argue that a generalist model with a composed prompting strategy can outperform special-purpose tuning in medicine. All numbers are the authors' own (self-reported), for GPT-4 as of 2023 and multiple-choice questions only.

## Mechanism

Preprocessing: embed each training question, have GPT-4 write a chain of thought and an answer, and keep only examples where the generated answer matches the label (wrong-answer samples are discarded because the reasoning cannot be trusted).

Inference for a test question:
1. Embed it and take the 5 nearest training questions by cosine distance (text-embedding-ada-002) as few-shot exemplars.
2. Five times, shuffle the order of the answer choices, generate a chain of thought and an answer with those exemplars, at temperature above zero.
3. Return the most common answer.

Choice shuffling is meant to counter position bias and add diversity beyond temperature sampling. The self-generated chains replace expert-written ones.

## Results (self-reported)

- MedQA (US four-option, 1273 questions), GPT-4, k = 5 exemplars, 5-call ensemble: 90.2%, against 81.7% for a simple-prompt baseline and 86.5% for the specialist Med-PaLM 2 (its "choose best" number). The authors report a 27% error-rate reduction against the best specialist models.
- Ablation on MedQA, cumulative, in an order the authors call subjective and noting the components are not statistically independent: random 5-shot, self-generated chain-of-thought, kNN exemplar selection, then the ensemble. The text says chain-of-thought contributes most (+3.4) and few-shot and ensembling +2.2 each; see Limits for the conflict.
- Self-generated chains beat expert-written chains by 3.1 points (86.9 versus 83.8, fixed 5-shot, no ensemble; expert chains from the Med-PaLM 2 prompt).
- Scaling to 20 exemplars and 11 ensemble calls gave 90.6% (+0.4). The authors present the 5-and-5 default as a compromise between cost and accuracy.
- Across nine MultiMedQA multiple-choice sets Medprompt reports the top score on each, with one strategy throughout, though Professional Medicine ties (95.2 each) and Med-PaLM figures are best-per-dataset and fine-tuned. Examples, Medprompt first then Med-PaLM 2: PubMedQA 82.0 against 81.8; MedMCQA dev 79.1 against 72.3; MMLU Clinical 95.8 against 88.7.
- Cost: 5 calls versus up to 44 inferences for Med-PaLM 2's Ensemble Refinement.
- Holdout check: a 20% eyes-off split scored 91.3% on average versus 90.6% eyes-on, which the authors read as no overfitting through prompt iteration.
- Out of domain: +7.3% average over zero-shot on six non-medical MMLU sets and two nursing sets, against +7.1% on MultiMedQA.

## Limits

- Multiple-choice exams only; open-text adaptations were not tested. Performance on exams does not show clinical efficacy; bias and equity were not assessed.
- Contamination cannot be excluded: a black-box memorisation test found nothing, but the authors say such tests cannot guarantee data was unseen.
- Needs a labelled training set; the answer filter catches wrong answers but not wrong reasoning reaching a right answer. Single model (GPT-4, 2023); no later or non-GPT-4 models tested.
- Internal inconsistency in the paper: three sources disagree on the step gains. Fig 4's running accuracies imply +1.1 for kNN selection and +1.8 for the ensemble; Fig 6 labels them +0.8 and +2.1; the body text gives +2.2 to both few-shot and ensembling. Any single ensemble figure needs that caveat. The extraction also notes Table 1 gives a 5-shot GPT-4 MedQA baseline of 81.4 versus 81.7 in Fig 1, which are different baselines.

## See Also

- [[Few-Shot Prompting]] — prerequisite-for
- [[Self-Consistency]] — prerequisite-for
- [[LLM Judge Biases]] — related (position bias, the problem choice shuffling targets)
- [[MEDEC]] — related
- [[PubMedQA]] — related (PubMedQA is one of its evaluation sets)
- [[MultiMedQA and Med-PaLM]] — related (another medical QA prompting result)
