---
title: Adaptive Branching MCTS
tags: [foundations, pattern]
summary: "AB-MCTS decides at each node whether to sample a new answer (wider) or refine an existing one using external feedback (deeper), via Thompson sampling; it had the best average rank in the paper, with margins often inside the error bars (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-inoue-2025-wider-or-deeper.md
---

# Adaptive Branching MCTS

AB-MCTS (Inoue et al.) frames inference-time search as a choice between width (a fresh sample from the prompt) and depth (refine a previous answer given a score from an external evaluator such as unit tests). Because new arms are created on the fly, UCT does not apply; it uses Thompson sampling over Bayesian posteriors, with a GEN node standing for "make a new child". AB-MCTS-M fits a mixed-effects model by MCMC; AB-MCTS-A uses cheap conjugate updates and grows wider trees.

## Reported results

- LiveCodeBench, CodeContest and ARC-AGI (Pass@2) with GPT-4o and DeepSeek-V3, 128 LLM calls, 3-5 runs: mean rank was 2.3 (-M) and 2.7 (-A); repeated sampling got 3.5, sequential refinement 5.5 and standard MCTS 4.2 (self-reported).
- No single baseline dominates: on ARC-AGI at the small budget, repeated sampling led (GPT-4o 15.0 against 12.3 for -M), while plain MCTS led on LiveCodeBench with DeepSeek-V3 (self-reported).
- At up to 512 calls on ARC-AGI with DeepSeek-V3, AB-MCTS kept improving while repeated sampling plateaued (read from a figure).
- Multi-LLM ARC-AGI-2: Pass@k from 23% to 27.5% to over 30%, but Pass@2 was only 19.2% (self-reported).
- MLE-Bench, three Kaggle tasks, one run: average rank 1.3 for -M (self-reported).

## Limits

- Needs an external score at each node; without a verifier there is nothing to refine against.
- Margins are small and often within error bars, with 3-5 runs per setting; MLE-Bench is n=1.
- Fixed-width MCTS was sensitive to its width and tuned progressive widening matched AB-MCTS in one test, so the claim is robustness, not dominance.
- MCMC adds per-step cost for -M.

## See Also
- [[Self-Consistency]] — prerequisite-for (repeated sampling is the width-only baseline)
- [[Tree of Thoughts]] — prerequisite-for
- [[Best-of-k Headline Inflation]] — related (Pass@k depends on the budget k)
- [[Verification Loops]] — related (the external evaluator)
- [[CoAT Associative-Memory MCTS]] — related
