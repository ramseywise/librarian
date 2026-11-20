---
title: "BERTopic: Clustering Embeddings with Class-Based TF-IDF"
tags: [data-science, nlp, concept]
summary: "BERTopic embeds documents, reduces them with UMAP, clusters with HDBSCAN and names each cluster with class-based TF-IDF; the paper reports it competitive with LDA, NMF, CTM and Top2Vec, with no variance or significance tests."
updated: 2026-11-20
sources:
  - data/raw/papers/2026-11-07-grootendorst-2022-bertopic.md
---

# BERTopic: Clustering Embeddings with Class-Based TF-IDF

Grootendorst's question is whether clustering transformer document embeddings and then describing each cluster with a class-based TF-IDF, instead of proximity to a centroid, gives topics that match classical and clustering-based topic models. Other topic models are on [[Topic Models and Extractive Summarisation]].

## Pipeline

1. Embed documents with a pre-trained SBERT model.
2. Reduce the embeddings with UMAP ([[UMAP Graph Construction and Layout]]).
3. Cluster with HDBSCAN, which allows noise ([[HDBSCAN with KMeans Fallback]]).
4. Concatenate each cluster's documents into one class and score words with **class-based TF-IDF (c-TF-IDF)**: the weight of term t in class c is the term's frequency in the class times log(1 + A / tf_t), where A is the average number of words per class and tf_t the term's frequency across classes.

A **dynamic** extension keeps the global IDF and takes term frequencies per timestep, optionally smoothed.

## Results (self-reported)

Setup for the static comparison: NPMI coherence and topic diversity on three datasets (Trump's tweets, 20 NewsGroups, BBC News), each score averaged over 15 runs (3 runs for each topic count from 10 to 50), run in OCTIS, with all-mpnet-base-v2 as BERTopic's encoder and default parameters for LDA and NMF. No variance or significance test is given.

- On Trump's tweets, BERTopic with MPNET scores the top coherence of the Table 1 models. The author reports it highest on the lightly preprocessed tweets and competitive on the heavily preprocessed sets.
- Top2Vec with Doc2Vec scores above BERTopic-MPNET in coherence on 20 NewsGroups and BBC News, yet its coherence on Trump's tweets is strongly negative.
- CTM scores above BERTopic in diversity on every one of the three datasets.
- LDA's coherence on Trump's tweets is slightly negative.
- On 20 NewsGroups, MiniLM lands near MPNET in coherence, and the author suggests MiniLM where GPU capacity is limited. BERTopic with Doc2Vec embeddings scores low on Trump's tweets, and Top2Vec's coherence and diversity drop with MPNET embeddings.
- Dynamic topics (50 topics, 9 timesteps, 3 runs, so 27 values per score): BERTopic beats LDA Sequence on Trump coherence and leads on UN coherence, while LDA Sequence leads on UN diversity. Assuming topics evolve linearly makes no difference to either measure.
- Wall time on the Trump data, with embedding on a P100 GPU: the classical models run faster than the neural ones, while CTM paired with MPNET is much slower, and BERTopic and Top2Vec take similar time given the same encoder.

## Limits

- Coherence and diversity stand in for a subjective judgement, and Hoyle et al. (2021) raise the possibility that NPMI diverges from human judgement for neural topic models.
- Each document gets one topic; HDBSCAN's probabilities are only a stand-in for topic mixtures.
- Topic words are drawn from bags of words and may repeat one another; the author did not try maximal marginal relevance.
- Timings assume a GPU and will be longer without one.
- UMAP and HDBSCAN settings, the share of documents labelled noise and the effect of topic count are not reported.
- No variance or significance test is reported.
- Only one short-text dataset (Trump's tweets) is used, and it is also the only lightly preprocessed one.

## See Also
- [[Topic Models and Extractive Summarisation]] — prerequisite-for
- [[Embedding Clustering and Anomaly Detection]] — prerequisite-for
- [[UMAP Graph Construction and Layout]] — prerequisite-for
- [[HDBSCAN with KMeans Fallback]] — prerequisite-for
- [[Bag of Words, n-grams and TF-IDF]] — prerequisite-for
