---
title: Cosine Similarity Rescaling Freedom
tags: [rag, concept]
summary: "Steck and colleagues show analytically that for some regularized linear embedding models the learned embeddings can be rescaled per latent dimension without changing the model's dot products, so cosine similarities between the embeddings can be made nearly arbitrary; the result covers linear models and simulated data only."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-06-steck-2024-cosine-similarity-embeddings-really-about.md
---

# Cosine Similarity Rescaling Freedom

Steck, Ekanadham and Kallus (2024 preprint, 9 pages) ask whether cosine similarity of learned embeddings really measures similarity. Their answer for a class of linear models is that cosine can yield arbitrary results, and that the cause is a degree of freedom in the embeddings rather than cosine itself.

## The argument

The setting is linear matrix factorization (a linear autoencoder), X approximated by X A B-transpose, with two training objectives.

- **Objective 1** puts one L2 penalty on the product A B-transpose, which the paper says is equivalent to denoising or dropout. It is invariant to rescaling the latent dimensions: if A B-transpose is a solution, so is A D times D-inverse times B-transpose, for any diagonal matrix D. The dot-product model is unchanged, but cosine similarities change with D (cosine is invariant to rotation, not to D).
- **Objective 2** penalizes XA and B separately, like weight decay. It lacks that freedom, so its cosine similarities are fixed up to a rotation. The paper leaves open whether this single scaling yields the best semantic similarity.
- **Worked example (full rank):** a first choice of D turns item-item cosine into the identity matrix, so each item resembles only itself, while another choice gives a nontrivial pattern. Under the first choice, user-item cosine ranks items for each user exactly as the dot product does, since the row normalization is constant per user. Under the opposite choice, user-user cosine reduces to similarities computed on the raw data matrix.
- The paper cites earlier work in which Objective 1 predicted held-out data more accurately than Objective 2; the more accurate model is therefore the one whose cosine is arbitrary.

## Remedies (discussed, not tested)

Options: train with cosine in the objective (for example via layer normalization); map back to the original space and take cosine over the rows of X A B-transpose; or correct for popularity before or while learning (standardize X, negative sampling, inverse propensity scaling). The paper notes word2vec samples negatives in proportion to frequency to the power 3/4, and argues that normalizing only after training can noticeably reduce semantic quality. It also cites earlier work finding cosine sometimes worse than the unnormalized dot product (DPR, ColBERT and another study).

## Evidence and limits

- Simulated cluster data: 20,000 users, 1,000 items, 5 clusters, rank 50, lambda 10,000 for Objective 1 and 100 for Objective 2. The three rescalings under Objective 1 and the unique Objective 2 solution give item-item cosine patterns that are very different from one another and from the true clusters. This is shown in heatmaps with no metric.
- Theory covers linear models only; the authors conjecture that deep models suffer similar or bigger problems. The setting is recommender-style user-item factorization.
- The paper tests no real text embeddings, retrieval benchmark, approximate nearest-neighbour index or vector database, and does not discuss metric choice in indexes. Carrying it over to RAG embeddings is an extrapolation; it supports only the caution that cosine is not automatically the semantic metric. The extraction notes the equations are garbled in places.

## See Also
- [[Word Embeddings and Similarity Measures]] — prerequisite-for
- [[Vector Database Comparison]] — related
- [[RAG Retrieval Strategies]] — prerequisite-for
- [[RAG Reranking]] — related
