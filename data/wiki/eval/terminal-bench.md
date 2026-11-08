---
title: Terminal-Bench
tags: [eval, reference]
summary: "A benchmark of 89 manually verified command-line tasks (version 2.0) run in containers; across six agents and 16 models the best pair, Codex CLI with GPT-5.2, resolved under two-thirds of tasks (self-reported), and the same model scored differently under different scaffolds."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-07-merrill-2026-terminal-bench.md
---

# Terminal-Bench

Terminal-Bench (Merrill et al., arXiv 2601.11868, 2026) measures agent performance on difficult, realistic tasks with long horizons that run in a command line. A task is an instruction, a Docker image, outcome tests, a human-written oracle solution and a time limit, in the Harbor task format. Version 2.0 has 89 tasks.

## How the tasks were built

The authors crowdsourced 229 tasks from 93 contributors and 89 survived expert review, CI checks, model trial runs and an adversarial audit for exploits. The release includes Terminus 2, a scaffold the authors describe as neutral, with one tool, and 26 adapters that port other benchmarks into the format. The command to run it is `harbor run -d terminal-bench@2.0`.

## Results (self-reported)

Setup: Terminal-Bench 2.0 (89 tasks), six agents over 16 frontier models, 32,155 trials in total with every agent-model combination run five or more times; the Harbor harness on Daytona containers; reasoning effort left at its default; the metric is resolution rate with a 95% interval.

- Codex CLI with GPT-5.2 was the top pair, resolving under two-thirds of tasks; Terminus 2 with Claude Opus 4.5 was second and Terminus 2 with Gemini 3 Pro third. Kimi K2 Thinking in Terminus 2 was the best open-weight model.
- The scaffold changed results for one model: GPT-5 did much better inside Codex CLI than inside Terminus 2, and Opus 4.5 scored higher in Terminus 2 than in Claude Code, its vendor's own agent.
- The authors nonetheless conclude that model choice matters more than scaffold, citing a 52-point gain for Codex CLI from GPT-5-Nano to GPT-5.2 (62.9 against 11.5) and a 17-point gain for Gemini 2.5 Pro in Terminus 2 over OpenHands (32.6 against 15.7). The extraction notes these are point differences, not relative changes.
- Scores with each model's best harness nearly doubled from the time of Gemini 2.5 Pro to that of GPT-5.2 (between April and December 2025), and the authors expect the benchmark to saturate within a year.
- A run of the benchmark costs from about one to about a hundred dollars, depending on the model's price (read from a cost-against-performance plot). A trial is usually under 20 minutes but can take two hours and nearly 100M tokens.
- In Terminus 2 trials, average turns show essentially no correlation with success and average output tokens a weak negative one.
- Authors' difficulty predictions correlate positively with empirical difficulty (Easy: resolved by at least 66.7% of selected frontier models; Hard: under 33.3%).

## Failure analysis

Failed Terminus 2 trials (two per model per task) were labelled by a GPT-5 judge at high reasoning effort, which agreed with human labels on 120 traces. Command-level failures were scored with GPT-5 at medium reasoning, which agreed 92.4% with the majority of three annotators on 66 pairs. The most frequent command failure was an executable that was not installed or not on the path, among 3,800 sampled failures classified at 82.0% agreement with 50 author annotations. The taxonomy simplifies MAST into Execution, Coherence and Verification.

## Limits

Because agents are online they could find public oracle solutions, though the authors report never seeing it in tens of thousands of trajectories. All tasks are public, the canary string is largely symbolic and there is no private test set. Internet access, package changes and machine variation leave flaky results. Some tasks may still fail verification criteria, with no estimate of the effect. Human completion times are author estimates, with no measured human baseline. Only default reasoning effort was run, the interval method is not stated and pass@k is not reported. The failure analysis covers only failed Terminus 2 trials, and its judge, GPT-5, is itself one of the benchmarked models. Models end at December 2025.

## See Also
- [[CLI Agent Failure Timeline]] — related (analysis of failed Terminal-Bench runs)
- [[Repository-Level Coding Benchmarks]] — related (LongCLI-Bench, another long command-line benchmark)
- [[Holistic Agent Leaderboard (HAL)]] — related (scaffold and cost effects)
- [[Eval Contamination Defenses]] — related (canary string, public tasks)
