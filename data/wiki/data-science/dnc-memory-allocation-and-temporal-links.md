---
title: DNC Memory Allocation and Temporal Links
tags: [data-science, concept]
summary: "The DNC extends the Neural Turing Machine with a usage vector, allocation weighting, a retention vector and a temporal link matrix, so a controller can free, reuse and re-read memory in order; a textbook TensorFlow reimplementation reaches 15.78% mean error on 20 bAbI tasks and fails badly on path finding."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-fundamentals-of-deep-learning-ch08-memory-augmented-neural-networks.md
---

# DNC Memory Allocation and Temporal Links

A textbook chapter on memory-augmented networks asks how an RNN can gain an external, differentiable working memory for algorithmic and reading-comprehension tasks. It builds on the [[Neural Turing Machine]] (a controller with content and location addressing over a memory matrix) and explains the DNC, which adds bookkeeping for freeing and reusing memory and for following the order of writes. The whole architecture is end-to-end differentiable, so the loss gradient reaches every parameter.

## Mechanism

- **Usage vector**: one value in [0, 1] per memory location, 0 meaning completely free and 1 completely used. The **free list** orders location indices by ascending usage.
- **Allocation weighting**: the intermediate weighting that decides where new data goes. Worked example from the chapter on four locations: usages of 1, 0.7, 0.2 and 0.4 yield allocation weights of 0, 0.024, 0.8 and 0.12, so the least-used location receives most of the weight.
- **Retention vector**: a value in [0, 1] per location, 0 meaning the location can be freed and 1 that it is retained.
- **Precedence vector**: a probability distribution over which location was written most recently. The **link matrix** is N x N; entry L[i, j] gives the likelihood that i was written to later than j.
- **Read modes**: a softmax per read head over backward, lookup (content) and forward emphasis.
- **Interface vector**: its size is R x W + 3W + 5R + 3, for R read heads and word size W.

The NTM-side addressing in the chapter uses a key strength beta to sharpen near-uniform content weights, and an interpolation gate g in [0, 1] mixing the content weighting with the previous weighting.

## Implementation notes

Looping over locations in Python builds many graph nodes: a naive link-matrix update makes N^2 - N node copies, 65,280 for N = 256 in TensorFlow's symbolic graph. The chapter's advice is to vectorise (pairwise addition, cumulative product, sort and scatter, with `top_k` on negated usage to get the free list) and to use `tf.while_loop` for the controller's loop over time steps. For bAbI the loss counts only at answer steps (weight 1, and 0 elsewhere), discards the supervisory signals, lowercases, strips punctuation other than "?" and ".", masks answer words with dashes and one-hot encodes over a 159-item lexicon.

## Results

- Copy-series demo (feed-forward controller, one read head): with just 10 memory locations a DNC copies four sequences of five binary vectors each (20 vectors in all) by freeing and reusing locations.
- bAbI, all 20 tasks, 10,000 training and 1,000 test questions per task, trained jointly on 200,000 questions for about 500,000 iterations with an LSTM controller (error is the share of questions with any wrong answer word); chapter author's reimplementation: 15.78% mean error against 16.7 ± 7.6% in the original paper; 8 tasks fail (error above 5%) against a paper mean of 11.2 ± 5.4.
- Per task: single supporting fact 0.00% (paper 9.0 ± 12.6%); basic deduction 45.44% (paper 27.2 ± 20.1%); basic induction 56.43% (paper 53.6 ± 1.9%); path finding 98.21% (paper 64.6 ± 37.4%).

## Limits

- The chapter does not implement the NTM.
- The bAbI reproduction is a single run with no seeds or variance, and the chapter omits learning rate, optimiser, batch size, memory size and controller size. It is compared with the paper's mean over runs, not a matched protocol.
- It fails badly on path finding, induction and deduction.
- Dated: the code relies on TensorFlow 1.x calls (`tf.concat(1, ...)`, `TensorArray.pack`), and the extraction observes that transformers have since displaced memory-augmented RNNs for such uses. The NTM paper's arXiv id in the extraction is from memory and unverified.

## See Also
- [[Neural Turing Machine]] — prerequisite-for
- [[End-to-End Memory Networks]] — alternative-to
