---
title: Multi-News
tags: [eval, reference]
summary: A multi-document news summarization dataset of 56,216 article-summary pairs built from editor-written summaries and their cited sources, released with Hi-MAP, a pointer-generator that rescales attention with a learned MMR score.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-08-fabbri-2019-multi-news.md
---

# Multi-News

Fabbri and colleagues (2019) build a large multi-document summarization (MDS) dataset on the premise that data sparsity holds back neural MDS, and test whether adding MMR (maximal marginal relevance, which trades query relevance against novelty) inside attention cuts redundancy.

## Data and method

Summaries written by editors at newser.com are linked to their 2 to 10 cited source articles, recovered through Wayback links. Each model reads the concatenated sources cut to 500 tokens. They are compared with extractive baselines by ROUGE, plus a small human study using Best-Worst Scaling. **Hi-MAP** extends the pointer-generator with an LSTM over sentences and a learned MMR score, MMR_i = lambda Sim1(h_i, s_sum) - (1 - lambda) score_i, which rescales the word-level attention.

## Results (self-reported)

- 56,216 pairs, roughly 100 times the size of earlier news MDS data (DUC/TAC). Summaries average around 264 words, well above CNN/Daily Mail's, and 17.76% of their unigrams are novel, about as abstractive as CNN/Daily Mail's.
- Trained and tested on Multi-News (inputs 500 tokens, single run): CopyTransformer scored best on R-1 and Hi-MAP best on R-2. The extractive First-3 baseline reached R-1 39.41 (extractive outputs of 300 tokens), above LexRank, TextRank and MMR.
- On DUC 2004 with models trained on CNN/Daily Mail, PG-MMR was best on R-1 and Hi-MAP was competitive.
- Human pairwise comparison (50 test documents, 3 annotators): Hi-MAP was chosen best for non-redundancy 100 times against 45 for PG-MMR, while CopyTransformer scored 107.
- Feeding extractive output into the abstractive model gave no gain, which the authors attribute to truncation mirroring First-3; a Multi-News-trained model tested on DUC also gained nothing significant, which they blame on domain differences (no numbers given).

## Limits

- Cutting inputs to 500 tokens (they average 2,103 words) hides most of the sources from the model; longer inputs and cross-document modelling are deferred.
- Training hyperparameters and seeds are not reported; ROUGE is single-run with no variance.
- The human study is small; its Table 7 has CopyTransformer ahead of Hi-MAP for informativeness and fluency.
- Few non-neural baselines; no pretrained language models.
- Only archive links and scripts are released, not article text, so reproducing the data depends on the archive staying available.

## See Also
- [[SQuAD]] — related (its CNN/Daily Mail predecessor is the corpus used to train for DUC)
- [[Seq2seq Bottleneck and Attention]] — prerequisite-for
