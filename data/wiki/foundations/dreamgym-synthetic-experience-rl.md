---
title: DreamGym Synthetic Experience RL
tags: [foundations, llm, pattern]
summary: "DreamGym replaces the real environment with an LLM experience model that predicts next states and rewards, plus a variance-based task curriculum; agents trained only on its output reached roughly the level of RL on 80K real transitions in two of three environments (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-chen-2025-scaling-agent-learning-experience-synthesis.md
---

# DreamGym Synthetic Experience RL

DreamGym (a Meta-affiliated preprint, November 2025) trains web and tool agents with RL while making no calls to the real environment during the main phase. Its premise is that the training environment need not be a faithful simulator; it needs to produce interaction data that is varied, informative and causally grounded.

## Mechanism

- **Reasoning experience model.** An SFT-tuned Llama-3.1-8B-Instruct predicts the next state and the reward for each agent action. It reasons in chain-of-thought first, and is conditioned on the interaction history, the task, and the top-k most similar transitions fetched from a replay buffer. States are abstract text (for example a cleaned list of page elements) rather than raw HTML. Reasoning traces used as SFT targets were annotated by a teacher LLM.
- **Curriculum task generator.** Candidate tasks are varied from seed tasks, and those with the highest variance of outcome reward within a rollout group are favoured, because balanced successes and failures give the most signal for credit assignment. The paper calls this a reward-entropy rule; the extraction notes it is variance of a binary reward. A bounded fraction of each batch is synthetic.
- **Reward.** Outcome-only and binary, emitted by the experience model at the final step.
- **DreamGym-S2R (sim-to-real).** Train synthetically first, then run a short real-environment RL phase.

## Results (self-reported)

Setups cover three environments (WebShop, ALFWorld, WebArena-Lite), three backbones (a 3B and an 8B Llama, plus Qwen-2.5-7B) and two optimisers (GRPO, PPO).

- Synthetic-only training is close to RL on 80K real transitions, not uniformly better. WebShop GRPO: 59.3 / 63.9 / 68.3 against 62.1 / 65.0 / 66.1 real. ALFWorld PPO with Qwen-2.5-7B: 72.7 against 81.1 real.
- On WebArena-Lite, which the authors call not RL-ready, DreamGym scores 9.1 to 14.5 against real-environment baselines of 4.8 to 7.3.
- S2R used 5K real transitions and beat the 80K-transition baseline in most cells (on WebShop with GRPO: 70.5, 75.0 and 72.1 across the three backbones).
- The paper says training effort on WebArena is roughly 20 to 33% of what real-environment RL needs.
- Ablation on WebShop (Llama-3.1-8B GRPO values inferred by the extraction): full 63.9; no experience replay 59.2; no reasoning 55.8; no task generation 57.3.
- A transfer test works between web domains but drops sharply from web to ALFWorld.

## Limits

- The extraction flags a text-versus-table conflict: the paper says DreamGym exceeds 30% on WebArena, while Table 1 shows 9.1 to 14.5; the headline gains of over 30% and over 40% are undefined relative figures, so do not quote them as success rates.
- The WebArena real baseline ran on four servers with a self-built pipeline, so the headline gap partly reflects infrastructure.
- No seeds or error bars; one experience-model size; reward accuracy against the real environment is never measured. The authors concede only single-environment setups.
- The theoretical lower bound is only informative if reward and transition errors are small; none is measured.

## See Also

- [[Post-Training for Agents]] — prerequisite-for
- [[FrogNano Online Task Synthesis]] — alternative-to (adapts synthetic tasks to the policy, but runs in a real sandbox)
- [[Web Agent Benchmarks (WebShop and Mind2Web)]] — related
- [[DAPO]] — related (also filters groups by reward variance)
- [[AutoGym Blueprint-First Verifiable Gyms]] — alternative-to
