---
title: LADDER and TTRL Verified Variant Trees
tags: [loop, pattern]
summary: "LADDER trains a model with reinforcement learning on a model-generated tree of easier variants of problems it cannot yet solve, scored by a programmatic checker; TTRL repeats the trick per question at test time and then rolls back."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-simonds-2025-ladder.md
---

# LADDER and TTRL Verified Variant Trees

LADDER (Simonds and Yoshiyama, Tufa Labs, March 2025) is a self-improvement loop with no human-written data beyond the starting problems. The model writes easier variants of a problem it fails, recursing to build a tree. It then trains with GRPO on the variants, and a programmatic verifier supplies the reward. The difficulty gradient is the ingredient: the paper reports that training on the raw hard problems alone never exceeded 3% and fell to 0% within 30 steps with identical hyperparameters, so the algorithm was not the cause.

## Mechanism

- **Variant generation.** A bare request for easier problems gave repetitive output, so the authors batch ten per prompt, cycle the temperature between 0.8 and 1.4, rotate mathematician personas, sample three to five transformations per prompt and recurse. Recursion is capped at depth 2 or 3 because third-level variants lost mathematical relevance.
- **Verifier.** Integration answers are checked numerically at five random points with a 1e-2 relative tolerance, a 2-second timeout and up to three retries. The authors say it may not be fully accurate, and the model exploited it early on until filters were added.
- **Reward.** An accuracy reward plus a format reward for answer tags.
- **TTRL (the paper's per-question RL step at test time).** For each question the loop still gets wrong, generate about 800 fresh variants and run 100 RL steps on them, crediting a question as solved if any step produces a right answer, then discard the update. Per question it took 3 to 30 steps to solve.

## Results (self-reported, setup beside each number)

- Llama 3.2 3B went from 1% to 82% pass@1 on 100 held-out integrals, trained on 10 problems with about 500 variants each (the 110-problem set was chosen so the base model failed it).
- A DeepSeek-R1-distilled Qwen2.5 7B moved from 50% to 73% on the qualifier exam of the 2025 MIT Integration Bee (20 questions, mean of 3 runs), against 42% for GPT-4o and 80% for o1 as the paper reports them. TTRL on the questions LADDER missed lifted it to 90%, with two questions unsolved.
- Variant quality control is weak: roughly 8% of Llama variants timed out unsolved at 5 seconds, and many came out harder than the problem they derived from.

The pattern is a verifier-bounded cousin of [[Recursive Self-Improvement]]: improvement only works where a cheap, sound checker exists, a point [[Oracle-Gap Recovery by Selection]] makes from the inference side.

## Limits

- One domain (integration) with a numerical checker; transfer to tasks without one is untested.
- The extraction notes that the introduction gives the starting score as 2% while the abstract gives 1%, and that 73% cannot be a whole count of 20 questions.
- The TTRL 90% counts a question as solved at any point in 100 steps, so it is a best-over-trajectory figure, not a single-pass score.
- The 7B test set is 20 questions, so a single question moves the score by 5 points.

## See Also
- [[Recursive Self-Improvement]] — prerequisite-for
- [[Evolve Loop]] — related
- [[SIFT Judge-Guided Self-Improvement Tree Search]] — alternative-to
