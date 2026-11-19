---
title: Eligibility Traces and TD(lambda)
tags: [llm, reinforcement-learning, concept]
summary: "An eligibility trace is a decaying memory vector that lets a TD error update recently visited states, so TD(lambda) interpolates between one-step TD (lambda=0) and Monte Carlo (lambda=1); the same trace ideas are mapped by Sutton and Barto onto stimulus traces in animal learning and onto dopamine-driven learning."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-sutton-barto-rl-ch12-eligibility-traces.md
  - data/raw/papers/2026-11-08-sutton-barto-rl-ch14-psychology.md
  - data/raw/papers/2026-11-08-sutton-barto-rl-ch15-neuroscience.md
  - data/raw/papers/2026-11-08-sutton-barto-rl-ch16-applications-case-studies.md
  - data/raw/papers/2026-11-08-ahilan-2023-succinct-summary-reinforcement-learning.md
  - data/raw/papers/2026-11-07-winder-reinforcement-learning-ch03-temporal-difference-learning-q-learning-and-n.md
---

# Eligibility Traces and TD(lambda)

Chapter 12 of Sutton and Barto looks for a way to join TD and Monte Carlo methods, running efficiently and online, in prediction and control, on and off policy. Attaching traces to any TD method (Q-learning, Sarsa) gives the join: lambda = 1 behaves as Monte Carlo and lambda = 0 as one-step TD. A summary paper (Ahilan 2023) frames the endpoints similarly: TD(0) bootstraps, adding bias but generally cutting variance relative to Monte Carlo, and as n grows the n-step return approaches the unbiased Monte Carlo return. The one-step update moves v(s_t) by alpha times the TD error r + gamma v(s_{t+1}) minus v(s_t).

## The mechanism

- **Lambda-return**: an average over all n-step returns where the n-step return gets weight (1 - lambda) lambda^(n-1). Updating a state from what happens after it is the forward view.
- **Eligibility trace**: a vector z, shaped like the weights, that decays at rate gamma times lambda and has the gradient of the current value estimate added each step. Weights then move by alpha times the TD error times z, so the present TD error is assigned to recently visited states; this is the backward view, and TD(lambda) is the backward view with accumulating traces.
- **True online TD(lambda)** uses dutch traces and reproduces the online lambda-return weights exactly. With linear function approximation it costs O(d) per step like TD(lambda), about 50% more computation, because the trace update needs one more inner product.
- **Replacing traces** set a component to 1 when its feature is active and suit only tabular or binary features. With nonlinear function approximation dutch traces cannot be used, so accumulating traces stay.
- Sarsa(lambda) brings traces into control. The chapter also treats variable lambda and gamma, and off-policy variants (control variates, Tree-Backup(lambda), GTD, GQ, HTD, Emphatic TD).

## Results and guidance from the chapter

- For on-policy, continuing, discounted linear TD(lambda) with a shrinking step size, the asymptotic error is within a factor (1 - gamma lambda)/(1 - gamma) of the best achievable. That factor is worst at lambda = 0 and best at lambda = 1, yet lambda = 1 is frequently the weakest setting in practice (reported).
- On the 19-state random walk (averaged over the first 10 episodes and the 19 states), TD(lambda) equals the offline lambda-return algorithm at the best step size or lower, but does much worse and may be unstable at higher ones. The online lambda-return algorithm edges ahead of the offline one.
- On four test problems (a random walk with TD(lambda); cart and pole, Mountain Car and Puddle World with Sarsa(lambda) and tile coding), middling lambda values did best and values near Monte Carlo fell off sharply (reported). The authors recommend a middling lambda, traces when data is scarce or reward arrives late, and plain one-step methods when simulated data costs little.
- Winder's practical advice for nontrivial tasks is lambda above 0 but below 1, since lambda = 1 made all first-state actions converge to about the same value in his gridworld (asserted by the author, not shown with numbers).
- With neural networks trained by backpropagation, traces about double memory and per-step computation; in a table, only recently visited states need to be touched.
- Off-policy traces repair the expected target but leave the update distribution unfixed. Because lambda below 1 still bootstraps, [[The Deadly Triad]] applies, and stability is assured only for tabular, state-aggregation and similar settings.

As the applications chapter tells it, TD-Gammon paired TD(lambda) with a backpropagation network (40 hidden units, self-play, afterstate move choice, an update every move). Its raw 198-unit board encoding reached the level of the best earlier programs after roughly 300,000 self-play games, and a later version (80 hidden units, 1.5 million games of training) won by 6 points over 20 games against a human player (reported secondhand). In the thermal-soaring study traces gave no help.

## Animal learning and dopamine

Chapter 14 connects these ideas to psychology and reports the book's account of the experiments. The Rescorla-Wagner model corrects errors using prediction error and accounts for blocking. The TD model of classical conditioning swaps its trial-level update for real-time TD(lambda), and setting gamma to 0 recovers Rescorla-Wagner. Since the TD error contains gamma v(S_{t+1}) minus v(S_t), the model yields second-order and higher-order conditioning; in a simulated second-order run, phase-one training raised the first stimulus's associative strength to 1.65 (TD model, presence representation). For delayed reward RL has two credit-assignment devices, traces and learned value functions, which parallel stimulus traces and secondary reinforcement in animals; in actor-critic the critic's TD error serves the actor as conditioned reinforcement.

Chapter 15 reports the reward prediction error hypothesis: phasic dopamine activity tracks the TD error rather than the reward, based on comparing monkey recordings with a TD model using a complete-serial-compound representation. In the idealised TD(0) account, after learning the error is zero at the reward and positive at the earliest predictor, and when the reward is omitted it is minus the reward. Actor and critic in an actor-critic with traces differ only in their trace: non-contingent for the critic, contingent for the actor. At corticostriatal synapses, reward-modulated STDP produces lasting change only when a neuromodulator pulse lands within a window of up to 10 seconds.

## Limits

- Chapter 12's Mountain Car, random-walk and Figure 12.14 results are plots only, run counts are partly given, and there is no theory for picking lambda (varying it reliably is described as unclear how to do).
- The practical value of the new off-policy trace methods is unestablished, and their variance is expected to be high. GAE and policy-gradient advantage estimation are outside the chapter.
- The psychology chapter says RL is not intended to model animal behaviour in detail and that the TD model is neither complete nor perfect. Its accounts are qualitative, with no effect or sample sizes, and its few numbers come from simulations adapted from earlier work. The presence and complete-serial-compound representations are admitted to be unrealistic.
- The neuroscience chapter's authors say they are not neuroscientists. It does not treat rival views, such as dopamine signalling reward prediction errors without being TD errors; early-reward timing departs from the model; the dopamine neurons likely do not act as one scalar broadcast; and cited findings stop around 2016.
- The applications chapter summarises other groups' work, and every number in it is reported rather than measured by the authors.
- The Ahilan summary is secondary (derived from lecture and textbook material), has no experiments and does not cover RLHF or LLM applications.

## See Also
- [[Reinforcement Learning Foundations]] — prerequisite-for
- [[The Deadly Triad]] — related (off-policy traces with bootstrapping)
- [[Deep Q-Network, Target Network and Experience Replay]] — related
- [[N-Step Bootstrapping]] — prerequisite-for
- [[Temporal-Difference Learning, Sarsa and Expected Sarsa]] — prerequisite-for
