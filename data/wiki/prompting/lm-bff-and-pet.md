---
title: LM-BFF and PET Prompt-Based Fine-Tuning
tags: [prompting, pattern]
summary: "Two 2021 recipes that recast classification as a cloze task for a small masked language model and fine-tune on few labels (LM-BFF 16 per class, PET 32 in total): LM-BFF (RoBERTa-large, searched templates, sampled demonstrations) and PET (ALBERT, ensembled patterns distilled into a classifier); each reports its own gains (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-gao-2021-making-pre-trained-language-models.md
  - data/raw/papers/2026-11-07-schick-2021-its-not-just-size-that.md
  - data/raw/papers/2026-11-08-schick-2021-exploiting-cloze-questions-few-shot.md
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

## PET in the EACL 2021 paper

Schick and Schütze (EACL 2021, "Exploiting Cloze Questions") define PET as a semi-supervised procedure. A **pattern** P maps x to a phrase with exactly one mask token; a **verbalizer** v is an injective map from labels to vocabulary words; (P, v) is a pattern-verbalizer pair. For each pair, one MLM is fine-tuned on the small labelled set plus an auxiliary MLM loss weighted at alpha=1e-4. The pair ensemble then soft-labels unlabelled data (temperature 2), and an ordinary classifier is trained on those labels. iPET repeats this over generations whose training sets grow by a factor of 5, and can run zero-shot. Appendix E adds automatic verbalizer search (AVS).

Setup: RoBERTa-large (355M), Yelp, AG's News, Yahoo and MNLI, three seeds, mean accuracy, 10,000 unlabelled examples per label, all self-reported.

- 10 labelled examples on Yelp: PET 52.9 against 21.1 for supervised fine-tuning (near chance). MNLI-m with 100 examples: PET 74.7, iPET 78.4, supervised 47.9.
- Zero-shot iPET on AG's News scores 87.5, above supervised training with 1000 examples (86.9).
- Without a dev set pattern choice matters: unsupervised single patterns on Yelp average 33.8 against 40.8 for the pattern best on test. With 10 examples, PET (52.9) is above the best single pattern once fine-tuned (52.4); distilling the ensemble beats the undistilled ensemble (52.9 against 51.7); uniform against weighted ensembling shows no clear difference.
- With RoBERTa-base at 10 examples on Yelp, PET 48.8 and iPET 52.9 beat UDA at 27.3 and MixText at 20.4; the steps of those two were tuned on the test set, which favours them. On the German part of x-stance with 1000 examples (XLM-R base, macro F1): PET 66.4 against 43.3 supervised, shrinking to 77.9 against 76.6 on the full German set.
- Handcrafted verbalizers beat AVS (Yelp, 50 examples: 60.0 against 55.2), though AVS still beats supervised (44.8). The auxiliary LM loss helps most at 10 examples and matters less or hurts with more data. Skipping iPET generations 2-3 is worse than gradual growth.
- A single PET model trained for 250 steps in roughly half an hour on a single GTX 1080 Ti, and the final classifier, at 5000 steps, took 2 hours.

## Limits

- LM-BFF: performance still lags fine-tuning on thousands of examples, with high variance across splits; automatic search still relies on a manual template or manual label words; it suits short inputs with few classes; SST-2 and SNLI were used for development; SBERT was trained on SNLI and MNLI; only BERT and RoBERTa-scale masked models; no significance tests.
- PET (EACL 2021 paper): It needs a task expressible as patterns with hand-written patterns and verbalizers, and AVS breaks down on 3 of the 10 Yahoo labels and every MNLI label; it needs a large unlabelled in-domain set; gains shrink as labelled data grows (no AG's News advantage at 1000); one supervised MNLI run was excluded as underfit; iPET iterations beyond those tested and in-domain pretraining beyond Yelp were not explored; it fine-tunes masked LMs by gradient updates and is a different thing from prompting a frozen generative LM in context.
- PET: GPT-3 was not available to the authors and was not given identical examples; PET needs up to 20,000 unlabelled examples and hand-written patterns; still below full-data SuperGLUE results (89.3); ALBERT's advantage is not isolated from unidirectionality; classification only.

## See Also
- [[Few-Shot Prompting]] — prerequisite-for
- [[Prompt Optimization]] — related (searched templates)
- [[Prompt Order Sensitivity and Entropy Probing]] — related (follows this paper's datasets and templates)
- [[Fine-Tuning as Prompt Compression]] — related
- [[Prompt-Based Learning Survey Typology]] — related (the survey covers both recipes)
- [[True Few-Shot Prompt Selection]] — related (tests prompt and hyperparameter selection without a validation set)
