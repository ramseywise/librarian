---
title: LM-BFF and PET Prompt-Based Fine-Tuning
tags: [prompting, pattern]
summary: "Two 2021 recipes that recast classification as a cloze task for a small masked language model and fine-tune on few labels (LM-BFF 16 per class, PET 32 in total): LM-BFF (RoBERTa-large, searched templates, sampled demonstrations) and PET (ALBERT, ensembled patterns distilled into a classifier); each reports its own gains (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-gao-2021-making-pre-trained-language-models.md
  - data/raw/papers/2026-11-07-schick-2021-its-not-just-size-that.md
---

# LM-BFF and PET Prompt-Based Fine-Tuning

Both papers turn a classification task into a fill-in-the-blank problem and fine-tune a masked language model on a handful of labelled examples. **Prompt-based fine-tuning** frames the downstream task as masked language modelling: given a template, the model outputs a label word. A **label word** is the token that fills the mask for a given label.

## LM-BFF

Gao, Fisch and Chen (ACL-IJCNLP 2021) fine-tune RoBERTa-large on a template with a mask slot, reusing the pretrained output embeddings so no new head is added. Templates come from a T5-3B beam search and label words from a pruned exhaustive search, both picked on a dev set of the training set's size. Optionally the input gets one demonstration per class appended, drawn from the 50% most similar examples by SBERT.

Setup for all numbers: RoBERTa-large, 16 examples per class, mean over 5 splits, self-reported.

- Automatic templates plus sampled demonstrations gain up to 30 points on SNLI and 11 on average over standard fine-tuning, across 15 tasks.
- Label-word choice matters: on SST-2, great/terrible gives 92.7 and the swapped assignment 83.2, against 81.4 for standard fine-tuning.
- On SNLI, template wording and sentence order shift accuracy by over 10 points with identical label words (77.2 for one order, 62.9 swapped).
- Sampling demonstrations by similarity does better than sampling uniformly on SNLI, TREC and MRPC.

## PET

Schick and Schütze (NAACL 2021) fine-tune ALBERT-xxlarge-v2 on cloze-formatted inputs. A **pattern-verbalizer pair** maps an input to a cloze question with one mask and maps outputs to tokens. Several patterns are ensembled and their output is distilled, with unlabelled data, into a sequence classifier; iPET repeats the process over generations. The comparison is with GPT-3 **priming**, where demonstrations are given as context and no gradient updates happen.

- Given 32 labelled examples, PET edges past the 175B GPT-3 in its SuperGLUE test average, and iPET goes higher (self-reported). It uses about 0.1% of GPT-3's parameters.
- On the dev set, PET is 18 points above a similar-sized GPT-3 model, 350M (self-reported).
- Without distillation on CB, RTE and MultiRC, ALBERT averages 71.8, RoBERTa 63.7 and GPT-2 52.0 (self-reported).
- Changing the 32-example training set moves results substantially (RTE 66.4 against 61.4); the average stays comparable to GPT-3 for every seed.

## Limits

- LM-BFF: performance still lags fine-tuning on thousands of examples, with high variance across splits; automatic search still relies on a manual template or manual label words; it suits short inputs with few classes; SST-2 and SNLI were used for development; SBERT was trained on SNLI and MNLI; only BERT and RoBERTa-scale masked models; no significance tests.
- PET: GPT-3 was not available to the authors and was not given identical examples; PET needs up to 20,000 unlabelled examples and hand-written patterns; still below full-data SuperGLUE results (89.3); ALBERT's advantage is not isolated from unidirectionality; classification only.

## See Also
- [[Few-Shot Prompting]] — prerequisite-for
- [[Prompt Optimization]] — related (searched templates)
- [[Prompt Order Sensitivity and Entropy Probing]] — related (follows this paper's datasets and templates)
- [[Fine-Tuning as Prompt Compression]] — related
