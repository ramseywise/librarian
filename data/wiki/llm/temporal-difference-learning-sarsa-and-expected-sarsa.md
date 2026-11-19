---
title: Temporal-Difference Learning, Sarsa and Expected Sarsa
tags: [llm, reinforcement-learning, concept]
summary: "TD learning updates a value estimate from the next step's estimate instead of a full return; Sarsa, Q-learning and Expected Sarsa differ only in the target they bootstrap from, which decides whether the learned policy accounts for its own exploration."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-sutton-barto-rl-ch01-introduction.md
  - data/raw/papers/2026-11-08-sutton-barto-rl-ch06-temporal-difference-learning.md
  - data/raw/papers/2026-11-07-winder-reinforcement-learning-ch03-temporal-difference-learning-q-learning-and-n.md
---

# Temporal-Difference Learning, Sarsa and Expected Sarsa

Sutton and Barto (2nd ed.) treat temporal-difference (TD) learning as learning from raw experience by bootstrapping: an estimate is updated partly from another learned estimate. The quantity driving each update is the TD error, δ = R + γV(S′) − V(S), where S′ follows S; the prediction rule (TD(0)) moves V(S) toward the bootstrapped target by a step α times that error. It needs no model, and unlike Monte Carlo it does not wait for an episode to end; the wider setting is on [[Reinforcement Learning Foundations]].

## The origin in chapter 1

Chapter 1 introduces the idea with tic-tac-toe. One table entry per board state holds the estimated probability of winning; terminal states with three Xs are set to 1, three Os or a full board to 0, and every other state starts at 0.5. After a greedy move, the earlier state's value is shifted a fraction α of the way toward the later state's value (V(S_t) ← V(S_t) + α[V(S_t+1) − V(S_t)]); exploratory moves trigger no update. With the step size reduced over time the authors assert (without proof or measurement) that this converges to the true win probabilities against a fixed opponent, and that keeping the step size above zero lets it track a slowly changing opponent.

## TD versus Monte Carlo

- On a 5-state random walk (states A to E, start at C, reward +1 only on the right exit, undiscounted, values initialised to 0.5), TD(0) beat constant-step-size Monte Carlo in RMS error across step sizes, averaged over 100 runs.
- With batch updating (every episode seen so far is replayed, with α small enough to converge), TD(0) came out ahead of constant-α Monte Carlo on the same walk throughout. The two settle on different answers: Monte Carlo on the sample-average returns, TD(0) on the value that would be exact if the maximum-likelihood model of the observed transitions were the true process (the certainty-equivalence estimate). In the book's eight-episode example both give V(B) = 3/4, but V(A) is 3/4 under TD and 0 under Monte Carlo.
- Solving for that estimate directly by matrix methods costs on the order of n² memory and n³ computation over n states, whereas TD approximates it using memory of order n.
- The authors advise TD(0) over constant-step-size Monte Carlo when episodes are long, when the task is continuing, or when exploratory actions occur. They state that no proof that TD learns faster than Monte Carlo exists.

## Three control updates

For control the same bootstrapping is applied to action values. The methods differ only in the term that stands in for the next state's value.

| Method | Update target | Policy it learns about |
|---|---|---|
| Sarsa | R + γQ(S′, A′) with the action actually taken next | the behaviour policy (on-policy) |
| Q-learning | R + γ · max over a of Q(S′, a) | the greedy policy (off-policy); see [[Q-Learning]] |
| Expected Sarsa | R + γ · Σ over a of π(a∣S′)Q(S′, a) | whichever policy `pi` is used in the expectation |

If its target policy is greedy while behaviour explores, Expected Sarsa coincides with Q-learning, which makes it a generalisation of Q-learning; compared with Sarsa it takes out the variance introduced by sampling the next action. Sutton and Barto advise it over Sarsa when the extra computation is affordable.

## What the examples show

