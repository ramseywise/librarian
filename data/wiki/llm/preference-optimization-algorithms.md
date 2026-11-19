---
title: Preference Optimization Algorithms
tags: [llm, preference-and-alignment, comparison]
summary: "The PPO → DPO → GRPO → KTO/IPO/ORPO family — what each removes from the stage before it, the five-algorithm decision table, and why the field shifted from choosing an algorithm to designing a reward structure."
updated: 2026-11-19
sources:
  - data/raw/repos/learn-ai-engineering/generative-ai--05-RL--preference-optimization.md
  - data/raw/claude-docs/learn-ai-engineering/docs/research/2026-07-22_rl_landscape.md
  - data/raw/repos/learn-ai-engineering/generative-ai--05-RL--post-training-for-agents.md
  - data/raw/papers/2026-11-06-kumar-2025-llm-post-training.md
  - data/raw/papers/2026-11-06-tie-2025-survey-post-training-large-language.md
  - data/raw/papers/2026-11-07-rafailov-2023-dpo.md
  - data/raw/papers/2026-11-07-lambert-2024-tulu-3.md
  - data/raw/papers/2026-11-07-meng-2024-simpo.md
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

This is the constraint that decides its applicability: verifiable rewards remove the
**learned-reward-model loophole** of [[Reward Hacking and Overoptimization]] — there is no
proxy model to drift away from — which is exactly why GRPO does not extend to open-ended
generation, where no such checker exists. They do not remove gaming altogether: an agent
can still game the verifier itself, for example by editing the tests it must pass
([[RLVP — Verifiable Path Penalties]] penalizes this).

Two weaknesses of the group baseline matter for agents:

- **Zero-variance groups.** If every sample in a group is correct, or every one is wrong,
  the advantage is zero and the group contributes no gradient. [[DAPO]] drops those groups
  (dynamic sampling); RLVP gives them variance back through path penalties.
- **Coarse credit.** One trajectory-level advantage is spread evenly over every token,
  which dilutes the signal over long multi-turn episodes. That is where PPO with a value
  network still earns its cost (see [[Post-Training for Agents]]).

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

## A 2025 survey's framing (Kumar et al.)

Kumar et al. (arXiv 2502.21321, preprint, March 2025) survey post-training as fine-tuning, RL and test-time scaling, citing other work and running no experiments. Claims worth keeping: generation is an MDP (state is tokens so far, action is the next token), and RL for LLMs differs from classic RL by a very large action space, sparse and delayed feedback, difficult credit assignment and several competing objectives. Reward models learn relative preferences (Bradley-Terry or Plackett-Luce), not calibrated scores. GRPO drops the critic and normalises rewards within a sampled group, with an outcome mode and a process mode. DPO loses per-step credit assignment because it treats whole trajectories uniformly. The survey's future-directions section says current RL methods for LLMs need heavy compute and often underperform distillation, and names reward misgeneralisation, overthinking and catastrophic forgetting as open problems.


## A second 2025 survey (Tie et al.)

Tie et al. (arXiv 2503.06072v3, preprint, cutoff about March 2025) is a breadth survey with no experiments. Points worth keeping:

- The advantage is Q minus V, and PPO limits the probability ratio to a clipped band around 1; the value function is fit by mean-squared error to the realised return.
- DPO's derivation takes five steps: the optimum under a KL penalty reweights the reference policy Boltzmann-style; solving for the reward gives a beta-weighted log-ratio plus a beta log Z(x) offset; that offset cancels in pairwise Bradley-Terry comparisons; what remains is a logistic loss over beta-scaled differences of log-ratios, so no explicit reward model is needed.
- GRPO has no critic and takes its baseline from a group of sampled outputs; RLOO is REINFORCE without a value model and treats the whole response as one action. The survey's alignment grid (its Table 2) compares methods on explicit versus implicit reward model, point versus preference data, response versus token level, on- versus off-policy and online versus offline.
- Reasoning is cast as an MDP whose state is the query plus prior steps, with four reward kinds: binary correctness (simple, high-variance), step-wise accuracy (denser), self-consistency and preference-based. It cites RLAIF as comparable to or better than RLHF by human raters (second-hand, from Lee et al.).
- The survey's account of DeepSeek-R1 is descriptive: R1-Zero is GRPO from the base model without SFT, and R1 adds a cold-start SFT stage and a second RL stage.

