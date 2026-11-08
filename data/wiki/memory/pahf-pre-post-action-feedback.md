---
title: PAHF Pre- and Post-Action Feedback Personalization
tags: [memory, pattern]
summary: "PAHF personalises an agent with a per-user note memory fed by two feedback channels, a clarifying question before acting and a correction after, so it can both learn a preference and notice when it changes; in simulation the combined version led after drift (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-liang-2026-learning-personalized-agents-human-feedback.md
---

# PAHF Pre- and Post-Action Feedback Personalization

PAHF (Meta Superintelligence Labs and academic co-authors, a February 2026 preprint) treats personalisation as continual learning from the user, not a fixed profile. The agent follows a ReAct loop with one simple memory, and learns from feedback at two moments.

## Mechanism

- **Memory.** A per-user store of notes (SQLite or a FAISS index) read by top-k dense retrieval. A write goes through a salience check on the feedback, a summary, and a similarity check against existing notes: above a threshold the LLM merges the new text into the old note, below it a new note is added.
- **Pre-action feedback.** When retrieved memory leaves the choice ambiguous, the agent may ask the user one clarifying question before acting.
- **Post-action feedback.** After acting the user's reaction is written back, which is how a changed preference gets corrected.
- **Protocol.** Four phases: learn, test, learn after a preference change, test. Metrics are success rate, feedback frequency, and ACPE (lower is better).

## Why both channels

The paper gives a proof sketch: with preferences switching at most K times and no post-action feedback, expected errors grow linearly in the horizon T; updating on the first error after each switch bounds them at O(K). Clarifying questions add a term that shrinks with the number of questions asked. Both results assume noise-free answers and a correction that identifies the right action.

## Results (self-reported)

Setup: GPT-4o agent and simulated user, SQLite memory; 40 embodied users with 30 scenarios per phase, and 20 shopping users with 45 per phase.

- Phase 2 and Phase 4 success, embodied: combined 70.5 and 68.8; post-only 67.9 and 68.3; pre-only 54.1 and 35.7; no memory 32.3 and 44.8. Shopping: combined 41.3 and 70.3; post-only 38.9 and 66.9; pre-only 34.4 and 56.0; no memory 27.8 and 27.0.
- Pre-only fell below no memory after the change in the embodied domain; the authors attribute this to confident notes suppressing questions.
- The two memory backends gave similar scores (embodied Phase 4 68.8 vs 68.2).

## Limits

- The extraction notes a text/table mismatch: the prose labels 67.9 and 70.5 as Phase-4 values, yet they sit in Table 1's Phase 2 column. Post-only versus combined is often within the reported spread.
- Users are LLM simulators or rule-based, change is abrupt, and one clarifying question per task is allowed. Shopping success stays low. The authors concede simple memory and no handling of mistaken feedback. Seed counts are unstated, and no cost or memory-growth numbers are given.

## See Also

- [[Agent Memory Types]] — prerequisite-for
- [[Simulated User Evaluation]] — related
- [[MIMESIS User Simulator Training]] — related (trains the simulated users)
- [[Self-Learning Agents]] — related
