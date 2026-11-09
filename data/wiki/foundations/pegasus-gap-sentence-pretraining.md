---
title: PEGASUS Gap-Sentence Pretraining
tags: [foundations, pattern]
summary: "PEGASUS pre-trains an encoder-decoder by masking the whole sentences that score highest in ROUGE1-F1 against the rest of the document and generating them as a pseudo-summary; the 568M model beat BART on XSum ROUGE-2 and fine-tuned from 1,000 examples beat the previous best on 6 of 12 datasets (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-zhang-2019-pegasus.md
---

# PEGASUS Gap-Sentence Pretraining

Zhang and colleagues (ICML 2020) test whether a pre-training objective that resembles summarisation, generating whole important sentences, gives better and faster fine-tuning than generic denoising. **Gap Sentences Generation** (GSG) selects whole sentences from a document, masks them, concatenates them into a pseudo-summary and generates it from the remaining document. The **gap sentence ratio** (GSR) is the share of sentences selected.

## Mechanism

- Standard transformer encoder-decoder. Each sentence is scored by its ROUGE1-F1 against the remainder of the document, and sentences are picked greedily (the top-scoring selection, "Ind-Orig", beat random and lead selection in the ablation); chosen sentences are replaced by a mask token and the model generates them as one output.
- Ablations ran on a 223M base model, then a 568M model was trained and fine-tuned on 12 summarisation datasets and in low-resource settings.

## Results (self-reported)

- On the XSum test set, PEGASUS-large pre-trained on HugeNews and fine-tuned on the full training set scores ROUGE 1/2/L 47.21/24.56/39.25 against BART 45.14/22.27/37.25.
- With only the first 1,000 fine-tuning examples (2000 steps, batch 256) the large model reaches CNN/DailyMail ROUGE-2 19.35, above a prior method using 3,000 examples, and beats the previous best on 6 of 12 datasets. Zero-shot it beats a GPT-2 summarisation prompt on CNN/DailyMail.
- Gains from pre-training are largest on small datasets: Reddit TIFU ROUGE-2 rises from 1.94 for a transformer without pre-training to 8.94.
- Ablations (PEGASUS-base, C4, 500k steps, XSum ROUGE-2): Ind-Orig scores 16.58, random selection 16.23 and lead selection 16.12, masked-language-modelling alone 14.48. Corpus should match the domain: HugeNews 18.47 against 16.58 on XSum, C4 better on WikiHow (15.64 against 14.67).
- Human evaluation (100 examples per dataset, Mechanical Turk, 3 raters, 1-5): XSum 3.0 against 3.0 for the human reference; CNN/DailyMail 3.6 against 3.1; on Reddit TIFU the model fine-tuned on 100 examples scored 2.1 against 3.3, and human level needed full supervision.
- Overlap of test targets with C4 mattered only for XSum (15-20%); filtering changed ROUGE by under 1%. The extraction notes that, on every dataset, the model's summaries are less abstractive than human-written ones.

## Limits

- The authors concede that ROUGE penalises abstractive summaries too harshly and ignores linguistic quality. No factuality evaluation.
- Inputs are capped at 1024 tokens; several datasets have longer inputs. Human evaluation covers 3 datasets with 100 examples each.
- Compute, seeds and warmup are not stated and the HugeNews corpus is not released. ROUGE-based claims have since been overtaken by LLMs.

## See Also
- [[UL2 Mixture of Denoisers]] — related (another pre-training objective study)
- [[BARTScore]] — related (scores summaries with a BART model)
- [[Summary Factual Consistency Metrics]] — related (the factuality check this paper lacks)
