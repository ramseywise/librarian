---
title: Live Multi-Market Trading Benchmark
tags: [eval, reference]
summary: "Qian et al.'s live benchmark runs four trading-agent designs on five LLM backbones across two stocks and two cryptocurrencies from August to September 2025, one BUY/SELL/HOLD decision a day; the best cell (40.83% on TSLA) trails buy-and-hold (46.88%), each cell is one run, and the authors argue architecture matters more than backbone from min-max bands, a claim weakened by identical rows in their table (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-05-qian-2025-when-agents-trade.md
---

# Live Multi-Market Trading Benchmark

Qian et al. (arXiv 2510.11695, 2025, "When Agents Trade") test agents on live market data
instead of a historical backtest. The window runs from 1 August to 30 September 2025 after a
warm-up from 1 May to 31 July. Agents trade a simulated portfolio on TSLA, BMRN, BTC and ETH,
making one BUY, SELL or HOLD decision a day at a fixed time. Four agent designs are crossed
with five backbones, plus a majority-vote row. The authors contrast this with DeepFund, a prior
live benchmark covering 24 days and 5 US stocks.

## Results (self-reported)

- **Best cell.** InvestorAgent with GPT-4.1 on TSLA: 40.83% cumulative return and Sharpe 6.47
  (one run over two months; risk-free rate set to 0, annualised on 252 days). Buy and Hold on TSLA scored
  46.88% and Sharpe 6.00.
- **Backbone swing.** TradeAgent's TSLA return ran from -38.72% with GPT-4.1 up to 21.91%
  with Gemini-2.0-Flash.
- **No winner.** The authors report no single model or agent leads on every asset.
- **Architecture against backbone.** The authors argue that changing the backbone inside a fixed
  agent changes profit modestly while changing the agent design with the backbone fixed changes it a
  lot. The evidence is the min-max bands in one figure, with no variance decomposition.
- **News summaries.** Two annotators checked summaries written by GPT-5-nano on 20 sampled days
  per asset class: they agreed on 87.5% of date-accuracy checks, 92.5% of coverage checks and all bias checks.

## Limits

The paper never tests live against backtest, shows no contamination measurement or model
cutoff dates, and compares nothing against static benchmarks. Each cell comes from a single run at
temperature 0.5; the shading shows spread across backbones or agents, not seeds. There is no
significance test or random-policy baseline, fees and slippage are excluded, and no real money
is traded. The extraction found that the text's claim agents consistently beat buy-and-hold
contradicts the table (no agent beats it on TSLA, most BTC cells are negative). Every
HedgeFundAgent row matches the others to two decimals on every asset, which the authors read as
robustness but which may mean the backbone did not affect its output, weakening the
architecture claim. Some cells reflect not trading: one DeepFundAgent cell is all zeros, and
another has a high Sharpe ratio from 1.08% volatility. There is no limitations section.

## See Also
- [[Eval Contamination Defenses]] — related (live data as a way around leakage, untested here)
- [[Eval Error Bars and Sample Size]] — related (single runs, no intervals)
- [[Best-of-k Headline Inflation]] — related
