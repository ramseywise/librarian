---
title: Graph of Thoughts
tags: [prompting, concept]
summary: Prompting framework where a user-written Graph of Operations (Generate, Aggregate, Score, KeepBest, Repeat) lets thoughts merge and loop; the paper reports lower sorting error than Tree of Thoughts at lower cost on GPT-3.5 (self-reported).
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-07-besta-2023-graph-thoughts.md
---

# Graph of Thoughts

Graph of Thoughts (GoT, preprint, arXiv v4 Feb 2024) models LLM reasoning as an arbitrary graph: thoughts are vertices and dependencies are edges, so thoughts can be merged (aggregated) and refined in loops, not only branched as in [[Tree of Thoughts]]. A user writes a **Graph of Operations** (GoO), a static structure built before execution that specifies how a task decomposes. A Controller executes it against the LLM, while a **Graph Reasoning State** (GRS) tracks the evolving reasoning. The architecture also has a Prompter, Parser and Scoring module. Operations are Generate, Aggregate, Score, KeepBest and Repeat. The paper defines the **volume of a thought** as the number of thoughts from which it is reachable along directed edges.

For sorting 64 numbers the paper's listing splits the list into four parts of 16, generates five sorted candidates per part, scores and keeps the best one, then aggregates the parts with a merge step.

## Results (self-reported)

Everything runs on GPT-3.5 with matched thought counts, compared with the IO, CoT and CoT-SC baselines and two ToT variants, over four decomposable tasks (sorting, keyword counting, set operations, document merging).

- Sorting digits 0-9 with duplicates (100 samples; temperature 1.0; a 4k context). At P=128 GoT cuts median error by about 62% against ToT while costing over 31% less; at P=64 median error is about 65% below CoT and 83% below IO.
- The gap between GoT and ToT2 widens as the problem grows: it is negligible at P=32, then GoT has 61% lower median error at P=64 and 69% at P=128.
- Across all four tasks GoT is cheaper than ToT and close to ToT2 in cost, while all of GoT, ToT and ToT2 are far dearer than IO and CoT. In keyword counting, 80 total responses cost $6 against $3 for 60.
- A theoretical latency-volume argument (with the total cost held at Theta(n) and each thought taking O(1) time) says GoT is the only scheme with log_k N latency and volume N.
- The document-merging run used 50 samples at 16k context.

## Limits

- Only GPT-3.5 results are reported; Llama-2 was worse and too slow, with no results shown because of budget.
- CoT-SC results were left out of the figures as uninformative.
- The GoO is hand-designed per task and static; the Controller follows the plan.
- Tasks are naturally decomposable, so there is no evidence for other task types.
- Most exact numbers appear only in figures, there are no significance tests, and neither seeds nor API settings beyond temperature are given.

## See Also
- [[Tree of Thoughts]] — prerequisite-for
- [[Chain of Thought]] — prerequisite-for
- [[Self-Consistency]] — related
- [[ThoughtSculpt]] — alternative-to (search that revises intermediate nodes instead of merging them)
