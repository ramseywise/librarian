---
title: "Word Embeddings and Similarity Measures"
tags: [data-science, nlp, concept]
summary: "word2vec, GloVe and FastText give dense vectors where shared contexts mean closeness; covers negative sampling, subwords, analogy and bias limits, document vectors, and why to normalise before cosine."
updated: 2026-11-20
sources:
  - data/raw/repos/learn-ai-engineering/data-science--03-nlp--notes--02-text-classification.md
  - data/raw/repos/learn-ai-engineering/data-science--03-nlp--notes--04-embeddings-and-similarity.md
  - data/raw/papers/2026-11-08-fundamentals-of-deep-learning-ch06-embedding-representation-learning.md
  - data/raw/papers/2026-11-08-fundamentals-of-deep-learning-ch07-models-sequence-analysis.md
  - data/raw/papers/2026-11-08-text-analytics-with-python-ch06-text-similarity-clustering.md
  - data/raw/papers/2026-11-07-building-ai-agents-llms-rag-kgs-ch01-analyzing-text-data-deep-learning.md
  - data/raw/papers/2026-11-08-pennington-2014-glove.md
  - data/raw/papers/2026-11-07-bojanowski-2017-enriching-word-vectors-subword-information.md
---

# Word Embeddings and Similarity Measures

In TF-IDF each word is its own axis, so "hotel" and "motel" are as far apart as "hotel" and "banana" (see [[Bag of Words, n-grams and TF-IDF]]). An embedding maps each word to a dense vector of 50 to 300 numbers, learned so words used in similar contexts get similar vectors. Nothing is labelled. This is the idea behind the [[Neural Probabilistic Language Model]] and, scaled up, the sentence encoders in [[Sentence Embeddings as Features for Classical ML]].

## word2vec

Two shallow architectures: **CBOW** predicts a target from the average of its context words (faster, frequent words); **skip-gram** predicts each context word from the target (rare words, small corpora; the rule of thumb comes from library documentation, not the original paper). In the original analogy test with 300-d vectors on 783M words, skip-gram scored 50.0% on semantic questions against CBOW's 15.5%, and 55.9% against 53.1% on syntactic ones; CBOW trained in about a day and skip-gram in about three.

**Negative sampling** replaces the expensive softmax over the vocabulary with binary classification: is this (word, context) pair real, or one of k random pairs? Noise words come from the unigram distribution raised to the 3/4 power; k of 5 to 20 suits small corpora and 2 to 5 large ones. **Subsampling** discards a frequent word with probability 1 - sqrt(t/f), t around 1e-5. On about 1B words, negative sampling with 5 noise words scored 59% in 38 minutes against 47% in 41 minutes for hierarchical softmax; adding subsampling gave 60% in 14 minutes. These are single runs without error bars. Merging frequent pairs into phrase tokens reached 72% on a phrase-analogy set, but only with 33B training words.

Skip-gram with negative sampling is two embedding tables, a dot product and a sigmoid; the learned table is the only thing kept. Trained on a 1.1M-token slice of public-domain books it took 12 seconds and already put "war" near "civil" and "treaty"; the corpus decides meaning, so "king" sat near "george" and "france", not "queen". The context window decides the kind of similarity: window 2 gives words that fill the same slot (past-tense motion verbs), window 15 gives topical surroundings.

## GloVe and FastText

- **GloVe** factorises the log word co-occurrence matrix; pretrained vectors (50 to 300 dimensions) are widely shipped. In its own paper, 300-d GloVe on 42B tokens reached 75.0% total analogy accuracy and beat word2vec on a shared 6B-token corpus (self-reported); details in [[GloVe Global Vectors]].
- **FastText** is word2vec over character n-grams: a word's vector is the sum of its n-gram vectors (3- to 6-grams hashed into 2M buckets). It answers for unseen words and typos: "fatherr" finds "father", though "kingly" finds "singly", so subwords carry form first. On a rare-words similarity set it scored 47 against 43 for skip-gram and CBOW; Czech syntactic analogies rose from 52.8% to 77.8%, but semantic analogies did not improve (German fell from 66.5% to 62.3%).

## Geometry, analogies and bias

Analogies are a demonstration, not a reasoning system. On 50-d GloVe, "man:woman :: king:?" returned "princess" under one formula and "queen" under another; comparatives gave "larger" for "small", and a good/bad analogy failed. The solver must exclude the input words.

- **Bias:** projecting occupations onto the woman-minus-man direction separates "receptionist" (+0.331) and "nurse" (+0.380) from "engineer" (-0.080) and "warrior" (-0.209). Neutralising (remove the bias component from gender-neutral words) and equalising (make gendered pairs equidistant from the neutral axis) reduce but do not remove the association. Check sensitive directions before vectors drive a decision.
- **Antonyms sit close:** good/bad cosine 0.796 against good/excellent 0.806. Neighbour lists mix synonyms and antonyms; do not rely on them to preserve polarity.
- **Polysemy:** one vector holds every sense, approximately a frequency-weighted superposition of sense vectors. Contextual models give each occurrence its own vector.
- **Mixing spaces:** vectors from different models or versions are not comparable; re-embed on model change.

## Task-trained versus pretrained vectors

An embedding layer trained inside a network organises by that task (a sentiment embedding splits into positive and negative poles). On six film genres, a 16-d embedding with average pooling reached validation accuracy near 0.53 with validation loss bottoming around epoch 20 while training loss kept falling: overfitting. Pretrained vectors carry general meaning: 50-d GloVe averaged per document reached macro-F1 0.428 (0.431 TF-IDF weighted) against 0.42 for tuned TF-IDF and 0.35 for word2vec trained on 2,877 documents. Weighting helped little despite the common claim. Document vectors: average, TF-IDF-weighted average, Doc2Vec, topic proportions, or sentence encoders.

