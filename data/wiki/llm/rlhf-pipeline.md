---
title: RLHF Pipeline
tags: [llm, preference-and-alignment, concept]
summary: "The three-stage InstructGPT pipeline — SFT, then a Bradley-Terry reward model on ~33k comparisons, then PPO with a KL penalty against the SFT policy — and why all three stages are load-bearing."
updated: 2026-11-19
sources:
  - data/raw/repos/learn-ai-engineering/generative-ai--05-RL--rlhf-pipeline.md
  - data/raw/repos/learn-ai-engineering/generative-ai--05-RL--README.md
  - data/raw/papers/2026-11-07-christiano-2017-deep-rl-from-human-preferences.md
  - data/raw/papers/2026-11-07-ziegler-2019-fine-tuning-language-models-human.md
  - data/raw/papers/2026-11-07-stiennon-2020-learning-summarize-human-feedback.md
  - data/raw/papers/2026-11-07-ouyang-2022-training-language-models-follow-instructions.md
  - data/raw/papers/2026-11-08-murphy-rl-ch06-llms-rl.md
  - data/raw/papers/2026-11-07-huyen-ai-engineering-ch02-understanding-foundation-models.md
  - data/raw/papers/2026-11-07-building-ai-agents-llms-rag-kgs-ch03-exploring-llms-as-powerful-ai-engine.md
  - data/raw/papers/2026-11-08-xiao-foundations-llms-ch04-alignment.md
---

# RLHF Pipeline

Reinforcement Learning from Human Feedback turns a next-token predictor into an
instruction-follower by learning a **model of human preference** and then optimizing
against it. The InstructGPT formulation is three stages, run in order, each producing an
artifact the next stage consumes.

```
Pretrained LM
    │
    ▼
[Stage 1] Supervised fine-tuning on demonstrations   →  π_SFT
    │
    ▼
[Stage 2] Reward model on pairwise comparisons       →  r_θ
    │
    ▼
[Stage 3] PPO against r_θ, KL-anchored to π_SFT      →  π_RLHF
```

## Stage 1 — Supervised fine-tuning

Human labelers write demonstration responses to prompts; the base model is fine-tuned on
them. InstructGPT used roughly **13k** demonstrations.

**Why SFT must come first.** A pretrained model's output distribution is too diffuse to
be a useful RL starting point — most sampled responses are off-task, so the reward signal
carries almost no gradient information. SFT concentrates the distribution on plausible
responses first, and only then is preference optimization discriminating between things
worth discriminating between. It also becomes the **reference policy** the KL penalty in
Stage 3 anchors to, so its quality bounds the whole pipeline.

Other textbooks describe the same stage. Huyen calls the (prompt, response) examples demonstration data and notes InstructGPT's 13,000 pairs, which at $10 per pair come to $130,000. Raieli and Iuculano put the supervised set for RLHF at 10,000 to 100,000 human-written pairs (claim, no model named). For a worked fine-tuning on pairs see [[Supervised Instruction Fine-Tuning of GPT-2 with an LLM Judge]].

## Stage 2 — Reward model

The reward model is the SFT model with the language-modeling head replaced by a **scalar
head** — one number per (prompt, response) pair. It is trained on human **rankings** of
multiple responses to the same prompt (~33k comparison pairs for InstructGPT), not on
absolute scores.

Ranking rather than scoring is deliberate: humans are unreliable at assigning calibrated
absolute quality scores but comparatively reliable at picking the better of two options.
The formal machinery for converting those pairwise choices into a scalar is the
[[Bradley-Terry Preference Model]], giving the loss

```
L_RM(θ) = -E_[(x, y_w, y_l) ~ D] [ log σ( r_θ(x, y_w) - r_θ(x, y_l) ) ]
```

where `y_w` is the preferred (won) response and `y_l` the rejected one. Only the
*difference* of rewards is ever supervised, so `r_θ` is identified up to an additive
constant — which is fine, because Stage 3 only uses relative reward.

## Stage 3 — PPO with a KL penalty

The policy is optimized to maximize reward while being penalized for drifting from the
SFT reference:

```
L_PPO(θ) = E[ r_θ(x, y) ] - β · KL[ π_θ(y|x) ‖ π_SFT(y|x) ]
```

with **β typically 0.02–0.2**, and PPO's clipped surrogate objective
`min(r_t · A_t, clip(r_t, 1-ε, 1+ε) · A_t)` bounding per-step policy movement.
InstructGPT used ~31k prompts here.

The KL term is not a regularizer in the ordinary sense — it is the thing preventing
[[Reward Hacking and Overoptimization]]. `r_θ` is a *learned approximation* of preference,
valid only near the distribution it was trained on. Unconstrained optimization walks the
policy off that distribution and into the reward model's errors. β sets how far you are
willing to walk.

**Why the KL is reverse, `KL(π_θ ‖ π_ref)`.** Reverse KL penalizes probability mass the
policy puts where the reference has almost none, which keeps the policy inside the region
where the reward model's scores can be trusted. It is also **mode-seeking**: the policy
settles on one or two high-reward response styles rather than covering every style the
SFT model produced, which is why RL-tuned models sound more decisive and less varied.
Forward KL would force coverage of every SFT mode, which is not the goal.

