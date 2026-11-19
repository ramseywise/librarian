---
title: Early LM Training Corpora
tags: [llm, pretraining-and-data, reference]
summary: "Four public text corpora and what each paper states about them: BookCorpus (11,038 books), the One Billion Word benchmark (WMT11 news), the Pushshift Reddit dump (651M submissions and 5.6B comments) and S2ORC (81.1M papers); the Zhu paper says nothing on licensing, consent or duplicates, and the Pushshift paper analyses no duplication."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-zhu-2015-aligning-books-movies.md
  - data/raw/papers/2026-11-08-chelba-2014-one-billion-word-benchmark-measuring.md
  - data/raw/papers/2026-11-08-baumgartner-2020-pushshift-reddit-dataset.md
  - data/raw/papers/2026-11-08-lo-2020-s2orc.md
---

# Early LM Training Corpora

One reference page for four corpora; the Zhu (BookCorpus) and Baumgartner (Pushshift) papers are not language-model papers. All figures are the papers' own (self-reported).

## BookCorpus (Zhu et al. 2015)

BookCorpus holds 11,038 books, roughly 985M words. Zhu, Kiros, Zemel et al. assembled it to train a sentence embedding (skip-thought, a GRU encoder-decoder) for a system that matches books with their film versions; the same paper releases MovieBook, 11 movie and book pairs with 2,070 annotated correspondences (90 hours of annotation). The alignment model stacks nine similarity measures through a 3-layer context CNN into a chain CRF, fitted on a single movie (Gone Girl) and evaluated on the remaining 10. The extraction states the paper says nothing about licensing, consent or duplicates of BookCorpus.

## One Billion Word benchmark (Chelba et al. 2014)

A reproducible benchmark built from WMT11 monolingual English text: deduplicate, tokenise, apply a vocabulary count cutoff of 3, shuffle and partition. After deduplication the corpus has 829,250,940 words, a vocabulary of 793,471 and a test out-of-vocabulary rate of 0.28% (test partition 159,658 words). Baselines on its test set:

| Model | Test perplexity |
|---|---|
| Unpruned interpolated KN 5-gram (1.1B n-grams) | 67.6 |
| RNN-256 / 512 / 1024 + MaxEnt 9-gram (60, 120, 240 hours) | 58.3 / 54.5 / 51.3 |
| Linear interpolation of all models | 43.8 (about 35% below KN) |

The RNN-1024 model has 20B parameters and trained 240 hours on 24 CPUs. Stupid Backoff scores 87.9 alone yet gets interpolation weight 0.20, against 0.06 for KN. Cutting the model to 15M n-grams damages KN much more than Katz (perplexity 243.2 versus 127.5).

## Pushshift Reddit dump (Baumgartner et al. 2020)

Monthly ndjson dumps of all Reddit submissions and comments from June 2005 to April 2019: 651,778,198 submissions, 5,601,331,385 comments and 2,888,885 subreddits, about 5M comments per day by April 2019, several terabytes in total. Pushshift also serves a search and aggregation API (500M requests per month at the time of writing). The authors count over 100 peer-reviewed publications using the data as of late 2019. It is a dataset paper: no models, filtering or quality analysis. The Reddit crawl behind [[Webis-TLDR-17 Reddit Summarization Corpus]] is a Pushshift-based crawl, and [[Dolma Open Pretraining Corpus]] takes 89B tokens from Reddit through Pushshift.

## S2ORC (Lo et al. 2020)

S2ORC aggregates PDF and LaTeX parses of academic papers into 81.1M English papers carrying metadata, abstracts and resolved citation links; 8.1M open-access PDFs (10.0% of the corpus) and 1.5M LaTeX parses also have structured full text. Filters remove 95.5M of about 200M clusters, 80.0M of them for under 100 characters of text. 380.5M citation links are resolved, 156.5M tied to inline mentions; links are accepted at title similarity above 0.8.

To show it works for pretraining, the authors train a BERT-Base on 16.4B tokens of cleaned PDF-parsed body text, nearly five times SciBERT's corpus (5 seeds). S2ORC-SciBERT is better than SciBERT on BC5CDR, ChemProt and SciERC, slightly above on PaperField, and below on ACL-ARC and SciCite. They estimate the whole corpus at about 25B body-text tokens and 15B abstract tokens, and claim it is large enough to pretrain ELMo, BERT, RoBERTa or GPT-2.

## Limits

- Pushshift: completeness, duplicates, deleted content, bots, toxicity and quality are all unanalysed; Reddit fuzzes the score; coverage ends April 2019; total bytes and token count are not given. LM pretraining appears only as a brief mention.
- BookCorpus: single training movie and one run with no variance; the ground truth is incomplete (about 200 correspondences per movie), which leaves precision unevaluated; many hyperparameters are not stated.
- One Billion Word: sentence order is randomised, so it cannot test long-context dependence; training times are implementation dependent and not comparable; there is no application-level evaluation and no seeds. Word-level perplexity on news is dated, and later neural LMs far surpassed these numbers.
- S2ORC: results are mixed ("comparable", not better), and corpus size, domain mix and cleaning are not ablated; pretraining learning rate, batch size, steps and sequence length are not stated; SciBERT reports no standard deviations. Only 35.6% of papers have PDFs; linking depends on titles and fails more on LaTeX physics bibliographies (6.8 against 19.3 linked entries); English only; later S2ORC releases supersede it.

## See Also
- [[Dolma Open Pretraining Corpus]] — related (uses Pushshift Reddit and peS2o papers as two of its sources)
- [[Deduplicating Training Data (ExactSubstr and NearDup)]] — related (measures duplication in C4, RealNews, LM1B and Wiki-40B)
- [[Webis-TLDR-17 Reddit Summarization Corpus]] — related
