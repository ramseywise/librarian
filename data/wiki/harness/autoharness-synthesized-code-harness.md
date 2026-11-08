---
title: AutoHarness Synthesized Code Harness
tags: [harness, pattern]
summary: An LLM writes and refines a code harness (a legality verifier or a whole policy) from environment feedback, using tree search; tested on text games, where the verifier removed illegal moves and the policy variant ran with no model call at test time.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-lou-2026-autoharness.md
---

# AutoHarness Synthesized Code Harness

AutoHarness (Google DeepMind, a March 2026 preprint) has a language model write the harness around itself as code, then refine that code from environment feedback instead of having a person hand-write it per game. The paper's motivating case is a Kaggle GameArena chess competition, where 78% of Gemini-2.5-Flash's losses came from illegal moves rather than strategic blunders. The authors describe the harness in its simplest form as a control loop that calls the model and rejects unacceptable answers, with the definition of "acceptable" learned.

## Mechanism

The learned artifact is a pair of functions, `propose_action()` and `is_legal_action()`. Search is a tree search with Thompson sampling, scoring nodes by their mean accuracy on legal moves. The LLM is the mutation operator. Every iteration runs 10 environments in parallel, each rollout lasting up to 1000 steps; no more than 5 failed steps are passed to a Critic and then a Refiner. If `is_legal_action` says True but the environment rejects the action, both functions are refined. When it says False and the action really is invalid, just `propose_action` gets refined.

Three variants are defined, and two are evaluated:

- **Action-filter** (not evaluated): the harness proposes a set of legal moves and the model ranks them.
- **Action-verifier**: the model proposes, `is_legal_action()` checks, and an invalid action triggers a retry with an illegal-action warning in the prompt.
- **Policy**: the whole policy is code, with no LLM call at test time (1-player games only).

## Results

All numbers below are self-reported by the authors.

- Verifier harness, trained with Gemini-2.5-Flash on TextArena 1-player and 2-player games: every one of the 145 games reached a legal-action rate of 100% (self-reported), measured on fresh test rollouts of 1000 steps with 10 random seeds for each game. Valid-move hints were removed from the observations in some games.
- Training took 14.5 tree-search iterations on average over 32 evaluation games, and 19 of 32 games finished in under 10 (self-reported). Chess needed 64 learning steps, Othello 62, and Breakthrough-v0-small 136, the maximum.
- 2-player, 16 games, 40 matches per game, opponent Gemini-2.5-Pro: the Flash-plus-harness agent won 9 of 16 games with a 56.3% overall win rate against 38.2% for Pro (self-reported). Against vanilla Flash it won 12 of 16 games at 64.8% (self-reported).
- 1-player, 16 games, 20 runs each: average reward 0.745 with the verifier harness, against 0.707 for Gemini-2.5-Pro and 0.673 for Gemini-2.5-Flash (self-reported). It was better in 8 of 16 games and tied in 5.
- Policy harness, 16 one-player games, trained with Gemini-2.5-Flash: average reward 0.870 (self-reported), against 0.844 for GPT-5.2-High, 0.707 for Gemini-2.5-Pro and 0.635 for GPT-5.2. Training averaged 89.4 iterations (maximum 256). The authors put the baseline runs' cost near $640 and the harness's test-time cost near zero.

## Limits

- One harness is learned per environment. The authors list a reusable library and distillation into the base model as future work.
- Only games with a simulator that reports legality were tested. Nothing is said about real tool use, shells, sandboxing, permissions or adversarial agents.
- The policy variant is 1-player only; the 2-player version would need an opponent model.
- Evaluation covers 32 of the 145 games. The legal-action rate is a fraction taken over sampled rollouts, so it does not show that states never seen are covered.
- No variance, confidence intervals or significance tests are reported. GPT-5.2 baselines ran 10 repeats and GPT-5.2-High ran 5, against 20 for the rest, for cost.
- The cost claim covers only the policy variant.

## See Also

- [[Harness Engineering]] — prerequisite-for
- [[Verification Loops]] — prerequisite-for
- [[Iterative Harness Simplification]] — related (the other direction: removing harness parts as models improve)
- [[Harness Continual Learning]] — alternative-to (harness evolved against anchors rather than a per-game simulator)
