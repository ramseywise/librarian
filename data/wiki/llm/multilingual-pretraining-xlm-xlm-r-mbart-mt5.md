---
title: "Multilingual Pretraining: XLM, XLM-R, mBART and mT5"
tags: [llm, pretraining-and-data, comparison]
summary: "XLM, XLM-R, mBART and mT5 carry masked-LM, denoising and span-corruption pretraining across many languages; they share language-sampling exponents and a shared subword vocabulary, and the XLM-R paper names the capacity trade-off as the curse of multilinguality."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-lample-2019-cross-lingual-language-model-pretraining.md
  - data/raw/papers/2026-11-08-conneau-2020-unsupervised-cross-lingual-representation-learning.md
  - data/raw/papers/2026-11-08-liu-2020-multilingual-denoising-pre-training-neural.md
  - data/raw/papers/2026-11-07-xue-2021-mt5.md
---

# Multilingual Pretraining: XLM, XLM-R, mBART and mT5

| Model | Objective | Data and vocabulary | Sampling exponent |
|---|---|---|---|
| XLM | CLM, MLM, or MLM + TLM on parallel pairs | Wikipedia plus parallel data; shared BPE vocabulary | exponent form given (q_i proportional to p_i^alpha), value not stated |
| XLM-R | multilingual MLM only (no TLM, no language embeddings) | CC-100, 100 languages, over 2 TB of filtered CommonCrawl; SentencePiece unigram, 250K vocabulary | 0.3 |
| mBART | BART-style noising (word spans masked at 35%, plus sentence permutation), 12+12 layer seq2seq | CC25, 25 languages | 0.7 |
| mT5 | T5 span corruption, T5.1.1 recipe | mC4, 101 languages; 250,000 wordpieces | 0.3 |

## XLM

Lample and Conneau pretrain one Transformer on many languages. Translation language modeling (TLM) concatenates a parallel pair, masks words on both sides and resets target positions, which lets the model draw on the other language; MLM here runs on 256-token streams. Results (self-reported): zero-shot XNLI with MLM + TLM sets a new average, and adding TLM to MLM adds 3.6 points to the XNLI average (English from 83.2 to 85.0). Unsupervised MLM-only XLM beats the supervised encoder of Artetxe and Schwenk, which used 223M parallel sentences. For unsupervised MT, encoder and decoder both initialised from MLM give 34.3 BLEU on de-en, over 9 above the previous best; pretraining only the lookup table gives 27.3. For ro-en in one direction the scores are 28.4 with no pretraining, 31.5 with CLM and 35.3 with MLM. A Nepali LM falls from perplexity 157.2 to 109.3 with English and Hindi data, and Hindi (shared Devanagari script, over 80% of tokens in the shared vocabulary) helps more than English (115.6 against 140.1).

## XLM-R

Conneau et al. train the multilingual MLM at scale. Their ablations (BERT-Base, Wikipedia) show the curse of multilinguality: for fixed capacity, adding languages first helps low-resource languages and then lowers overall accuracy; a larger vocabulary at constant parameter count improves XNLI accuracy; alpha = 0.3 was best overall. Results (self-reported): XLM-R improves XNLI, MLQA (average EM 52.7 against 43.5 for mBERT) and NER over mBERT; Swahili and Urdu gain strongly; low-resource languages benefit far more from CommonCrawl than from Wikipedia. On GLUE it is about 1 point behind RoBERTa. Validation perplexity proved a poor stopping signal: a longer-trained XLM MLM went from 71.3 to above 75 average XNLI. From their experience, with no table, the authors put the floor for learning a BERT model at a few hundred MiB of text.

## mBART

Liu et al. denoise full texts in 25 languages with a 12+12 layer model, then fine-tune on bi-text or use it to initialise unsupervised MT. Results (self-reported): with only 10K En-De pairs mBART02 reaches 20.7+ BLEU while a randomly initialised model scores 0.0; for Ne-En with unsupervised back-translation, mBART scores 10.0 BLEU against 0.5 for XLM; on WMT16 Ro-En, mBART02 38.5 beats mBART25 37.8 and random 34.0. Fine-tuning on one pair transfers to others (Zh fine-tune then test Ja: 9.9 BLEU). Above 25M pairs pretraining gives no gain and slightly hurts (Zh-En 33.3 against 35.0 from random initialisation), and at about 10K pairs it fails (En-Gu 0.3 BLEU). Pretraining for En-My costs 300 to 3000 GPU hours.

## mT5

Xue et al. apply the T5.1.1 recipe to mC4 (1M steps; each batch holds 1024 sequences, each 1024 long), with vocabulary size and alpha following XLM-R. Results (self-reported): mT5-XXL gets 85.0 zero-shot XNLI accuracy and beats humans on TyDi QA in-language in four of its nine languages; mT5-Small trails T5-Small on SQuAD (T5-Small 87.2) while mT5-XXL nearly closes the gap to T5-XXL (96.2). Ablations on mT5-Large (XNLI zero-shot, single changes) found harm from removing the line-length filter, dropout 0.1, span length 10, sequence length 512 and added Wikipedia data; alpha = 0.7 lowers the average, lifting Russian (81.5 to 82.8) but cutting Swahili (75.4 to 70.6). Accidental translation, where a generative model translates its prediction into the wrong language, is reduced by mixing the unsupervised task into fine-tuning at 1:100 (Domain Preserving Training), shown for mT5-Small and Base on XQuAD.

## Limits

- XLM: no seeds or variance; parameter counts, steps, tokens and compute are not given; TLM needs English-centric parallel data; the XNLI comparison with Artetxe and Schwenk and the MLM against MLM + TLM comparison are not equal-data; the EMB baseline was re-run and exceeded published figures, which the authors put down to larger batches; the Nepali gains cover one language and Wikipedia-scale data, and the shared-n-gram explanation is untested; the text is arXiv v1 and later models supersede the numbers.
- XLM-R: the curse of multilinguality remains for modest-size models; RoBERTa beats it by 1.0 on GLUE; optimiser, learning rate, sequence length and token count are not stated; ablations use BERT-Base on Wikipedia and may not transfer to the 550M CC model; the baselines (mBERT, XLM, Unicoder, RoBERTa) are now out of date.
- mBART: expensive to deploy; adding languages costs under 1 BLEU when plenty of target-language monolingual data exists; the noising strategy was not explored; single runs; the back-translation comparison is not equal in monolingual data.
- mT5: illegal (non-substring) predictions remain, with the fix shown only for XQuAD; ablations are single runs on mT5-Large; hardware, compute and optimiser are not stated; XLM-R saw over 6 times more tokens (6.3T against 1T).

## See Also
- [[XGLM Multilingual Few-Shot Language Models]] — related (30-language decoder-only model, CC100-XL)
- [[BERT Masked-LM Pretraining and Its Refinements]] — prerequisite-for (the MLM objective)
- [[T5 Text-to-Text Transfer Transformer]] — prerequisite-for (mT5's base recipe)
- [[Denoising Seq2Seq Pretraining: BART, MASS and GLM]] — prerequisite-for (mBART's noising)
- [[XP3, BLOOMZ and mT0]] — extends (finetunes mT5 on a multilingual prompted mixture)
