---
title: Webis-TLDR-17 Reddit Summarization Corpus
tags: [eval, language-tasks, concept]
summary: "Webis-TLDR-17 mines about 4 million content-summary pairs from Reddit posts that end in a TL;DR line; 95% of 1,000 reviewed pairs were correct, but only 966,430 pairs share a noun phrase between post and summary (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-volske-2017-tl-dr.md
---

# Webis-TLDR-17 Reddit Summarization Corpus

Volske, Potthast, Syed et al. (NFiS workshop, EMNLP 2017) ask whether summaries that authors append to social media posts with a TL;DR line can be harvested in bulk as training data for abstractive summarisation outside the news domain. They propose that such posts supply text and summary pairs by one author, and expect the method to carry over to other sites and crawls.

## Pipeline

A five-step filter is applied to the Pushshift Reddit crawl (see [[Early LM Training Corpora]]), which spans 2006-2016 with 286M submissions and 1.6B comments. It finds posts with TL;DR spelling variants, removes bots, splits each post at the TL;DR marker into a content part and a summary part, and enforces length rules. The length threshold is very lenient (2 content words). A manual check of 1,000 random pairs estimates precision.

## What the corpus holds (self-reported)

- Around 4 million content-summary pairs: about the size of English Gigaword (4M) and bigger than CNN/Daily Mail (300,000) or DUC.
- 95% of the 1,000 reviewed pairs were correct.
- A noun phrase is shared between content and summary in 966,430 pairs (580,391 from submissions, 386,039 from comments), which the authors give as a lower bound on genuine summaries.
- Median summary length is 22 words for submissions and 15 for comments. Summaries run to about 11% of the content's words for submissions and 8% for comments, and summary length correlates with post length (Pearson 0.40 for submissions, 0.35 for comments).
- Heuristic subsets: 78,710 pairs have question summaries and 299,145 summaries are vulgar.

## Limits

- No quantitative evaluation of summarisers trained on the corpus; early experiments with models by Rush et al. (2015) and by Nallapati et al. (2016) were judged only by reading outputs.
- The 95% precision rests on 1,000 pairs, and the reviewer count and criteria are not given.
- A good share of TL;DRs are questions, opinions or vulgar remarks, not real summaries.
- There is no ontology for subreddits, and the crawl covers 2006-2016 only.

## See Also
- [[ELI5 Long-Form QA Dataset]] — related (another dataset mined from Reddit)
- [[Summarization and Translation Hallucination Studies]] — related
- [[XSum Extreme Summarisation]] — related
