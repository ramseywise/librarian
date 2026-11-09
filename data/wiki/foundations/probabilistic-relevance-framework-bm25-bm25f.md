---
title: Probabilistic Relevance Framework (BM25 and BM25F)
tags: [foundations, concept]
summary: "The survey that derives BM25 and BM25F from the probability ranking principle through eliteness and saturation, and gives starting ranges and a tuning order for k1 and b."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-robertson-2009-probabilistic-relevance-framework.md
---

# Probabilistic Relevance Framework (BM25 and BM25F)

This is a survey, not an experiment: it derives the Probabilistic Relevance Framework (PRF) from the **Probability Ranking Principle** (ordering by decreasing probability of relevance gives the best effectiveness for the available data) down to sum-of-weights scoring. Performance statements summarise many uncited experiments by many people.

## Mechanism

- The **RSJ weight** (Robertson/Sparck Jones) uses a 0.5 pseudo-count. Absent any relevance information it becomes nearly the classical idf formula: a log of (N-ni+0.5) over (ni+0.5).
- **Eliteness** is a hidden yes/no property of a document-term pair, a kind of aboutness, and term frequency depends on it. **Saturation** follows: however often a term occurs, its contribution stays below an asymptote. The proof covers the 2-Poisson case; other distributions are described as likely.
- BM25 normalises length with B = (1-b) + b*dl/avdl and tf' = tf/B; b=1 is full normalisation and b=0 switches it off. The (k1+1) factor in the numerator is shared by every term and leaves the ranking unchanged.
- **BM25F** handles fielded documents: sum weighted, length-normalised term frequency over streams first, then saturate once per term. For BM25F, the right k1 shifts with the stream weights.

## Practice (reported by the survey)

- Experiments suggest (self-reported; uncited experiments summarised by the survey) k1 between 1.2 and 2 and b between 0.5 and 0.8 as reasonable starting values; the model itself offers no guidance on choosing them. A frequently published setting is b=0.5 with k1=2, yet many of those experiments favour a lower k1 and a higher b.
- Both functions tolerate parameter changes fairly well, yet tuning on a new collection pays off significantly.
- The survey's own practice is a cached grid search: k1 and b first, then stream weights, then k1 with per-stream b. Greedy recursive robust line search grows exponentially with parameter count and is impractical past three.
- BM25F values reported (self-reported) for the TREC 2003 web tasks: k1=27.5 and title weight 38.4 for topic distillation (TD), k1=4.9 and title weight 13.5 for name page (NP), body weight 1.0 in both.
- Query expansion by offer weight adds only the top x terms (of the order of 10). Blind feedback assumes the top 5 or 10 documents are relevant; on average that helps, but difficult queries break it.
- Positional information has surprisingly little effect on average.

## Limits

- Not an experimental survey; performance claims derive from uncited experiments.
- Relevance is assumed binary and document-independent, and terms independent; the survey calls both arguable.
- Discarding terms that cannot affect rank leaves no calibrated relevance probability, which hurts blind feedback and filtering.
- Position information does not extend PRF naturally, and IDF across BM25F streams remains open research.
- The extraction notes it predates dense and neural retrieval (2009).

## See Also
- [[BM25 and the Lexical Gap]] — prerequisite-for
- [[Bag of Words, n-grams and TF-IDF]] — prerequisite-for
- [[RAG Retrieval Strategies]] — related
- [[Dense Passage Retrieval (DPR)]] — related (uses BM25 as baseline and hard-negative source)
