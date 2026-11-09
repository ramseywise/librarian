---
title: "Word Embeddings and Similarity Measures"
tags: [foundations, concept]
summary: "word2vec, GloVe and FastText give dense vectors where shared contexts mean closeness; covers negative sampling, subwords, analogy and bias limits, document vectors, and why to normalise before cosine."
updated: 2026-11-09
sources:
  - data/raw/repos/learn-ai-engineering/data-science--03-nlp--notes--02-text-classification.md
  - data/raw/repos/learn-ai-engineering/data-science--03-nlp--notes--04-embeddings-and-similarity.md
---

# Word Embeddings and Similarity Measures

In TF-IDF each word is its own axis, so "hotel" and "motel" are as far apart as "hotel" and "banana" (see [[Bag of Words, n-grams and TF-IDF]]). An embedding maps each word to a dense vector of 50 to 300 numbers, learned so words used in similar contexts get similar vectors. Nothing is labelled. This is the idea behind the [[Neural Probabilistic Language Model]] and, scaled up, the sentence encoders in [[Sentence Embeddings as Features for Classical ML]].

## word2vec

Two shallow architectures: **CBOW** predicts a target from the average of its context words (faster, frequent words); **skip-gram** predicts each context word from the target (rare words, small corpora; the rule of thumb comes from library documentation, not the original paper). In the original analogy test with 300-d vectors on 783M words, skip-gram scored 50.0% on semantic questions against CBOW's 15.5%, and 55.9% against 53.1% on syntactic ones; CBOW trained in about a day and skip-gram in about three.

**Negative sampling** replaces the expensive softmax over the vocabulary with binary classification: is this (word, context) pair real, or one of k random pairs? Noise words come from the unigram distribution raised to the 3/4 power; k of 5 to 20 suits small corpora and 2 to 5 large ones. **Subsampling** discards a frequent word with probability 1 - sqrt(t/f), t around 1e-5. On about 1B words, negative sampling with 5 noise words scored 59% in 38 minutes against 47% in 41 minutes for hierarchical softmax; adding subsampling gave 60% in 14 minutes. These are single runs without error bars. Merging frequent pairs into phrase tokens reached 72% on a phrase-analogy set, but only with 33B training words.

Skip-gram with negative sampling is two embedding tables, a dot product and a sigmoid; the learned table is the only thing kept. Trained on a 1.1M-token slice of public-domain books it took 12 seconds and already put "war" near "civil" and "treaty"; the corpus decides meaning, so "king" sat near "george" and "france", not "queen". The context window decides the kind of similarity: window 2 gives words that fill the same slot (past-tense motion verbs), window 15 gives topical surroundings.

## GloVe and FastText

- **GloVe** factorises the log word co-occurrence matrix; pretrained vectors (50 to 300 dimensions) are widely shipped.
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

## See Also
- [[Bag of Words, n-grams and TF-IDF]] — prerequisite-for
- [[Neural Probabilistic Language Model]] — prerequisite-for
- [[BM25 and the Lexical Gap]] — related (the lexical alternative)
- [[Sentence Embeddings as Features for Classical ML]] — extends
- [[Semantic Analysis, WordNet and Lexical Ambiguity]] — related
- [[Cosine Similarity Rescaling Freedom]] — extends
