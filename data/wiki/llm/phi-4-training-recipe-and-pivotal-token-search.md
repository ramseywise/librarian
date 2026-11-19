---
title: Phi-4 Training Recipe and Pivotal Token Search
tags: [llm, pretraining-and-data, concept]
summary: "Phi-4 is a 14B model trained on a synthetic-heavy mixture, then post-trained with SFT and two DPO rounds, the first built from Pivotal Token Search pairs; it beats GPT-4o on GPQA and MATH (self-reported) but is weak at strict instruction following."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-abdin-2024-phi-4-technical-report.md
---

# Phi-4 Training Recipe and Pivotal Token Search

The Phi-4 report (arXiv 2412.08905, preprint) argues that data quality, driven by synthetic data used throughout training, can match what scaling compute buys and can lift a student above its GPT-4o teacher on STEM question answering.

## Recipe

- Architecture: 14B decoder-only transformer, close to phi-3-medium, with the tiktoken tokeniser and full 4K attention; context extended to 16K in midtraining.
- Pretraining: about 10T tokens. Final mixture (Table 5): web 15% (1.2 epochs), web rewrites 15% (5.2), synthetic 40% (13.8), code 20% (2.4), acquired 10% (1.7).
- Post-training: an SFT round, then DPO on pivotal-token pairs (stage 1), then a judge-guided DPO round (stage 2) using full-length response pairs that GPT-4o labelled for accuracy, style and detail.

## Pivotal Token Search

A pivotal token is one whose generation changes the probability of a correct answer sharply. PTS finds them by recursive binary search: cut a response where the running sum of token log probabilities reaches its halfway point, and estimate p(success) for each prefix by sampling completions checked by an oracle (a test suite for code, a ground-truth match for maths). A segment is split further until its p(success) change is below p_gap or only one token remains. Prompts are kept only if 0.2 <= p(success) <= 0.8. DPO pairs are then built from one accepted and one rejected token. The authors see it as a token-level analogue of automated process supervision that needs no learned proxy.

## Reported results (self-reported)

- phi-4 scores 56.1 on GPQA against 50.6 for GPT-4o, and 80.4 on MATH against 74.6 (simple-evals, temperature 0.5). On four fresh November 2024 AMC 10/12 tests it averages 91.8 of 150.
- Stage 1 (pivotal-token DPO) takes GPQA from 47.3 after SFT up to 53.6 and MATH from 77.1 up to 80.5. Stage 2 alone lifts ArenaHard from 56.7 to 69.8, and both stages give 75.4; on its own stage 2 trails stage 1 on MATH (77.6) and GPQA (52.4), so the authors call the stages complementary.
- Against Qwen-2.5-14B-Instruct it wins 9 of 12 benchmarks, and is weakest on SimpleQA, DROP and IFEval (63.0 versus 78.7).
- Synthetic data repeated for 12 epochs beat fresh web tokens in smaller phase-2 runs (5-shot MMLU, 4 against 12 epochs). A 13B model trained on synthetic data alone fell 14.8 points behind phi-3-medium on TriviaQA. Over phi-3-medium (4K, internal eval), pretraining brought gains of 10.3 points for MMLU-pro and 8.9 for MATH.
- Post-training pushed SimpleQA answers toward refusal: the final model leaves 81.1% unattempted, gets 15.8% wrong and 3.0% right; F1 is 3.0 against 7.6 for phi-3.
- Long context (HELMET, 16K): 99.0 recall and 36.0 QA. Its jailbreak defect rate of 0.073 is the lowest among the models compared, but its harmful-content continuation rate (0.036) is above the phi-3 variants (in-house benchmark, simulated by GPT-4o).

## Limits

- The authors concede factual hallucination, weak strict instruction following, lengthy chain-of-thought replies to easy problems, and tuning for single-turn queries.
- N-gram decontamination does not catch rephrasing, so generalisation is uncertain. The final model was picked after seeing other candidates' AMC scores, and the caption of Figure 1 says 100 runs while Appendix C says 10 generations.
- Post-training numbers are single runs with no seeds; the report omits DPO hyperparameters, PTS thresholds and compute, and releases no weights, code or data. The SimpleQA F1 drop below the base model is attributed to post-training swapping guesses for refusals.

## See Also
- [[Preference Optimization Algorithms]] — prerequisite-for (the DPO family it uses)
- [[Continued Pretraining for Domain Adaptation]] — related (another data-centred route to capability)
- [[Outcome vs Process Reward Models]] — related (process supervision, of which PTS is a token-level analogue)
- [[Post-Training Reasoning Data Primer]] — related
