---
title: Reinforcement Learning Foundations
tags: [llm, reinforcement-learning, concept]
summary: "The MDP tuple (S, A, P, R, γ), the Markov property that makes RL tractable, the four algorithm families, and the exploration/exploitation tension — with how each maps onto LLM training and agentic tool use."
updated: 2026-11-19
sources:
  - data/raw/repos/learn-ai-engineering/generative-ai--01-llm-fundamentals--rl.md
  - data/raw/repos/learn-ai-engineering/interviewing--notes--rl.md
  - data/raw/papers/2026-11-08-fundamentals-of-deep-learning-ch09-deep-reinforcement-learning.md
  - data/raw/papers/2026-11-08-bandit-algorithms-ch38-markov-decision-processes.md
  - data/raw/papers/2026-11-08-sutton-barto-rl-ch01-introduction.md
  - data/raw/papers/2026-11-08-sutton-barto-rl-ch02-multi-armed-bandits.md
  - data/raw/papers/2026-11-08-sutton-barto-rl-ch03-finite-markov-decision-processes.md
  - data/raw/papers/2026-11-08-sutton-barto-rl-ch04-dynamic-programming.md
  - data/raw/papers/2026-11-08-sutton-barto-rl-ch05-monte-carlo-methods.md
  - data/raw/papers/2026-11-08-sutton-barto-rl-ch06-temporal-difference-learning.md
  - data/raw/papers/2026-11-08-sutton-barto-rl-ch07-n-step-bootstrapping.md
  - data/raw/papers/2026-11-08-sutton-barto-rl-ch08-planning-learning-tabular-methods.md
  - data/raw/papers/2026-11-08-sutton-barto-rl-ch09-policy-prediction-approximation.md
  - data/raw/papers/2026-11-08-watkins-1989-learning-delayed-rewards.md
  - data/raw/papers/2026-11-08-williams-1992-simple-statistical-gradient-following-algorithms.md
  - data/raw/papers/2026-11-08-murphy-rl-ch01-introduction.md
  - data/raw/papers/2026-11-08-winder-reinforcement-learning-ch01-why-reinforcement-learning.md
  - data/raw/papers/2026-11-08-winder-reinforcement-learning-ch02-markov-decision-processes-dynamic-programming.md
---

# Reinforcement Learning Foundations

Unlike supervised learning (a labeled answer key) or unsupervised learning (patterns in
unlabeled data), RL learns by **trial and error** — an agent interacting with an unknown
environment to maximize cumulative reward.

## The MDP

The mathematical foundation: a tuple `(S, A, P, R, γ)`.

