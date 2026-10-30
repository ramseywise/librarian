---
title: DAPO
tags: [foundations, llm, concept]
summary: "Four changes to PPO/GRPO-style RL — Clip-Higher, token-level loss, dynamic sampling and overlong reward shaping — each aimed at stopping the policy from collapsing early onto a single strategy; the reported state-of-the-art recipe for verifiable-reward math RL."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/generative-ai--05-RL--post-training-for-agents.md
  - data/raw/repos/learn-ai-engineering/generative-ai--05-RL--preference-optimization.md
  - data/raw/repos/learn-ai-engineering/generative-ai--05-RL--rlhf-pipeline.md
---

# DAPO

DAPO (Yu et al. 2025) keeps GRPO's group-relative advantage (see [[Preference
Optimization Algorithms]]) and changes four things. All four target the same failure:
**premature collapse onto one strategy** before the policy has explored.

| Change | Mechanism | Problem it addresses |
|---|---|---|
| **Clip-Higher** | Raises the upper bound of the PPO clip range | The symmetric clip stops low-probability but clearly better paths from gaining mass, which shrinks exploration |
| **Token-level loss** | Normalises the loss over all tokens in the batch, not per response | Per-response averaging dilutes each token of a long response by 1/\|oᵢ\|, so long reasoning chains are under-trained |
| **Dynamic sampling** | Spends samples on prompts with roughly 20–80% success; drops all-pass and all-fail groups | Uniform groups have zero variance, hence zero advantage and no gradient |
| **Overlong reward shaping** | Soft penalty for length that does not improve the answer | Verbosity drift, and the long-tail rollouts that idle the GPUs |

DAPO also drops the KL penalty against the reference policy, as does Open-Reasoner-Zero,
whereas the R1-Zero GRPO setup keeps it ([[RLHF Pipeline]] explains what the reverse-KL
anchor does).

A robot-policy RL run used similar levers — dynamic sampling, an asymmetric clip range of
[0.8, 1.28] and sampling temperature 1.6 — and reached about 30% within 300 steps.

Dynamic sampling only reallocates budget inside an existing task pool. Two alternatives
change more: [[RLVP — Verifiable Path Penalties]] restores variance to uniform groups
instead of discarding them, and agentic self-instruct changes the task distribution itself
([[Post-Training for Agents]]).

## See Also
- [[Preference Optimization Algorithms]] — extends (GRPO with four anti-collapse changes)
- [[Post-Training for Agents]] — instance-of (the RL-for-tool-calling recipe)
- [[RLVP — Verifiable Path Penalties]] — alternative-to (restore variance rather than drop the group)
- [[RL Training Frameworks for LLMs]] — prerequisite-for (the backbones that ship the DAPO recipe)
