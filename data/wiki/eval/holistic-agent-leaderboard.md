---
title: Holistic Agent Leaderboard (HAL)
tags: [eval, reference]
summary: "HAL is a shared harness that ran 21,730 agent rollouts (9 models, 9 benchmarks, about $40,000, self-reported), mostly single runs; it found higher reasoning effort gave equal or lower accuracy in 21 of 36 pairs, the costliest model on the cost-accuracy frontier in 1 of 9 benchmarks, and log analysis surfacing leakage, shortcuts and unsafe actions."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-05-kapoor-2025-holistic-agent-leaderboard.md
  - data/raw/papers/2026-11-05-yehudai-2025-survey-evaluation-llm-based-agents.md
---

# Holistic Agent Leaderboard (HAL)

Kapoor et al. (arXiv 2510.11977, 2025) built HAL as common infrastructure for running agent
benchmarks: a scaffold is any function from input to output, runs are logged, and results are
reported on three axes (model, scaffold, benchmark) plus cost. The first sweep covered coding,
web navigation, science and customer-service benchmarks. Prices are those of 24 September 2025.

## Scale

The sweep totals 21,730 rollouts over 9 models and 9 benchmarks, costing about $40,000 and
producing 2.5B tokens of logs (self-reported).
The analysis uses 142 model-scaffold-benchmark combinations drawn from 186 runs.

## Results (self-reported, mostly single runs)

- **Reasoning effort.** In 21 of 36 model-scaffold-benchmark pairs, higher effort gave equal or
  lower accuracy. The pairs were Opus 4.1, Sonnet 4 and Sonnet 3.7 (thinking off against a high setting with a 4,096-token thinking budget) and o4-mini (low effort
  against high), with scaffold and benchmark held fixed. The
  abstract's "majority of runs" wording is looser than the body; the body count is used here.
- **Cost-accuracy frontier.** The most expensive model sat on the Pareto frontier in only 1 of 9
  benchmarks, and under a third of tested models were on the frontier for any benchmark.
  Gemini 2.0 Flash was on it in 7 of 9, GPT-5 in 4 of 9 and o4-mini (low) in 4 of 9.
- **Scaffold changes cost.** On Online Mind2Web (300 tasks), SeeAct with GPT-5 Medium cost $171
  and Browser-Use with Claude Sonnet 4 cost $1,577, about 9 times as much, for accuracies two
  points apart.
- **Task-specific against generalist scaffolds.** On CORE-Bench the task-specific CORE-Agent beat
  the generalist scaffold in 9 of 12 runs, and on SWE-bench Verified Mini in 11 of 12. The
  generalist scaffolds were cheaper in 20 of 24 model comparisons.
- **Benchmarks differ in price.** ScienceAgentBench averaged $13 per evaluation and Online
  Mind2Web over $450; Opus 4.1 was not run on the latter, at an estimated $20,000.

## What log inspection found

The authors had GPT-5 Medium, through the Docent tool, apply six rubrics covering
instruction violations, tool-use failures, self-correction, verification, environmental
barriers and shortcuts or gaming to 1,634 transcripts from 36 model-scaffold pairs. Against human labels, precision
was 0.87 for instruction following on AssistantBench (n=49), 1.00 for verification on
CORE-Bench (n=31) and 0.94 for instruction following on TAU-bench (n=36); recall was not measured.

- The few-shot agent shipped in one official benchmark repository contained actual benchmark
  examples; the authors found this after about $1,000 of runs and excluded it.
- Agents located gold answers on HuggingFace or arXiv in what the authors count as eight cases,
  and wrote fixed values into code so tests passed on CORE-Bench and SciCode.
- On TAU-bench, unsafe actions included charging the wrong credit card and charging $2,010
  against a $1,000 budget.
- AssistantBench's abstention instruction conflicts with the Browser-Use scaffold's, so
  abstentions that were intended get graded as answers.

## Limits

Most results are single runs with no noise estimate, so the 21-of-36 count and frontier
membership are unqualified by variance. Several subsets are small: 50 tasks each for SWE-bench Verified Mini and TAU-bench Airline, 33
of 214 for AssistantBench, 45 for CORE-Bench Hard. The log findings are
correlations; the authors say they cannot tell whether fixing the failures would produce
success. Only one rubric per benchmark was checked against human labels, and no prevalence rate for
shortcuts is given. SWE-Agent costs ignore cache hits, effort levels are not comparable across providers and
latency is not reported. The extraction found the "eight cases" shown as three in the appendix
table, two without the agent using the answer, and found the "consistently outperform"
claim for task-specific scaffolds at odds with a table where the generalist leads on GAIA
(64.8%). Prices and models are from September 2025.

## Related survey

Yehudai et al. (arXiv 2503.16416, a survey, no experiments) list cost as a gap in two senses:
benchmarks ignore what the agent costs, and the frameworks do not count what it costs to
run the evaluation itself over many traces with expensive judges. They also say most benchmarks
conflate the backbone model with its harness and ask for protocols that vary each separately.

## See Also
- [[Price Reversal in Reasoning-Model Costs]] — related (listed price versus measured cost)
- [[Best-of-k Headline Inflation]] — related
- [[Eval Non-Determinism]] — related (single runs against repeated trials)
- [[Trajectory Over Outcome]] — related (log inspection grades the path)
- [[Eval Contamination Defenses]] — related (leakage and gold-answer lookup)
- [[MLE-bench]] — related (scaffold moved scores there too)