Murphy's survey (reported) likewise says to put the KL penalty in the token-level reward rather than the advantage. Concretely the penalty is evaluated **per token and folded into the reward** instead of being a distinct loss term, so it reaches the PPO or GRPO advantage through the reward. Most RL-with-verifiable-
rewards runs keep it for stability; [[DAPO]] and Open-Reasoner-Zero drop it, while
DeepSeek-R1-Zero's GRPO keeps it. The SFT-memorizes / RL-generalizes framing behind this is
in [[Post-Training for Agents]].

Huyen calls the Stage 2 data comparison data, (prompt, winning_response, losing_response). Her reported figures: about 73% agreement between InstructGPT labelers on pairwise rankings; a Llama 2 comparison cost $3.50 against $25 for writing a response (per Thomas Scialom, Discord talk); LMSYS comparisons took three to five minutes each. She also reports more hallucination from InstructGPT's RLHF model than from SFT alone, even though labelers liked the RLHF model better. Raieli and Iuculano list the stages as SFT, then a reward model trained from rankings, then PPO under a KL penalty, and recommend DPO as a way to skip the reward model and the RL step.

In Xiao and Zhu's chapter 4 the reward model is a decoder topped by a linear layer that reads the final token's state, fit with the Bradley-Terry pairwise loss. For RL, the reward and value models start from the pretrained LLM, whereas the policy and reference models start from the instruction-tuned one.

## Practical cost

Stage 3 holds **four models simultaneously** — policy, reference, reward model, and
value/critic — for roughly **4× the memory** of ordinary fine-tuning. This cost is the
main reason the field moved toward the offline methods in
[[Preference Optimization Algorithms]], which drop one or more of the four.

**Labeler quality dominates labeler volume.** Inconsistent preference labels put a
ceiling on the reward model that no amount of additional Stage 3 compute can lift — the
policy will faithfully optimize toward whatever the labels actually encoded.

## What the lineage papers report

The pipeline above descends from four papers. Each number is (self-reported) and keeps its setup.

**Christiano et al. 2017 (Atari and MuJoCo, no language model).** A reward predictor is trained by Bradley-Terry cross-entropy on comparisons, from a human or a synthetic oracle, between pairs of trajectory segments 1-2 s long: `P(s1 > s2) = exp(sum r(o1,a1)) / (exp(sum r(o1,a1)) + exp(sum r(o2,a2)))`. A2C is the policy learner on Atari and TRPO on MuJoCo; predictor, policy and labelling run asynchronously, and the queries chosen are those where an ensemble disagrees most. MuJoCo agents given 700 labels come close to RL on the true reward (8 MuJoCo tasks plus pendulum; 5 runs with synthetic feedback, one human run). The paper claims this needs about three orders of magnitude less interaction than treating human feedback as the reward directly. Training the predictor offline rather than online did badly, for example Pong agents that volleyed forever (700 synthetic labels on MuJoCo, 5,500 on Atari). The new behaviours, a hopper backflip from 900 queries and a one-legged half-cheetah from 800, were labelled by the authors rather than contractors.

**Ziegler et al. 2019 (774M GPT-2, PPO).** The reward model is the LM with a randomly initialised linear head, fit to human best-of-4 choices, and the policy maximises `R = r - beta log(pi/rho)` with rho the pretrained model. After 5,000 offline comparisons, the descriptiveness policy won 86% of judgements against zero-shot output (BookCorpus test set, 1024 excerpts, 3 labelers). On TL;DR the 60k online policy beat the offline one 71% of the time. The 60k RL summarisers beat human reference summaries on 96% (TL;DR) and 84% (CNN/DM) of comparisons, yet lost to the lead-3 baseline (45% and 40%), and copied entire sentences 71% and 98% of the time (RL run without supervised initialisation); the extraction reads this as the policy exploiting a labeler heuristic. With the KL penalty removed, mock-sentiment policies reached a mean score of +8.0 but emitted gibberish. The paper also describes a sign bug that flipped reward and KL and produced only sexually explicit text; it was found after training ended (reported as a claim).

**Stiennon et al. 2020 (TL;DR; 1.3B and 6.7B GPT-3-style models).** On preference against reference summaries, a 1.3B policy tuned on human feedback beat a supervised policy ten times larger, and the 6.7B model keeps its preference once length is controlled for. Across 7 reward models (160M to 13B parameters, 8k to 64k comparisons), doubling the data raises validation accuracy by roughly 1.1 points and doubling the model by roughly 1.8. Optimising against an early reward model first helped and then hurt true preference. For PPO, a separate value network outperformed a policy-value network with shared weights. Fine-tuning the 6.7B model with RL cost approximately 320 GPU-days. The 64,832 TL;DR comparisons were released. Loss: `-E log sigma(r(x,y_i) - r(x,y_{1-i}))`; reward: `r - beta log(pi_RL/pi_SFT)`.

