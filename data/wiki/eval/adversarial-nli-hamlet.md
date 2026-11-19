---
title: Adversarial NLI and HAMLET Collection
tags: [eval, language-tasks, benchmark]
summary: ANLI is built in three rounds where annotators write hypotheses to fool the current best model, other humans verify, and a stronger model is trained for the next round (HAMLET); RoBERTa trained on SNLI, MNLI, FEVER and ANLI scores 53.7% on the full test set (self-reported).
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-nie-2020-adversarial-nli.md
---

# Adversarial NLI and HAMLET Collection

Nie and colleagues (ACL 2020) collect an NLI benchmark with an iterative procedure they call HAMLET, rather than one static pass. The claim is that even non-expert annotators can find weaknesses in the current best model, that training on what they find improves robustness, and that a moving target resists saturation.

## Mechanism

1. Mechanical Turk annotators get a context and a target label (entailment, neutral or contradiction) and write a hypothesis intended to fool the best current model; the model reports its label probabilities back to them.
2. Examples the model misclassified are checked by two or three other humans. Those that pass become dev and test material, and all remaining examples go to train.
3. A stronger model is then trained on the enlarged data and serves as the next round's adversary.

Three rounds (A1, A2, A3) were collected. Contexts for A1 and A2 come from HotpotQA; round 3 brings in new domains and also a stronger adversary. Annotators also supply explanations. Training examples were not verified.

## Results (self-reported)

- Round difficulty: RoBERTa trained on SNLI, MNLI, FEVER-NLI and ANLI scores 73.8 on A1 test, 48.9 on A2 and 44.4 on A3, and 53.7% across the whole ANLI test set; trained on SNLI and MNLI alone it scores 31.1% on the full set and 22.1% on A3 (chance is 33%, labels balanced).
- Fooling rate: the rate of verified model errors dropped from 18.33% (A1) to 8.07% (A2), 9.52% overall, while the mean number of tries behind each verified example went up, 3.4 in A1 against 6.4 in both A2 and A3.
- Training value: ANLI alone (about 163k examples) matches BERT trained on SNLI plus MNLI (943k) at about 86 on MNLI. At equal training size, the mix containing adversarial data (SMD1+A) scores 72.6 on A1 against 45.1 for the mix with a second static set (SMD1+SMD2). Verified examples are worth much more than unverified ones, which fall to random in later rounds.
- State of the art at the time: SNLI test 92.9 (RoBERTa with FEVER, A1 and A2 added) against 91.6 for MT-DNN; MNLI dev 91.0 matched and 90.7 mismatched.
- A hypothesis-only RoBERTa trained on ANLI scores 51.0 on A1, 42.6 on A2 and 41.5 on A3.
- Annotators agree: Fleiss kappa across the writer and first two verifiers (dev plus test) is 0.7210 for A1, 0.6910 for A2 and 0.6786 for A3. The share of numerical and quantitative reasoning in 500 tagged dev examples per round drops from 38% (A1) to 10% (A3).
- On the antonym stress test the ANLI-trained model scores 85.9 and 82.1 where the previous model scored 14.4 and 10.2.

## Limits

- Training examples are unverified, so some label noise remains; hypothesis-only models are slightly above chance on ANLI.
- Round-to-round difficulty is partly confounded because round 3 changes contexts as well as the adversary.
- The paper gives no cost or time comparison with static collection, and applying the method to generative tasks is left unclear.
- Only three rounds; later saturation by stronger models is not assessed. Hyperparameters, seeds and compute are not stated.

## See Also
- [[SNLI and MultiNLI Crowdsourced NLI Corpora]] — prerequisite-for (the static corpora ANLI is trained alongside and compared with)
- [[Dynabench]] — related (the same write-to-fool-a-live-model loop as an open platform)
- [[HotpotQA]] — related (source of A1/A2 contexts)
- [[FEVER Fact Verification Dataset]] — related (its NLI version is one training set)