- **Windy gridworld** (undiscounted, -1 per step, epsilon 0.1, alpha 0.5, Q initialised to 0, per-column wind): epsilon-greedy Sarsa holds average episode length near 17 steps against an optimum of 15, because exploration keeps costing steps, read after 8,000 time steps. Monte Carlo is awkward here, the authors note, because some policies never terminate; Sarsa instead finds out during the episode that a looping policy is bad.
- **Cliff walking** (undiscounted, -1 per step, -100 for falling off, epsilon 0.1): Q-learning learns the optimal route along the cliff edge but keeps stepping off it during epsilon-greedy play, so its online reward trails Sarsa, which settles on the longer, safer path. Expected Sarsa kept Sarsa's online advantage and did better than Sarsa over a wide range of step sizes; because the transitions are deterministic it can use alpha = 1 safely, whereas Sarsa does well in the long run only at small alpha.

Winder's cliff gridworld agrees (−1 per step, −100 for the fall, 0 at the goal, tabular ε-greedy agents, 500 episodes averaged over 100 parallel runs, parameter values lost from the text): Sarsa's reward was higher and steadier than Q-learning's, which hugged the edge and sometimes fell. Early on, episode reward dipped to roughly −125 as the agent steered from the cliff, wasted steps and fell anyway. In his real-time-bidding toys (episode of 100 auctions, budget 10,000, each action moves the bid by 50%, 10% or nothing), Sarsa slightly overbid and ran out of budget sooner than Q-learning, with high ε keeping both below the optimum of 100. On the grid, Double Q-learning ended with a better policy than the standard form, while delayed Q-learning ended very good but with discontinuities and stopped learning after a fixed number of updates.

## Maximization bias and Double Q-learning

Reading the best of several noisy value estimates as though it were the best true value is biased upward, since one set of samples both selects the apparent best action and evaluates it. Double Q-learning keeps two tables, Q1 and Q2; on a coin flip it updates one table, selecting the argmax with that table and scoring it with the other: Q1(S,A) ← Q1(S,A) + α[R + γQ2(S′, argmax Q1(S′,·)) − Q1(S,A)]. Memory doubles, per-step computation does not. In the book's two-state example (the left action reaches B with reward 0, where many actions have reward N(−0.1, 1); the right action ends with 0; ε = 0.1, α = 0.1, γ = 1), Q-learning picked the wrong left action roughly 5% more often than the optimum even at the asymptote, while Double Q-learning was essentially unaffected (curves averaged over 10,000 runs, 300 episodes shown).

## Afterstates

An afterstate value function is defined over the position that results from the agent's move. What is learned about one position-move pair then carries straight over to every other pair leading to the same position; the book calls this more efficient than an ordinary action-value function and uses tic-tac-toe as its example.

## Limits

- The chapter covers tabular, one-step, model-free methods only.
- The chapter's own summary says no proof exists that TD learns faster than Monte Carlo; the random-walk and cliff curves are small chain and gridworld examples.
- Step-size grids appear only in figures, and the step sizes used in the cliff-walking curves are not stated in the text.
- The tic-tac-toe convergence claim in chapter 1 is asserted without proof, and chapter 1 reports no measured results.
- The extraction gives the cliff-walking averaging two ways, 100,000 episodes for asymptotic performance in one line and 50,000 runs (interim) with 10 runs (asymptotic) in another, and does not reconcile them.
- Winder's chapter 3, behind the cliff and bidding comparisons, runs single small tabular environments with no hyperparameters, seeds or error bars in the text (the cliff-figure settings are lost from the extraction). His rule-of-thumb claims are asserted rather than shown, it was written in 2020, and it defers importance sampling to a later chapter.

## See Also
- [[Q-Learning]] — alternative-to (the off-policy control update; Watkins's convergence proof)
- [[N-Step Bootstrapping]] — extends (the span between one-step TD and Monte Carlo)
- [[Dyna Planning]] — extends (adds a learned model to Q-learning updates)
- [[Semi-Gradient TD and Tile Coding]] — extends (TD with a parameterised value function)
- [[Reinforcement Learning Foundations]] — prerequisite-for
- [[Eligibility Traces and TD(lambda)]] — extends
