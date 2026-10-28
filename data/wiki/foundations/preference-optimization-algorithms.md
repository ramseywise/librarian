---
title: Preference Optimization Algorithms
tags: [foundations, llm, comparison]
summary: "The PPO → DPO → GRPO → KTO/IPO/ORPO family — what each removes from the stage before it, the five-algorithm decision table, and why the field shifted from choosing an algorithm to designing a reward structure."
updated: 2026-10-16
sources:
  - data/raw/repos/learn-ai-engineering/generative-ai--05-RL--preference-optimization.md
  - data/raw/claude-docs/learn-ai-engineering/docs/research/2026-07-22_rl_landscape.md
---

# Preference Optimization Algorithms

```
PPO (online RL, reward model, 4 models in memory)
 │  remove the reward model + the RL loop
 ▼
DPO (offline, closed-form, policy + reference)
 │  remove the value model, normalize within a sampled group
 ▼
GRPO (online, verifiable rewards, no critic)
 │  relax the data requirement
 ▼
KTO / IPO / ORPO (unpaired feedback, collapse-safe, reference-free)
```

The family reads as a **sequence of removals**. Each method drops a component the
previous one required, and the question when choosing is which components your data and
budget can actually support.

## PPO

The [[RLHF Pipeline]] Stage 3 optimizer. Ratio `r_t(θ) = π_θ(a_t|s_t) / π_θ_old(a_t|s_t)`,
clipped surrogate, with the full training objective

```
L_total = L_PPO + β · KL[π_θ ‖ π_SFT] + γ · L_pretrain
```

Most expressive and most expensive: four models resident, roughly **28GB for a 7B model
at 4-bit**. Choose it when you need reward *shaping* — a reward composed of several
weighted signals — which none of the offline methods can express.

## DPO

The key result: for the KL-constrained objective, the optimal policy has a closed form
in terms of the reward,

```
π*(y|x) = π_ref(y|x) · exp( r*(x,y) / β ) / Z(x)
```

Rearranging for `r*` and substituting into the [[Bradley-Terry Preference Model]] loss
makes the intractable partition function `Z(x)` **cancel**, because the objective only
ever sees reward *differences*. What remains is a supervised classification loss on
preference pairs, with the policy's own log-ratios standing in for the reward. No reward
model, no sampling loop, no critic.

The cost is the **DPO length problem**: with no KL-anchored online sampling, the policy
tends to inflate response length — the verbosity failure from
[[Reward Hacking and Overoptimization]] surviving the removal of the reward model,
because it was always a property of the preference data.

The existing [[Direct Preference Optimization]] page covers when DPO is worth reaching for
in an applied agent context.

## GRPO

Group Relative Policy Optimization drops the value model by estimating the advantage
**within a sampled group**:

1. Sample G responses for the same prompt
2. Score each with a reward function
3. Normalize: `A_i = (r_i - mean(r)) / std(r)`
4. Policy-gradient update using those normalized advantages

The group's own mean is the baseline, so no critic is needed — about a **25% memory
reduction** versus PPO. The trade is that GRPO wants **verifiable rewards**, of which
there are three practical kinds:

| Reward type | Verified by |
|---|---|
| Math | Checking the final answer |
| Code | Running the tests |
| Format | Matching the required structure |

This is the constraint that decides its applicability: verifiable rewards **cannot be
hacked in the [[Reward Hacking and Overoptimization]] sense** — a test either passes or
it does not — which is exactly why GRPO does not extend to open-ended generation, where
no such checker exists.

## The 2025 split: alignment vs reasoning

A 2026 landscape review notes that through early 2024, PPO-based RLHF was *the* RL technique
and it was used for alignment. From late 2024, RL became the main tool for **reasoning**
as well. The family above then splits into three groups that answer different questions:

| Group | Methods | Question it answers |
|---|---|---|
| **Alignment** | RLHF (PPO), DPO, KTO, CPO | Does the output match human preference? |
| **Reasoning** | GRPO, DAPO, REINFORCE++ | Does the chain of thought reach a checkable right answer? |
| **Training backbones** | verl, OpenRLHF, TRL | What runs the rollouts and updates at scale? See [[RL Training Frameworks for LLMs]] |

Two additions to the methods covered above:

- **DAPO** applies the group-baseline idea to verified rewards and is the reported
  state-of-the-art recipe for math (50 points on AIME 2024 with a Qwen2.5-32B base).
- **REINFORCE++** uses a plain baseline plus KL regularization with an optional critic. The
  source associates it with agentic, long-horizon RL.

The memory framing differs by source but is consistent. PPO keeps a critic on top of the
policy, reference, and reward models, which puts it at roughly 3–4× the memory of the
policy alone. Dropping the critic is the ~25% reduction quoted above. The reasoning group's
other design choice is *what the reward scores*, a whole answer or each step. That choice
is covered in [[Outcome vs Process Reward Models]].

## KTO, IPO, ORPO

Three relaxations of DPO's requirements:

- **KTO** (Ethayarajh 2023) — grounded in **prospect theory**, and trains on **unpaired
  binary feedback** (this response was good / bad). Removes the requirement that every
  example be a matched pair, which is usually the hardest data constraint to satisfy in
  production.
- **IPO** — modifies the objective to prevent the policy collapsing to zero probability
  on rejected responses, a degenerate solution DPO can reach when preferences are near-
  deterministic.
- **ORPO** — folds preference optimization into SFT as a single stage with **no reference
  model at all**:

  ```
  L_ORPO = L_SFT - λ · log σ( log( odds_θ(y_w|x) / odds_θ(y_l|x) ) )
  ```

## Choosing

| If you have | Use |
|---|---|
| Paired preferences, limited compute | **DPO** |
| Unpaired binary feedback | **KTO** |
| Verifiable rewards (math, code, format) | **GRPO** |
| Need composite reward shaping | **PPO** |
| Want one stage, no reference model | **ORPO** |

Practitioner heuristics from the source, in order: **start with DPO** — it is the
strongest default and the cheapest to run; move to PPO only when reward shaping is
genuinely required; use GRPO when a checker exists; reach for KTO when your feedback is
not paired; and treat labeler/data quality as the dominant term over algorithm choice.

## DeepSeek-R1 and the shift in the question

DeepSeek-R1 trained reasoning via RL against **verifiable rewards** with no explicit
supervision of the reasoning process — and chain-of-thought reasoning **emerged**, along
with the widely-cited "aha moment" where the model spontaneously backtracks and re-examines
its own approach mid-solution. Capability came from scaling the **RL stage** rather than
the model.

The consequence for practice: the field's live question moved from *"which alignment
algorithm?"* to *"what reward structure?"* — the algorithm table above is increasingly
the easy half of the decision, and designing a reward that is both verifiable and
aligned with what you actually want is the hard half.

## See Also
- [[RLHF Pipeline]] — prerequisite-for (PPO is its Stage 3; every method here is a removal from it)
- [[Bradley-Terry Preference Model]] — depends-on (the objective DPO fits directly)
- [[Direct Preference Optimization]] — extends (applied guidance on when DPO fits an agent project)
- [[Reward Hacking and Overoptimization]] — complements (the length problem DPO inherits; what verifiable rewards avoid)
- [[Constitutional AI and RLAIF]] — complements (supplies preference data, independent of which optimizer consumes it)
- [[Outcome vs Process Reward Models]] — extends (what the reward scores in the reasoning group)
- [[RL Training Frameworks for LLMs]] — extends (the backbones these algorithms run on)
