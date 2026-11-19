---
title: REINFORCE with a Baseline
tags: [llm, reinforcement-learning, pattern]
summary: "REINFORCE (Williams 1992) updates each weight by a rate times an offset reinforcement times the characteristic eligibility, so the expected update follows the gradient of expected reward; any baseline independent of the current output leaves that expectation unchanged, and the gradient bandit is the same idea."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-williams-1992-simple-statistical-gradient-following-algorithms.md
  - data/raw/papers/2026-11-08-sutton-barto-rl-ch02-multi-armed-bandits.md
  - data/raw/papers/2026-11-08-sutton-barto-rl-ch13-policy-gradient-methods.md
  - data/raw/papers/2026-11-07-winder-reinforcement-learning-ch05-policy-gradient-methods.md
---

# REINFORCE with a Baseline

Williams (1992) looks for update rules for networks of stochastic units that, averaged over trials, climb the gradient of expected reinforcement, yet never compute or store an estimate of that gradient. The rules he finds form the REINFORCE class, where each weight changes by

Δw = α · (r − b) · e

with e = ∂ ln g / ∂w. Here α is a nonnegative rate (depending at most on the unit's weights and the time step), r is the reinforcement, b is a baseline, and e, the characteristic eligibility, is the log-derivative, taken with respect to that weight, of the probability (or density) that the unit emits its output. The paper gives the name as an acronym: REward Increment = Nonnegative Factor × Offset Reinforcement × Characteristic Eligibility. The general setting is on [[Reinforcement Learning Foundations]].

## What is proved

- **Theorem 1.** For every REINFORCE algorithm the expected update has a nonnegative inner product with the gradient of expected reinforcement; with all rates positive it is zero only where the gradient is zero, and with one shared rate the expected update is α times the gradient. Conditions: an associative immediate-reinforcement task, a feedforward net of stochastic units, a baseline conditionally independent of the unit's output given weights and input, and stationary, independent input and reward distributions.
- **A baseline costs nothing in expectation.** Under the same conditions and a shared rate, (r − b)·∂ln g/∂w is an unbiased estimate of the gradient whatever baseline satisfies the independence condition, since the output probabilities' derivatives sum to zero.
- **Adaptive baselines.** The baseline can be a running prediction of the reinforcement to come (reinforcement comparison), provided it is never computed from the present output or present reward. For a Bernoulli-logistic unit the rule is Δw = α(r − r̄)(y − p)x, with r̄ an exponential average of earlier rewards.
- **Older algorithms fit.** L_R-I and A_R-I are REINFORCE with b = 0, their Bernoulli-logistic eligibility being (y − p)x. For exponential-family densities with mean μ, the log-derivative with respect to μ is (y − μ)/σ², which covers the Bernoulli, normal, Poisson and exponential cases.
- **Episodes.** For episodic tasks the eligibilities are summed across the k steps before multiplying by (r − b), which shares credit evenly over time steps; Williams found this especially slow.

## Why the baseline matters in practice

Theory speaks only to the direction of the expected update and offers no way to rank baselines. A lone Bernoulli unit with just a bias weight, zero baseline and always-positive reinforcement does a biased random walk and can end at the worse output; a baseline between the two reward values always pushes toward the better one. From Sutton (1984) and later work, with no figures, Williams reports that an adaptive baseline can speed convergence a great deal and that reinforcement comparison was the best algorithm tried on single-Bernoulli-unit tasks. The variance-minimising baseline differs from the mean reinforcement, but Dayan (1990) saw only a slight gain in speed. With no baseline, a Gaussian unit under always-nonnegative reward can shrink σ to 0 before μ gets to the top of a hill.

## The same rule on a bandit

In Sutton and Barto's chapter 2 the gradient bandit is a special case of this gradient-following class: preferences H(a) feed a softmax policy, the chosen action's preference rises by α(R − R̄)(1 − π) and every other action's falls by α(R − R̄)π, where R̄ is the reward baseline. Their derivation shows this is stochastic gradient ascent on expected reward for any baseline that does not depend on the action, and they cite Williams for the general class. On the 10-armed testbed with true values shifted to a mean of +4 (α = 0.1 and 0.4), the version with a baseline was unaffected by the shift and the version without it was significantly degraded. The authors advise the baseline because it reduces variance while leaving the expected update alone. Other bandit methods are on [[Thompson Sampling and Bandit Regret]].

## In the episodic and actor-critic form

Sutton and Barto's chapter 13 restates the idea for full MDPs. The policy gradient theorem says performance's gradient is proportional to a sum over states, weighted by how often each occurs, of q multiplied by ∇π; the state distribution itself is never differentiated. Setup: episodic case, J(θ) = v_π(s0), γ = 1. The constant of proportionality is the average episode length in the episodic case and exactly 1 in the continuing case, where the theorem keeps its form with average reward and differential return.

- **REINFORCE here** is a Monte Carlo, episodic-only update, θ moves by α·G_t·∇ln π(A_t|S_t), with a γ^t factor in the boxed algorithm for discounted problems. The authors credit Thomas (2014) with first noting that factor. It is unbiased in expectation but can have high variance and learn slowly.
- **Baseline.** Any b(s) that does not vary with the action leaves the expected update unchanged, because b(s) times the sum over actions of ∇π is zero, and it can cut variance a lot. For a linear baseline the rule of thumb is α_w = 0.1 / E[‖∇v̂‖²].
- **One-step actor-critic** swaps the Monte Carlo return for δ = R + γV(S') − V(S), with learned V as the critic. This adds bias, though bootstrapping is not the only cause, since a Monte Carlo critic is biased as well. The family is sometimes called advantage actor-critic.
- **Short corridor (Example 13.1).** Setup: switched-action gridworld, reward −1 per step, identical features for every state, x(s,right) = [1,0] and x(s,left) = [0,1]. The best stochastic policy takes right with probability about 0.59, for a value of about −11.6. With ε = 0.1, ε-greedy is limited to two policies whose start-state values are below −44 and −82.
- **Soft-max versus ε-greedy.** Soft-max over action preferences can approach a deterministic policy and allows arbitrary action probabilities, which ε-greedy cannot.
- **Gaussian policy** for continuous actions: μ is linear in features, μ = θ_μᵀx_μ(s), and σ = exp(θ_σᵀx_σ(s)).
- **Step sizes (Figures 13.1 and 13.2).** Setup: short corridor, v̂(s,w) a single component, 100 runs of 1000 episodes. The baseline version learns much faster, with α_θ = 2⁻⁹ and α_w = 2⁻⁶ read off the figure labels, while plain REINFORCE did best at α = 2⁻¹³.

Winder's chapter 5 compares the variants on CartPole with a linear four-weight policy, his own runs, with gamma and rates missing from the extracted text. The baseline here is a rolling average of rewards. REINFORCE with it learned slightly more stably than plain REINFORCE, and 50 runs were needed to see that. His n-step actor-critic, given a raised policy rate, used a linear critic over 605 tile-coded features (10 cells on each of pole angle and angular velocity, with 5 overlapping tilings) and levelled off near reward 400; the Monte Carlo baseline agent could not be sped up. With the policy decay rate fixed at an unstated value, a state-value decay of about 0.1 worked best, 0.01 was better in the long run and 0.5 was unstable.

## Limits

- Williams says the class lacks a general convergence theory and, like all gradient methods, seems prone to false optima. L_R-I drifts toward the best action on average yet reaches an inferior one with nonzero probability, so Theorem 1 cannot be read as a convergence result.
- The theorems are silent on variance. The setting assumes stationary, independent inputs and rewards and immediate reinforcement, with only the episodic extension beyond it.
- Simulation evidence is borrowed from other work or called preliminary, with no numbers, hyperparameters, seeds or datasets. REINFORCE is typically very slow even when it works.
- Chapter 13 covers tabular and linear teaching examples only, with no PPO, trust region, GAE or LLM material, and the authors concede policy gradient theory is in places less developed than that for action-value methods. The policy step size is hard to set and depends on the reward range and the parameterization.
- Winder's CartPole runs are simple, he expects little difference there between REINFORCE and a baseline, and seeds and hardware are unstated.
- The bandit results come from one stationary Gaussian 10-armed testbed, and its parameter study is shown only as plots.

## See Also
- [[Thompson Sampling and Bandit Regret]] — related (other bandit methods)
- [[Preference Optimization Algorithms]] — related (another family built on a baseline-style signal)
- [[Reinforcement Learning Foundations]] — prerequisite-for
- [[MIXER Sequence-Level Training and Exposure Bias]] — instance-of
- [[Deep RL Dialogue Generation Rewards]] — instance-of
- [[Policy Gradient Theorem and Compatible Function Approximation]] — extends
