---
title: "Embedding Clustering and Anomaly Detection"
tags: [foundations, pattern]
summary: "Sentence-embedding matrices cluster and flag outliers far better than TF-IDF, with k-means, UMAP plus HDBSCAN plus c-TF-IDF, and kNN or LOF detectors, but each result needs its setup and a manual look."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-science--03-nlp--notes--07-llm-embeddings-as-features.md
---

# Embedding Clustering and Anomaly Detection

With the cached matrix from [[Sentence Embeddings as Features for Classical ML]], two label-free jobs need no new model: finding groups and finding lines that do not belong.

## Clustering

Setup: about 4,775 film descriptions, genre as an outside check scored by normalised mutual information (NMI). Because vectors have unit length, Euclidean k-means behaves like cosine.

| representation | k | NMI with genre | largest cluster |
|---|---|---|---|
| TF-IDF | 6 | 0.041 | 40% |
| TF-IDF | 20 | 0.066 | 16% |
| TF-IDF + SVD 100 | 6 | 0.046 | 43% |
| encoder | 6 | 0.141 | 22% |
| encoder | 20 | 0.143 | 9% |

Sparse vectors with little shared vocabulary are near-equidistant, producing a catch-all cluster; SVD does not rescue it. More clusters gave the encoder no more genre agreement, because extra clusters split by subject, which genre does not record. Genre is one outside view: a good cluster of submarine films scores badly on it. Classical alternatives are in [[Topic Models and Extractive Summarisation]] and [[Clustering Algorithms: k-means, Agglomerative and DBSCAN]].

### UMAP, HDBSCAN and c-TF-IDF

The BERTopic-style route: reduce with UMAP (distances lose contrast in high dimensions), cluster with HDBSCAN (varying density, leftovers become noise; see [[HDBSCAN with KMeans Fallback]]), then describe each cluster by class-based TF-IDF, treating a cluster's text as one document and asking which words distinguish it. Here (n_neighbors 15, 5 components, min_cluster_size 15): 35 clusters, 54% noise, NMI 0.223 on the clustered films. The top terms read as subjects: crime, animals, space, team sports, fantasy kingdoms.

- Report the noise share and settings with the clusters; 54% depends on them.
- The 0.223 cannot be compared with k-means' 0.14, since it scores only the films HDBSCAN agreed to cluster, the easy ones.
- Either accept noise as "uncategorised" or assign those points afterwards.
- Distances between far-apart clusters in a UMAP plot carry no meaning, and seeds move things; see [[t-SNE and UMAP Visualisation Rules]].
- Score a clustering against an outcome before it drives a decision.

## Anomaly detection

Task: flag text that does not belong, without labels or a list of what wrong looks like. Keep a clean reference set and score new lines by distance from it. Test: 3,800 reference films; 1,055 lines to score, 80 of them intruders (40 song-lyric chunks, 40 chunks of old prose, about film-description length), so the base rate is under 8%.

Detectors: **kNN distance** (far from nearest reference neighbours), **local outlier factor** (that distance relative to the neighbours' own density), and **isolation forest** (random splits; few splits to isolate means anomalous; see [[Isolation Forest vs Gaussian Anomaly Detection]]).

| representation, detector | AUROC | precision in top 80 |
|---|---|---|
| TF-IDF, kNN | 0.643 | 0.12 |
| TF-IDF SVD, LOF | 0.253 | 0.05 |
| TF-IDF SVD, forest | 0.255 | 0.03 |
| encoder, kNN | 0.939 | 0.59 |
| encoder, LOF | 0.944 | 0.60 |
| encoder, isolation forest | 0.799 | 0.30 |

- Encoder with kNN or LOF ranks a random intruder above a random film about 94% of the time. Lyrics (0.914 to 0.919) are harder than prose (0.964 to 0.968), since lyrics are stories about people. LOF barely beats plain kNN.
- Isolation forest is weaker: it splits on single coordinates, and one embedding dimension means little alone.
- **AUROC below 0.5 on TF-IDF.** Intruders share few words with the film vocabulary, so their SVD vectors are short (mean norm 0.18 against 0.35 for films) and sit near the origin, the densest region, so density methods call them typical. A vocabulary-bound representation cannot make "unlike anything I know" look unusual.
- **Read the top of the list.** The highest-scoring real films were themselves odd (a non-English description in an English catalogue, a marketing question, a one-line pitch), so some false alarms are worth finding. The lowest-scoring intruders were narrative text that reads like a plot summary.
- These intruders differ in subject; a subtly wrong description of a real film would score as normal.
- Keep the reference clean: intruders inside it become their own neighbours.
- Scores rank; pick a threshold from review capacity, not from the score.

## See Also
- [[Sentence Embeddings as Features for Classical ML]] — prerequisite-for
- [[Topic Models and Extractive Summarisation]] — alternative-to
- [[HDBSCAN with KMeans Fallback]] — related
- [[Isolation Forest vs Gaussian Anomaly Detection]] — related
