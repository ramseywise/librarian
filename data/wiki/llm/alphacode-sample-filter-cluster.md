---
title: AlphaCode Sample, Filter and Cluster
tags: [llm, reasoning-and-planning, pattern]
summary: "AlphaCode draws up to a million programs per problem from a fine-tuned encoder-decoder, discards those failing the example tests (over 99%), clusters survivors by outputs on generated inputs and submits at most 10; it reached top 54.3% on simulated Codeforces contests (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-li-2022-competition-level-code-generation-alphacode.md
---

# AlphaCode Sample, Filter and Cluster

Li et al. (DeepMind) ask if a big code transformer can solve unseen competition problems that call for algorithmic reasoning, provided it draws a huge number of programs and screens them by what they do when run. The authors call sampling at scale a critical driver of performance.

## Pipeline

1. **Train.** Encoder-decoder transformers from 300M to 41B parameters begin with 715.1 GB of GitHub code as pre-training data and then move to fine-tuning on CodeContests. Fine-tuning mixes next-token and masked-LM losses with tempering (T=0.2), tags and ratings, value conditioning and prediction, and GOLD, an offline-RL objective that weights the likelihood gradient by an off-policy importance term.
2. **Sample.** Draw as many as 1M programs per problem, split evenly between Python and C++, with randomised tags and ratings. Multi-query attention in an asymmetric encoder-decoder sampled roughly 12 times faster than standard multi-head attention at a similar solve rate (1B model).
3. **Filter.** Keep only programs passing the example tests, which discards more than 99% of samples.
4. **Cluster.** Execute the survivors on generated test inputs (the ablation used 50 inputs and 8192 samples), group programs that behave the same, and submit no more than 10.

## Results (self-reported)

- Setup: ten simulated Codeforces contests from Dec 2021 with over 5,000 participants, the 41B+9B ensemble with clustering, at most 10 submissions per problem, three evaluations averaged. Result: an average rank in the top 54.3% and an estimated rating of 1238, ahead of 72% of users active in the previous six months. Allowing more than 10 submissions moved it to the top 48.8%, at 28.8 submissions per solved problem.
- CodeContests validation, 10 submissions from 1M samples: 41B plus clustering solves 34.2% (31.8% without clustering), and the ensemble with clustering 35.5%. On the test set, 41B plus clustering from 100k samples solves 29.6%.
- 1B ablation on validation: stacking the five fine-tuning enhancements takes 10@100k from 15.2% up to 24.1%, clustering included. Clustering contributes 21.5% to 24.1% at 10@100k and 24.2% to 28.4% at 10@1M, and barely matters at 10@1K. Skipping pre-training leaves 10@100K at 10.5%, versus 21.5% with the full GitHub set.
- Solve rate rises roughly log-linearly with sample count, and bigger models climb more steeply.
- CodeContests generated tests cut the false positive rate from 62% to 4% (1B solutions, 1M samples per problem); APPS has 60% and HumanEval 30%.
- In an early 1B run, validation loss started rising around 50k fine-tuning steps in, even as solve rate went on improving, so the authors call loss a poor proxy.
- On APPS, AlphaCode 1B (50,000 samples, 5 submissions) beats Codex 12B on interview (9.66% against 3.23%) and competition (7.75% against 3.08%) but not introductory (20.36% against 24.52%).

## Limits

- The authors write that better solve rates demand exponentially more samples, with costs quickly becoming prohibitive; a wide gap also remains between filtering plus clustering and the pass@k ceiling.
- CodeContests still lets slow solutions through (46% false-positive-or-slow despite 4% false positives). Judging presumes one correct output even for multi-output problems (about a quarter of validation problems) and cannot handle interactive ones.
- Codeforces was evaluated three times reusing one set of models and samples; how much results vary with training and sampling is unmeasured, the hacking phase is not simulated, and the 41B model was stopped early and is undertrained.
- The Table 8 ablations use one 1B model and mostly a single seed; on the test set the 41B+9B ensemble does not beat 41B alone (29.7% against 29.6%).
- Fine-tuning steps, batch size, wall-clock time and exact compute are not given, and the Codeforces comparison group is self-selected.
- On HumanEval the encoder-decoder models trail decoder-only ones; weights are unreleased, so only the CodeContests dataset supports reproduction.

## See Also
- [[Rejection Sampling Fine-Tuning]] — related
- [[CodeRL Unit-Test Actor-Critic]] — alternative-to
- [[AlphaCodium Flow Engineering]] — extends
- [[EvalPlus and HumanEval+]] — related
- [[Code LLM Training Recipes]] — prerequisite-for
- [[CodeT Generated-Test Reranking]] — alternative-to (generated tests with dual agreement; its replication of AlphaCode's clustering scores lower)
- [[Planning-Guided Transformer Decoding (PG-TD)]] — alternative-to
