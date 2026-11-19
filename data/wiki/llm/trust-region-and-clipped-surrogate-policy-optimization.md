---
title: Trust Region and Clipped Surrogate Policy Optimization
tags: [llm, reinforcement-learning, concept]
summary: "TRPO limits each policy update with a KL trust region solved by conjugate gradient and a line search; PPO replaces that machinery with a clipped probability-ratio objective that allows several minibatch epochs per batch. Both keep the new policy close to the one that collected the data."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-schulman-2015-trust-region-policy-optimization.md
  - data/raw/papers/2026-11-07-schulman-2017-proximal-policy-optimization-algorithms.md
  - data/raw/papers/2026-11-08-murphy-rl-ch03-policy-based-rl.md
  - data/raw/papers/2026-11-07-building-ai-agents-llms-rag-kgs-ch08-reinforcement-learning-ai-agents.md
  - data/raw/papers/2026-11-08-murphy-rl-ch05-multi-agent-rl.md
  - data/raw/papers/2026-11-08-murphy-rl-ch06-llms-rl.md
  - data/raw/papers/2026-11-07-winder-reinforcement-learning-ch06-beyond-policy-gradients.md
  - data/raw/papers/2026-11-08-xiao-foundations-llms-ch04-alignment.md
---

# Trust Region and Clipped Surrogate Policy Optimization

Both methods address one question: how far can a policy be moved using data sampled from the previous policy before the estimate stops being trustworthy? The shared ingredient is the **probability ratio** r_t(θ) = π_θ(a_t|s_t) / π_θold(a_t|s_t), which equals 1 at the old parameters. A surrogate objective weights each advantage by this ratio. TRPO limits the average KL between the old and new policy; PPO clips the ratio.

## TRPO: a hard KL constraint

Schulman et al. (2015) prove that maximising a surrogate objective minus a penalty tied to the maximum KL between old and new policy gives a guaranteed improvement in expected return (Theorem 1, using D_TV² ≤ D_KL). Murphy's survey gives the same bound in total-variation form and notes that a KL bound δ implies the total-variation constraint with δ = ε²/2.

The practical algorithm departs from the theory in three ways:

- the penalty becomes a hard constraint on the **average** KL over states;
- the surrogate is expanded to first order and the KL to second order, which gives a natural-gradient step with size sqrt(2δ / sᵀFs);
- the step direction comes from conjugate gradient, which sidesteps inverting the Fisher matrix, then a backtracking line search shrinks the step geometrically until the constraint is met and the objective has improved.

Two sampling schemes are used: *single path* (the discounted future reward along each simulated trajectory is the Q estimate) and *vine* (several actions and short rollouts from states along trunk trajectories, with common random numbers; this needs a simulator that can reset to a state).

## PPO: clip the ratio instead

PPO (Schulman et al. 2017) keeps a first-order method and optimises

L^CLIP(θ) = E_t[ min( r_t(θ) A_t, clip(r_t(θ), 1−ε, 1+ε) A_t ) ]

The clipped term makes the objective a pessimistic lower bound on the unclipped surrogate. Murphy's survey shows that for A ≥ 0 this reduces to min(rA, (1+ε)A) and for A < 0 to min(rA, (1−ε)A), and derives it as a simplification of the total-variation constraint, where E[TV] = ½ E|ratio − 1|. It requires the new policy's support to lie within the old policy's support. Each iteration has N parallel actors run the old policy for T steps and compute truncated [[Generalized Advantage Estimation]] advantages; K epochs of minibatch SGD on the surrogate follow (a value loss and an entropy bonus can be added), and the result becomes the new old policy. A variant with an adaptive KL penalty is the other form the paper compares.

Setup for the table below: seven MuJoCo tasks, each trained for 1M timesteps with three seeds, using tanh MLP policies of two 64-unit layers.

| Variant (7 MuJoCo tasks, normalised score) | Score (self-reported) |
|---|---|
| Clipping, ε = 0.2 | best of all variants tried |
| Clipping, ε = 0.1 or 0.3 | lower than ε = 0.2 |
| Adaptive KL penalty, d_targ 0.003 / 0.01 / 0.03 | 0.68 / 0.74 / 0.71 |
| Fixed KL penalty, β 0.3 / 1 / 3 / 10 | 0.62, 0.71, 0.72 and 0.69 respectively |
| No clipping, no penalty | negative (HalfCheetah ends worse than the random policy) |

## Reported comparisons (self-reported)

- Against TRPO, CEM, vanilla policy gradient, A2C and A2C with a trust region, clipped PPO does better in nearly every MuJoCo environment by 1M timesteps (ε = 0.2; shown as learning curves only).
- Atari (49 games trained for 40M frames, three trials): averaged over the whole of training PPO takes more games than A2C and ACER; scored on the last 100 episodes, ACER takes more games than PPO (28 to 19).
- TRPO's own results: both the single-path and vine variants solved every locomotion problem tried (five runs), whereas natural gradient with a fixed penalty never produced a forward hopping or walking gait. On Q*bert, one vine run scored 7732.5; single path scored 1973.5, DQN 1952 and UCC-I 20025. The Atari runs of 500 iterations each needed roughly 30 hours on 16 cores.