## Head-to-head evidence for DPO, PPO and SimPO

- Rafailov et al. (self-reported; GPT-J 6B SFT model, TL;DR test split, GPT-4 judging against reference summaries): DPO reaches about a 61% win rate and PPO 57% at its best sampling temperature.
- Lambert et al., the Tulu 3 report (self-reported; Table 18 ablation, one early SFT checkpoint, UltraFeedback only, one run each): length-normalised DPO was the only preference algorithm to beat the SFT base overall. Plain DPO (55.2), PPO (55.5) and SimPO (best 52.9) stayed under the base at 55.7.
- Meng et al. (self-reported; Llama-3-Instruct v0.2): with ArmoRM as the preference labeller, DPO ties SimPO on raw win rate (47.5 each), so the gaps between algorithms shrink.

## Limits

- Kumar et al. (survey): many of its numbers carry a citation and no setup (22% wasted computation, 29% forgetting, 94% on MATH, r=0.34), so do not cite them from here. The extraction found citation errors (the DPO reference points at a different paper), a description of ORPO that does not match the ORPO paper, a DPO loss printed without its log and minus sign, and dubious rows in its model table. It covers R1, o1 and Kimi K1.5 only in outline and predates later GRPO variants.
- Tie et al. (survey): the survey never writes out the GRPO advantage formula and does not separate PPO's KL penalty from its clip. Its R1 detail contradicts itself (a critic and a stepwise reward model are described next to a rule-based reward figure) and the entropy and dual-attention mechanisms are unsourced, so do not cite them. Table 1 parameter sizes are dubious (GPT-3 at 17.5B, for instance), the text gives "30-bit floating point", RLHF is dated to 2021 against InstructGPT's 2022, and it predates DAPO-style and later RLVR work.
- Rafailov et al.: models up to 6B only; GPT-4 win rates depend on the judge prompt; DPO's beta was barely tuned, the PPO baselines lean on the authors' tuning and a public checkpoint, and there are no seeds or significance tests.
- Lambert et al.: the Table 18 comparison is a single run per row with no variance, on an early checkpoint with one dataset; the authors call the PPO setup untuned (reward model trained once), so PPO might improve with more tuning.
- Meng et al.: no PPO comparison, offline training only, GPT-4 judges, and seeds and run counts are not stated; the authors note the gains get smaller when the SFT model is stronger or the labels better.

## See Also
- [[RLHF Pipeline]] — prerequisite-for (PPO is its Stage 3; every method here is a removal from it)
- [[Bradley-Terry Preference Model]] — prerequisite-for (the objective DPO fits directly)
- [[Direct Preference Optimization]] — extends (applied guidance on when DPO fits an agent project)
- [[Reward Hacking and Overoptimization]] — related (the length problem DPO inherits; what verifiable rewards avoid)
- [[Constitutional AI and RLAIF]] — related (supplies preference data, independent of which optimizer consumes it)
- [[Outcome vs Process Reward Models]] — extends (what the reward scores in the reasoning group)
- [[RL Training Frameworks for LLMs]] — extends (the backbones these algorithms run on)
- [[DAPO]] — extends (four fixes to GRPO for long reasoning)
- [[RLVP — Verifiable Path Penalties]] — extends (restores variance to uniform groups)
- [[Phi-4 Training Recipe and Pivotal Token Search]] — extends (a DPO round built from token-level pairs)
- [[Post-Training for Agents]] — extends (how these algorithms apply to tool-using agents)
- [[REINFORCE with a Baseline]] — related (the baseline idea in its original form)
- [[Trust Region and Clipped Surrogate Policy Optimization]] — prerequisite-for (PPO's clipped objective)
- [[RULER and ART Hybrid Reward Agent Training]] — extends (GRPO-based agent training with an LLM judge)
- [[GRPO Group Relative Policy Optimization]] — extends (the GRPO section's source paper, with reported results)
- [[DPO Loss and Implicit Reward]] — extends (the DPO objective, implicit reward and measured results)
- [[SimPO and PRO Reference-Free Preference Optimization]] — extends (length-normalised and ranking-based reference-free variants)
- [[Tulu 3 Post-Training Recipe and RLVR]] — related (ablation of DPO, SimPO and PPO on one SFT checkpoint)
