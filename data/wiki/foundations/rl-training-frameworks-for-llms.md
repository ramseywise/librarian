---
title: RL Training Frameworks for LLMs
tags: [foundations, llm, comparison]
summary: "verl, OpenRLHF, and TRL are the three open-source backbones for RL on language models: verl for 70B+ reasoning runs, OpenRLHF for the broadest production use up to ~30B, and TRL for the flattest learning curve up to ~13B. Pick by model scale and algorithm, not popularity."
updated: 2026-10-30
sources:
  - data/raw/claude-docs/learn-ai-engineering/docs/research/2026-07-22_rl_landscape.md
---

# RL Training Frameworks for LLMs

The algorithms in [[Preference Optimization Algorithms]] are the easy half of an RL
fine-tuning project. The other half is the distributed system that generates rollouts,
scores them, and updates the policy. All three backbones below are open source and support
PPO and DPO. They differ in scale ceiling, setup cost, and which newer algorithms they ship.

| | **verl** | **OpenRLHF** | **TRL** |
|---|---|---|---|
| Scale ceiling | Best: 70B+ across many GPUs | ~30B on FSDP | ~13B practical; ~30B with FSDP via Accelerate |
| Orchestration | Ray; steepest setup | Ray for distributed rollout; well documented | Minimal config; Hugging Face Hub native |
| Algorithms | PPO, GRPO, DAPO, advanced rollout strategies | PPO, DPO, DAPO, REINFORCE++, token-level importance sampling, VLM support | PPO, DPO, SFT, structured output |
| Position | Reference backbone for state-of-the-art reasoning runs (the DAPO recipe was trained on it) | Widest industry and research adoption | Lowest barrier to a first run |

## Selection by need

| Need | Best fit | Backup |
|---|---|---|
| Math reasoning at competition level | verl (DAPO recipe) | OpenRLHF (DAPO) |
| DPO preference tuning | TRL or OpenRLHF | — |
| Agentic, long-horizon RL | OpenRLHF (REINFORCE++) | verl (custom) |
| Quick experiment | TRL | — |
| Production alignment | OpenRLHF | verl |

The practical rule is the **~30B line**. Below it, TRL (with FSDP) is usually enough and
costs the least to set up. Above it, a Ray-based backbone is required, because rollout
generation has to be distributed separately from training.

**Confidence:** the comparison itself is rated high in the source (multiple 2026
analyses). The claim that verl is the de facto backbone is rated medium-high, since the
landscape moves quickly.

## See Also
- [[Preference Optimization Algorithms]] — prerequisite-for (the algorithms these frameworks implement)
- [[Reinforcement Learning Foundations]] — prerequisite-for (the MDP and actor-critic background)
- [[Outcome vs Process Reward Models]] — related (the reward signal plugged into the training loop)
- [[RLHF Pipeline]] — instance-of (the three-stage pipeline these frameworks run end to end)
- [[Training-Agent Disaggregation]] — extends (wiring an existing multi-agent graph to a trainer via logical model names)
