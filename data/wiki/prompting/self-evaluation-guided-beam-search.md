---
title: Self-Evaluation Guided Beam Search
tags: [prompting, concept]
summary: Decoding method that scores each reasoning step by the model's own probability that the step is correct, combines it with generation probability and samples beams by that score; the paper reports gains on GSM8K and long chains at about three times the cost of self-consistency (self-reported).
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-08-xie-2023-self-evaluation-guided-beam-search.md
---

# Self-Evaluation Guided Beam Search

This NeurIPS 2023 paper asks whether stepwise self-evaluation can steer a stochastic beam search over reasoning steps and so reduce error accumulation in long chains. A decoding unit is one step: a CoT sentence or one PAL program line. Every one of the k beams spawns n sampled step candidates from the generator. The same LLM is then prompted, using few-shot exemplars in multiple-choice evaluation form, to score each candidate with C, the token probability of option (A) "Correct". Candidates are ranked by E = P^lambda x C^(1-lambda), where P is generation probability, and the next k beams are drawn without replacement from softmax(E/tau), where tau decays over the steps. The final answer is a majority vote over the last beam.

## Results (self-reported)

- Codex, PAL on GSM8K, single chain (tau=0): 72.0 rises to 80.2. Restricted to the 358 instances with at least 9 steps: 72.9 to 82.6.
- Codex, CoT on StrategyQA: gains concentrate in chains of 5 or more steps (351 instances, 68.4 to 71.8); Codex with the method beats the ChatGPT CoT figure of 65.9.
- Weights: lambda=0.5 gives 80.2 on GSM8K, lambda=0 gives 77.1, and correctness confidence alone (lambda=1) lowers accuracy.
- Cost-matched, Llama-2 13B PAL on GSM8K, multi-chain n=2: the method beats PAL with self-consistency at 12.6k against 13.9k tokens. Beam size k=10 reaches 42.8% against 35.7% for a single chain.
- No gain where the baseline is already strong, for example Object Counting at a 96.7 PAL baseline.

## Limits

- Token logits are required, so GPT-4 or ChatGPT-style APIs cannot be used, as the authors state.
- Candidate sampling and self-evaluation add cost: single-chain PAL on GSM8K costs about 3x self-consistency at n=16, StrategyQA with Codex CoT 11.6k tokens against 0.06k, and the headline k=5, n=16 runs cost roughly 3x to 75x baseline tokens.
- Weaker on short chains: Llama-2 13B on commonsense StrategyQA falls below CoT at equal cost.
- On StrategyQA the correctness confidence hardly distinguishes right chains from wrong ones, because plausible yet wrong chains also score highly.
- The model grades its own steps; no seeds or significance tests; Codex is deprecated.

## See Also
- [[Program-Aided Language Models (PAL)]] — prerequisite-for
- [[Self-Consistency]] — alternative-to (sampling whole chains and voting)
- [[Tree of Thoughts]] — alternative-to
- [[SelfCheck Step Verification]] — alternative-to (also scores steps with the model itself)
