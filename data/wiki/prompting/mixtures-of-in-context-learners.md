---
title: Mixtures of In-Context Learners
tags: [prompting, concept]
summary: MoICL splits demonstrations into subsets, runs the model on each as an expert, and mixes their next-token log-probabilities with learned weights, including negative ones; it beat concatenated ICL on 5 of 7 classification sets and resisted noisy or imbalanced demonstrations (self-reported).
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-hong-2024-mixtures-context-learners.md
---

# Mixtures of In-Context Learners

Hong et al. (Edinburgh, ACL 2025) treat each subset of the demonstrations as an expert and combine the experts' next-token log-probabilities with weights tuned on labelled data. Weights may be negative, so a bad subset acts as an anti-expert. A hyper-network (T5-small) can predict weights for demonstration sets not seen in tuning. Cost is about k times (n/k + 1) squared forward-pass units, against (n+1) squared for concatenation.

## Results (self-reported)

Llama-3-8B-Instruct, n=30 demonstrations, 5 seeds, accuracy.
- Beat concatenated ICL on Offensive (76.44 to 81.33, k=30), Hate (53.54 to 66.52, k=10), FEVER, PAWS and QNLI; tied on SST2 and lost on RTE (86.43 to between 79.93 and 84.12).
- Uniform weights without tuning did no better than concatenation (Offensive 73.37), and positive-only weights lost the gain (76.05), so tuning and anti-experts matter.
- Mixing SST2 demonstrations into Offensive (half of them): concatenation fell to 70.67, scalar MoICL stayed at 80.95. With 29 of 30 demonstrations from one label, concatenation fell to 28.49 and MoICL to 77.77.
- On NQ-open with wrong answers injected (12 demonstrations, one seed), tuned weights held up while concatenation fell; without noise concatenation was best (0.4083 exact match against 0.3864 for uniform MoICL).
- About 20 annotated examples sufficed to beat concatenation, which is capped near 160 demonstrations by the window.

## Limits

- Needs token logits, so black-box APIs are out, and needs labelled data to tune the weights. Only Llama-2/3 models of 7B to 70B were tried.
- Out-of-domain, imbalance and model-size tests are mostly on one dataset (Offensive). Noise robustness used one seed, and there are no significance tests.
- Generation tasks show no gain on clean data. The LoRA baseline got no hyperparameter search.

## See Also
- [[Few-Shot Prompting]] — prerequisite-for
- [[LongICLBench and Many-Shot ICL Scaling]] — alternative-to
- [[Implicit Weight-Patch Theory of In-Context Learning]] — related
