---
title: Rehearse Focused Outcome Memory
tags: [loop, pattern]
summary: "Rehearse keeps a plain-file store of earlier changes and whether they worked, retrieves only similar ones for a pre-execution judge, and so avoids the accuracy drop a memoryless judge shows once a loop has accumulated successes."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-ji-2026-rehearse.md
---

# Rehearse Focused Outcome Memory

Rehearse (Ji and Ding, a July 2026 preprint) addresses an autoresearch loop that proposes several changes and predicts which one is worth running. The paper names a "confidence cliff": a judge with no memory predicts well at the start and badly once successes have piled up, while still committing just as readily.

## Mechanism

1. Propose five candidates, each with description, hypothesis, implementation and type.
2. Run a pairwise tournament in both orders; the judge abstains when the two orders disagree (strict consensus).
3. Execute only the top candidate.
4. Record the change and a binary outcome. A run is recorded as worked only when it strictly beats the accepted baseline; crashes and timeouts are recorded as failures.
5. For later judging, retrieve earlier attempts on the same task by embedding similarity above a cut-off and show one line each: the change and its outcome.

The store is plain files; nothing is fine-tuned.

## Findings (self-reported)

- On a 366-pair benchmark from 39 AutoSOTA tasks, selective accuracy for a memoryless judge fell from 82.8% at cold start to 56.9% after three or more successes. Focused retrieval gave 83.5% in that bucket, against 80.9% for an LLM summary, 74.1% for a Reflexion-style note, 70.8% for dumping the full history.
- More history was worse than selected history. Adding the recorded failure reasons lowered selective accuracy on the cliff calls from 83.5% to 80.6%, and to 54.8% on the calls that carried a reason (self-reported).
- In a live nanochat loop (100 experiments, 5 seeds) mean improvement was 7.1% for the plain loop, 8.4% when selecting among candidates, and 10.7% with the store.
- The memory is candidate-level, not a blacklist: a reverted weight-decay decrease did not stop an increase being kept.

## Limits

- Depth is observational, not randomised; headroom and difficulty change as a run goes on.
- Three loops with measurable outcomes, five seeds each, and each loop paired with one model.
- The budget counts training runs only, not the twenty judge calls per step.
- The early-run gap comes largely from one batch-size reduction, per the paper.
- Baseline memories are the authors' adaptations, not full reproductions.
- The paper reports diminishing returns in late-run AutoSOTA logs (helpful modifications 70% at iterations 1-2 against 43% from iteration 6), which sits against the idea on [[Recursive Self-Improvement]] that a low hit rate is acceptable when attempts are cheap.

## See Also
- [[Recursive Self-Improvement]] — prerequisite-for
- [[Loop State File]] — prerequisite-for
- [[Loop Scorekeeper]] — prerequisite-for
- [[AI Research Preference Model]] — alternative-to
- [[SIFT Judge-Guided Self-Improvement Tree Search]] — alternative-to
