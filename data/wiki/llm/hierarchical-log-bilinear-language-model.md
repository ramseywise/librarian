---
title: "Hierarchical Log-Bilinear Language Model"
tags: [llm, architecture, concept]
summary: "Mnih and Hinton's HLBL replaces the full softmax with a product of binary decisions down a word tree built from the data itself, with optional multiple codes per word, training over 200 times faster per epoch than the non-hierarchical model on APNews."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-mnih-2008-scalable-hierarchical-distributed-language-model.md
---

# Hierarchical Log-Bilinear Language Model

Mnih and Hinton set out to make a neural language model with a tree-shaped output layer (a hierarchy over words, here learned from data) competitive with flat neural and n-gram models while training far faster. They expect that a well-built tree, in which a word may sit under several codes, lets the hierarchical log-bilinear model (HLBL) beat the flat log-bilinear model (LBL) and n-grams.

## Mechanism

- **Prediction.** Each context word's vector is scaled by a diagonal matrix for its position and the results are summed into one predicted vector r_hat. A word's probability adds up, over its codes, the product of binary logistic decisions along the tree path, each taking the dot product of r_hat with that node's feature vector q (plus a bias). A code is the binary string of decisions from root to a word's leaf.
- **Tree building.** The first step trains an HLBL on a random tree. Each word's predicted vectors are averaged across its contexts, and the words are then split recursively by fitting two-component Gaussian mixtures (10 EM steps). A tree for a vocabulary of nearly 18,000 words with 100-d vectors took a few minutes.
- **Overcomplete trees.** Several generated trees are joined under one root so each word appears more than once; average code length rises with overcompleteness, from 14.2 for the random tree to 143.2 for the 4x tree.

## Results (self-reported)

Setup: APNews, 14M-word training set, 1M validation, 1M test, vocabulary 17,964, 100-d features, context 5, perplexity (lower is better).

- A twice-overcomplete ADAPTIVE(0.4) tree gets below the flat LBL (117.0) and both Kneser-Ney n-gram models; the 4x tree has the lowest perplexity, 112.1, at 32 minutes an epoch.
- Per epoch, even the slowest HLBL runs over 200 times faster than LBL (32 minutes against 6,420).
- A random tree scores 151.2 and the data-driven BALANCED tree 131.3, both at 4 minutes an epoch; the unbalanced ADAPTIVE tree improves further at the same cost. Using a learned tree instead of a random one lowers perplexity by 19.9 at 100 dimensions and 29.2 at 25.
- Words given the most codes turned out to be rare ones that cluster poorly, not words with several senses.

## Limits

- Only one dataset (APNews, 14M words); single runs with no variance or significance tests.
- The paper omits batch size, L2 strength, initialisation variance, hardware and epoch counts, and gives no code.
- The authors concede that extra codes duplicate rare words rather than model multiple senses.
- Overcomplete trees add parameters and cost in proportion (32 minutes an epoch at 4x).
- The LBL and Kneser-Ney scores are taken from an earlier paper by the same group.
- Periodic tree rebuilding during training is proposed but not tested.

## See Also
- [[Neural Probabilistic Language Model]] — prerequisite-for
- [[Word2vec: CBOW, Skip-gram and Negative Sampling]] — extends
