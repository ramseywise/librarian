---
title: AgentSkiller Cross-Domain Trajectory Synthesis
tags: [llm, agent-training, pattern]
summary: "An 18-step pipeline that synthesises tool-use environments (SQL databases, MCP servers, tool graphs) and cross-domain tasks verified by execution and an all-or-nothing rollout judge; SFT on about 11K trajectories reports strong tau2-bench results for a 14B model (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-06-sun-2026-agentskiller.md
---

# AgentSkiller Cross-Domain Trajectory Synthesis

AgentSkiller (Sun et al., February 2026) synthesises agent training data end to end: environments, tasks and trajectories. It runs as an 18-step LangGraph DAG. Two models split the labour: GPT-5.2 handles the semantic steps, while Claude Opus writes the SQL, MCP servers and unit tests. When code fails, a Block Editor repairs it, with at most K=5 attempts. 15 seed domains are expanded to N=300.

## Mechanism

- Tasks come from enumerating simple paths between a minimum and maximum length in a tool graph (NetworkX). Gold tasks get tied to database rows in one of two ways: single-domain tasks by sampling under constraints, cross-domain tasks by being created and then validated, with the database backed up and rolled back.
- A persona simulator writes a deliberately vague query about one pressing pain point and withholds some user knowledge, so the agent has to ask clarifying questions. Rollouts pit an LLM agent against an LLM user simulator on mock MCP servers.
- Verification at three levels: unit tests per MCP server; execution-based filtering, where the gold tool path is run against the grounded database and each failure is classed as a policy violation, invalid entity data or a server bug; and a rollout evaluator, whose final score multiplies a binary action score, an environment score and an LLM-judge score. Environment success requires the golden database diff to be contained in the agent's diff. Cross-domain tasks bypass the filter, having been validated when created.
- Of a 13,649-sample rollout pool, 4,299 (about 31.5%) were excluded under the all-or-nothing rule; the top exclusion reasons were S1 confirmation omission (30.5% of 9,120 issues) and R4 unnecessary tool calls (22.4%).

## Reported results (self-reported)

Setup: SFT only (verl, 128k sequence length, lr 1e-5) on AgentSkiller-11K, a mix of single-domain (5,941) and cross-domain (5,581) samples, with Qwen3-4B, 8B and 14B. GPT-5.2 plays the user simulator in tau-bench and tau2-bench. Scores are single runs without seeds.

- AgentSkiller-14B: 79.1 overall on tau2-bench, split as Retail 77.2, Airline 56.0 and Telecom 91.2; 67.2 on tau-bench; 78.0 on ACEBench-Agent. On tau2 the paper sets this beside GPT-o3 (68.4) and Claude-Sonnet-4 (56.8); GPT-5-think is still ahead on tau2 (84.2) and, narrowly, on tau-bench (67.8). Base Qwen3-14B scores 36.1 on tau2.
- AgentSkiller-4B scores 66.0 on tau2 against 41.0 for xLAM-2-70B and 58.6 for Qwen3-Thinking-235B. Competing data-synthesis baselines at 14B score lower on tau2: ToolACE manages only 31.6, EnvScaler 42.3, ToolMind 47.5 and MUA 53.6.
- The one pipeline ablation, single-domain data versus the full mix at 14B lifts tau2 from 71.2 to 79.1 and tau-bench from 45.4 to 67.2, while ACEBench-Agent does not move from 78.0. The 4B model behaves differently there, falling from 64.0 to 54.0, and the paper gives no explanation.
- For the 14B model on tau2-bench, accuracy falls with tool-call count on Retail (Pearson -0.688) and Airline (-0.566) but not significantly on Telecom (+0.300).

## Limits

- No limitations section. The paper does not check for contamination against tau-bench, tau2-bench or ACEBench, and the synthetic domains share the benchmarks' retail/airline/telecom form. No verification-filter, persona, policy-generation or unit-test ablation.
- SFT only, despite the POMDP and reward framing; the rollout agent that generates trajectories is not named, so teacher strength is unquantified.
- Single runs; small Airline subsets make differences of a few points likely noise. Baselines mix retrained and released checkpoints, so the comparison does not control for recipe. "Scaling law" claims rest on three sizes of one family.
- Sample counts disagree across the paper: about 11,522 in the text, N=11,763 for the cross-domain subset in Section 4.1, 1,887 excluded out of 6,906 plus 6,773 in a figure, and subtracting 4,299 from 13,649 leaves 9,350 rather than 11.5K. The counts cannot be relied on.
- The extraction's Telecom comparison of the single-domain and full sets at 14B is garbled, so no Telecom ablation number is given here.
- The appendix prompts were only skimmed.

## See Also
- [[AgentScaler Environment Scaling]] — alternative-to
- [[APIGen]] — prerequisite-for
- [[Post-Training for Agents]] — prerequisite-for
- [[AgenticQwen Dual Data Flywheels]] — related
- [[AgentTuning and AgentInstruct]] — related
