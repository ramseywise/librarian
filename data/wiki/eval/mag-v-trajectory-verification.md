---
title: MAG-V Trajectory Verification
tags: [eval, pattern]
summary: "MAG-V generates synthetic test questions with an investigator agent, then verifies a tool-calling agent's trajectory by asking it three reverse-engineered alternate questions and feeding trajectory similarity features to a classical classifier; on 45 annotated trajectories, k-NN matched a GPT-4 judge (82.33 vs 82.83 accuracy) (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-08-sengupta-2024-mag-v.md
---

# MAG-V Trajectory Verification

Sengupta and colleagues (2024 preprint) ask how an enterprise can create lifelike queries to test a tool-calling agent, and check its **trajectory** (the ordered tool calls) without an LLM judge. The working idea: when rephrasings of a base question lead to the same trajectory, trust in that path rises, and when trajectories vary a lot, trust falls.

## Mechanism

1. Starting from 19 seed questions, an investigator agent uses in-context learning to write synthetic questions in the style of customers. The assistant answers each 5 times and experts annotate the most common trajectory.
2. To verify, a reverse-engineer agent works back from the assistant's response to write 3 alternate questions, which the assistant then answers.
3. Similarity features between the base and alternate trajectories (edit distance among them), with or without the tool arguments, feed classical classifiers, which are set against GPT-4 and GPT-4o judges.

## Results (self-reported)

Setup: 45 annotated trajectories (30 incorrect, 15 correct), 10-fold stratified cross-validation, 3 seeds, unless noted.

- k-NN with all features and arguments: 82.33 accuracy against 82.83 for the GPT-4 judge; about 11% accuracy and 4% F1 above the GPT-4o judge.
- Adding the system prompt "You are a helpful AI Assistant." raised the GPT-4o judge's accuracy by about 12%, which the authors read as prompt sensitivity.
- Using only edit distance (6 features, 5-fold, 3 seeds), random forest and XGBoost reach 80% against 71.11 for GPT-4o and 82.22 for GPT-4. Every classifier benefited from including tool arguments.
- Two domain experts agreed on 34 of the 45 trajectories. One anecdote: with the synthetic examples added to its context, a GPT-4o-mini assistant got the time range right on a real customer query that it had missed ten times.

## Limits

- Only 45 trajectories from one proprietary domain; annotator agreement is moderate (kappa 0.42); in F1, k-NN trails GPT-4 (71.73 against 76.06).
- Each item needs three extra questions and trajectories, so more API calls. Only the trajectory is verified, not the answer text.
- The synthetic-data benefit is a single anecdote; the extraction notes the abstract claims more. No code or data released, no standard errors across seeds, and judge non-determinism is not quantified.

## See Also
- [[LLM-as-Judge Evaluation]] — alternative-to (the judge baseline it compares against)
- [[Trajectory Over Outcome]] — related
- [[Verification Loops]] — related
- [[Self-Consistency]] — related (agreement across repeated runs as a confidence signal)
