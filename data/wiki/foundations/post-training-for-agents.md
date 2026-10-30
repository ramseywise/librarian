---
title: Post-Training for Agents
tags: [foundations, llm, concept]
summary: "How SFT, RL and distillation divide the work of training an agent — SFT writes form and protocol, RL learns transferable strategy, on-policy distillation gives RL's on-policy data with SFT's dense signal — and why the environment, data and reward shape matter more than the choice of algorithm."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/generative-ai--05-RL--post-training-for-agents.md
  - data/raw/repos/learn-ai-engineering/generative-ai--05-RL--README.md
  - data/raw/repos/learn-ai-engineering/generative-ai--05-RL--rlhf-pipeline.md
---

# Post-Training for Agents

The [[RLHF Pipeline]] describes post-training for a chat model. An agent adds tool calls,
multi-turn credit assignment and an environment that has to be built. Two claims organise
the topic: **SFT memorizes, RL generalizes**, and **data and environment matter more than
the algorithm**.

## Three stages and what each one writes into the weights

| Stage | Data | Objective | What it learns | Relative cost |
|---|---|---|---|---|
| Pretraining | Raw text | Next-token prediction | Language, world knowledge, basic reasoning | Largest |
| SFT | Thousands to tens of thousands of demos | Next-token prediction, loss masked to the response | Format, instruction following, style, process protocol | Hours to days |
| RL | Task plus reward function, no reference answer | Expected reward | Strategy that transfers; solutions nobody demonstrated | Often 10–100× SFT |

SFT is pretraining on different data. The loss is the same, and the only engineering
difference is masking the prompt so the model learns to answer rather than to ask. Because
it maximises the likelihood of one reference answer, SFT stores **protocol knowledge** (how
to say or do something), not large amounts of **factual knowledge**. Facts come from
pretraining, continued pretraining or retrieval.

**Form first, then strategy.** RL scores the model's own outputs. If an output is not a
parseable tool call, the reward cannot be computed and RL learns from noise. A rule of
thumb from the source: if the parse-failure rate is above about 20%, RL will fail. Two
boundary cases: a strong enough base model can skip SFT (pure-RL reasoning runs learned long
chains of thought, at the cost of readability and mixed languages, so a cold-start SFT stage
was added back), and a small base model with strict structured output fails completely
under RL without SFT.

**LoRA defaults** reported for post-training: apply LoRA to every weight matrix, the MLPs
especially (attention-only LoRA loses accuracy); use a learning rate about 10× the
full-fine-tuning rate; rank 64–256 for SFT, and rank 1–32 for RL, because each RL episode
carries little information.

## Why SFT memorizes and RL generalizes

| | SFT | RL |
|---|---|---|
| Signal | Dense, every token | Sparse, one scalar per rollout |
| Learns | A fixed input → output mapping | A strategy that produces good outcomes |
| Under distribution shift | Re-applies the old answer and degrades | Re-solves and holds |
| Distribution shape | **Mass-covering**: spreads probability over every mode in the demos | **Mode-seeking**: the reverse-KL anchor concentrates on a few high-reward modes |

The controlled evidence (Chu et al. 2025) held the base model and compute fixed and varied
only SFT vs. RL. On rule changes, colour changes and a switch from absolute to relative
navigation directions, RL gained a few to 17 points while SFT lost points, by 79.5 points
on the navigation shift. On unseen cities RL went from 16.7% to 77.8% while SFT fell to
11.1%. RL also improved the visual encoder, because the outcome signal back-propagates into
perception. Over-trained SFT leaves RL unable to recover out-of-distribution performance,
so stop SFT once format is stable.

RL's ceiling is higher because it is **online**:

1. Offline imitation is capped by the demonstrator; online RL is capped by the task. RL can
   reinforce behaviour no human showed, such as a grasp that emerged in a robot-arm run.
2. **Verifying is easier than generating.** SFT needs the right answer written down; RL
   needs only a way to recognise one (answer key, test suite, proof checker). This
   asymmetry is what RL with verifiable rewards is built on.
