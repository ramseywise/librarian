---
title: Sakana Fugu Learned Orchestration
tags: [graph, concept]
summary: "Sakana's Fugu trains a small orchestrator over a pool of three frontier models, either to pick one worker per input or (Fugu-Ultra) to write a workflow with an access list per step; the report claims best results on SWE-Bench Pro and Terminal Bench 2.1 but runs no ablations (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-06-tang-2026-sakana-fugu-technical-report.md
---

# Sakana Fugu Learned Orchestration

Vendor technical report from Sakana AI's Fugu team (arXiv 2606.21228, 2026), not peer reviewed. Two variants draw on one worker pool: GPT-5.5, Claude-Opus-4.8 and Gemini-3.1-Pro.

## Mechanism

- **Fugu (single selection).** A small head reads the orchestrator's hidden state at an early token and emits a logit for each worker, so nothing is decoded autoregressively and no roles are assigned. The trainable parts are the head and scale factors on the singular values of a few selected matrices. Stage one is supervised on single-step verifiable tasks against a softmax over each worker's mean reward; stage two uses sep-CMA-ES on multi-turn trajectories gathered from Claude Code, Codex and OpenCode, rewarded 0 or 1 at the end, which the report finds steadier than supervised fine-tuning in that setting.
- **Fugu-Ultra (workflow writer).** For each query the orchestrator writes a natural-language workflow of at most 5 steps; each step has a subtask, a worker id and an access list of the earlier outputs that worker may see. Reward is 0 if the workflow cannot be parsed, 0.5 if it is well formed but the answer is wrong, 1 if correct; GRPO without a KL penalty trains it. The orchestrator may also serve as a worker.
- **Two memory rules for multi-agent function calling.** An agent sees its own tool trajectory only, plus what the access list gives it; without this, the report describes "orchestration collapse", in which whichever agent first touches the environment fixes the path for the others. Tool calls from earlier workflows remain visible in later ones to avoid repeating calls.

## Results (self-reported)

- Fugu-Ultra (harnesses: Mini-SWE-agent and Terminus 2, both minimal; provider-reported baselines for the most part): SWE-Bench Pro 73.7 against 69.2 for Opus 4.8 and 58.6 for GPT-5.5; Terminal Bench 2.1 82.1 against 78.2 for GPT-5.5. Single-selection Fugu scored 80.2 on Terminal Bench 2.1 and 92.9 on LiveCodeBench (best baseline 88.5), but 59.0 on SWE-Bench Pro.
- Routing varies by domain according to the report: GPT-5.5 dominates Terminal Bench orchestration, Gemini dominates GPQA-Diamond, and Ultra spreads across three agents on HLE. The shown topologies (tree with a per-query aggregator, build-and-debug, lead plus clean-slate second opinion, specialist handoff) are anecdotes from single trajectories, with no per-topology frequency or win rate.
- Where it does not win: SciCode 58.7 for Ultra against 58.9 for Gemini; MRCRv2 93.6 against 94.8 for GPT-5.5; Long Context Reasoning 73.3 against 74.3; tau-3 Banking 20.6, equal to Opus and GPT. AutoResearch (123 experiments, about 14 h per seed, one H100, 3 seeds): 0.9774 mean bits per byte against 0.9781 for the best single model, within about one standard deviation.
- A reading-order task built by the authors (25 expert pages, same beam search): Ultra 0.776 normalised edit distance against 0.642 for the best frontier model; one frontier model did not complete.

## Limits

- No ablations: isolation against shared context, orchestrator against best-of-N or fixed debate, topology against the same models run independently, SFT against ES, and the reward design are all untested. The report gives no cost, latency or token figures for Ultra, and its Fugu latency claim is not quantified.
- Baselines are mostly provider-reported or taken from leaderboards, not rerun under one harness. The pool is three closed models, the orchestrator is not named, and the benchmarks have neither seeds nor error bars. The claim of "no pre-defined topology" is not compared with fixed topologies.
- Internal inconsistency: the chart labels in Figure 1 for HLE (Ultra, Fugu and a comparison model read 50.0, 48.5 and 53.3 respectively) disagree with the Table 1 HLE row (Fugu 47.2, Opus 49.8); the extraction could not tell which is current.
- "State of the art" is claimed against publicly accessible models only. Model names and benchmark versions are mid-2026.

## See Also
- [[Conductor Learned Orchestration]] — prerequisite-for (Fugu-Ultra builds on the Conductor RL workflow orchestrator)
- [[Multi-Agent Topology Patterns]] — prerequisite-for
- [[Self-MoA Single-Model Aggregation]] — alternative-to (fixed-aggregator mixing)
- [[Archon Inference-Time Architecture Search]] — related
