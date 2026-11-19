---
title: Policy Gradient Theorem and Compatible Function Approximation
tags: [llm, reinforcement-learning, concept]
summary: "Sutton et al. (1999) prove that the gradient of expected reward has no term for the derivative of the state distribution, that a compatible critic gives the exact gradient, and that a form of policy iteration with such a critic converges to a local optimum; the paper has no experiments."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-sutton-1999-policy-gradient-methods-reinforcement-learning.md
---

# Policy Gradient Theorem and Compatible Function Approximation

Sutton, McAllester, Singh et al. (NIPS 12, 1999) study a policy that has its own function approximator and is moved along the gradient of expected reward, where that gradient is estimated from experience through a learned value approximation, and ask if the procedure converges. They hypothesise that an approximate action-value or advantage function meeting a compatibility condition yields an unbiased gradient, so that policy iteration with function approximation reaches a local optimum.

## The three results

1. **Policy gradient theorem (Theorem 1).** For any MDP, in the average-reward or start-state formulation and with the policy differentiable in its parameters theta, the performance gradient is a weighted sum over states and actions: the state weight d(s), the derivative of pi in theta, and Q multiply together. The state distribution's own derivative does not enter. Written out: dρ/dθ = Σ_s d^π(s) Σ_a [dπ(s,a)/dθ] Q^π(s,a).
2. **Compatible approximation (Theorem 2).** If the approximate Q, f_w, satisfies the compatibility condition (the derivative of f with respect to w equals the derivative of pi with respect to theta divided by pi) and w has reached a least-squares optimum, then using f_w in place of Q gives the gradient exactly.
3. **Convergence (Theorem 3).** Policy iteration with a compatible differentiable approximator reaches a point at which the gradient vanishes. The conditions are bounded second derivatives of pi, bounded rewards and standard step sizes (alpha_k going to 0 with their sum infinite); the proof relies on Proposition 3.5 of Bertsekas and Tsitsiklis (1996). The authors describe it as the first proof, to a locally optimal policy, that converges for one form of policy iteration, one using general differentiable function approximation.

## Consequences the paper states

- Take a Gibbs (softmax) policy built linearly on features: its compatible f_w is a linear function of the same features, centred on the per-state mean, which makes it an approximation of the advantage (Q minus V).
- Adding any function of the state alone, a baseline, leaves both theorems unchanged because the policy's derivatives sum to zero over actions in every state, but it can change the variance of the estimator.
- REINFORCE's gradient estimate is unbiased and needs no value function, yet it is far slower to learn. The authors assert, with no experiment behind it, that rapid learning seems to require a learned value function that reduces variance.
- It extends Williams' REINFORCE and a tabular POMDP result of Jaakkola, Singh and Jordan to arbitrary differentiable approximators. In the authors' view VAPS (Baird and Moore) does not follow the performance gradient, hence cannot be expected to converge to a local optimum.

## Limits

- The paper is theory only; it has no experiments and so no empirical support for gains in speed or variance.
- Only a local optimum is guaranteed, and Theorem 3 concerns a policy-iteration variant in which f_w is assumed to be solved exactly every iteration.
- The compatibility condition restricts the critic's form, and practical critics usually violate it.
- The result assumes a stationary state distribution independent of the start state, bounded rewards and bounded second derivatives.
- The authors frame this as an early step toward convergence proofs for actor-critic methods; no such proof is given.

## See Also
- [[Reinforcement Learning Foundations]] — prerequisite-for
- [[REINFORCE with a Baseline]] — prerequisite-for (the estimator whose variance a learned critic is meant to reduce)
- [[Trust Region and Clipped Surrogate Policy Optimization]] — extends (builds on the policy gradient)
- [[Soft Actor-Critic and Maximum-Entropy RL]] — related
