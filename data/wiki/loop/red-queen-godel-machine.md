---
title: Red Queen Gödel Machine
tags: [loop, pattern]
summary: "RQGM lets the evaluator co-evolve with the agent in epochs, holding it frozen within an epoch and checking replacements against an independent anchor; its guarantees hold per epoch, not across them."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-iacob-2026-red-queen-godel-machine.md
---

# Red Queen Gödel Machine

Iacob et al. (a 2026 preprint) start from a Gödel-machine search that relies on a fixed evaluator and ask what happens when the evaluator is itself an agent that can be gamed. RQGM trains agents and their evaluators together: the evaluator is frozen within an epoch, a pool of candidate reviewers is scored against a small validation anchor, and a reviewer is replaced only when the anchor says the new one is better.

## What the extraction reports

- Theory: Propositions hold per epoch under stationarity (binary outcomes, fixed evaluator, workspace and scoring rule). With a changing pool there is no monotone improvement guarantee, only a bound that loosens by the pool drift. The guarantees are about the validation anchor and say nothing directly about the true objective.
- Paper-writing task: a fixed reviewer saturates (writer validation 100.0 against reviewer anchor accuracy 78.2); the full mechanism reaches 95.0, but intervals overlap with replacement-only and no-erasure arms.
- Proof task: the co-evolved grader flatters its own specialist. Under the two independent graders the specialist scores 4.03, against 4.08 for a static prover and 3.60 for the baseline search.
- Coding (DeepSWE, 28 held-out tasks): 85.7 at high effort against 82.1 for the baseline search and 83.0 for the base model, so the margin over the base model is 2.7 points. Cost is about 14% more tokens than the baseline search; validation takes 65 to 70% of tokens.
- Reviewers seated early accepted nearly every patch; only the final one separated passing from failing (balanced accuracy 0.64).

All figures are the authors' own (self-reported).

## Limits

- Table 15 prints 35.0% and 20.8% for the final reviewer, while the prose gives 47% and 19% on 337 patches.
- The extraction's reader covered pages 18 to 40 in full and did not re-read the main text.
- Many ablation intervals overlap; one task is 3.6 points on DeepSWE.
- The coder gain over the baseline search is 1.8 points on Polyglot with no interval.

## See Also
- [[Recursive Self-Improvement]] — prerequisite-for
- [[Loop Scorekeeper]] — prerequisite-for
- [[Reward Hacking and Overoptimization]] — prerequisite-for
- [[Meta^n Recursive Operator Stack]] — alternative-to
- [[Harness Updating vs Harness Benefit]] — related (evolver capability)
- [[Darwin Gödel Machine]] — prerequisite-for
