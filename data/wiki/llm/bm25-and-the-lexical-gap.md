---
title: "BM25 and the Lexical Gap"
tags: [llm, concept]
summary: "BM25 ranks documents by saturated, length-normalised term matches; both it and TF-IDF cosine are blind to synonyms, which is the gap dense encoders and hybrid retrieval fill."
updated: 2026-11-19
sources:
  - data/raw/repos/learn-ai-engineering/data-science--03-nlp--notes--04-embeddings-and-similarity.md
  - data/raw/papers/2026-11-08-text-analytics-with-python-ch06-text-similarity-clustering.md
---

# BM25 and the Lexical Gap

BM25 is the probabilistic ranking function behind classic search engines. For each query term it sums idf times a saturated term frequency:

BM25(q, d) = sum over query terms t of idf(t) * f(t,d) * (k1 + 1) / (f(t,d) + k1 * (1 - b + b * |d| / avgdl))

k1 (about 1.2 to 2) saturates term frequency so repeating a word stops helping; b (about 0.75) normalises for document length relative to the average. It fits in a few lines over a sparse count matrix and returns keyword results in milliseconds. It remains the lexical half of hybrid retrieval ([[RAG Retrieval Strategies]], [[Reciprocal Rank Fusion (RRF)]]).

## Content-based recommendation as the same machinery

A TF-IDF recommender (unit-length rows, so a dot product is cosine) finds sequels from descriptions alone. It works for new items but not new users; collaborative filtering has the opposite cold-start profile; hybrids use both. Swapping cosine for BM25 turns it into a search engine: "haunted house teenagers" returns films with those words.

## The lexical gap

On a catalogue of film descriptions, 7 documents match "motel" and none of the 36 documents that say "hotel" are among them. A searcher using one word never finds the other. This is the opening problem of [[Word Embeddings and Similarity Measures]]: only a dense encoder links the two.

- **Use lexical when:** product codes, names and rare terms matter. Fuse BM25 with dense scores rather than replacing it.
- **Use dense when:** synonyms and paraphrase matter. Everything in retrieval is here in small: documents and queries become vectors, cosine ranks candidates, hybrid systems fuse lexical and dense scores. The jump is the encoder (contextual sentence embeddings trained contrastively, instead of averaged word vectors).

## A toy-corpus comparison of three rankers

Sarkar's chapter 6 ranks a 9-document corpus against 3 queries (lemmatised, TF-IDF unigrams) with cosine, Hellinger-Bhattacharya distance and BM25. Because cosine ignores word order, it rates the sentence about a dog being smarter than a fox as a perfect match for the query with the animals swapped. For the Java and Python query the nearest document scores 0.837, and the sky-and-relaxing query scores 0.72 against 'The sky is blue'. Hellinger returns 0.0 for that perfect match. On the Java query, Hellinger's second hit is document 4 at 0.766, whereas cosine and BM25 put document 6 there. BM25 (k1 1.5, b 0.75, bag-of-words counts, query terms binarised) returns the same top document for the first query at 7.334. The book gives k1 as usually between 1.2 and 2.0 and b as usually 0.75, and cites a web post, with no data shown, that BM25 does much better than Lucene's default similarity (reported).

## Limits

- The comparison has no relevance judgements, so the metrics are compared by eye; its code is Python 2 era and the book notes no production BM25 existed in NLTK or scikit-learn then.
- Cosine and BM25 ignore order and synonyms, and the chapter does not cover embeddings.

## See Also
- [[Word Embeddings and Similarity Measures]] — extends
- [[Bag of Words, n-grams and TF-IDF]] — prerequisite-for
- [[RAG Retrieval Strategies]] — related
- [[Reciprocal Rank Fusion (RRF)]] — related
- [[Probabilistic Relevance Framework (BM25 and BM25F)]] — extends (the framework BM25 comes from)
- [[LIMIT Embedding Dimension Retrieval Benchmark]] — related (BM25 beats single-vector models, then collapses without overlap)
- [[M3-Embedding Self-Knowledge Distillation]] — related (learned sparse head against BM25)
