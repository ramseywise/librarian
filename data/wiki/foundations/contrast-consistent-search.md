---
title: Contrast-Consistent Search
tags: [foundations, llm, pattern]
summary: "Contrast-Consistent Search (CCS) trains a linear probe on a frozen model's unlabeled hidden states so that a yes-no statement and its negation get opposite probabilities; Burns et al. report it beating calibrated zero-shot on average over 5 models and 10 datasets, and holding up under a misleading prefix (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-08-burns-2022-discovering-latent-knowledge-language-models.md
---

# Contrast-Consistent Search

Burns, Ye, Klein and colleagues (arXiv preprint, 2022; v2 March 2024) ask whether what a language model internally represents as true can be read from its unlabeled hidden activations alone, with no labels and no use of the model's outputs. Their hypothesis is that truth satisfies a logical consistency property that few other features satisfy: negating a statement flips its truth value. A direction in activation space that enforces this should therefore pick out truth.

## Mechanism

1. For each yes-no question q build a contrast pair: the statement answering Yes (x+) and the one answering No (x-).
2. Take the last-token hidden state of each statement from a frozen model, and normalise each of the two sets by subtracting its own mean.
3. Train a linear layer with a sigmoid to give each statement a probability. The loss has two terms: a consistency term pushing p(x+) toward 1 - p(x-), and a confidence term, the square of the smaller of the two probabilities, which rules out the trivial answer of 0.5 for both.

Model weights stay frozen, and no labels or model outputs enter training. Nothing in the method says which side is the true one, so evaluation keeps whichever of the two labelings scores higher. A neighbouring family, Contrastive Representation Clustering, trains no probe: it clusters the differences between normalised states by the top principal component (TPC) or by bimodal salience search (BSS).

## Results (self-reported)

- **Against zero-shot.** Averaged over five models (RoBERTa, DeBERTa, GPT-J, T5 and UnifiedQA, with T0 left out), CCS scores above calibrated zero-shot; the setup is 10 datasets, about 9 prompts each, last-layer last-token states and 1000 examples per dataset with 40% held out for test. Its accuracy varies half as much across prompts as calibrated zero-shot does. Calibration alone lifts zero-shot accuracy by roughly 5% on average.
- **Misleading prefix.** With a few-shot prefix of incorrectly answered questions (UnifiedQA, 10 datasets), calibrated zero-shot falls from 80.4 to 70.9 while CCS moves from 82.1 to 83.8. Using decoder states instead of encoder states, accuracy under the prefix falls like zero-shot.
- **No output format needed.** On DeBERTa-v2 without NLI fine-tuning, with the label placed mid-prompt and no mask token, CCS still works while zero-shot does not (Amazon, 1000 new points, 60/40 split).
- **Transfer and data.** A probe trained on Amazon and tested on every dataset averages slightly higher accuracy than probes trained in-dataset. Pooling all datasets for training adds an insignificant average gain, though a large one for T0.
- **Clustering variants.** The CRC variants with no trained probe are nearly as good as CCS (BSS gets 70.2).
- **Where it loses.** On RoBERTa and on T0, CCS trails zero-shot; T0's zero-shot score is inflated because it was trained on the evaluation datasets.

## Limits

- Success depends on the model actively assessing truth along some direction; the authors say it is unclear when that holds. Deliberate lying or deception by models was not tested.
- Reported accuracy is optimistic because the better labeling is chosen after the fact; an unsupervised fix using conjunctions is only sketched in an appendix.
- The tasks are binary (yes-no) with unambiguous answers, and accuracy stays below a supervised logistic-regression ceiling.
- The misleading-prefix result is ambiguous, since a prefix of correct answers has a qualitatively similar effect, and UnifiedQA alone showed a significant drop.
- T0 is contaminated by training on 9 of the 10 datasets and UnifiedQA was trained on BoolQ. RoBERTa, GPT-J and T5 transfer weakly and sit near chance on some datasets.
- Model sizes are not stated, and the models are from 2020-2021. The extraction notes that later work questioned whether CCS finds truth or other salient features; that is not in this paper.

## See Also
- [[Hidden-State Hallucination Probes]] — related (probes on hidden states; those use labels, CCS does not)
- [[Language Model Self-Knowledge]] — related (another route to what a model knows, from probabilities)
- [[TruthfulQA]] — related (models mimic human falsehoods, cited by the paper)
- [[Contrastive Self-Supervised Pretraining]] — related (a different use of contrastive pairs)
