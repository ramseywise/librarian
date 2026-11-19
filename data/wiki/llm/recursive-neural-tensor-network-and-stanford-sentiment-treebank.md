---
title: "Recursive Neural Tensor Network and the Stanford Sentiment Treebank"
tags: [llm, architecture, concept]
summary: "The RNTN composes child vectors up a parse tree with one tensor-based function, trained on a treebank with sentiment labels for 215,154 phrases, and reaches 85.4% on binary full-sentence sentiment."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-socher-2013-recursive-deep-models-semantic-compositionality.md
---

# Recursive Neural Tensor Network and the Stanford Sentiment Treebank

Socher and colleagues test two things together: a treebank with a sentiment label on every phrase, and a recursive network whose composition step uses a tensor. They want to know whether the pair handles negation and similar effects better than bag-of-words and older recursive models. Their bet is that one multiplicative composition function with a fixed parameter count combines meanings more faithfully than the many input-specific composition functions (MV-RNN) or a plain RNN.

## Resource and method

- **Stanford Sentiment Treebank (SST):** a sentiment label on each of 215,154 phrases, taken from the parse trees of 11,855 sentences. The sentences are movie-review sentences from Pang and Lee, parsed with the Stanford parser; every phrase was labelled by Mechanical Turk workers on a slider. Fine-grained classification has five classes: very negative, negative, neutral, positive, very positive.
- **RNTN:** the parent vector comes from the concatenated child vectors b and c, through a bilinear tensor term plus an ordinary linear term, then a nonlinearity; a softmax classifier sits at every node of the tree. All three models (RNN, MV-RNN, RNTN) were trained by backpropagation through structure with AdaGrad, tuning hyperparameters on the dev set.

## Results (self-reported)

- 85.4% on binary full-sentence sentiment (SST test, root level), up from a previous best under 80%. The abstract also claims +9.7% over bag-of-features baselines on 5-class accuracy over all phrases; the extraction records the fine-grained and all-node values without numbers.
- Naive Bayes reaches about 41% fine-grained accuracy at the sentence root; the RNTN stays under 46% there.
- Negation: on 21 positive sentences and their negations the RNTN reverses sentiment, and on negated negative sentences it increases positive activation. It is also analysed on 131 test sentences of the form "X but Y" where X and Y differ in sentiment.

## Limits

- A single corpus of movie-review sentences and one split; the paper reports no seeds, variance or significance tests.
- It needs parse trees and phrase-level labels; the negation test sets are tiny (21 sentences, 131 cases).
- Learning rate, regularisation value and parameter counts are not stated; collection details sit in supplementary material the extraction did not see.
- Fine-grained root accuracy stays under 46% and the neutral class is hard.
- Several result lines in the extraction carry no number (RNTN fine-grained and all-node accuracies), so only the headline figures are given here.
- Dated: recursive parse-tree models, with SST still used as an evaluation set.

## See Also
- [[Neural Probabilistic Language Model]] — prerequisite-for
- [[Sentiment Analysis Methods and Failure Modes]] — related (benchmarks and methods for sentiment)
- [[Text CNNs: Kim Sentence CNN and Character-level ConvNets]] — related (Kim evaluates on SST)