## Use in LLM training

- A book chapter on agents describes RLHF as three steps (collect human feedback, train a reward model, fine-tune with RL) and names PPO as the usual RL choice, since the aligned model is meant to stay near the original. The chapter gives ε = 0.2 as an example clip value and advises tuning ε, the learning rate and the batch size. It describes this as a claim; there is no experiment.
- Murphy's LLM chapter lists PPO beside GRPO, DAPO, GSPO, RLOO and REINFORCE++, and advises a per-token KL penalty to keep the policy near the reference; the KL term should go into the token-level reward, not the advantage. See [[RLHF Pipeline]] and [[Preference Optimization Algorithms]] for PPO within RLHF and the critic-free methods, and [[DAPO]] for an asymmetric-clip variant (ε_high 0.28 against ε_low 0.2).
- In two-player zero-sum games, Rudolph et al. (as reported by Murphy) attribute PPO's weak showing to an untuned entropy penalty: single-agent PPO uses 0 to 0.01, while those games call for an α of roughly 0.05 to 2.0. See [[Multi-Agent Reinforcement Learning]].
- Murphy notes that PPO needs action likelihoods, which is hard for diffusion policies; DPPO treats the denoising steps as an inner MDP and NCDPO fixes the noise and backpropagates through the chain.

## Practitioner guidance (Winder)

Winder's book chapter on off-policy and trust-region methods defines trust-region methods as picking a parameter-space region inside which gradient steps are considered reliable, with the step size adjusted as it goes. His recommendations, given as the author's view with no data, are to prefer trust-region methods when dynamics are unstable (where even a small policy change could be catastrophic), deterministic methods when dynamics are stable, plain algorithms with small networks if robustness is the goal, and TD3 over DDPG.

- He notes that Schulman et al. used a PPO clip range ε between 0.1 and 0.3, and reads the clipped objective as a lower bound: importance sampling is ignored when the policy is improving and included when it is getting worse (his interpretation of the chapter's figures).
- TRPO's KL constraint is solved with conjugate gradients, which he calls complex, and it cannot use a multihead network sharing policy and value outputs (explanation, no experiment).
- Citing Henderson et al., he reports that whether ACKTR or TRPO comes out ahead varies by environment; TRPO wins on Swimmer-v1 and loses on HalfCheetah-v1 (MuJoCo).
- Servo example (one simulated and one real servo, stable-baselines PPO2): for the fixed-goal task the default learning rate (2.5e-4) was much too low, and 0.05 solved it within a few updates. Most runs used minibatch size 2 or 4 and 32 or 64 steps per update. The random-goal task needed about 1,000 steps before the policy was reasonably stable. He advises tuning in a simulator before real hardware and using several episodes per update.

## Xiao and Zhu's RLHF recipe

For RLHF, Xiao and Zhu start the reward and value models from the pretrained LLM, while the reference and policy models begin from the instruction-tuned model. The PPO step subtracts a value-function baseline (the advantage, written as the temporal-difference error), clips the importance ratio, and subtracts a penalty for distance to the reference policy, written as the sum of log-probabilities under the policy minus the same under the reference.

## Limits

- PPO's ε and KL settings were tuned on a small base (seven MuJoCo tasks, three seeds, 1M timesteps). The paper reports no significance tests or baseline hyperparameters, and its wall-time, simplicity and robustness claims have no timing figures.
- Atari final-score results favour ACER; PPO's edge there is sample efficiency.
- PPO's claim that multiple epochs on the plain policy-gradient objective cause destructively large updates is not backed by results in the paper.
- TRPO's monotonic-improvement proof covers the penalised form with the theory's large coefficient. The practical constrained algorithm ignores advantage-estimation error, and the authors claim only that it tends to improve monotonically. The Atari results are single runs without error statistics, vine needs resettable simulators, the max-KL variant was tried only on cart-pole, and TRPO estimates Q by Monte Carlo with no learned value function.
- Murphy's chapter is a survey with no experiments of its own, and the agent-book chapter's RLHF coverage is a few paragraphs.
- Winder's only benchmark of his own is a one-servo toy task with no seeds, error bars or network sizes; his equations are images and his algorithm boxes were not recoverable. His chapter covers 2020-era continuous control, offers no LLM guidance, and labels some of its own explanations as speculation.
- Xiao and Zhu's chapter calls the reference policy theta_ref in prose but theta_old in a figure, writes the clipped objective without the baseline-subtracted clip in one equation, and its penalty is a sequence log-ratio rather than a per-token KL; the extraction also notes sign conventions differ between its gradient and loss forms.


## See Also
- [[Reinforcement Learning Foundations]] — prerequisite-for
- [[Generalized Advantage Estimation]] — prerequisite-for (the advantage estimator PPO and TRPO are paired with)
- [[RLHF Pipeline]] — extends (PPO as the RL step)
- [[Preference Optimization Algorithms]] — alternative-to (critic-free and direct alternatives to PPO)
- [[DAPO]] — extends (asymmetric clipping)
- [[Multi-Agent Reinforcement Learning]] — extends (MAPPO, PPO in zero-sum games)
- [[Policy Gradient Theorem and Compatible Function Approximation]] — prerequisite-for
