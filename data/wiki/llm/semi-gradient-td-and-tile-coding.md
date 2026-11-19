---
title: Semi-Gradient TD and Tile Coding
tags: [llm, reinforcement-learning, concept]
summary: "With a parameterised value function, each RL update becomes a supervised example; bootstrapping targets make the update semi-gradient, linear semi-gradient TD(0) converges to the TD fixed point within 1/(1-gamma) of the best error, and tile coding with offset tilings is the book's practical feature construction."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-sutton-barto-rl-ch09-policy-prediction-approximation.md
  - data/raw/papers/2026-11-08-sutton-barto-rl-ch10-policy-control-approximation.md
---

# Semi-Gradient TD and Tile Coding

Chapter 9 of Sutton and Barto swaps the value table for a parameterised function v̂(s, w) and asks how to estimate state values from on-policy experience. Every update from a state s toward a target u is read as a supervised training example, so any approximator that can learn online is usable. Error is scored as the value error VE(w), the sum over states of μ(s)·(v_π(s) − v̂(s, w))², where μ is the on-policy distribution: how much of the time the policy spends in each state.

## Gradient Monte Carlo and semi-gradient TD

- **Gradient Monte Carlo** nudges w along ∇v̂ by α times the gap between the return and the current estimate.
- **Semi-gradient TD(0)** does the same with the bootstrapped target R + γv̂(S′, w). That target itself depends on w, and the update disregards this dependence, so it follows only part of the gradient and is not true gradient descent. The authors advise it when online, continual learning and speed matter. The tabular rule it generalises is on [[Temporal-Difference Learning, Sarsa and Expected Sarsa]].
- **Linear case.** With linear features, the weights of semi-gradient TD(0) settle at the TD fixed point, w = A⁻¹b, with A = E[x(x − γx′)ᵀ] and b = E[Rx]; its VE is no worse than 1/(1 − γ) times the smallest achievable VE (continuing case, on-policy, γ < 1). Away from the on-policy distribution, bootstrapping combined with approximation can diverge to infinity, a topic the book defers to chapter 11.
- **LSTD** (least-squares TD) forms sample estimates of A and b and solves for the fixed point in one step. Of the linear TD(0) variants it uses data most efficiently, yet it needs O(d²) memory and per-step compute where semi-gradient TD needs O(d), and it never forgets.

## The 1000-state random walk

States run from 1 to 1000, the walk starts at 500, each move jumps up to 100 states either way, and the terminal rewards are −1 and +1.

- Aggregating states into 10 blocks of 100 and running gradient Monte Carlo (α = 2×10⁻⁵, 100,000 episodes) ended close to the global VE minimum; about 1.37% of steps fall on the start state.
- Semi-gradient TD(0) ended with values farther from the truth than the Monte Carlo ones, while n-step TD with 20 groups of 50 states acted like the tabular version (see [[N-Step Bootstrapping]]).
- Tile coding with 50 tilings (each tile 200 states wide, successive tilings shifted 4 states, step size divided by 50) learned faster than one tiling, which is plain state aggregation; curves average 30 runs.
- On the same walk a Fourier basis outperformed polynomials of order 5, 10 and 20 under gradient Monte Carlo, and the authors steer away from polynomials for online use.

## Features and step size

- **Tile coding** is coarse coding built from offset partitions called tilings, so each tiling has exactly one active tile. With n tilings, α = 1/n learns a trained state's target in one trial, and α = 1/(10n) closes a tenth of the gap. For a k-dimensional continuous space the book reports offsetting by the first k odd integers (1, 3, 5, …) with the tiling count a power of 2 and at least 4k, and using hashing to save memory.
- **Step size.** To learn in roughly τ experiences with nearly the same feature vector, take α = 1/(τ·E[xᵀx]); this works best when feature vectors have nearly constant length. The authors call the 1/t schedule inappropriate for TD with approximation.
- **Interest and emphasis.** Interest I_t measures how much the value at time t matters, and emphasis M_t = I_t + γⁿM_{t−n} rescales the update. In a four-state reward process (+1 per step, interest 1 on the first state only, two aggregated parameters), two-step semi-gradient TD with them learns the first state's value exactly, w reaching (4, 2); without them both gradient Monte Carlo and two-step TD reach (3.5, 1.5) and value that state at 3.5.
- **Networks.** For deep networks the authors recommend dropout, batch normalisation, residual connections or convolutional structure. The convolutional example (LeCun et al. 1998 handwriting network, reported secondhand) has a first layer of six feature maps of 5×5 shared-weight units, needing 25 weights per map.

## Control with approximation (chapter 10)

- **Mountain Car.** Setup: linear q̂ over 8-tiling tile coding (4096-entry hash table), ε-greedy, 100 runs, step sizes 0.5/8 (n = 1) and 0.3/8 (n = 8). Semi-gradient n-step Sarsa learned faster and ended better at n = 8 than at n = 1. Among n = 1, 2, 4, 8, 16, with steps per episode averaged over the first 50 episodes, n = 4 did best early; standard errors grew from 0.5 at n = 1 to about 4 at n = 16. The multi-step return itself is on [[N-Step Bootstrapping]].
- **Optimistic starts.** All true values are negative (−1 per step), so zero initial action values drove heavy exploration even at ε = 0.
- **Average reward.** The differential semi-gradient form of Sarsa, run on an access-control queue with 10 servers (priorities 1, 2, 4, 8; a busy server frees with p = 0.06; α = β = 0.01, ε = 0.1; zero initial values; tabular; 2 million steps, one run) estimated an average reward near 2.31. It converges to differential values up to an arbitrary offset, which does not affect TD errors.
- **Why not discount.** In a continuing ergodic MDP the average of discounted returns equals r(π)/(1 − γ), so γ never changes how policies rank, and the authors conclude discounting plays no role in defining continuing control with approximation.
- **No improvement guarantee.** Function approximation loses the policy improvement theorem, and ε-greedification can yield a worse policy.

## Limits

- Only prediction is covered, for a fixed policy under on-policy data; control with approximation is chapter 10 and off-policy divergence chapter 11.
- VE may not suit the goal of finding a better policy. Convergence theory is mostly confined to tabular and linear settings and does not explain deep-network successes.
- The comment that backpropagation works poorly in deep networks without extra techniques belongs to the 2018 edition and has dated.
- The examples are single toy tasks, with few hyperparameters and no seeds beyond run counts in figure captions.
- The chapter 10 Mountain Car results use linear tile coding only, with no deep networks. Differential Sarsa has an arbitrary-offset limitation, and removing it is left as future research. The access-control example is one run, and the authors suspect too little data explains the fall at high free-server counts. The Figure 10.1 data came from Sarsa(λ), not plain Sarsa.

## See Also
- [[Temporal-Difference Learning, Sarsa and Expected Sarsa]] — prerequisite-for
- [[Deep Q-Network, Target Network and Experience Replay]] — related (a neural network as the approximator, with its own stabilisers)
- [[Reinforcement Learning Foundations]] — prerequisite-for