**Ouyang et al. 2022 (InstructGPT, GPT-3).** Stages: SFT on about 13k demonstrations; a 6B reward model fit to rankings over K=4 to 9 outputs per prompt (about 33k prompts) under a pairwise logistic loss averaged over the C(K,2) pairs; then PPO with a per-token KL penalty, optionally combined with pretraining log-likelihood (PPO-ptx, coefficient gamma). On held-out customer API prompts (3,196 prompts), people preferred a 1.3B InstructGPT to 175B GPT-3. In the paper's setups InstructGPT about doubles truthful-and-informative answers on TruthfulQA and hallucinates about half as often on closed-domain tasks. It emits about a quarter fewer toxic outputs when told to be respectful, but when told to be biased it is considerably more toxic than GPT-3, and Winogender shows no significant bias gain. Multiplying the KL coefficient by 100 does not repair the NLP regressions (1.3B, default beta 0.02), whereas gamma of 20 or more does. A single 6B reward model and value function served every policy size, because a 175B reward model was unstable. SFT at 175B took 4.9 petaflops/s-days, against 3,640 for pretraining GPT-3.

## Limits

- Christiano 2017: the human-feedback runs are one run per task with no significance testing; selecting queries by ensemble variance is called crude and can hurt; termination conditions were removed; there is no text setting.
- Ziegler 2019: no error bars; the evaluation relied on the same Scale labelers who trained the model; online collection proved hard to debug; the online-versus-offline difference could be mostly noise; sharing parameters between reward model and policy failed because the data was unbalanced (60k against 2M); compute is unstated.
- Stiennon 2020: no baseline of SFT on an equal volume of high-quality demonstrations; about two-thirds of TL;DR is posts about relationships; the 6.7B reward model leans toward longer outputs; the labeler pool skews White and American.
- Ouyang 2022: alignment is to roughly 40 contractors' preferences, not to wide human values; one contractor labelled most comparisons; training favoured helpfulness while evaluation favoured truthfulness and harmlessness; PPO-ptx remains behind GPT-3 on DROP, SQuADv2 and translation; the authors thank Owain Evans and Stephanie Lin for pointing out that automatic TruthfulQA metrics exaggerated PPO's gains.
- Xiao and Zhu ch04: no experiments of its own and no hyperparameters for any method; the authors concede no satisfactory solution to reward overoptimisation exists; the text has notation slips (equation and figure references, theta_ref against theta_old).
- Huyen ch02 and Raieli and Iuculano ch03: the numbers are relayed from other work (Huyen's are time-bound), and no experiments are run.

## See Also
- [[Data Engineering Foundations]] <!-- auto-linked -->
- [[Bradley-Terry Preference Model]] — related (part of; the Stage 2 objective)
- [[Reward Hacking and Overoptimization]] — extends (the three failure modes of Stage 3)
- [[Preference Optimization Algorithms]] — alternative-to (offline methods that collapse or skip stages)
- [[Constitutional AI and RLAIF]] — extends (replaces the human labels in Stage 2 with AI feedback)
- [[Direct Preference Optimization]] — alternative-to (removes the reward model entirely)
- [[Post-Training for Agents]] — extends (SFT vs RL, and RL for tool-using agents)
- [[DAPO]] — extends (a GRPO variant that drops the KL term)
- [[RLVP — Verifiable Path Penalties]] — extends
- [[Chain of Hindsight]] — alternative-to
- [[DPO Loss and Implicit Reward]] — alternative-to (the offline loss that removes the reward model; measured against PPO)
- [[RLOO REINFORCE Leave-One-Out]] — alternative-to (a REINFORCE-style replacement for PPO in Stage 3)
- [[Reward Model Overoptimization Scaling Laws]] — extends (fitted gold-reward curves for the KL-penalised stage)
- [[Tulu 3 Post-Training Recipe and RLVR]] — extends (DPO plus a verifiable-reward PPO stage)
- [[OpenAssistant OASST1 Conversation Trees]] — related (open data used to run the three stages)
- [[BeaverTails Decoupled Safety Preference Dataset]] — related (separate helpfulness and harmlessness comparisons)
- [[Harmful Fine-Tuning of Aligned Models]] — related (fine-tuning can undo the alignment the pipeline installs)
- [[Multitask Prompted Instruction Tuning (FLAN, T0, Super-NaturalInstructions, MetaICL)]] — related (supervised instruction tuning on task collections)
- [[Trust Region and Clipped Surrogate Policy Optimization]] — prerequisite-for (the PPO step)
- [[Knowledge Distillation with Soft Targets]] — related (teacher-student training without a reward)
- [[LLaMA 1 and Llama 2 Open Foundation Models]] — instance-of
- [[GPT-4 Technical Report and Predictable Scaling]] — related
- [[Supervised Instruction Fine-Tuning of GPT-2 with an LLM Judge]] — prerequisite-for (a worked SFT run, the first stage)
- [[Helpful-Harmless RLHF and Iterated Online Training]] — extends (separate harmlessness data and iterated online collection)
- [[HHH Assistant Alignment Baselines]] — related (prompting, context distillation and preference-model pre-training before RLHF)
- [[WebGPT Browser-Assisted Question Answering]] — instance-of (behaviour cloning, reward model and PPO or best-of-n applied to browsing)
