---
title: "Topic Models and Extractive Summarisation"
tags: [foundations, concept]
summary: "LSI, LDA and NMF factor the document-term matrix into readable topics; choose k by coherence plus reading, check seed stability; document clustering and TextRank/LSA summaries share the same machinery."
updated: 2026-11-08
sources:
  - data/raw/repos/learn-ai-engineering/data-science--03-nlp--notes--03-topic-models-and-summarization.md
---

# Topic Models and Extractive Summarisation

With no labels, reading the output is the evaluation. Nearly everything here is matrix factorisation or graph ranking over the matrices from [[Bag of Words, n-grams and TF-IDF]]. Phrase merging beforehand is covered in [[Collocations and Pointwise Mutual Information]].

## Three factorisations of the document-term matrix

A topic is a distribution over words and a document a mixture of topics. All three methods factor X into W (documents by topics) times H (topics by words); the constraint on the factorisation decides readability.

| Method | Factorisation | Input | Weights |
|---|---|---|---|
| LSI / LSA | Truncated SVD | TF-IDF or counts | Signed, hard to read |
| LDA | Bayesian generative model with Dirichlet priors | Counts, not TF-IDF | Probabilities |
| NMF | Non-negative factorisation | TF-IDF | Non-negative, readable parts |

- **LSI:** components have mixed signs, so one component can pit "world, war" against "life, school, love". The first component is negative on everything because it measures general word frequency. Real directions, but not topics.
- **LDA's generative story:** draw a word distribution per topic and topic proportions per document (Dirichlet priors), then for each word position draw a topic and then a word. Fitting inverts this. Small alpha means each document uses few topics. Because it generates word counts, feed it counts; the story is an instance of [[Generative Story Models]]; priors are conjugate Dirichlet. NMF has no story and takes TF-IDF.
- **On short text** (4,799 film descriptions, 12 topics) NMF topics were immediately nameable (romance, true stories, world-in-peril, New York, school, coming of age) while LDA's were vaguer, with "life", "one", "man" everywhere. Short documents give LDA few words to estimate each mixture, so this is no verdict on LDA in general, but it makes NMF worth trying first on short text.
- **Read top documents, not just top words.** A topic's highest-weight documents are the cheapest way to see what it means.

## Choosing the number of topics

No held-out accuracy exists, so use a proxy.

| Measure | Direction | Note |
|---|---|---|
| Coherence c_v | Higher | Correlates best with human judgement |
| Coherence u_mass | Higher (less negative) | Fast, corpus-only |
| Perplexity | Lower | Often disagrees with humans; do not select on it alone |

On the film corpus c_v barely moved (0.347 at 5 topics, 0.346 at 10, 0.318 at 20, 0.325 at 40), so there was no knee. Over three seeds the mean fell from 0.352 to 0.322 with seeds about 0.01 apart, so single-run wiggles are noise. The perplexity bound fell steadily and selected nothing useful. Read topics at a couple of settings rather than obeying a curve. On a larger paper collection a knee near 20 topics was used, and Gibbs-sampled LDA was more coherent than variational LDA.

**Stability.** Refit with another seed and check the same topics return. Matching topics (at least 4 of 7 shared top words) between two seeds: NMF 11 of 12, LDA 7 of 12, with fewer iterations than production. Never publish one run.

**Topic features** as classifier input: 12 NMF proportions gave ROC-AUC 0.637 for detecting Horror against 0.912 for full TF-IDF. They are compact and interpretable, and earn their place when labels are scarce.

**BERTopic** (embed, reduce with UMAP, cluster with HDBSCAN, describe with class-based TF-IDF; see [[Embedding Clustering and Anomaly Detection]]) addresses the bag-of-words limit but assumes one topic per document and its words are still bags. Evidence for short text is one dataset (NPMI 0.066 against 0.009 for NMF and -0.011 for LDA), and it fell to -0.088 with a different embedding.

## Document clustering

k-means on TF-IDF with 6 clusters over the film corpus gave one grab-bag cluster of 2,291 films with generic terms and tight themes elsewhere (888, 636, 591, 202, 191). Two films landed together only because both mention New York: it groups by shared vocabulary, not genre. Ward linkage gives a tree to cut at any level. Affinity propagation picks the cluster count itself but tends toward many small clusters (91 over 500 films, median size 5). Validate by reading members, and score clusters against a holdout since k-means always returns the k asked for; see [[Clustering Validation Against Named Baselines]] and [[HDBSCAN with KMeans Fallback]].

## Extractive summarisation

Pick representative sentences in original order. Extractive methods cannot invent a claim and cost nothing; abstractive summarisation is now an LLM task.

| Method | Signal | Weakness |
|---|---|---|
| LSA | Sentences loading on dominant SVD concepts | Sensitive to k and the threshold |
| TextRank (TF-IDF) | PageRank on a sentence-similarity graph | Lexical overlap only; misses paraphrase |
| TextRank (embeddings) | Same with semantic similarity | Averaged word vectors are crude |
| LLM | Generates | Can hallucinate; hard to evaluate |

On a 29-sentence article both methods opened with the defining sentence and shared 5 of 8 picks. Mean sentence length 17.2 words against 18.1 for TextRank picks and 17.1 for LSA: no length bias here, but test a document with a wider range.

## Pitfalls
- LDA on counts, NMF and LSI on TF-IDF; prune vocabulary and merge phrases first or topics become stop words and fragments.
- Treating a topic as a fact: it is a pattern a model found and needs a human to name it.

## See Also
- [[Bag of Words, n-grams and TF-IDF]] — prerequisite-for
- [[Collocations and Pointwise Mutual Information]] — prerequisite-for
- [[Generative Story Models]] — related
- [[Embedding Clustering and Anomaly Detection]] — extends
- [[Clustering Validation Against Named Baselines]] — related
- [[HDBSCAN with KMeans Fallback]] — related
- [[Multi-News]] — related (multi-document summarization dataset with extractive baselines)
