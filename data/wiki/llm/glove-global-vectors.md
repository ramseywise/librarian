---
title: "GloVe Global Vectors"
tags: [llm, pretraining-and-data, concept]
summary: "GloVe fits word vectors by weighted least squares on the log of the word-word co-occurrence matrix, starting from probability ratios rather than raw probabilities, and reports gains over word2vec on analogy tests at equal corpus size."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-pennington-2014-glove.md
---

# GloVe Global Vectors

Pennington, Socher and Manning start from two questions: which properties let vector arithmetic reflect word regularities, and can a model fitted to corpus-wide counts match methods that slide a context window. They hypothesise that the quantity to model is the ratio of two co-occurrence probabilities, and that a weighted least-squares log-bilinear fit on counts can keep the efficiency of count methods and the linear structure of prediction methods. The name is short for Global Vectors.

## Mechanism

1. Count word pairs in a tokenised, lowercased corpus into a matrix X, weighting each pair by 1/d for distance d.
2. Fit word vectors w and context vectors w~, plus a bias for each, so that the dot product of w_i and w~_j approximates log X_ij; the squared error of each entry is scaled by a weight f(X_ij), defined as a power of the count (exponent alpha) up to a cutoff xmax and 1 above it.
3. Train with AdaGrad over the nonzero entries only; the final vector is W + W~.

The motivating example is a 6-billion-token corpus: the probability ratio for "ice" over "steam" is large with "solid", small with "gas", and near 1 with "water" and "fashion". Zero entries make up 75 to 95% of X depending on vocabulary size and corpus, and typical pair frequencies follow a power law in rank with exponent 1.25, so the number of nonzero entries grows as O(|C|^0.8) in corpus size C.

## Results (self-reported)

- 300-d vectors on Common Crawl 42B tokens (window 10, 400K vocabulary) reach 75.0% total accuracy on the 19,544-question analogy set.
- On the same 6B-token corpus (Wikipedia 2014 plus Gigaword 5, 300-d, window 10), GloVe beats word2vec skip-gram and CBOW trained with 10 negative samples on total analogy accuracy.
- At 100-d on 1.6B tokens GloVe is ahead of ivLBL and HPCA.
- Plain SVD of the counts does very badly on analogies (300-d, 6B tokens), and the SVD-L variant lost total accuracy once the corpus was enlarged from 6B to 42B tokens.
- Similarity (Spearman correlation on WordSim-353 and rare words, 42B-token vectors) and CoNLL-2003 NER dev and MUC7 (CRF with 50-d vectors) are reported above the baselines. The exceptions: on the 6B-token WordSim-353 comparison with skip-gram the result is mixed, and on the NER test set GloVe is slightly below HPCA.
- Cost: filling X took about 85 minutes on one thread of a dual 2.1GHz Xeon E5-2658 (6B tokens, symmetric window of 10, 400K vocabulary); one 300-d training iteration took 14 minutes on 32 cores.
- Analogy gains diminish beyond about 200 dimensions (6B corpus, window 10). At equal training time GloVe beats word2vec, and word2vec's accuracy drops once the number of negative samples goes beyond about 10 (300-d, 6B tokens, window 10).

## Limits

- Single runs, no variance, seeds or significance tests.
- The word2vec comparison holds unspecified parameters at defaults, a simplification the authors say a fuller analysis should relax.
- The value alpha = 3/4 is justified only empirically.
- Semantic analogy accuracy is lower on Gigaword than on Wikipedia; the authors blame the analogy set's emphasis on cities and countries, which they did not test.
- The 840B-token run is reported without numbers and is not comparable (cased).
- Static word-level vectors with one vector per word, no handling of unseen words or subwords; only 2014 baselines; analogy evaluation has since been criticised (stated as not in the paper).
- The paper cites Baroni et al. ("Don't count, predict!") as arguing that prediction models are better; GloVe argues the two families are not fundamentally different.

## See Also
- [[Word2vec: CBOW, Skip-gram and Negative Sampling]] — alternative-to
- [[Word Embeddings and Similarity Measures]] — prerequisite-for
- [[FastText Subword Skip-gram]] — related (the other pretrained static-vector method that data-science page compares)
