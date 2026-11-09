---
title: bAbI Toy Tasks
tags: [eval, benchmark]
summary: "Twenty automatically generated question-answering tasks, each isolating one reasoning skill, with a 95% pass threshold; Weston et al. report an extended Memory Network averaging well above LSTM (49%) and N-gram (34%) baselines but failing path finding (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-08-weston-2015-towards-ai-complete-question-answering.md
---

# bAbI Toy Tasks

Weston and colleagues (2015) argue that doing well on 20 simple, automatically generated tasks is a prerequisite for text understanding and reasoning, and that failing one is likely to mean failing real tasks that need the same skill.

## Construction

- Statements come from a simulated world in which actors and objects move between locations; a simple grammar with synonyms renders them and the true answers come from simulation state. The vocabulary is about 150 words, and a task typically involves 4 actors, 6 locations and 3 objects.
- Every task comes with 1000 training questions and 1000 test questions, and counts as passed at 95% test accuracy. The authors say the threshold and the training size are arbitrary.
- **Weak supervision** gives question-answer pairs only; **strong supervision** also gives the supporting facts at training time. Memory Network extensions add **adaptive memory** (a variable number of hops, ending in a STOP prediction), N-gram features and nonlinear matching.

## Results (self-reported)

Setup: 1000 training examples per task unless noted.

- The extended Memory Network (strong supervision) has the best mean accuracy and turns 9 tasks from failures into successes compared with the original; joint training on all tasks averages 92% against 93% per task.
- LSTM (answers only) averages 49% and the N-gram classifier 34%. A structured SVM with coreference and role-labelling features and external data averages 79% and fails 9 tasks.
- Path finding (task 19) is hardest, best 36%, and is not solved even with 10000 examples. Most passing tasks need 100 to 500 examples; task 7 (counting) needs 10000 and task 8 needs 5000.
- The original Memory Network fails yes/no (task 6, 47%); the authors put this down to linear scoring, which cannot capture how the query, the fact and the answer interact together.

## Limits

- The data are synthetic, with a very small vocabulary and brief, unnested sentences. The authors say real data cannot be replaced by them and that solving them does not imply real reasoning.
- The Memory Network results use strong supervision, which the authors call far stronger than realistic.
- One accuracy per cell, no seeds or variance; training details are not given. Later memory and transformer models solve these tasks.

## See Also
- [[BABILong Benchmark]] — extends (places bAbI-style facts inside long distractor text)
- [[HotpotQA]] — related (real-text multi-hop counterpart)
