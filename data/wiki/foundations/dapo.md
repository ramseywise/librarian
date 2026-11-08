---
title: DAPO
tags: [foundations, llm, concept]
summary: "Four changes to PPO/GRPO-style RL — Clip-Higher, token-level loss, dynamic sampling and overlong reward shaping — each aimed at stopping the policy from collapsing early onto a single strategy; the reported state-of-the-art recipe for verifiable-reward math RL."
updated: 2026-11-08
sources:
  - data/raw/repos/learn-ai-engineering/generative-ai--05-RL--post-training-for-agents.md
  - data/raw/repos/learn-ai-engineering/generative-ai--05-RL--preference-optimization.md
  - data/raw/repos/learn-ai-engineering/generative-ai--05-RL--rlhf-pipeline.md
  - data/raw/papers/2026-11-06-liu-2025-part-i.md
---

# DAPO

DAPO (Yu et al. 2025) keeps GRPO's group-relative advantage (see
[[Preference Optimization Algorithms]]) and changes four things. All four target the same failure:
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

## Lite PPO: which tricks matter, by setup (Liu et al.)

Liu et al. (Alibaba ROLL team, arXiv 2508.08221, preprint) ran one-seed ablations of RL tricks on Qwen3-4B and 8B, base and aligned, math only, with a REINFORCE advantage, no KL term, 1024 rollouts per step (128 prompts times 8), 8192-token responses and 5,000-problem Easy, Medium and Hard sets (self-reported setup). Results are read from smoothed curves; the paper gives no results table, and the extraction reports no plotted values.

- **Std in the advantage:** a small group std in the denominator inflates gradients when rewards are concentrated (easy data), which can destabilise training; on hard data it matters little. Group mean with batch-level std beat group mean with group std.
- **Clip-Higher** (upper clip 0.28 against 0.2): helped aligned models, did nothing or hurt base models, whose policy clipping rate was about 0.003 (self-reported). Most tokens in the base model sat in the top probability bin (91.7% and 88.2% in one reading of Fig 9, which is the extractor's inference from number order; self-reported). The best upper bound varied with size: 4B improved up to 0.32, 8B peaked at 0.28 (two sizes only; self-reported).
- **Token-level loss:** more effective on base models, limited gain on aligned ones.
- **Overlong filtering:** helped with an 8k length cap, little at 20k.
- **Lite PPO:** group-mean, batch-std advantage plus token-level loss on a critic-free PPO loss, which the authors say beat GRPO and DAPO on the base models, without reported numbers (self-reported).

## Limits

- Lite PPO (Liu et al.): Qwen3 family only, 4B and 8B, verifiable math rewards, one seed, no error bars. Clip-Higher and dynamic sampling are not ablated inside Lite PPO. The extraction is missing the text of one takeaway (group against batch normalisation under different reward scales) and has broken cross-references.
- Lite PPO (Liu et al.): the authors frame the conflicting advice in the literature (group against batch normalisation, with or without std, sequence against token loss) as likely reflecting differing setups. Only Clip-Higher and token-level loss were shown to depend on base against aligned model; the other changes were not ablated that way.

## See Also
- [[Preference Optimization Algorithms]] — extends (GRPO with four anti-collapse changes)
- [[Post-Training for Agents]] — instance-of (the RL-for-tool-calling recipe)
- [[RLVP — Verifiable Path Penalties]] — alternative-to (restore variance rather than drop the group)
- [[RL Training Frameworks for LLMs]] — prerequisite-for (the backbones that ship the DAPO recipe)
- [[FrogNano Online Task Synthesis]] — related
- [[Composer 2 Training Recipe]] — related
- [[Post-Training Reasoning Data Primer]] — related (data-side view of the same recipes, including dynamic sampling as a difficulty filter)
- [[LaMer Meta-RL Exploration]] — related
- [[Critical-State RL]] — related
- [[GUI Agent RL with GUI-R1 and ARPO]] — related
