---
title: Chain-of-Agents AFM Distillation
tags: [foundations, pattern]
summary: Chain-of-Agents distils trajectories of a multi-agent system into one agent foundation model with supervised fine-tuning and then DAPO reinforcement learning, reporting 59.8 on AIME25 and 55.3 on GAIA for 32B models (self-reported, industry team, small-sample evaluations).
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-li-2025-chain-agents.md
---

# Chain-of-Agents AFM Distillation

The OPPO AI Agent Team (arXiv 2508.13167, August 2025 preprint) trains agent foundation models (AFM)
that internally play planner, reflector, verifier and tool agents in one trajectory, instead of
running separate agents.

## Pipeline

1. Collect multi-agent trajectories from the OAgents system using a think, plan, tools, observation,
   reflection, answer layout.
2. Filter for complexity (fewer than 5 interactions dropped), quality, reflection enrichment and
   error-correction upsampling; mask observation tokens in the SFT loss.
3. Run DAPO (through VeRL) on queries that a 72B model without tools solves in at most 0.3 of 32 tries;
   code queries solved 8 of 8 times by a 7B AFM are dropped.
4. Rewards: web agents use a binary LLM-judge with no format reward, since SFT fixes format; code agents
   use correctness times format. Data sizes: 16,433 web SFT trajectories; RL on 169,615 multi-hop QA,
   10,427 web and 47,560 code queries.

## Results (self-reported)

- Code agent, 32B (Qwen2.5-Coder-32B-Instruct, avg@16 on AIME and AMC): 59.8 on AIME25 against 49.3 for ReTool-32B; average 78.0 against 74.4.
  Average score went 36.6 (base), 60.0 (SFT), 78.0 (RL); at 7B 21.5, 43.5, 64.3.
- Web agent, 32B, pass@1 gave 55.3 on GAIA, 63.0 on WebWalker, 11.1 on BrowseComp and 18.0 on HLE, judged by Qwen2.5-72B, which
  also gives the training reward.
- Multi-hop QA, 7B-instruct: average 41.7 after SFT and 45.5 after RL.
- Efficiency: 84.6% fewer tokens than multi-agent systems, stated in the introduction and
  based on 10 sampled GAIA instances; the figure values are garbled in the extraction.
- Pass@3 is an oracle selector (GAIA 55.3 to 69.9); best-of-3 with the 72B judge gave 57.3.

## Limits

- The extraction notes there is no ablation against plain tool-integrated reasoning on the same data,
  so the paradigm effect is not isolated, and that the teacher bounds the data. It also notes AIME sets have 30 problems each and that the paper has no limitations section,
  reward-hacking or failure analysis; prompts are not deduplicated between SFT and RL sets, which the
  authors say they handle by relying on DAPO's filtering.
- Internal inconsistencies noted by the extraction: the text gives about 47k code traces while the data
  table has 59,929; BrowseComp 11.1 in one table and 11.0 in another; one baseline's GAIA score is attributed
  inconsistently; unlabelled duplicate rows in the code table; backbones mix base and instruct.

## See Also
- [[Post-Training for Agents]] — prerequisite-for
- [[AgentArk Multi-Agent Distillation]] — alternative-to
- [[Harness Orchestration]] — related
- [[Reinforcement-Learned Teachers]] — related
- [[DualDistill Agentic-R1]] — related
