---
title: Self-MoA Single-Model Aggregation
tags: [graph, pattern]
summary: "Self-MoA samples one strong model several times and has an aggregator synthesise the samples; Li et al. report it beating a mixed-model mixture-of-agents on AlpacaEval 2.0 (65.7 vs 59.1) because proposer quality mattered more than diversity in their regressions (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-li-2025-rethinking-mixture-agents.md
  - data/raw/papers/2026-11-06-li-2024-more-agents-all-you-need.md
---

# Self-MoA Single-Model Aggregation

Mixture-of-Agents (MoA) has several different models propose answers and an aggregator model synthesise them, optionally over more layers. Li et al. (Princeton, arXiv 2502.00674, a preprint) test whether mixing models is the source of the gain. Self-MoA keeps the aggregation step but draws every proposal from the single best model; Self-MoA-Seq feeds the samples to the aggregator through a sliding window so the number of samples is not capped by its context.

## Results (self-reported)

- AlpacaEval 2.0 length-controlled win rate, six open models as in the original MoA setup, Qwen1.5-110B-Chat aggregating: Self-MoA with six WizardLM-2-8x22B samples scored 65.7 against 59.1 for the mixed two-layer MoA; WizardLM alone scored 53.1. The authors could not reproduce an earlier single-proposer result and guess the proposer choice differed.
- Seven-billion-parameter task specialists (Qwen2-7B-Instruct, DeepSeek-Coder-V2-Lite, Qwen2-Math-7B), six proposers: Self-MoA with the best model per task scored MMLU 69.01, CRUX 50.75 and MATH 68.42, against best mixed configurations of 68.90, 47.00 and 67.62. This needs prior knowledge of the task.
- In about 70 proposer mixtures per dataset, regression coefficients on quality (accuracy) exceeded those on diversity (Vendi Score) on all three datasets (for example MATH 4.719 against 2.839), so performance was more sensitive to quality.
- Mixing helped only when models were of similar quality and differed in strengths, and the margin was tiny (59.86 and 60.04 against 59.69 for same-model sampling on a mixed-task set).
- At equal quality it was cheaper: 65.7 with 7 forward passes against 65.4 for a three-layer mixed MoA with 13. Against Universal Self-Consistency over the same samples it scored 65.7 to 60.2.
- Adding samples did not reliably help: a similar-quality second model added about 2%, a model about 5% weaker cost over 1.5%.

## Agent Forest (sample and vote)

Li et al. (Tencent, TMLR 2024, arXiv 2402.05120) sample the same model N times and majority-vote, with a similarity-based vote for code. Setup: Llama2-13B/70B-Chat and GPT-3.5-Turbo, 40 samples, mean of 10 runs. Gains at 40 samples were +12 to +24 points on GSM8K, +6 to +10 on MATH, +1 to +4 on Chess, +5 to +11 on MMLU and +4 to +9 on HumanEval (self-reported); Llama2-13B reached 59% on GSM8K against 54% for a single Llama2-70B query. Voting stacked on other methods except debate, which gave zero on HumanEval with both Llama2 models; the authors attribute it to noise from referencing other agents' answers, untested. Gains grew with problem difficulty in a synthetic task and tapered at the hardest setting, and token cost grew in proportion to the number of agents.

## Limits

- Models are small, open and from 2024; the frontier only appears as an aggregator in one test. The regression is correlational. Only parallel proposers with one aggregator are tested, not adaptive topologies.
- Agent Forest's "agents" are independent samples with no interaction, so the title overstates the multi-agent angle (the extraction's reading); GPT-4 was not voted; debate was capped at ensemble 10; the large relative MATH gains come from base accuracies of 0.03-0.09.
- Sample diversity from one model plateaus, and context length caps how many samples an aggregator reads.

## See Also
- [[Self-Consistency]] — prerequisite-for
- [[Multi-Agent Topology Patterns]] — prerequisite-for
- [[TUMIX Tool-Use Mixture]] — related (heterogeneous agents beat one repeated agent there, which the TUMIX authors note differs from Self-MoA)
- [[HSE and Router Robustness in Model Societies]] — related
- [[Best-of-k Headline Inflation]] — related
