---
title: AutoMix Self-Verification Routing
tags: [infra, pattern]
summary: "AutoMix has a small model draft an answer, check it against the context by sampling its own verdicts, and hands the noisy score to a POMDP router that decides whether to keep the answer or call a larger model; the authors report gains over FrugalGPT and HybridLLM on context-grounded tasks (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-aggarwal-2023-automix.md
---

# AutoMix Self-Verification Routing

AutoMix (Aggarwal et al., NeurIPS 2024, arXiv 2310.12963) is a three-step cascade for black-box language models: the small model answers, the same small model judges that answer against the supplied context, and a router turns the judgement into a keep-or-escalate decision. The verifier is not trained. It runs a few-shot prompt that asks whether the generated answer is correct given the context and question, samples several verdicts at high temperature, and reports the fraction that say "Correct" as its confidence.

## The router

The router treats the verifier score as a noisy observation of a hidden variable, how hard the question is for each model. It is a partially observable decision process: actions are keep the current answer or route to a larger model, the reward is performance minus a weighted cost, and the observation model is fitted on a training set by kernel density estimation. A simpler variant just thresholds the verifier score. Inference takes under 1 ms per query in the two-model case (self-reported). The router can also choose to keep a weak small-model answer when low verifier scores mark the question as unsolvable even by the large model, which a plain threshold cannot do.

## Efficiency metric

The paper scores a method by incremental benefit per unit cost, the slope from the small model's point to the method's point, and reports the percentage lift of that slope over always-calling-the-large-model (a random mix on the straight line between the two). Because it is a ratio against a baseline slope, the extraction notes it can exceed 100% and is not an absolute saving.

## Results (self-reported)

- Headline: over 50% lower compute cost at comparable performance, across five datasets (QASPER, QUALITY, COQA, MUTUAL, DIPLOMAT) and three black-box small models (LLaMA2-13B, Mistral-7B, GPT-3.5), each paired with GPT-4 as the large one; costs are simulated from assumed price ratios (large model 60, 100 or 200 times the small one).
- With the POMDP router, lift over FrugalGPT and HybridLLM is positive in every dataset and small-model pairing; for example with Mistral-7B the lift is 156.8% on DIPLOMAT against 16.8% for FrugalGPT and 67.1% for HybridLLM. The threshold variant wins a few cells.
- Low data: with 50 training examples AutoMix keeps a 15% lift and beats the trained baselines by more than 20 points absolute (macro average).
- With the router fitted on a single dataset and applied to the remaining four, it still beat the baselines (average lift 28.3% Mistral-7B, 31.5% LLaMA2-13B, 70.9% GPT-3.5).
- With three models (small, LLaMA2-70B, GPT-4) it skips a middle model that underperforms the small one.

## Limits

- Designed for context-grounded tasks, where the context lets the verifier check an answer; the authors say it does not cover factual or commonsense question answering, and extending to subjective generation is left open.
- The cost figures are simulated from price ratios rather than measured in latency or dollars; baselines are given zero router cost, and eight verifier samples are costed as one call.
- Only 2023-2024 black-box models; GPT-4 is the only large model. Training the router needs answers from every model on a labelled set.
- Inconsistencies in the paper: verifier shots (3 in a listing, 4 in the method text), verifier temperature (1.0 against 0.7), the lowest useful cost ratio (1:10 in the main text, 1:25 in an appendix), and mislabelled model names in two figure captions. The significance claims give no test details.

## See Also
- [[Cheap-First Gating and Model Cascades]] — prerequisite-for
- [[Confidence-Gated Escalation]] — related (the gate here is a sampled self-verification score)
- [[Self-Consistency]] — related (the verifier's score is an agreement fraction over samples)
- [[LLMSelector Per-Module Model Assignment]] — related
