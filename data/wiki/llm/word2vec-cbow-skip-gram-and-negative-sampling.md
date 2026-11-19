---
title: "Word2vec: CBOW, Skip-gram and Negative Sampling"
tags: [llm, pretraining-and-data, concept]
summary: "Two log-linear word-vector models (CBOW and Skip-gram) without a hidden layer, then three training changes (negative sampling, frequent-word subsampling, phrase tokens) that made Skip-gram faster and more accurate on analogy tests."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-mikolov-2013-efficient-estimation-word-representations-vector.md
  - data/raw/papers/2026-11-07-mikolov-2013-distributed-representations-words-phrases-their.md
---

# Word2vec: CBOW, Skip-gram and Negative Sampling

Mikolov and colleagues removed the non-linear hidden layer from a neural language model. Their hypothesis was that simpler log-linear models trained on far more text give more accurate word vectors for syntactic and semantic regularities. Two papers define the family: the first introduces the architectures and a test set, the second the training tricks and phrase vectors.

## The two architectures

- **CBOW** takes four words before and four after the target and predicts the middle word.
- **Skip-gram** takes one word and classifies the words within a window around it (C=10 in the first paper).

The first paper trains both with a tree-structured softmax (Huffman coding of the vocabulary), running SGD with Adagrad inside the DistBelief system. It gives the per-example cost as N x D + D x log2(V) for CBOW and C x (D + D x log2(V)) for Skip-gram, where V is the vocabulary size and D the vector size. Vectors are scored on analogy questions: take vec(b) - vec(a) + vec(c) and look for the cosine nearest neighbour. The test set has 8,869 semantic and 10,675 syntactic questions.

## Training changes in the second paper

- **Negative sampling** uses logistic regression to separate the real context word from k words sampled from a noise distribution, needing only samples. The objective is log sigma(v'_wO . v_wI) plus, over the k noise words, the expectation of log sigma(-v'_wi . v_wI). It is a simplified form of noise-contrastive estimation.
- **Subsampling** discards each training word w with probability 1 - sqrt(t / f(w)), where f(w) is its frequency.
- **Hierarchical softmax** places the words at the leaves of a binary tree (Huffman-shaped here) so that scoring a word takes about log2(W) node evaluations. See [[Hierarchical Log-Bilinear Language Model]] for how a tree is built from data.
- **Phrases** are found by the bigram score (count(wi wj) - delta) / (count(wi) x count(wj)) and merged into single tokens.

## Results (self-reported)

| Setup | Result |
|---|---|
| 300-d, 783M Google News words, three passes, first test set | Skip-gram 53.3% total, CBOW 36.1%; semantic 50.0% vs 15.5%, syntactic 55.9% vs 53.1%; Skip-gram took about 3x the training time |
| 1000-d vectors, 6B words, DistBelief | Skip-gram scores 65.6% overall, CBOW 63.7%, a 100-d NNLM 50.8%; CBOW's syntactic score of 68.9% is the best |
| Cost on 6B words | NNLM 14 x 180 days x CPU cores, CBOW 2 x 140, Skip-gram 2.5 x 125 |
| Skip-gram, 300-d, 1B-word news corpus, vocabulary 692K | NEG-5 59% total; with 10^-5 subsampling 60% and training time 38 to 14 minutes |
| Same setup, hierarchical softmax | 47% rising to 55% with subsampling, 41 to 21 minutes; NEG-5 beats NCE-5 (59 vs 53) without subsampling |
| Phrase analogies, 3,218 examples | best 300-d model HS with subsampling 47% (19% without); best overall HS, 1000-d, whole-sentence context, about 33B words: 72%, falling to 66% on 6B words |
| Microsoft Sentence Completion, 1,040 sentences | Skip-gram with RNNLMs 58.9%; Skip-gram alone 48.0% (640-d, 50M words) |

The first paper also reports that a single pass over 1.6B words matches three passes over 783M, and that building the relationship vector from the average of ten example pairs gains the best models roughly 10 points (a claim with no table).

## Limits

- Single runs, no seeds or variance; accuracy is on the authors' own analogy sets, and exact-match scoring makes 100% unreachable.
- The training corpora (Google News, internal news data) are not public, so the large results cannot be rerun.
- Optimizer, learning rate, schedule, phrase threshold and delta are not stated in the second paper; the Skip-gram plus RNNLM combination weights are not given.
- The subsampling formula and the 3/4-power noise distribution are chosen heuristically; the ranking of negative sampling against hierarchical softmax flips with subsampling, and the noise-distribution comparison is "not reported here".
- The first paper's tables vary data size and dimension between architectures, so some comparisons are not like for like; its CPU-core figures are estimates taken from shared machines.
- The extraction's line for the best word-analogy setting (negative sampling with k=15 and subsampling) is garbled ("tied with k=15 NEG at 61%"), so that value is read as 61%.
- The nearest-neighbour comparison with older models is qualitative, and Skip-gram had two to three orders of magnitude more training data.
- Static vectors: no context-dependent meaning.

## See Also
- [[Neural Probabilistic Language Model]] — prerequisite-for
- [[Word Embeddings and Similarity Measures]] — prerequisite-for
- [[Hierarchical Log-Bilinear Language Model]] — prerequisite-for
- [[GloVe Global Vectors]] — alternative-to
- [[FastText Subword Skip-gram]] — extends
- [[Skip-Thought Vectors]] — extends
- [[Text CNNs: Kim Sentence CNN and Character-level ConvNets]] — extends
