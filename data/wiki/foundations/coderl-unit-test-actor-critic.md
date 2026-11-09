---
title: CodeRL Unit-Test Actor-Critic
tags: [foundations, pattern]
summary: "CodeRL finetunes a pretrained code model (CodeT5-770M) with an actor-critic loop that uses unit-test outcomes as rewards, then at inference refines passing programs and repairs failing ones from error messages (Critic Sampling); it set new APPS pass@k results in 2022 (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-08-le-2022-coderl.md
---

# CodeRL Unit-Test Actor-Critic

Le et al. (NeurIPS 2022). Plain next-token training never sees unit-test signals; the paper turns test outcomes into critic-based rewards during training and into feedback at inference time.

## Mechanism

- **Training.** The actor is CodeT5-770M, pretrained and then warm-started on APPS with cross-entropy. A small critic learns to predict how sampled programs fare on unit tests, after which the actor is finetuned on cross-entropy plus an RL loss. Rewards run: compile error -1.0, runtime error -0.6, failed test -0.3, all tests passed +1.0. The baseline is a greedy-decoded program, and the critic provides per-token values.
- **Critic Sampling at inference.** Draw N=200 programs and run them on the example tests; programs that pass are refined starting from critic-chosen prefixes, and the best failing program is repaired using its error type and message, in a single round at most.

## Results (self-reported)

The extraction lost most pass@k values, so these are given by direction and by the numbers it kept.

- On the APPS test set (all levels), CodeRL with CodeT5 posted new pass@1000 marks, above Codex 12B (7.87) and GPT-J 6B (17.63), and the authors say that with example-test filtering k=1000 equals AlphaCode at k=50000. Trained on APPS and run zero-shot on MBPP (500 test problems, temperature 1.2), it outscored a finetuned 137B model; plain CodeT5 without RL reached 78.4 pass@1000 on that benchmark.
- On APPS pass@1000, Critic Sampling moved the score from 17.78 to 20.98, while refinement alone reached 19.36. Best results came from repairing only the single top candidate; two or four candidates did slightly worse.
- Ablations on APPS: the RL loss alone suffers vanishing gradients, and cross-entropy plus RL is best; a relative baseline plus critic is the best return estimate and absolute returns without a baseline the worst. Adding the extra pretraining data and the next-token objective raised pass@5.
- A GPT-2-small critic exceeded 75% accuracy at predicting errors. Over 90% of compile errors were syntax errors. CodeRL reduced compile errors but runtime errors rose.

## Limits

- Critic training adds cost. Example tests are weaker than hidden tests, so false positives cap the gain from Critic Sampling. One round of refine and repair only.
- Runs are single, without seeds or variance, and many scores are low (pass@1 2.69%). Generated code can be biased or insecure, so a human must verify it. The results date from 2022 and the strongest baselines are now old.

## See Also
- [[Reinforcement Learning Foundations]] — prerequisite-for
- [[Code Generation Prompting]] — related
- [[Repository-Level Coding Benchmarks]] — related
