---
title: E-Commerce Operation Benchmarks
tags: [eval, comparison]
summary: "Two 2026 benchmarks that have an agent run an online store for a simulated 365 days and score terminal assets: E-Commerce Bench (18 models, 5 episodes each; top mean 1,431,425 yuan, 10 of 90 episodes bankrupt) and MerchantBench (best LLM configuration 27.3% of the human mean); all numbers self-reported."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-fan-2026-e-commerce-bench.md
  - data/raw/papers/2026-11-06-shi-2026-merchantbench.md
---

# E-Commerce Operation Benchmarks

Both benchmarks put an agent in charge of a simulated online store for 365 days and grade the assets the agent ends with. Neither uses an LLM as the grader: the simulator computes the score. They differ in what they simulate and what they measure on top of assets.

## E-Commerce Bench (Fan et al., arXiv 2608.30730, 2026)

The agent runs up to four stores. Customers follow a fixed demand model and suppliers follow a rule-based negotiation kernel; an LLM only rewords the supplier's replies. The authors present this as the reason outcome differences belong to the agent rather than to sampling noise. They report seven axes (profit plus six diagnostics) and that no model leads on all seven.

Setup for every number in this section (self-reported): 18 models (8 proprietary, 10 open-weight) with 5 episodes apiece, 90 in total; a single fixed world; 18 tools common to all models; each provider's default settings, with thinking switched on wherever the model allows; at most 4,000 turns; and 100,000 yuan to start. The metric is end-of-year total assets across bank, wallet and escrow; bankrupt episodes stay in every mean.

- **Assets.** GPT-5.6 Sol (max) averaged 1,431,425 yuan (std about 314k); Qwen3.5-Plus averaged about 1.1k, which the paper puts at a factor of 1,264. Qwen3.8-Max-Preview averaged about 416k, which the paper calls 38% above GLM 5.2 (high) at about 301k.
- **Bankruptcy.** 10 of 90 episodes went bankrupt (the tenth consecutive negative bank day), and four models account for all of them: GPT-5.5 (2 of its 5 episodes), Claude Opus 4.6 (2 of 5), Gemini 3.1 Pro (2 of 5) and Qwen3.5-Plus (4 of 5).
- **Fraud.** Bad-spend share was 18.48% for GPT-5.6 Sol (16th of 18) and 0.12% for Claude Opus 4.7 (best). Between 4.0% and 31.7% of supplier approaches turned into orders, depending on the model. For 15 of 18 models the spread of that share is larger than its average, which the extraction takes to mean the rankings are noisy.
- **Efficiency.** Fable5 earned 479 yuan of profit per tool call against 363 for GPT-5.6 Sol, with 59.9% fewer calls. Across all models 71.8% of calls were shipping, advancing the day, withdrawing or publishing, and 0.66% revised prices.
- **Learning.** The AnchorRatio compares the agent's repeat purchase prices with a random ordering of its own prices (1.0 means random, lower is better): 0.834 for Qwen3.8-Max-Preview, 0.918 for Gemini 3.5 Flash, a field median of 1.369. The paper reports no clear price decline for 16 of 18 models.
- **Negotiation.** The score ranged from 0.811 (Claude Opus 4.7) to 0.596 (Kimi K2.6); accepting the opening quote scores 0.50.

The paper also observes that a ranking by assets captures just part of the underlying skill, and that every model breaks at least five of the failure rules, with Gemini 3.1 Pro breaking all ten.

## MerchantBench (Shi et al., arXiv 2607.28956, 2026)

A seller-side simulation that advances hourly while the agent acts once per 12 hours. It offers 26 tools and draws on 98,843 product records from 1688 and 36,576 suppliers, and order outcomes arrive late. The authors attribute the gap to humans to two losses in trace analysis: activity decay (operational coherence) and strategy drift, meaning policies that are never revised (strategic coherence).

Setup (self-reported): 8 LLMs, each under two frameworks (ReAct, Hermes), 3 runs each (48 runs); 3 human participants who had never worked in e-commerce, one run apiece; a rule-based baseline over 3 runs. Start: 2,000 yuan cash, 1,000 deposit, 50 listing slots. Metric: terminal net assets in thousand RMB.

- **Headline.** Qwen3.7-Max under Hermes averaged 59.46 against 217.61 for humans, the 27.3% in the abstract. The rule-based baseline scored 24.48, above several LLM configurations (DeepSeek-V4-Pro scored 6.56 under ReAct and 16.71 under Hermes, and Qwen3.7-Max scored 20.66 under ReAct).
- **Best per framework.** GPT-5.6 Sol led ReAct at 40.89; its Hermes score was 52.93.
- **Framework effect.** Taking the mean over all eight models, Hermes produced 53.3% higher net assets, 71.5% higher GMV and 71.2% more orders than ReAct. Seven of eight models gained (from 11.5% for Claude Opus 4.8 to 187.8% for Qwen3.7-Max); Kimi K2.6 was 4.1% lower.
- **Variance.** Across the 3 runs, the coefficient of variation was 3.3% for GPT-5.6 Sol under ReAct, 10.0% for Claude Opus 4.8 under Hermes, and 55.1% for the top configuration, Qwen3.7-Max under Hermes.
- **Activity.** The Sustained Window Rate, the smallest fraction of scheduled windows containing a tool call, taken over every rolling 30-day period, was 100% for humans, 10.6-99.4% for LLMs under ReAct and 17.8-66.1% under Hermes. One Kimi K2.6 Hermes run took no environment action in 355 of its last 523 decision windows after giving up on day 104.

## Limits

E-Commerce Bench: 5 episodes per model in one fixed world, which the authors flag as small; the simulator is synthetic with a fixed demand model; supplier wording is LLM-rendered, so it varies between runs; the authors assigned the model tiers; cost and latency are not scored; the paper says its evaluation cannot tell apart three possible reasons for the missing learning (evicted context, a memory store the agent ignores, no gradient within an episode); the extraction saw no human baseline and no comparison of the simulator with real sellers. The extraction notes the authors are the Qwen team, whose model leads the open-weight tier. The extraction read the appendices only by their contents list.

MerchantBench: 3 runs per configuration and 3 inexperienced humans, so no significance tests; one domain (1688 dropshipping, 10 categories) with simulated customer and supplier behaviour; each model summarizes its own context, so memory and model effects are confounded; the failure accounts come from representative traces, not controlled ablations; the frameworks differ in several ways (Hermes adds code execution, planning, memory and skills), so the authors credit no single component. With n=3 the extraction treats rankings as noisy.

## See Also
- [[TheAgentCompany]] — alternative-to (another simulated-business agent benchmark)
- [[Live Multi-Market Trading Benchmark]] — related (another long-horizon market simulation)
- [[Multi-Session Agent Benchmarks]] — related
- [[Eval Non-Determinism]] — related (MerchantBench's 3 runs and a 55.1% coefficient of variation)