3. **On-policy data fixes covariate shift.** An imitator drifts into states its demos never
   covered and its error grows roughly as T² in trajectory length; training on its own
   trajectories brings that to roughly T.

## Priors beat algorithms

Tabular Q-learning needs about 10,000 episodes to win a small treasure-hunt game every
time; an LLM agent wins on its first try, because "key", "door" and "sword" mean something
to it. The ordering the source draws from the history of RL is **prior > environment >
algorithm**. Classic RL still wins where simulation is cheap and repeatable; where every
trial is a phone call or a browser session, sample efficiency dominates and priors pay. See
[[Reinforcement Learning Foundations]] for the classical machinery.

## What SFT is good for

- **Distillation.** *Prompt distillation* trains a short-prompt, non-thinking student on a
  long-prompt thinking teacher's final answers (20–30× faster at inference). *CoT
  distillation* trains on the teacher's full reasoning traces; a same-size student recovers
  70–80% of the teacher. The student inherits the teacher's systematic errors and loses any
  robustness the teacher got from tools.
- **[[Rejection Sampling Fine-Tuning]]**, which sits between SFT and RL.
- **Voice and style**, including paralinguistic tokens such as laughter; too few speakers in
  the data makes every voice sound alike.
- **Activating latent capability.** An instruction to reason in a given language, trained
  with no data in that language, worked because multilingual pretraining already held the
  shared representation.
- **New knowledge needs continued pretraining, not SFT.** Teaching a 7B model a new
  language worked from raw text in that language mixed about 80/20 with English to avoid
  forgetting, with instruction SFT afterwards.

SFT data usually comes from three layers: human seed demos to pin format, a teacher model
to scale them, rejection sampling to raise quality.

## Choosing SFT, RL or neither

1. **Does it need training at all?** If prompts, tools or context management solve it, no.
   Most agent applications stop here; see [[Harness Engineering]].
2. **SFT first** for schemas, tool-call format, protocol habits, tone and length. Never to
   inject facts.
3. **Add RL when SFT plateaus**: deployment drifts from training, demonstrations are
   suboptimal, or demonstrating every path costs too much. The test is that *more
   demonstrations stop improving new scenarios*, which is a limit of the objective, not of
   dataset size.

Each carrier holds a different kind of capability: in-context examples carry strategies
that can be stated in language, retrieval carries facts (updatable, citable, deletable),
code carries hard constraints, and weights carry what cannot be written down — perception,
tone, implicit policy. A per-customer LoRA beats a knowledge base for stable style and
loses for facts that change or must be cited.

## Data and environment over algorithm

**The environment is the practice field**, and a distorted one (scripted counterparts,
error messages unlike production) teaches a test-taking strategy that dies on deployment.
This is the most common way RL projects fail. A replayable "shadow world" often costs more
than the training run; the reward function is part of it.

When a real environment is not available, a model can play it:

- **Tool-return level** — an LLM simulates the search engine, with a curriculum that starts
  clean and mixes in noise, and the policy transfers to real search.
- **Dynamics level** — a distilled "experience model" predicts state transitions; user
  simulators serve as both training ground and exam (see [[ADK User Simulation Eval]]).
- **Risk** — the simulator's knowledge is the ceiling, the policy absorbs its biases, and RL
  hunts for its loopholes. Mix in real rollouts and recalibrate periodically.

Data quality decides how far post-training can go: check coverage of the long tail,
diversity (or the model collapses to one mode) and label accuracy (filter wrong reasoning
before distilling it). The source notes that before 2025 one frontier lab's recipe was
large-scale high-quality SFT plus [[Constitutional AI and RLAIF]], with little verifiable-reward
RL, and its coding models were already strong. **Agentic self-instruct** goes further and
changes the task distribution itself: a challenger writes tasks, and the kept tasks are those
a strong solver passes, a weak solver fails, and a verifier can judge reliably.

Order of effort: strong base model, then environment and data, then algorithm and
hyperparameters, which are a few lines of config in the frameworks in
[[RL Training Frameworks for LLMs]].

## Reward design for multi-turn agents

Multi-turn adds credit assignment (which turn solved the ticket?) and partial
observability.

