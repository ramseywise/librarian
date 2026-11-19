---
title: Generalized Advantage Estimation
tags: [llm, reinforcement-learning, concept]
summary: "GAE(gamma, lambda) estimates the advantage as an exponentially weighted sum of one-step TD residuals, with lambda trading bias against variance between the one-step TD advantage and the full Monte Carlo return minus a baseline."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-schulman-2015-high-dimensional-continuous-control-using.md
  - data/raw/papers/2026-11-08-murphy-rl-ch03-policy-based-rl.md
  - data/raw/papers/2026-11-07-building-ai-agents-llms-rag-kgs-ch08-reinforcement-learning-ai-agents.md
  - data/raw/papers/2026-11-08-murphy-rl-ch06-llms-rl.md
---

# Generalized Advantage Estimation

A policy gradient needs each action's advantage, defined as Q(s,a) minus V(s). A Monte Carlo return minus V(s) is unbiased but noisy; the one-step TD residual δ_t = r_t + γV(s_{t+1}) − V(s_t) is low variance but biased whenever V is inaccurate. Generalized advantage estimation (Schulman et al., ICLR 2016) takes an exponentially weighted average of the k-step advantage estimators between those poles:

A_t = Σ_l (γλ)^l δ_{t+l}

with the recursion A_t = δ_t + γλ A_{t+1} (Murphy's Algorithm 6 also returns value targets y_t = A_t + v_t). Setting λ = 0 gives the one-step TD residual; λ = 1 gives the empirical return minus V(s_t). The construction mirrors TD(λ), applied to advantages rather than values. The paper notes the same formula had been proposed earlier for online actor-critic methods; what it adds is the analysis and its use with batch trust-region methods.

## Why two parameters

The authors argue that the best λ is much lower than the best γ, because λ adds bias only when the value function is inaccurate, whereas γ < 1 biases the policy gradient regardless of V. In the paper γ is treated as a variance-reduction parameter on an undiscounted problem. They also read GAE as reward shaping with potential Φ = V: summing the shaped rewards with a (γλ) discount reproduces the GAE.

## Reported results (self-reported)

The policy is updated with TRPO (see [[Trust Region and Clipped Surrogate Policy Optimization]]) and the value function is fitted by Monte Carlo regression under its own trust region using conjugate gradient.

- Intermediate γ and λ work best on cart-pole (linear policy, a 20-unit value network, 21 seeds) and on the 3D biped (tanh networks of 100, 50 and 25 units, 50000 timesteps per batch, 9 seeds).
- The 3D biped's learning to walk used about 5.8 days of simulated experience (0.01 s per step, 50000 steps per batch, 1000 batches).
- The λ = 0 one-step return gave excessive bias and poor performance on locomotion tasks, with no number printed.
- Quadruped (γ = 0.995): the best run combined a value function with λ = 0.96. Stand-up (γ = 0.99): a value function always helped, and λ = 0.96 and 1 were roughly equal.

## Where it appears elsewhere

- Murphy's survey lists the general form Σ_t Ψ_t ∇log π, where Ψ_t can be the Monte Carlo return, return with a baseline, advantage, Q or TD residual, and places GAE in the PPO loop.
- PPO uses a truncated GAE over each T-step segment from N actors.
- A book chapter's A3C Super Mario agent accumulates `gae = gae + reward + gamma * next_value - value` and uses actor-critic with GAE to lower gradient variance.
- For long multi-turn LLM tasks, Murphy advises truncating or summarising history and learning a critic with GAE, warm-starting the actor from an instruct model. Critic-free LLM methods such as GRPO replace the learned advantage with a group-normalised one; see [[Preference Optimization Algorithms]].

## Limits

- The authors describe their advantage-estimation analysis as intuitive but informal. How value-function error feeds into policy-gradient error, adaptive choice of γ and λ, shared policy and value architectures, and convergence guarantees are all left open.
- Quadruped and stand-up received only a limited γ/λ comparison because of compute cost; seeds differ by task (21, 9, 5) with no confidence intervals or significance tests.
- TRPO and value-trust-region ε values and learning rates are not reported, and there is no comparison with deterministic-policy-gradient approaches.
- Murphy's chapter is a survey with no experiments of its own.

## See Also
- [[Reinforcement Learning Foundations]] — prerequisite-for
- [[Trust Region and Clipped Surrogate Policy Optimization]] — extends (TRPO and PPO consume GAE advantages)
- [[Preference Optimization Algorithms]] — related (group-normalised advantage replaces the learned one)
