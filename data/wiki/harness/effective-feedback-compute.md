---
title: Effective Feedback Compute
tags: [harness, concept]
summary: A proposed predictor of agent-harness success that counts feedback events by informativeness, validity, non-redundancy and retention rather than raw tokens or cost; evidence is largely synthetic.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-zhang-2026-scaling-laws-agent-harnesses-effective.md
---

# Effective Feedback Compute

Effective Feedback Compute (EFC, Zhang et al., a June 2026 preprint) is a quantity the authors propose for predicting harness success. The authors argue that spend measured raw at test time, whether tokens, tool calls, wall time or cost, fails to predict success. EFC scores each feedback event differently, as a product of four factors (informativeness, validity, non-redundancy and retention), scaled by a constant of 10. Divided by a task-demand term, it feeds a power-law fit to failure rate. A companion layer, EFC-Adapter, orders, keeps and halts feedback actions according to EFC per unit of raw cost.

## Results

Numbers are the authors' (self-reported), averaged over three small models, namely DeepSeek-V4-Flash, gpt-5.4-nano and Claude-Haiku-4.5. Run counts and task counts are not given.

- On the controlled synthetic tasks (Needle Lookup, State Tracking and Rule Filter), R2 reaches 0.99 for oracle EFC divided by task demand, 0.95 for oracle and estimated EFC, 0.68 for the SAS baseline, 0.27 for the best raw-token predictor and 0.01 for raw cost.
- Matched-budget intervention, same raw cost and tool calls: changing nothing but feedback quality moves success from 0.27 to 0.90.
- Real traces pooled from HumanEval, Terminal-Bench 2.0 and SWE-bench Verified: R2 0.93 for the demand-normalised form, 0.44 for SAS, and slightly negative for raw baselines. A prospective holdout with a frozen protocol gives 0.89 against 0.28 for SAS.
- Module ablation: the largest efficiency gains come from router quality (+0.28), then verifier strength (+0.22), then memory fidelity (+0.20). Losses come from state pressure (-0.05), tool entropy (-0.11) and observation noise (-0.17).
- Applying EFC-Adapter to four harnesses (mini-SWE-agent, AHE, RTV, PDR) over the three models, the mean pass rate goes from 61.2% to 68.2% and the mean raw cost from 213.8 to 85.1, under identical model, tools and budget caps.
- Slice results are mixed: closed-loop harnesses lead on HumanEval, all are low on Terminal-Bench, and simple harnesses lead on SWE-bench, so the authors read efficiency as a harness-task interaction.

## Limits

- The core evidence is synthetic; the extraction notes that harnesses H0 to H6 are partly simulated roles and "cost" is a synthetic weighted unit.
- For real benchmarks, the estimated EFC relies on gates and constants that the authors set by hand.
- Per-benchmark pass rates, task counts and repeat counts are not given.
- R2 values come from fitting 2 to 3 parameters to failure rates aggregated by group, so they reveal little about predicting individual tasks.
- Small, cheap models only; no test of a verifier stronger than the executor, and no ablation of adapter parts. The paper has no limitations section.

## See Also

- [[Harness Anatomy]] — prerequisite-for
- [[Budget Tracker and BATS]] — related (budget-aware tool use)
- [[Agentic Harness Engineering]] — related (one of the harnesses the adapter was tried on)
- [[VeriHarness Agentic Verification]] — related
