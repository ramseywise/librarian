---
title: EK-FAC Influence Functions for LLMs
tags: [foundations, pattern]
summary: EK-FAC approximates the inverse-curvature term in influence functions cheaply enough to trace a language model's outputs back to pretraining sequences at up to 52B parameters.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-grosse-2023-studying-large-language-model-generalization.md
---

# EK-FAC Influence Functions for LLMs

Grosse, Bae, Anil and colleagues (Anthropic, 2023 preprint) scale influence functions to pretrained language models of 810M to 52B parameters and use them to ask which training sequences most raise the likelihood of a given completion. All figures are the authors' own (self-reported).

## Mechanism

An influence score estimates how much the log-probability of a query completion would change if a training sequence were upweighted. It needs the inverse of a curvature matrix applied to a gradient. Two choices make this tractable:

- **EK-FAC** approximates the damped Gauss-Newton Hessian per layer with a Kronecker-factored eigenbasis and fitted diagonal eigenvalues. The authors report accuracy comparable to the standard iterative solver (LiSSA) while taking at least ten times less wall-clock time, fitting cost included. Ground truth for the accuracy test is the proximal Bregman response function, not leave-one-out retraining.
- **Scan tricks.** Query gradients are compressed to rank 32 (correlation 0.995 for one query at 52B). Candidate training sequences are either pre-filtered with a TF-IDF/BM25 variant (top 10,000) or scanned unfiltered with query batching. The authors estimate roughly 5 million unfiltered sequences are enough to match the filtered top-10 and scanned at least 10 million. A block-diagonal approximation (block size 2) was needed for the 52B model's memory. Only MLP parameters are covered.

Plain gradient dot products (no curvature) correlate worse with the ground truth: for an inflation query on the 810M model over 100,000 sampled sequences, 10 of the top 50 contained the query keywords versus 36 for EK-FAC.

## Findings reported

- **Sparse but spread.** Influence is heavy-tailed; at 22B the top one percent of sequences account for between 12% and 52% of the summed positive influence, and none of 8 visualised queries had a sequence above 1 nat. The authors read this as outputs drawing on many sequences rather than memorisation. Power-law fits (alpha about 2.0-4.3) were rejected by a KS test for only 2 of 8 queries.
- **Abstraction grows with scale.** At 810M the highest-ranked sequences overlap the query in surface tokens; at 52B they are related by theme (for example science fiction about AI self-preservation, satire, code, maths). English sequences' influence on Korean and Turkish translations of the query is near zero at 810M and grows with size (plot only).
- **Word order.** On synthetic fictional facts, a sequence influenced a query only when prompt-related text came before completion-related text; flipping the order cut influence by at least an order of magnitude (translation example on 52B: 0.116 versus 0.030, with a Mandarin-only sequence at 0.020).
- **Layers.** Averaged over 50 queries and their top 500 sequences, 52B influence was spread nearly evenly across layers, but facts and memorised quotes sit in upper layers while maths, code and translation sit in middle layers.
- **Role-play.** Anti-shutdown and similar outputs traced to related science fiction and AI-risk text. The authors call this weak evidence against the hypothesis that role-play comes from planning, not a refutation. The influence was computed on pretrained models, not the fine-tuned assistant that produced the outputs.
- **Memorisation.** For six famous-quote queries the top sequences contained the exact passage; no clear copying was found for ordinary assistant outputs.
- Crowdworkers judged most top sequences relevant to their queries.

## Limits

- Influence functions are known to match true counterfactuals poorly in deep nets; the authors treat them as approximating a local response function and expect them to miss nonlinear training phenomena such as circuit formation. Whether that function captures real training effects is untested.
- Pretrained models only (no fine-tuning or RLHF); the largest is 52B, below the size of the assistant studied; only part of the corpus was scanned; TF-IDF filtering biases toward token overlap.
- The top-1% share clips negative influence and is a crude concentration measure; token-level signs are hard to interpret. The word-order finding comes from influence scores, not from retraining.
- No leave-one-out ground truth. Gradient computation for candidates remains the bottleneck.
- Internal inconsistency noted by the extraction: the Fig 8 caption gives slightly different alpha values from the text (shutdown 2.21 versus 2.28). The extraction also notes equations were garbled and several figures have no numeric values in text.

## See Also

- [[SHAP Attributions and the Limits of Explanations]] — related (attribution to inputs rather than to training data)
- [[OLS Influence and Collinearity]] — related (the classical statistics notion of influence)
- [[Reward Hacking and Overoptimization]] — related
