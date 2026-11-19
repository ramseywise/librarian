---
title: DAPO
tags: [llm, reinforcement-learning, concept]
summary: "Four changes to PPO/GRPO-style RL — Clip-Higher, token-level loss, dynamic sampling and overlong reward shaping — each aimed at stopping the policy from collapsing early onto a single strategy; the reported state-of-the-art recipe for verifiable-reward math RL."
updated: 2026-11-19
sources:
  - data/raw/repos/learn-ai-engineering/generative-ai--05-RL--post-training-for-agents.md
  - data/raw/papers/2026-11-08-murphy-rl-ch06-llms-rl.md
  - data/raw/repos/learn-ai-engineering/generative-ai--05-RL--preference-optimization.md
  - data/raw/repos/learn-ai-engineering/generative-ai--05-RL--rlhf-pipeline.md
  - data/raw/papers/2026-11-06-liu-2025-part-i.md
  - data/raw/papers/2026-11-07-yu-2025-dapo.md
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

## The DAPO paper's own setup and numbers (Yu et al.)

Yu et al. (ByteDance Seed and collaborators, 2025, preprint) wrote DAPO because the R1 report omits key details. The method is a group-normalised, GRPO-style policy gradient without a KL term and a rule-based +1/-1 reward, with separate lower and upper clip ranges (0.2 below, 0.28 above), dynamic sampling, which over-samples and discards prompts for which every sample is right or every sample is wrong, loss averaged over all tokens in the group, and Overlong Filtering (mask the loss of truncated samples) plus Soft Overlong Punishment (a penalty that depends on length and applies only in a band below the maximum: 0 up to Lmax-Lcache, falling linearly to -1 at Lmax, and -1 beyond). It was trained on Qwen2.5-32B base with verl on DAPO-Math-17K (17K prompts with integer answers). Murphy's RL textbook chapter likewise describes DAPO's asymmetric clipping (eps_high 0.28 against eps_low 0.2) as a guard against entropy collapse. The comparison of the algorithm family is on [[GRPO Group Relative Policy Optimization]].

Results (self-reported; AIME 2024 avg@32 with 32 repeats, temperature 1.0, top_p 0.7):

- DAPO reaches 50, against 47 for DeepSeek-R1-Zero-Qwen-32B (cited from the R1 report, matched with 50% of its training steps), and 30 for naive GRPO.
- The cumulative ablation adds Overlong Filtering, Clip-Higher, Soft Overlong Punishment, token-level loss and dynamic sampling in that order, the last giving full DAPO.
- Token-level loss brings a smaller accuracy gain yet steadier training and healthier length growth; dynamic sampling samples more but needs fewer steps to converge (authors' claims from figures).
- Worked example: with eps 0.2 a token at probability 0.01 has an upper bound of 0.012 and one at 0.9 has 1.08. With eps=0.2 the average probability of the tokens that get clipped upward stays under 0.2.
- Training entropy should rise slowly; response length does not always grow, and training-set reward correlates little with validation accuracy.

An independent pass@k study found DAPO needed 3 to 6x more samples per batch than other algorithms and dropped at k=256 ([[RLVR Pass@k Reasoning Boundary]]).

## Limits

- DAPO paper (Yu et al.): math with verifiable integer answers only (transfer is asserted, not shown); one model and one benchmark, no seeds or error bars, and an order-dependent cumulative ablation; total steps, hardware and compute not stated; the R1-Zero comparison uses the report's number under differing setups; emergent reflection is one case study.
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
- [[GRPO Group Relative Policy Optimization]] — prerequisite-for (the baseline algorithm DAPO modifies)
- [[GSPO Group Sequence Policy Optimization]] — alternative-to (sequence-level ratio instead of the four changes)
- [[GDPO Decoupled Reward Normalization]] — related (borrows DAPO's techniques in its setup)
- [[Critical-State RL]] — related
- [[GUI Agent RL with GUI-R1 and ARPO]] — related
- [[Tool-N1 Binary-Reward Tool-Calling RL]] — related (binary reward for tool calls)
- [[Trust Region and Clipped Surrogate Policy Optimization]] — prerequisite-for (the clipped objective DAPO modifies)
- [[rStar2-Agent GRPO-RoC]] — extends (Clip-Higher plus rollout resampling for tool-integrated math)
- [[Demystifying Agentic RL (DemyAgent-4B)]] — extends (clip-higher and overlong shaping tested on agentic RL)
