---
title: XSum Extreme Summarisation
tags: [eval, language-tasks, concept]
summary: "XSum is a one-sentence news summarisation dataset built from 226,711 BBC articles whose first sentence is the author's summary; Narayan et al. show it is far less extractive than CNN, DailyMail or NY Times, and pair it with T-ConvS2S, a convolutional seq2seq model conditioned on LDA topics."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-narayan-2018-dont-give-me-details-just.md
---

# XSum Extreme Summarisation

Narayan, Cohen and Lapata (EMNLP 2018) define **extreme summarisation** as a single-document task producing a one-sentence news summary that answers the question "What is the article about?". Their hypothesis is that existing datasets favour extractive models, that a one-sentence BBC summary set is less extractive, and that a convolutional seq2seq model given LDA topics should capture long-range, whole-document content better than RNNs do.

## The dataset

XSum has 226,711 BBC articles, each paired with its own opening sentence, which the author wrote and which serves as the summary. The test set has 11,334 articles.

- XSum's gold summaries contain many more unigrams absent from the article than those of CNN, DailyMail or NY Times (17%, 17% and 23% for those), and the share of novel higher-order n-grams is also high (the comparison sets have 47 to 55% novel bigrams).
- The best single-sentence extractive oracle gets just 29.79 ROUGE-1 on XSum, against 50.38 on CNN.
- LEAD, which takes the first sentence, has a very low ROUGE-2 on XSum, where CNN gives 11.13; the extraction notes that two tables print different values for this system (Table 4 shows 1.60).

## T-ConvS2S

T-ConvS2S extends fairseq's convolutional seq2seq model (see [[Encoder-Decoder Translation Before the Transformer]]) by adding LDA word-topic and document-topic vectors to both encoder and decoder: each input embedding is the sum of word and position embeddings concatenated with a term built from the word-topic vector and the document-topic vector. Setup: 512 LDA topics, beam 10.

The comparison systems are Random, LEAD, EXT-ORACLE, an RNN seq2seq, the pointer-generator (with coverage and without) and unmodified ConvS2S.

## Results (self-reported)

- T-ConvS2S with topics in encoder and decoder has the best ROUGE-1, ROUGE-2 and ROUGE-L on the XSum test set; its variants differ little (ROUGE-1 from 31.71 to 31.89), and no significance test is reported.
- The pointer-generator beats EXT-ORACLE on ROUGE-2; adding coverage does worse than without it.
- Human best-worst ranking (50 test documents; every pair among 5 systems, judged by 3 people per comparison): T-ConvS2S ranks second behind gold, and the pointer-generator ranks worst.
- A question-answering test (100 questions over 50 documents, 5 participants per summary, half credit for partial answers): the pointer-generator scores 21.40, and its difference from EXT-ORACLE is not significant. Gold scores 97.23% because the questions were written from it.
- Novel n-grams: ConvS2S 31.26, pointer-generator 27.40, gold 35.76. Trained on XSum, the pointer-generator copies few n-grams from the source; on CNN/Daily Mail See et al. report it copies 99% of unigrams.

## Limits

- XSum is not diverse: a single outlet (BBC) and a single-sentence style, a concession by the authors.
- ROUGE alone can mislead about informativeness: EXT-ORACLE gets high ROUGE yet low QA and human scores.
- Both human studies use only 50 test documents, and the authors wrote the QA questions from the gold summary, which favours gold.
- Seeds, variance, parameter counts, epochs and training time are all absent.

## See Also
- [[Pointer-Generator Network and Coverage]] — prerequisite-for (the baseline model)
- [[ROUGE Overlap Metrics for Summaries]] — prerequisite-for
- [[Webis-TLDR-17 Reddit Summarization Corpus]] — related (another summarisation dataset)
- [[Summarization and Translation Hallucination Studies]] — related
