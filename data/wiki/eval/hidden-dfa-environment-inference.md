---
title: Hidden-DFA Environment Inference Testbed
tags: [eval, reference]
summary: "A procedurally generated, size-controlled testbed in which a tool-calling agent must learn a hidden automaton by querying it; success drops sharply with automaton size, and the paper grades failures by whether classic passive learners could have recovered the automaton from the agent's own evidence (self-reported, three models)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-menaged-2026-can-agents-infer-environment-interaction.md
---

# Hidden-DFA Environment Inference Testbed

Menaged et al. (arXiv 2606.16576, under review at ICLR 2027) test whether a tool-calling agent can infer a hidden environment from interaction alone. The environment is a hidden DFA over a binary alphabet. The agent has two tools: one asks whether a word is in the language (a membership query) and one submits a candidate automaton (an equivalence query). A correct candidate within the query budget ends the run, so grading is deterministic. A wrong one returns a short counterexample chosen deterministically from a small range of lengths. Malformed calls are discarded without counting against the budget.

## Why the design is useful as a template

- **Size-controlled difficulty.** Instances are minimal DFAs sampled with Boltzmann sampling, seeds 1 to 20 for each size from 2 to 9 states, so difficulty scales along one axis.
- **A provable reference.** Classic query learners (L* and TTT) give a known cost. The budget is twice the cheaper of the two, so a correct solution is guaranteed to fit.
- **A partial-credit complement.** Best Hypothesis Similarity scores the closest hypothesis over all words up to length 200 by a product-automaton dynamic programme.

## Results (self-reported)

Setup: three models at high reasoning (Gemini 3.8 Flash, Gemini 3.1 Pro Preview and DeepSeek-V4-Pro); 160 instances in four state buckets of 40; bootstrapped 95% intervals; apparently one run per instance. "Stateful" means the agent carries goal, working-memory and thought fields from turn to turn, ReAct-style.

- At 8 to 9 states the best success rate was 30.0% with the stateless scaffold and 57.5% with the stateful one.
- Setup: best model and scaffold (Gemini 3.1 Pro, stateful), 8 to 9 states, successful runs only. On average it needed roughly 23.5% more tool calls than TTT.
- In a separate coding-environment run all models wrote L*, but in the interaction runs none reproduced the L* query sequence. The closest combination (DeepSeek-V4-Pro, stateful) kept equivalence queries within the state count and hypotheses growing monotonically in only 31% of runs.
- The stateful scaffold lowered Gemini 3.1 Pro's average cost per run from $10 to $3.25, but pushed Gemini 3.8 Flash's invalid-call rate from 0.2% up to 8.7%.
- Stateless budget sweep: DeepSeek went from 3.1% at the baseline budget to 55.6% at double it, while Gemini 3.1 Pro had 54.4% at 125% of that budget and 70.6% at 200%.
- No trajectory crossed the context limit, so the authors rule out context overflow as the cause. A full run reached about 16M tokens, 20 hours and $50; the whole suite cost about $3000.

## Failure classification

A failure counts as planning when none of three classic passive learners (RPNI, EDSM, Blue-Fringe) can recover the DFA from the observations the agent collected, and as reasoning when one can but the agent did not. Non-informative queries (a repeated word, a repeated or evidence-contradicting hypothesis) rise as interactions lengthen; tracking state lowers their rate without eliminating them.

## Limits

- The authors state that these automata are simpler than real environments, that the alphabet is binary and that evaluation is costly; OpenAI and Claude models were omitted because of that cost.
- The extraction notes that only three models were tested, two from one vendor, and that repeats per instance are not stated, so pass@k and run variance cannot be read off; the intervals are over instances only.
- The extraction observes that the efficiency figure covers successful runs only, which biases it toward easy cases, and that the planning-versus-reasoning shares are plotted but not stated in the text and depend on the passive learners' power.
- The model names (for example DeepSeek-V4-Pro and Gemini 3.8 Flash) are as printed in the paper; the extractor could not verify them.
- The two prompts differ by more than state tracking (the stateless one bans visible text), so the extraction notes the gain is partly permission to think aloud. No human baseline.
- Internal inconsistencies: the abstract says models can run L* in a coding environment but reports no success numbers for that arm; the stateful scaffold is said to cut cost across models, yet no cost is given for Gemini 3.8 Flash; budget-sweep percentages are overall and stateless, so they are not directly comparable with the 30.0% headline.

## See Also
- [[Trajectory Over Outcome]] — related (separating evidence gathered from evidence used)
- [[Eval Failure Taxonomy]] — related
- [[Parameterised Benchmark Instances]] — related (generated instances with controlled difficulty)
- [[Eval Non-Determinism]] — related (single-run results with no repeat variance)
