---
title: BitFit Bias-Term Fine-Tuning
tags: [llm, fine-tuning, concept]
summary: "BitFit freezes every weight matrix of a BERT-style encoder and trains only its bias vectors plus the classifier, matching full fine-tuning on GLUE averages with under 0.1% of the parameters (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-zaken-2022-bitfit.md
---

# BitFit Bias-Term Fine-Tuning

Ben-Zaken, Ravfogel and Goldberg (ACL 2022, short paper) ask whether fine-tuning a masked language model needs to change anything but its bias terms. Their hypothesis is that fine-tuning mostly exposes knowledge learned during language-model pretraining rather than teaching new task knowledge, so few parameters should suffice.

## Mechanism

Frozen: every weight matrix in BERT or RoBERTa, plus the layer-norm gains. Trained: the bias vectors and a linear classifier on the [CLS] token. Bias terms are 0.09% of BERT-Base and 0.08% of BERT-Large parameters. Tuning only the query biases and the intermediate-MLP biases uses 0.04%.

## Reported results (self-reported)

- BERT-Large, GLUE dev average over nine tasks, mean of five seeds: 84.2 for BitFit against 84.1 for full fine-tuning, with 0.08% of parameters. On GLUE test, BERT-Large averaged 80.9 against 81.8 for full fine-tuning and 81.1 for adapters (baselines copied from earlier papers).
- BERT-Base dev: 82.4 against 82.3 for full fine-tuning; RoBERTa-Base 84.6 against 85.3.
- Query and intermediate-MLP biases alone (0.04%) scored 81.1 against 82.4 for all biases (BERT-Base). A randomly chosen set of equal size (0.09%) did clearly worse, 78.5 uniform and 79.5 by rows and columns, and a fully frozen BERT-Base with only the classifier scored 62.1.
- PTB part-of-speech tagging: 97.2, 97.4 and 97.1 for BERT-Base, BERT-Large and RoBERTa-Base against 97.2, 97.4 and 97.2 for full fine-tuning.
- On SQuAD v1.0 BitFit beat full fine-tuning with small training subsets and the trend reversed with more data (values only in figures).
- It has about six times fewer trainable parameters than Diff-Pruning and 45 times fewer than Houlsby's adapters, which use 3.6%.

## Limits

- Only BERT-family masked language models; no decoder or large LLMs.
- On large datasets full fine-tuning wins: QQP (85.4 versus 87.5 F1 on BERT-Large), MNLI, and SQuAD given more data.
- The Diff-Pruning and adapter baselines are taken from their own papers; only four learning rates were tried; hardware, schedule and sequence length go unreported; the QNLI test score cannot be lined up with earlier published figures.
- Why bias terms work is left open.

## See Also
- [[Parameter-Efficient Fine-Tuning Methods]] — prerequisite-for (the family overview)
- [[Prefix-Tuning and Prompt Tuning]] — alternative-to (adds vectors instead of training existing biases)
- [[LoReFT Representation Finetuning]] — related (the ReFT paper lists BitFit among its baselines)
- [[Diff Pruning Sparse Task Difference Vectors]] — alternative-to