| Symbol | Meaning |
|---|---|
| **S** | State space — situations the agent can observe |
| **A** | Action space — decisions available |
| **P(s'\|s, a)** | Transition function — probability of reaching `s'` from `s` via `a` |
| **R(s, a)** | Reward function — scalar feedback after acting |
| **γ** | Discount factor (0 ≤ γ ≤ 1) — weight on future vs immediate reward |

**The Markov property:** the next state depends only on the current state and action, not
the full history. This is the assumption that makes RL tractable — without it, the policy
would have to be a function of an unbounded trajectory rather than a fixed-size state.

It is also the assumption most often violated in practice by LLM agents, where "state"
is a context window that manifestly *is* the history. The practical consequence is that
what an agent can learn to do is bounded by what its state representation actually
captures — a point that recurs in [[Context Engineering]] terms as the question of what
belongs in the window.

## Core components

**Agent** (the learner), **environment** (the world), **state** (current observation),
**action** (the decision), **reward** (scalar feedback), and **policy π** — the strategy
mapping states to actions, and the thing actually being optimized. Policies are either
deterministic (`π(s) → a`) or stochastic (`π(a|s) → [0,1]`).

## Algorithm families

| Family | Learns | Examples |
|---|---|---|
| **Value-based** | Expected long-term return of states or state-action pairs, then acts greedily | Q-Learning, DQN |
| **Policy-based** | The policy directly, via `∇E[R]`, with no explicit value function | Policy gradient |
| **Actor-critic** | Both — an actor picks actions, a critic estimates value as a lower-variance update signal | PPO (dominant today) |

Cross-cutting: **model-free** agents learn purely from experience; **model-based** agents
learn `P(s'|s,a)` and plan against it — more sample-efficient, but only as good as the
learned model.

The actor-critic split is worth holding onto, because it explains a structural fact about
[[Preference Optimization Algorithms]]: the critic is the component GRPO removes (using a
sampled group's mean as the baseline instead), and the critic is one of the four resident
models that make PPO expensive.

## Value functions, returns and the Bellman equations

Sutton and Barto (2nd ed., chapters 1 and 3) name four elements: a policy, a reward signal, a value function and, optionally, a model. Their reward hypothesis holds that every goal or purpose can be expressed as maximising the expected total of one scalar signal; reward should say what to achieve, not how, and subgoals should not be rewarded. The discounted return is a γ-weighted sum of future rewards and obeys the recursion return = next reward + γ × next return; a constant reward of +1 gives 1/(1 − γ). The state-value and action-value functions are the expected return from a state, or from a state-action pair, under a policy. The Bellman equation writes the state value as a policy-weighted average, over actions and outcomes, of reward plus γ times the successor's value; the optimality equation replaces the average over actions with a max, and a policy that is greedy with respect to the optimal values is itself optimal. On a 5x5 gridworld (off-grid -1, A to A' +10, B to B' +5, gamma 0.9, equiprobable policy) state A is valued 8.8 under the random policy, below its immediate reward of 10, and the best state's optimal value is 24.4. Solving the optimality equation outright requires known dynamics, sufficient computation and the Markov property, a combination the chapter says is rare; backgammon, at roughly 10^20 states, is out of reach.

## Three ways to learn values, and where each leads

- **Dynamic programming** (chapter 4) computes optimal policies from a perfect model: iterative policy evaluation, policy improvement (a new policy whose one-step action values are nowhere below the old state values is at least as good everywhere), policy iteration, and value iteration (evaluation cut to one sweep). Policy iteration terminates in finitely many iterations on a finite MDP; DP's running time for finding an optimal policy is polynomial in the state and action counts, even though the number of deterministic policies grows as k^n. Asynchronous value iteration converges if gamma is below 1 and every state is updated infinitely often. The authors describe almost all RL methods as generalized policy iteration (evaluation and improvement processes interacting at any granularity). In the 4x4 gridworld (undiscounted, -1 per step, equiprobable random policy) the greedy policy after the first evaluation was already optimal. Practices they give: update in place, warm-start each evaluation, and favour asynchronous updates on large state spaces.
- **Monte Carlo** (chapter 5) learns from sampled episodes with no model: first-visit and every-visit averaging, Monte Carlo ES (exploring starts), and on-policy epsilon-soft control. It is defined for episodic tasks and updates only when an episode ends. On blackjack (200 states, infinite deck), first-visit evaluation of "stick on 20 or 21" was well approximated after 500,000 games, and Monte Carlo ES found a policy that agrees with Thorp's basic strategy apart from a one-notch difference when the player holds a usable ace.
- **Temporal-difference learning** bootstraps from the next estimate and needs neither a model nor a finished episode: see [[Temporal-Difference Learning, Sarsa and Expected Sarsa]], the off-policy [[Q-Learning]] update, [[N-Step Bootstrapping]] for the span between the two, [[Dyna Planning]] for adding a learned model, and [[Semi-Gradient TD and Tile Coding]] for replacing the table with a parametric function.

### Off-policy Monte Carlo and importance sampling

Off-policy methods evaluate a target policy `pi` from data generated by a different behaviour policy `b`; coverage requires `pi(a|s) > 0` to imply `b(a|s) > 0`. Each return is scaled by the importance-sampling ratio, the product of `pi(A_k|S_k)/b(A_k|S_k)`. Ordinary importance sampling averages the scaled returns: it is unbiased but has unbounded variance. Weighted importance sampling divides by the sum of ratios: it is biased (the bias goes to zero asymptotically) and the authors advise it in practice. On a single blackjack state (dealer shows 2, player holds 13 with a usable ace; the target policy sticks only on 20 or 21, the behaviour policy picks hit or stick with equal chance; true value about −0.27726 estimated by running the target policy for a hundred million episodes) both approximated the value after 1,000 episodes (100 runs of 10,000 episodes), with the weighted version far lower in error early. On a one-state looping MDP ordinary importance sampling failed to converge after millions of episodes, while the weighted version gave exactly 1 after the first episode ending in left. Off-policy Monte Carlo control learns only from episode tails where the remaining actions are greedy, and the authors say experience is insufficient to know how serious that is. The same ratio drives the off-policy n-step methods on [[N-Step Bootstrapping]].

## Policy gradients and bandits

The simplest case of choosing among actions is the k-armed bandit of chapter 2, solved with epsilon-greedy, optimistic initial values, UCB and gradient bandits (other bandit methods are on [[Thompson Sampling and Bandit Regret]]). The gradient bandit is stochastic gradient ascent on expected reward, the same update as [[REINFORCE with a Baseline]].

Under the average-reward criterion, the quantities are the gain, the average-reward Bellman optimality equation and the MDP's diameter; regret bounds in those terms are on [[UCRL2 Average-Reward Regret]].

## Exploration versus exploitation

Should the agent **exploit** the best known action, or **explore** actions that might pay
off more later? Three standard answers:

- **ε-greedy** — random action with probability ε, otherwise exploit
- **UCB** — prefer actions with high uncertainty, to reduce that uncertainty faster
- **Entropy regularization** (SAC, GRPO) — an entropy bonus in the reward, rewarding
  diverse action distributions

**In LLM contexts, temperature sampling at inference time is the primary exploration
mechanism during data collection.** This is the operational form the tension takes: too
low a temperature and the rollouts are near-duplicates carrying little training signal;
too high and they leave the region where the reward model is valid.

## Where RL enters LLM training

Two distinct stages, often conflated:

1. **RLHF alignment (post-pretraining)** — the LLM *is* the policy, each token is an
   action, the reward model scores completed responses. See [[RLHF Pipeline]].
2. **Agentic RL (tool use, retrieval, reasoning)** — the LLM takes multi-step actions in
   an environment (browser, code executor, knowledge base), with task completion as the
   reward. See [[RL for Retrieval Policies]].

The difference that matters: in (1) the environment is trivial (a single generation step)
and the difficulty is in the reward model; in (2) the reward is often obvious (did the
task complete?) and the difficulty is credit assignment across a long trajectory.

## Deep RL in a 2017-era textbook

*Fundamentals of Deep Learning* chapter 9 gives rules of thumb: a discount factor between 0.97 and 0.99, and annealing epsilon downward, exploring early and exploiting late (typical runs go from 0.99 down to 0.1 across 10,000 scenarios; the authors report that fixed values did poorly on a CartPole policy-gradient agent). It states the Q-function and Bellman equation and builds a policy-gradient agent and a DQN agent; the DQN mechanism is on [[Deep Q-Network, Target Network and Experience Replay]]. It also reports A3C learning Atari Breakout in under 12 hours against 3 to 4 days for DQN, and UNREAL about 10 times faster than A3C on Labyrinth (both reported secondhand).

## Framing, shaping and practice notes

- **Taxonomy.** Murphy's introduction names the canonical models as the POMDP, the MDP, goal-conditioned and contextual MDPs, the contextual bandit, the belief-state MDP, and optimisation treated as a decision problem. The exact solution of a POMDP is stated to be wildly intractable, recurrent policies do not deliberately plan to gather information, and frame stacking cannot capture long-range dependencies.
- **Reward shaping.** Potential-based shaping, F = γΦ(s′) − Φ(s), leaves the optimal policy unchanged, and in the tabular case it is equivalent to initialising V(s) = Φ(s). Winder warns that reward design is the main hazard, since agents optimise the wrong thing, and advises keeping the reward as simple as possible.
- **Exploration.** Every action keeps at least probability ε/|A| under ε-greedy, so it stays suboptimal until ε is annealed to 0. Boltzmann exploration varies smoothly with the estimates instead.
- **Reporting.** For aggregating across environments such as Atari games, Murphy relays the advice to use the interquartile mean, the mean of samples between the 25th and 75th percentiles, with bootstrap or Gaussian uncertainty.
- **Discount.** Typical values in nontrivial problems run from 0.9 to 0.99, per Winder's guidance without data. Murphy's rule is γ = 1 − 1/T for a horizon near T steps; with γ = 0.99, a terminal reward of 1.0 reached in 15 steps is worth about 0.86.
- **When to use RL.** Winder says it fits complex sequential decisions aimed at a long-term goal, and advises the simplest solution that works.

## Limits

- The *Fundamentals of Deep Learning* chapter prints no numeric results, and its code is TensorFlow 1.x with known bugs. It covers only 2013 to 2016 methods; PPO, which this page calls dominant, and RLHF are absent.
- The Sutton and Barto chapters are the 2018 edition and cover the tabular case (chapters 1 to 8) or on-policy prediction with approximation (chapter 9); control with approximation and off-policy divergence are in later chapters not covered here.
- Their worked examples (gridworlds, blackjack, random walks) are small and several results are given only in figures. Monte Carlo ES convergence is described as a basic open theoretical question; the authors say it is unclear which of policy iteration and value iteration is better overall; classical DP's perfect-model assumption makes it of limited use in RL itself; the DP million-state capacity reflects 2018 hardware.
- Murphy's chapter 1 is an introductory survey with no experiments of its own; its numbers are worked examples or quoted. Winder's chapters 1 and 2 are informal, written in 2020 (before RLHF and LLM use), and rest on toy simulations with several parameter values given only in figures; his chapter 2 lists dynamic programming's caveats (needs discounting, heavy computation for many states, a sample from every state-action pair, and transition probabilities).

## See Also
- [[Temporal-Difference Learning, Sarsa and Expected Sarsa]] — extends (bootstrapped value learning)
- [[Q-Learning]] — extends (off-policy action-value control)
- [[N-Step Bootstrapping]] — extends
- [[Dyna Planning]] — extends (model-based planning with Q-learning)
- [[Semi-Gradient TD and Tile Coding]] — extends (parametric value functions)
- [[REINFORCE with a Baseline]] — extends (the policy-gradient update)
- [[RLHF Pipeline]] — instance-of (the LLM-as-policy formulation)
- [[Preference Optimization Algorithms]] — extends (actor-critic and what each method removes)
- [[Multi-Agent Reinforcement Learning]] — extends (the same MDP with multiple interacting policies)
- [[RL for Retrieval Policies]] — instance-of (RAG as a sequential decision process)
- [[Reward Hacking and Overoptimization]] — related (what goes wrong when the reward is a learned proxy)
- [[RL Training Frameworks for LLMs]] — extends (the distributed systems that run these algorithms on LLMs)
- [[Training-Agent Disaggregation]] — extends (traces of an existing agent as MDP rollouts for an external trainer)
- [[Post-Training for Agents]] — extends (RL applied to tool-using LLM agents)
- [[Reflection in Pre-Training]] — related
- [[RLMF Metacognitive Advantage Scaling]] — related
- [[Multi-Agent Evolve Self-Play]] — instance-of
- [[Autodata Agentic Self-Instruct]] — instance-of
- [[CodeRL Unit-Test Actor-Critic]] — instance-of
- [[Foundation Models as Decision Makers (MDP View)]] — extends
- [[Deep Q-Network, Target Network and Experience Replay]] — instance-of (value-based deep RL)
- [[Soft Actor-Critic and Maximum-Entropy RL]] — extends
- [[Imitation Learning and Inverse RL]] — extends
- [[Hierarchical Reinforcement Learning]] — extends
- [[RL Reward and State Engineering]] — related
- [[Operational Reinforcement Learning]] — extends
- [[Eligibility Traces and TD(lambda)]] — extends
- [[The Deadly Triad]] — extends
- [[Arcade Learning Environment]] — instance-of
- [[DreamerV3 World Model with Fixed Hyperparameters]] — extends
- [[Bandit Regret Lower Bounds]] — related (exploration cost in the one-state case)
- [[UCRL2 Average-Reward Regret]] — extends (regret for learning an unknown MDP)
- [[Trust Region and Clipped Surrogate Policy Optimization]] — extends (policy-gradient family: TRPO and PPO)
- [[Generalized Advantage Estimation]] — extends (the bias-variance advantage estimator)
- [[GRPO Group Relative Policy Optimization]] — extends
- [[RLVR Pass@k Reasoning Boundary]] — related
