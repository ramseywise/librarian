---
title: T5 Text-to-Text Transfer Transformer
tags: [llm, pretraining-and-data, concept]
summary: "T5 casts every NLP task as text in and text out for one encoder-decoder Transformer, and Raffel et al. vary architecture, objective, data, transfer method and scale one factor at a time on the C4 corpus before scaling to 11B parameters."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-raffel-2019-exploring-limits-transfer-learning-unified.md
---

# T5 Text-to-Text Transfer Transformer

Raffel et al. cast each task as text with a task prefix and train one encoder-decoder Transformer by maximum likelihood. They say they are not proposing new methods but surveying and comparing existing ones. Their baseline is 220M parameters with span-style denoising on C4 for 2^35 tokens, followed by per-task fine-tuning. Variants change one factor at a time, and the best settings are then merged and scaled up to the T5 sizes Small, Base, Large, 3B and 11B, pretrained on about 1T tokens.

## Named pieces

- **C4:** the Colossal Clean Crawled Corpus, heuristically cleaned English Common Crawl text (about 750 GB).
- **Span corruption:** contiguous token spans are dropped from the input, each marked by its own sentinel, and the model outputs the dropped spans. The authors credit SpanBERT as the inspiration.
- **Prefix LM:** a decoder-only model that attends freely within the input prefix and causally over the target.

## Comparative findings (self-reported)

- Pretraining matters: the baseline does better on GLUE than no pretraining.
- An encoder-decoder with a denoising objective is the best architecture tried; a decoder-only language model with denoising is much worse on GLUE.
- Data: removing C4's heuristic filtering (an unfiltered 6.1TB set) hurts GLUE, and repeating the first 2^23 tokens of C4 4,096 times degrades GLUE.
- Scale: with 4x compute, a model 4x larger trained for 1x steps beats 1x size trained 4x steps on SuperGLUE. Non-scaling changes still help beyond 1T tokens (T5-Base on validation).
- Transfer: adapter layers with a small bottleneck (d=32) land well under full fine-tuning on translation.
- Final T5-11B (1T-token multi-task pretraining, per-task fine-tuning) reaches the best GLUE test average, takes SuperGLUE test to near the human 89.8, and sets the best SQuAD validation exact match, is also evaluated on CNN/DM ROUGE-2 (test, beam 4), but did not beat the prior best on WMT En-Fr BLEU.

## Limits

- The coordinate-ascent design misses interactions between factors (the authors concede). Non-baseline variants ran once, and the variance estimate comes from 10 baseline runs.
- The baseline is small (220M, 34B tokens); the authors say bigger models may overfit small pretraining sets more.
- English-only pretraining and no state of the art on any WMT task. Almost every comparison uses validation sets, SQuAD's final number included.
- The low-resource tasks CoLA, CB and COPA vary a lot, so the GLUE and SuperGLUE averages are noisy. Table 10 seems to repeat the d=128 row where d=2048 should be.
- State-of-the-art claims and model sizes are as of October 24, 2019 and have dated.

## See Also
- [[Transformer Architecture]] — prerequisite-for
- [[BERT Masked-LM Pretraining and Its Refinements]] — prerequisite-for (the masked-LM objective it adapts)
- [[Denoising Seq2Seq Pretraining: BART, MASS and GLM]] — alternative-to (other denoising encoder-decoder objectives; BART is described as concurrent work)
- [[Multilingual Pretraining: XLM, XLM-R, mBART and mT5]] — extends (mT5 applies the recipe to 101 languages)
- [[Multitask Prompted Instruction Tuning (FLAN, T0, Super-NaturalInstructions, MetaICL)]] — extends
- [[Parameter-Efficient Fine-Tuning Methods]] — related (adapter layers are one of the transfer methods compared)
- [[UnifiedQA Format-Agnostic QA]] — extends
- [[Code Encoder and Encoder-Decoder Pretraining]] — extends (CodeT5 adapts T5 span masking to code)
