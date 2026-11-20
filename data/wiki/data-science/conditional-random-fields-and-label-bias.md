---
title: "Conditional Random Fields and Label Bias"
tags: [data-science, nlp, concept]
summary: "A CRF models p(y|x) with one exponential model normalised over whole label sequences, which avoids the label bias problem of per-state normalised MEMMs; the original paper pays for it with slower training."
updated: 2026-11-20
sources:
  - data/raw/papers/2026-11-08-lafferty-2001-conditional-random-fields.md
---

# Conditional Random Fields and Label Bias

Lafferty, McCallum and Pereira propose labelling sequences with one exponential model normalised over whole label sequences, to remove the label bias of maximum entropy Markov models (MEMMs) yet still allow arbitrary features of the observations. They expect CRFs to fix label bias and to hold up better than MEMMs and HMMs when the data's dependencies run deeper than the model assumes.

## Label bias and the fix

In **label bias**, the transitions out of one state are normalised among themselves, so they never have to compete with transitions elsewhere in the model. A **conditional random field** is a pair (X, Y) in which, given X, the labels Y_v satisfy the Markov property over a graph G. On a chain, the probability of a label sequence given x is proportional to the exponential of weighted edge-feature and vertex-feature sums, and the normaliser Z(x) covers all whole label sequences; it is obtained as a product of per-position matrices. Parameters are fitted by maximum likelihood using two improved-iterative-scaling variants (Algorithm S and T) with forward-backward.

## Results (self-reported)

- Label-bias data (noisy rib/rob sequences from an HMM; 2,000 training and 500 test samples; same topology; a typical run): CRF error is 4.6% and MEMM error 42%.
- Synthetic data from mixed first- and second-order HMMs (1,000 sequences of length 25, over 5 labels and 26 observation symbols): the CRF generally beats the MEMM by 10% to 20% in relative error.
- Penn treebank POS tagging (first-order models with 45 tags, a 50-50 split of the 1.1 million-word corpus, 5.45% out-of-vocabulary rate): with no spelling features the CRF has the lowest overall error of the three, yet on unseen words the errors are 45.99% for the HMM, 48.05% for the CRF and 54.61% for the MEMM. With spelling features CRF+ gets 4.27% overall against 4.81% for MEMM+, and 23.76% against 26.99% on unseen words; for both MEMM and CRF, these features reduce overall error by roughly a quarter.
- Convergence: started from uniform parameters, a CRF was still not converged after 2,000 iterations, whereas CRF+ started from the fitted MEMM+ converged within 1,000; on the synthetic data a CRF takes about 500 iterations and the MEMM about 100.

## Limits

- The authors' chief stated drawback is that training converges more slowly than for MEMMs and HMMs.
- The convergence proof is only a sketch; there is no learning rate, regularisation, seeds or significance testing, the POS results are single runs, and no held-out dev set is used.
- Per the Figure 3 caption, the synthetic experiments cannot show any extra representational power of CRFs over HMMs; and with no spelling features the HMM does better than the CRF on unseen words.
- Experiments cover only chain CRFs with a first-order model; the authors leave tree-structured CRFs, induced features and boosting-like training for later.
- The text does not print the venue; year and venue come from the reading ledger.

## See Also
- [[Named Entity Recognition and Sequence Tagging]] — extends
- [[NLP (Almost) from Scratch: Window Network and Sentence-Level Likelihood]] — extends