## Similarity and distance

| Measure | Use |
|---|---|
| Hamming | Fixed-length codes |
| Manhattan, Euclidean | Dense vectors of similar magnitude |
| Levenshtein (edit distance) | Typos and fuzzy matching ("belief"/"believe" is 2) |
| Cosine | Text vectors; ignores length |
| Jaccard on token sets | Near-duplicate detection |

A raw dot product grows with vector length and favours long vectors; on GloVe the effect is modest (mean norm 5.68 for dot-product neighbours against 5.51 for cosine, and "queen" dropped out of the top six) but in count vectors long ones are frequent uninformative words. **Normalise before cosine or dot product.** On L2-normalised vectors cosine is the dot product and Euclidean distance is monotone in it, so all three rank identically; vector databases rely on this.

## Skip-Gram with NCE in a textbook walkthrough (Fundamentals of Deep Learning, chapters 6-7)

The chapter contrasts two Word2Vec forms: CBOW builds an embedding from the whole context and predicts the target word (the book says it works best on smaller datasets), while Skip-Gram takes the target word and predicts one context word. Its Skip-Gram uses noise-contrastive estimation, described as a binary logistic regression that scores the input embedding against the true context word and a random sample of non-context words. The toy TensorFlow run uses 128-dimensional embeddings initialised uniformly in [-1, 1], 64 sampled non-context words, minibatch 32, plain SGD at learning rate 0.1 and 5 epochs, on an unnamed corpus with a 10,000-word vocabulary. For validation it draws 20 words at random from the 500 most frequent and lists their cosine-similarity neighbours; the neighbours are qualitatively sensible ("white" gives yellow, black, red; "eight" gives six, seven, five). It visualises the matrix with t-SNE (perplexity 30) and advises Word2Vec embeddings over one-hot vectors for language models.

Chapter 7 uses the Google News word2vec vectors (reported as 3 million words and phrases, trained on about 100 billion words) frozen as 300-dimensional inputs to a feed-forward 3-gram part-of-speech tagger, but learns embeddings jointly with the task (512 dimensions, 30,000-word vocabulary) for an LSTM IMDB sentiment classifier, advising that over a separate Skip-Gram step.

## Limits

- The chapter's NCE account (a sum over noise probabilities minus the context probability) is simplified and is not the standard NCE or negative-sampling loss.
- Neighbour checks are qualitative; no downstream accuracy is reported, and the corpus is not named.
- Dated code: Python 2 and TensorFlow 0.x.

## Term distances on one word (Text Analytics with Python, chapter 6)

The chapter measures the root term "Believe" against "beleive", "bargain" and "Elephant", ignoring case and using character-code vectors (bag-of-characters over 12 unique characters for cosine):

| Measure | beleive | bargain | Elephant |
|---|---|---|---|
| Hamming | 2 | 6 | ValueError (lengths 7 and 8 differ) |
| Euclidean | 5.66 | 17.94 | not stated |
| Levenshtein | not stated | not stated | 7 |
| Bag-of-characters cosine | 1.0 | 0.18 | 0.61 |

The chapter attributes the cosine of 1.0 for "beleive" to order being ignored, and advises Levenshtein when terms differ in length. It also notes that KL divergence fails to be a true metric since swapping its arguments changes the value, and it recommends testing any candidate distance against the four metric axioms (non-negativity, zero only for identical items, symmetry, triangle inequality) first.

## Word2vec rules of thumb asserted in a 2025 book chapter

The first chapter of a 2025 book on LLM agents, RAG and knowledge graphs (Raieli and Iuculano) asserts the following with no citation:

- roughly 300 dimensions is the best trade-off, with little gain from going larger;
- the typical window is 4: a window of 2 favours part-of-speech information and long windows favour broad similarity;
- a typical language holds around 200,000 words, which sets the length of a one-hot vector;
- cosine similarity is preferable to a raw dot product, and embeddings can be visualised with UMAP, PCA or t-SNE;
- an LSTM keeps information for as many as 100 steps, whereas a plain RNN begins to lose it after about 7.

## Limits (these two chapters)

- Chapter 6 uses a small toy collection (nine documents, three queries) and has no relevance labels, so the measures are judged by eye alone. It never scores its clusterings, and the code dates from the Python 2 era.
- Cosine and BM25 here are bag-of-words measures that ignore word order and synonyms; semantic similarity through embeddings is not covered.
- The 300-dimension, window, vocabulary-size and cosine-versus-dot-product statements are the chapter's general claims, with no experiment or citation in the extraction.
- The 100-versus-7 time-step figures are asserted with no source or experiment.

## See Also
- [[Bag of Words, n-grams and TF-IDF]] — prerequisite-for
- [[Neural Probabilistic Language Model]] — prerequisite-for
- [[BM25 and the Lexical Gap]] — related (the lexical alternative)
- [[Sentence Embeddings as Features for Classical ML]] — extends
- [[Semantic Analysis, WordNet and Lexical Ambiguity]] — related
- [[Cosine Similarity Rescaling Freedom]] — extends
- [[Seq2seq Bottleneck and Attention]] — related (frozen versus jointly learned embeddings in the same textbook)
- [[Word2vec: CBOW, Skip-gram and Negative Sampling]] — extends
- [[GloVe Global Vectors]] — extends
- [[FastText Subword Skip-gram]] — extends
- [[ELMo and TagLM: Contextual Embeddings from Bidirectional LMs]] — extends
- [[CoVe: Contextualised Word Vectors from MT Encoders]] — extends
