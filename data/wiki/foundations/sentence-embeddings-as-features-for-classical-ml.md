---
title: "Sentence Embeddings as Features for Classical ML"
tags: [foundations, pattern]
summary: "A pretrained sentence encoder turns text into a cached matrix for ordinary scikit-learn heads; it beats TF-IDF most when labels are few, at about 50 times the encoding cost."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-science--03-nlp--notes--07-llm-embeddings-as-features.md
---

# Sentence Embeddings as Features for Classical ML

A pretrained sentence encoder (MiniLM-style: a small transformer, six attention layers, pooled and normalised to unit length) maps any text to a fixed vector, 384 dimensions for the model used here, with input cut off at 256 word pieces. Once text is a matrix, classifiers, clustering and anomaly scoring work as on any features. The encoder is trained contrastively on sentence pairs, so related sentences land close together. Training matters: untuned mean-pooled BERT scored below averaged GloVe on similarity benchmarks, and the fine-tuned versions scored well above both. Encoding is the only slow step, so cache the matrix, keyed by model name.

The vectors match on meaning, including the wrong meaning, and similarity scores are on a different scale from [[Bag of Words, n-grams and TF-IDF]] cosines (0.53 against 0.20 for the same query), so no threshold carries across. Silent truncation past the input limit needs chunking for long documents. Compared with static [[Word Embeddings and Similarity Measures]], the context-aware vector is one per text, not per word.

## The label-count curve

Setup: six commonest genres of film descriptions, a fixed test split, regularisation tuned by inner cross-validation for both models, five draws per training size.

| train size | TF-IDF macro-F1 | encoder macro-F1 |
|---|---|---|
| 60 | 0.144 | 0.261 |
| 150 | 0.199 | 0.346 |
| 600 | 0.271 | 0.419 |
| 1200 | 0.335 | 0.439 |
| 2877 | 0.404 | 0.484 |

The encoder wins at every size. The gap in points peaks at 0.15 to 0.16 between 150 and 600 labels and shrinks to 0.08 on the full set, as sparse features collect enough vocabulary. Majority-class accuracy is 0.315. Even a tuned TF-IDF at 0.423 stays 0.06 behind. The sparse baseline is the [[Linear Text Classifiers and the TF-IDF Baseline]]; run it first anyway, since it tells you what the embedding must beat.

## Head, extra features, dimensions

- **Use a linear head first.** On the full training set: logistic regression 0.484, RBF SVM 0.496, gradient boosting 0.407 (27.9 s against 0.1 s). The SVM's 0.013 gain has a bootstrap interval of -0.022 to +0.047, so it is noise. Trees suit a few meaningful columns, not 384 anonymous ones.
- **Beat on noise, not digits.** The encoder's lead over TF-IDF is +0.076 with a 95% interval of +0.034 to +0.120 over 960 test films; see [[Bootstrap Resampling and Its Failures]].
- **Embeddings are just more columns.** Adding runtime, budget and revenue gave 0.487; stacking TF-IDF on top raised accuracy slightly but not macro-F1 (0.484).
- **Dimensions.** PCA fitted on training vectors only: 16 components keep 28% of the variance and score 0.477 against 0.482 for all 384. The rest wobbles inside the noise. This holds for a coarse target; a finer task may use more. The PCA must then be saved and applied to every new document; see [[PCA, NMF and Low-Rank Factorisation]].

## SetFit for very few labels

SetFit fine-tunes the encoder on pairs built from the few labels (same class positive, different class negative), then fits a logistic head on the tuned vectors. With 8 labels per class over three draws, macro-F1 was 0.201 / 0.244 / 0.240 for TF-IDF, 0.272 / 0.371 / 0.341 for a frozen encoder, and 0.309 / 0.430 / 0.373 for SetFit, about 15 s on CPU per fit. SetFit beat the frozen encoder by 0.03 to 0.06 in every draw: real, modest. Which 48 films were labelled moved the score by about 0.1, more than the method. With few labels, what you label matters as much as how you train.

## Choosing an encoder and paying for it

A multi-task benchmark (MTEB, 33 models, 8 task types, 58 datasets) found no method dominates every task, so a leaderboard narrows the field and your task decides. Swapping the encoder is one line because everything downstream wants a matrix.

| encoder | dims | macro-F1 | CPU docs/s |
|---|---|---|---|
| MiniLM | 384 | 0.484 | 391 |
| BGE small | 384 | 0.471 | 275 |
| MPNet | 768 | 0.507 | 79 |

MPNet's lead over MiniLM is +0.024 with an interval of -0.012 to +0.061, so it includes zero: let the cheapest adequate model stand until something beats it by more than the noise.

Against sparse features, encoding ran 616 docs/s against 35,425 for the TF-IDF transform, roughly 50 times slower. Storage is close: a short description has about 62 non-zeros, 744 bytes per document against 1,536 for a 384-float vector. Sparse columns stay readable (linear weights); dense coordinates do not.

## API embeddings

A hosted embedding model changes only the function that fills the matrix. Texts leave your machine, and a provider can retire a model, after which its vectors are incomparable with its successor's, so store the model name beside the matrix and plan to re-embed everything on a change. Same-dimension vectors from different models live in unrelated spaces. Vectors also inherit associations from their training text. For retrieval use see [[RAG Retrieval Strategies]].

## Pitfalls

- Fit PCA or scalers on training vectors only; see [[Pipelines Prevent Preprocessing Leakage]].
- Anomaly scores and cosine distances rank; they are not probabilities.
- For the unsupervised uses of the same matrix see [[Embedding Clustering and Anomaly Detection]].

## See Also
- [[Linear Text Classifiers and the TF-IDF Baseline]] — prerequisite-for
- [[Embedding Clustering and Anomaly Detection]] — extends
- [[Word Embeddings and Similarity Measures]] — prerequisite-for
- [[Bootstrap Resampling and Its Failures]] — related
- [[RAG Retrieval Strategies]] — related
