---
title: "NLP (Almost) from Scratch: Window Network and Sentence-Level Likelihood"
tags: [llm, architecture, concept]
summary: "Collobert et al. use one word-lookup-table network for POS, chunking, NER and semantic role labelling, with a CRF-like sentence-level likelihood and lookup tables initialised from a ranking-loss language model trained on unlabeled text."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-collobert-2011-natural-language-processing-almost-scratch.md
---

# NLP (Almost) from Scratch: Window Network and Sentence-Level Likelihood

Collobert, Weston, Bottou and colleagues test whether a single neural network, using word embeddings learned from large amounts of unlabeled text, can match systems engineered per task on part-of-speech tagging, chunking, named entity recognition and semantic role labelling. They expect that representations learned from unlabeled text generalise beyond any single benchmark and can stand in for hand-built features.

## Mechanism

- **Lookup table.** Each word indexes a column of a trainable matrix (50 dimensions, with a 5-dimensional capitalisation feature added). Tagging tasks other than role labelling use a fixed-window network; role labelling uses a sentence network of convolution and max pooling over time.
- **Sentence-level log-likelihood.** A tag path is scored by adding transition scores to the network's per-word scores, and the score is normalised over every possible path. It resembles a nonlinear CRF (see [[Conditional Random Fields and Label Bias]]) and has no normalisation at each step.
- **Pretraining the table.** A window language model is trained with a pairwise ranking loss, summing a hinge term (zero unless the true window's score f(x) fails to beat the corrupted window's f(x(w)) by 1) over windows x and replacement words w, first on 631M words of Wikipedia (LM1) and then on 852M words of Wikipedia and Reuters (LM2). Only the embeddings are transferred.
- **SENNA** is the fast, small-memory C tagger built from this.

## Results (self-reported)

- Starting the lookup table from LM2 raises NER F1 from 81.47 to 88.67 (CoNLL 2003 test, window network, sentence-level likelihood), role labelling from 70.99 to 74.15 (CoNLL 2005), and chunking from 90.33 up to 93.63; all against random initialisation.
- Without pretraining a plain network trails the benchmark systems (POS 96.37 against 97.24, WSJ test). Without pretraining, the sentence-level objective is far better than a word-level one for role labelling (70.99 against 55.40 F1).
- A table trained only on the supervised task gives unrelated neighbours for rare words, whereas LM1 gives related ones (for "france": austria, belgium, germany).
- Training the tasks jointly brings little or nothing over separate semi-supervised networks (window network, sentence-level likelihood, LM2).
- SENNA equals the benchmark on POS, chunking and NER but is behind on role labelling (75.49 against 77.92); adding Charniak parse-tree features raises role labelling to 76.06. As features, LM2 embeddings are at least as good as Brown clusters (NER 89.59 fine-tuned, 88.79 fixed, 87.15 with 1,000 Brown clusters).
- SENNA runs the POS test set in 4 seconds and 32 MB on a 3GHz core; the Toutanova et al. tagger takes 64 seconds and 800 MB. LM1 took about four weeks to train; supervised networks took from about an hour to three days.

## Limits

- The authors concede it is only "almost" from scratch: lowercasing and the capitalisation feature stay, and characters-only input is beyond scope.
- A full hyperparameter grid search was infeasible; language-model hyperparameters were chosen by "breeding" and an arbitrary dictionary schedule, and the language-model learning rate is not stated.
- The language model uses a fixed window the authors call probably too restrictive.
- One vector per word type, no subword handling: rare words map to RARE in a 100,000-word dictionary.
- role labelling still trails the benchmark, which uses six parse trees.
- Dated: fixed-window feed-forward models and CoNLL-era benchmarks.

## See Also
- [[Neural Probabilistic Language Model]] — prerequisite-for
- [[Conditional Random Fields and Label Bias]] — prerequisite-for
- [[Text CNNs: Kim Sentence CNN and Character-level ConvNets]] — extends
- [[Word2vec: CBOW, Skip-gram and Negative Sampling]] — related (the later vectors Kim compares against Collobert's)
