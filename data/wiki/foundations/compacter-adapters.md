---
title: Compacter Adapters
tags: [foundations, concept]
summary: "Compacter builds adapter weights from shared Kronecker factors and per-adapter rank-one factors, so a frozen T5-base trains 0.047 to 0.073% of its parameters yet matches full fine-tuning on GLUE and SuperGLUE (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-mahabadi-2021-compacter.md
---

# Compacter Adapters

Mahabadi, Henderson and Ruder (NeurIPS 2021) ask how few trainable parameters a pretrained language model needs to match full fine-tuning. The hypothesis is that adapter weights written as shared slow factors times cheap per-layer fast factors reach that with O(k+d) parameters.

## Mechanism

- Adapters sit after the attention and feed-forward blocks of a frozen T5-base. Each down or up projection is a sum of n Kronecker products A_i (x) B_i, where the A_i are shared across all layers and each B_i is a rank-one matrix s_i t_i^T owned by one adapter. This is a low-rank parameterized hypercomplex multiplication layer (LPHM).
- Compacter++ places a single adapter, the one following the feed-forward sublayer.
- Parameter count per the paper's analysis is 4L(k+d)+n^3 against 2L(2kd) for standard adapters, a reduction of 11.4x for Compacter and 17.7x for Compacter++ at n=4 on T5-base.

## Results (self-reported)

- On GLUE with T5-base (222M), a single run per cell, the output layer frozen and layer norms trained, and n picked from 4, 8 or 12 plus adapter size by validation: Compacter++ (0.047% of parameters trained) matches full fine-tuning on the average, while Compacter (0.073%) edges past it. The standard Adapter (0.832% trained) scores 85.78 and a Pfeiffer-style adapter (0.427%) 86.32. BitFit (0.126%) scores 84.97. Prompt tuning (0.034%) is far lower, and Intrinsic-SAID (0.009%) sits 1.05 under fine-tuning.
- On SuperGLUE, using T5-base with n=12 and half of each small validation set as test data, Compacter++ averages above full fine-tuning.
- Cost (T5-base, 1 epoch MNLI, one RTX 3090, adapter size 24, n=4): Compacter++ cuts training memory 41.94% and epoch time 26.51% against full fine-tuning; BitFit is cheapest (64.20% less memory, 35.06% faster); prompt tuning with 100 prefix tokens uses 24.42% more memory; Intrinsic-SAID takes 241.82% longer.
- Low-resource GLUE subsets (100 to 4000 examples, 5 seeds): Compacter++ improves over full fine-tuning, read from a figure with no numbers in text.

## Limits

- Just T5-base and T5-small were tried. At T5-small size, each parameter-efficient method lands under full fine-tuning on GLUE; the best Adapter reaches 81.06 and Compacter 80.97.
- Single run per cell with no error bars in the main tables, selected on validation. Prompt tuning was unstable and the best of 6 seeds is reported.
- Much of what gets trained is layer norms and biases. Also training the output layer raises Adapter to 86.48, yet that layer then accounts for roughly 11% of the trained parameters.
- The extraction notes there is no LoRA baseline and LoRA is not cited.

## See Also
- [[Bottleneck Adapters for Parameter-Efficient Transfer]] — prerequisite-for