- **Density.** Binary rewards suit checkable tasks. Sparse rewards stall on open-ended ones:
  a phone agent can fail a hundred calls before stumbling on the three facts a counterpart
  needs, even though the counterpart *said* what was missing — outcome-only RL cannot learn
  from that sentence.
- **Form.** A scalar (7.2) says nothing about why; a vector of per-dimension scores points at
  the phase that failed; a **generative reward model** writes an analysis, sampled several
  times and aggregated, and scales with inference compute. One published recipe has the
  model write task-specific principles, judge the trajectory against each, and get rewarded
  when its judgments match the actual trajectory, which keeps the judge's biases inspectable.
- **Process vs. outcome.** See [[Outcome vs Process Reward Models]] for the agent-side
  evidence (step-scored navigation vs. a binary-success robot policy).
- **Credit assignment.** GRPO spreads one trajectory-level advantage evenly over every
  token, so over long multi-turn episodes the signal dilutes; PPO with a value network and
  GAE still earns its cost there ([[Preference Optimization Algorithms]]).
- **Outcome-neutral constraints** need [[RLVP — Verifiable Path Penalties]], because outcome
  rewards actively reward breaking them.

## RL for tool calling

Difficulty climbs from one tool (format, timing, errors) to choosing among dozens to
orchestrating chains with dependencies and costs.

- **Loss-mask environment tokens.** Tool output, search results and user replies are not
  generated by the policy; including them in the gradient trains the model to predict the
  sandbox and destabilises training. Mainstream RL frameworks mask them by default.
- **Tool-integrated reasoning works.** A code-interpreter RL run (about an hour of SFT
  warm-up, then 400 PPO steps over nine days) took a 32B model from about 25% to 67% on a
  competition-math benchmark, against 40% for text-only RL after 1,080 steps. Tool use moved
  earlier, from late verification to early exploration, and responses got 40% shorter. RL
  took about 200× the SFT wall-clock time.
- **[[DAPO]]** is the set of four changes that keeps GRPO-style training from collapsing
  early onto one strategy.
- **Learning when not to think.** A constrained objective that rewards skipping the
  thinking block without losing accuracy cut response length 45–64% at no accuracy cost,
  and pairs with prompt distillation into a fast/slow system.

## Dense signals without a reward

[[On-Policy Distillation]] scores every token the student generates against a teacher's
distribution: RL's on-policy data with SFT's dense signal. In a case teaching a small model
behavioural traits (urgency, persistence), DPO and four RL reward designs each failed
differently and none beat SFT, while on-policy distillation from a frozen larger model beat
SFT by 23–47 points. **What stalls post-training is usually signal density, not reward
cleverness.**

## Practical pitfalls

Storing facts in weights; starting RL before format is stable; rewarding a proxy such as
length ([[Reward Hacking and Overoptimization]]); a low-fidelity simulator; over-training
(train loss falls, validation rises); value-function collapse and under-exploration; under-
estimating RL compute; dirty data. Validate cheaply before scaling: does SFT fix format on a
small set, does RL converge in a simplified environment, does the reward track the real goal
on a sample? Reuse benchmark *environments* for training, never benchmark *items*.

## See Also
- [[RLHF Pipeline]] — prerequisite-for (the chat-model pipeline this extends)
- [[Preference Optimization Algorithms]] — prerequisite-for (PPO, DPO and GRPO mechanics)
- [[RLVP — Verifiable Path Penalties]] — extends (dense path penalties on top of outcome reward)
- [[On-Policy Distillation]] — extends (dense on-policy signal from a teacher)
- [[DAPO]] — extends (the four anti-collapse changes to GRPO)
- [[Rejection Sampling Fine-Tuning]] — extends (verified self-generated SFT data)
- [[Outcome vs Process Reward Models]] — extends (reward granularity for agents)
- [[Agent Fundamentals]] — prerequisite-for (trajectories are the raw material for training)
- [[Self-Learning Agents]] — alternative-to (improvement without touching weights)
- [[Real-Time Multimodal Agents]] — extends (voice SFT and robot-policy RL in practice)
