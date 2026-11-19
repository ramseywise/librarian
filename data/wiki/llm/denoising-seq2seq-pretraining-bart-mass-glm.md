---
title: "Denoising Seq2Seq Pretraining: BART, MASS and GLM"
tags: [llm, pretraining-and-data, comparison]
summary: "BART, MASS and GLM each pretrain a model to rebuild masked or corrupted text, but differ in what is corrupted and what the decoder sees: arbitrary noising with a bidirectional encoder (BART), one masked fragment with a fragment-only decoder (MASS), and shuffled blanks in one model (GLM)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-lewis-2020-bart.md
  - data/raw/papers/2026-11-08-song-2019-mass.md
  - data/raw/papers/2026-11-08-du-2022-glm.md
---

# Denoising Seq2Seq Pretraining: BART, MASS and GLM

All three pretrain a generation-capable model by reconstructing text from a corrupted version. They differ in the corruption and in how the decoder is fed.

| Method | Architecture | What is corrupted | Decoder input |
|---|---|---|---|
| BART | encoder-decoder | any noising function; best: text infilling plus sentence permutation | the original document, left to right |
| MASS | encoder-decoder | one consecutive fragment (about 50% of tokens) | fragment tokens only; other positions replaced by [M] |
| GLM | one Transformer | several blanks, each replaced by one [MASK] | spans generated in random order, two-part attention |

## BART

Lewis et al. pretrain an ordinary seq2seq Transformer, whose encoder is bidirectional and whose decoder runs left to right, to rebuild the original documents. Text infilling samples spans with Poisson lengths (lambda = 3) and replaces each by a single [MASK], with zero-length spans inserting a mask; sentence permutation shuffles the sentences of a document. They say text infilling plus sentence shuffling worked best.

Claims (self-reported): BART large improves on the previous best (RoBERTa-based) XSum system by roughly 3.5 ROUGE points and is the best reported on CNN/DailyMail, while equalling RoBERTa on GLUE and SQuAD 1.1. For WMT16 RO-EN with back-translation data, a tuned BART beats a strong back-translation baseline, though a fixed BART scores 36.29, under it. In the base-size ablation (1M steps, same data) text-infilling variants are the most consistent and document rotation or sentence shuffling alone perform poorly. On XSum humans prefer BART to BERTSUMEXTABS but prefer the human reference (reference 67%, BART 33%).

## MASS

Song et al. mask a consecutive fragment in the encoder input and train the decoder to predict that fragment, replacing the decoder's other inputs with [M]. They show BERT's masked LM is the k=1 special case and a standard language model the k=m case. Results (self-reported, 6-layer Transformers pretrained on News Crawl): unsupervised en-fr newstest2014 37.5 BLEU, 4.1 above XLM; under the same fine-tuning on en-fr, MASS 37.5 against BERT+LM 33.4 and a denoising autoencoder 30.1 (BERT+LM taken from XLM). Gigaword summarisation with 3.8M pairs: ROUGE-1 38.73 against 37.75 (BERT+LM) and 35.97 (denoising autoencoder). Random discrete masking and feeding all tokens to the decoder both lower BLEU. Pretraining validation perplexity is best for fragment length between 50% and 70% of the sentence, downstream best near 50%; k=1 and k=m are both poor.

## GLM

Du et al. mask spans, each replaced by one [MASK], then generate the spans autoregressively in random order. Part A (the corrupted text) attends bidirectionally and Part B (the spans) causally, with a 2D positional encoding: position in the corrupted text and position within a span. NLU tasks are fine-tuned as cloze questions with verbalizers. Document-level and sentence-level long-span variants add multi-task objectives.

Claims (self-reported): on SuperGLUE dev, GLM Base averages 4.6% above BERT Base and GLM Large 5.0% above BERT Large (BookCorpus and Wikipedia pretraining). A reproduced BERT Large averages 71.2 against 77.0 for GLM Large. Removing span shuffling drops GLM Large from 77.0 to 68.5; sentinel tokens instead of one [MASK] give 76.0; cloze fine-tuning against a classifier is 77.0 against 70.0. GLM RoBERTa (158GB, 250K steps) reaches a SuperGLUE dev average of 82.9. On XSum GLM RoBERTa gets ROUGE-1 45.5 against 45.1 for BART Large. GLM Large pretraining took roughly 2.5 days on 64 V100 GPUs.

## Limits

- BART: fine-tuning hyperparameters, optimiser, learning rate, hardware and compute go unreported; the permuted-LM ablation leaves out two XLNet components (relative position embeddings, segment recurrence) and so is not a full XLNet replication; runs are single, with no variance. A plain language model reaches lower ELI5 perplexity, translation works less well and overfits more without back-translation data, and the authors name hallucination of unsupported content as the main qualitative weakness.
- MASS: pretraining steps, schedule, dropout and seeds are not stated; models are small (6 layers); the dialogue data size is inconsistent (140K pairs, then 110K for training); some BERT+LM numbers come from XLM rather than a rerun; the extraction notes DAE dialogue numbers mentioned in the text are absent from Table 5.
- GLM: no variance or significance tests; the comparison with T5 is not direct because data and parameter counts differ; GLM RoBERTa trained only 250K steps and its data differs from RoBERTa's (Stories replaced); the document-level objective slightly lowers NLU and conditional-generation results; a GLM Large without the generative objective cannot do zero-shot language modelling (perplexity above 100); zero-shot LM numbers are only in a figure; generated samples contain factual errors.

## See Also
- [[Code Encoder and Encoder-Decoder Pretraining]] — extends (PLBART applies BART denoising to code)
- [[T5 Text-to-Text Transfer Transformer]] — alternative-to (span corruption with an encoder-decoder; BART is described as concurrent work)
- [[BERT Masked-LM Pretraining and Its Refinements]] — prerequisite-for (BART, MASS and GLM generalise masked LM; BART's infilling follows SpanBERT)
- [[XLNet Permutation Language Modeling]] — prerequisite-for (GLM takes the idea of permuted span order)
- [[Multilingual Pretraining: XLM, XLM-R, mBART and mT5]] — extends (mBART applies BART's noising to many languages)
- [[PEGASUS Gap-Sentence Pretraining]] — related
