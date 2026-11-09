---
title: Prompt Order Sensitivity and Entropy Probing
tags: [prompting, concept]
summary: "The order of the same few-shot examples can swing GPT-2 and GPT-3 classification accuracy from about 85% to about 50%; Lu et al. rank orderings without labels by the entropy of predictions on a model-generated probing set (GlobalE, LocalE), reporting gains (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-07-lu-2022-fantastically-ordered-prompts-where-find.md
---

# Prompt Order Sensitivity and Entropy Probing

Lu et al. (ACL 2022) study how much the order of in-context examples changes classification accuracy, and whether good orders can be chosen without a labelled development set.

## What they find

- On SST-2 with four examples, all 24 orderings of one balanced set range from over 85% to around 50% accuracy, across GPT-2 (0.1B to 1.5B) and GPT-3 (2.7B to 175B).
- One particular permutation can fall sharply when GPT2-XL is replaced by GPT2-Large. Rank correlation of orderings between the 175B and 2.7B models is near zero, so a good order does not transfer across sizes. Good label orderings are likewise inconsistent across models.
- Calibration raises accuracy but variance stays high, and most failing prompts predict an unbalanced label distribution. Adding more training examples raises accuracy while variance remains and can grow.
- The paper contrasts this with supervised fine-tuning seeds, which it cites as typically under 1% standard deviation.

## The probing method

For a random set of four training examples, all 24 orderings are tried. Each ordering is used to sample text from the model (temperature 2), which builds an **unlabelled probing set** for that ordering. Orderings are then ranked by two scores:

- **GlobalE**: entropy of the label distribution the model predicts across the probing set.
- **LocalE**: prediction entropy averaged per item across the probing set.

The top 4 of 24 orderings are evaluated on 11 classification datasets. The authors report an average 13% relative improvement across tasks (self-reported). Example from the table: SST-2 with a 0.8B GPT-2 and four shots, five example sets times 24 permutations, baseline 74.5 (std 10.3) against GlobalE 84.8 (std 4.1), with an oracle at 88.9 (self-reported). Splitting the four examples into a train half and a validation half scored 75.1 in the same setup, below entropy probing. LocalE gives a slightly smaller gain than GlobalE; GlobalE lifts GPT-3 175B on CB from 75.1 to 79.9 (self-reported).

## Limits

- The paper itself has no section on limitations.
- Probing needs a sampling run per ordering, so cost grows factorially with the number of shots; only 4-shot was tested (1 to 2 shot for DBPedia and AGNews) since GPT-2's context is limited to 1024 word pieces.
- Classification only. To save cost, GPT-3 175B used 2 example sets with 12 permutations each. There are no significance tests.
- GPT-2 scores close to random on CB and RTE, where the gains stay within chance or majority-vote levels.
- The order-sensitivity figures use one fixed 4-example SST-2 set; other sets appear only as variance summaries.
- Models are GPT-2 and GPT-3 from 2021; instruction-tuned models were not studied.
- The extraction notes that the paper reaches the opposite conclusion from an earlier study that found order matters little after nearest-neighbour retrieval.

## See Also
- [[Few-Shot Prompting]] — prerequisite-for
- [[FormatSpread]] — related (the same sensitivity along the format axis)
- [[Benchmark Prompt Format Sensitivity]] — related
- [[LM-BFF and PET Prompt-Based Fine-Tuning]] — related
