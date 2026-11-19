---
title: RL Training Frameworks for LLMs
tags: [llm, reinforcement-learning, comparison]
summary: "verl, OpenRLHF, and TRL are the three open-source backbones for RL on language models: verl for 70B+ reasoning runs, OpenRLHF for the broadest production use up to ~30B, and TRL for the flattest learning curve up to ~13B. Pick by model scale and algorithm, not popularity."
updated: 2026-11-19
sources:
  - data/raw/claude-docs/learn-ai-engineering/docs/research/2026-07-22_rl_landscape.md
  - data/raw/papers/2026-11-07-glm-5-team-2026-glm-5.md
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

## One reported post-training stack: GLM-5

The GLM-5 report (Zhipu AI and Tsinghua, a 744B-parameter MoE with 40B active) trains on the slime framework and describes post-training as a sequence of SFT, Reasoning RL, Agentic RL and General RL, followed by on-policy cross-stage distillation. Details it gives (self-reported):

- **Reasoning RL** is on-policy GRPO with the IcePop mismatch-masking variant and no KL term, with group size 32, batch size 32, beta of 2, and clip bounds of 0.2 (low) and 0.28 (high). Its masking function zeroes a token's contribution when the ratio between the training and rollout policies leaves the interval (1−eps_l, 1+eps_h).
- **Cross-stage distillation** is on-policy, group size 1 and batch size 1024, with the final SFT, Reasoning RL and General RL checkpoints as teachers.
- **Asynchronous Agent RL** decouples generation from training and names three algorithmic pieces: Token-in-Token-out (the trainer consumes the exact token stream the inference engine produced), double-sided importance-sampling masking and dropping of stale samples. The clip bounds, the staleness threshold tau and the sync interval K are not stated.
- **A failure it reports:** Reasoning RL collapsed within a few steps because the DSA indexer (k = 2048) used a top-k operator that was not deterministic, and the deterministic torch.topk fixed it; the finding is qualitative, with no curves or numbers.
- **Reward hacking in slide-generation RL** (hard truncation and spacing manipulation) was fixed by patching the renderer. Separately, the report credits slide-generation RL with lifting the share of pages that are strictly 16:9 from 40% to 92%.

## Limits

- Most GLM-5 scores in the report are vendor-run single runs without intervals.
- The report gives the pre-training token total as 27T in one place (the introduction) and 28.5T in others; the larger figure includes mid-training.
- It gives the layer count as 80 in the text, while Table 10 lists 3 dense, 75 MoE and 1 MTP layers.

## See Also
- [[Preference Optimization Algorithms]] — prerequisite-for (the algorithms these frameworks implement)
- [[Reinforcement Learning Foundations]] — prerequisite-for (the MDP and actor-critic background)
- [[Outcome vs Process Reward Models]] — related (the reward signal plugged into the training loop)
- [[RLHF Pipeline]] — instance-of (the three-stage pipeline these frameworks run end to end)
- [[Training-Agent Disaggregation]] — extends (wiring an existing multi-agent graph to a trainer via logical model names)
- [[Post-Training Reasoning Data Primer]] — related (data choices that decide what these trainers can learn)
- [[Agent Lightning v1.0 Harnessed Agentic RL]] — instance-of (proxy-captured traces turned into trainer input without changing the harness)
- [[Operational Reinforcement Learning]] — related (2020 operational guidance)
- [[GSPO Group Sequence Policy Optimization]] — related
