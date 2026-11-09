---
title: Price Reversal in Reasoning-Model Costs
tags: [eval, concept]
summary: "Chen et al. measured the total cost of 8 reasoning models on 12 tasks and found that in 106 of 336 pairwise comparisons (31.5%, self-reported) the model with the lower listed per-token price cost more; the authors attribute over 95% of the gap on reversed single-turn pairs to thinking tokens, and show per-query cost for one model and query varies up to 9.7 times."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-06-chen-2026-price-reversal-phenomenon.md
---

# Price Reversal in Reasoning-Model Costs

Chen et al. (arXiv 2603.23971, 2026) define **listed price** as a model's input price plus its
output price per million tokens, and ask whether it predicts what a workload costs. They call
the case where the lower-listed-price model has the higher total cost a **price reversal**.
Their study covers eight models (GPT-5.4 and its Mini, Gemini 3.1 Pro and 3 Flash, Claude Opus
4.7 and Haiku 4.5, plus Kimi K2.6 and MiniMax M2.7) on twelve tasks, nine single-turn and three agentic,
using 1 May 2026 prices; only cost is compared, not accuracy.

## Results (self-reported)

- **Frequency.** 106 of 336 pairwise comparisons (28 model pairs on 12 tasks) reversed. The
  abstract rounds this to 32%; 106/336 is 31.5%.
- **Headline example.** Gemini 3 Flash carries a listed price of $3.50 whereas GPT-5.4's is $17.50, yet summed
  over all 12 tasks it cost $705 against GPT-5.4's $509, which is 38% more.
- **Task dependence.** The reversal rate ranged from 11% (ArenaHard) to 57% (MMLU-Pro). On
  MMLU-Pro Gemini 3 Flash cost $219 against $44 for GPT-5.4, though it is the second cheapest
  by listed price. On Cybench, Kimi K2.6 carries a listed price 72% below GPT-5.4's but cost about
  twice as much.
- **Attribution.** A Shapley-value split of each cost gap over eight cost factors (turns, fresh
  input, output, cached and thinking tokens, three prices) credited thinking tokens with more than 95%
  of the cost gap for single-turn pairs that reversed. For Kimi K2.6 against GPT-5.4 on Cybench,
  agent turns accounted for over 80%. One MMLU-Pro query took Gemini 3 Flash over 60,000
  thinking tokens against 25 for GPT-5.4; this is a single query, not an average.
- **Cost is noisy.** Repeated rollouts of one fixed model and query varied by up to 9.7 times
  between cheapest and dearest run, with the spread within a query (coefficient of variation) often above
  0.3 (AIME and Terminal-Bench 2.0, three models). The authors say individual reversal verdicts can
  flip between runs.
- **Mean against quantiles.** Pooled over tasks, reversal is 31.5% when comparing mean cost but about 39 to 40%
  at the 15th to 40th cost percentiles (peak 39.6% at the 40th), falling to 25.0% at the 99th.
- **Difficulty.** The authors report much less reversal on easy questions (6 to 8 of 8 models
  correct) than on hard ones (0 to 2 correct). For agentic tasks the appendix states that
  reversed pairs cost 3 to 10 times more on incorrect runs against within 2 times for correct
  runs; the supporting diagnostics are only in the authors' code repository.

## Limits

Prices are a single snapshot (1 May 2026) and each model ran at one reasoning setting, so
effort against cost is not studied. Cost is not tied to quality; the authors argue adding
quality would strengthen the finding but do not test it, and no cost-per-correct-answer is
computed. The base case is one run per task, which the paper's own noise result makes
uncertain, and the 32% has no confidence interval. The Shapley attribution accounts for a mean gap and not for tail risk. Agentic scaffolds differ in thinking-token and turn caps. Several datasets are
subsets (MMLU-Pro 3,000, HLE 500, SimpleQA 500, AIME 60 tasks; Cybench 39, Terminal-Bench 89,
GAIA 165). HLE, SimpleQA and ArenaHard are judged by Gemini 3.1 Pro, one of the evaluated
models. The abstract's "28x" and "900%" figures are not found in the body, so they are
omitted here. Code and data were described as forthcoming.

## See Also
- [[Holistic Agent Leaderboard (HAL)]] — related (cost-accuracy frontiers; this paper does not cite it)
- [[Eval Non-Determinism]] — related (cost per query also varies between runs)
- [[Eval Metric Interpretation Pitfalls]] — related
- [[Overthinking and Concise Reasoning]] — related
- [[Inverse Scaling in Test-Time Compute]] — related
- [[Cost-of-Pass and Efficient Agent Design]] — related
