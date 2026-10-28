---
title: Intake Option Separability via Reach Vectors
tags: [patterns, rag, pattern]
summary: Measure whether intake options are actually different requests by taking the cosine of each option's reach vector over the tag space; the options that look distinct often form a clique, and because coverage and separation both flow through the same adjacency graph, the lever is pruning adjacency edges, not splitting options.
updated: 2026-10-16
sources:
  - data/raw/claude-docs/akira/docs/research/2026-09-19-mood-vocabulary-coverage.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-19-mood-vocabulary-coverage.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-19-mood-vocabulary-coverage.md
---

# Intake Option Separability via Reach Vectors

From a measurement of akira's mood intake (six mood tiles mapped onto a 26-tag vibe
vocabulary through a weighted adjacency graph).

## The measurement

For each intake option, compute its **reach vector**: the weight it assigns to each of the
26 tags after adjacency expansion (direct, strong and weak tiers). The cosine between two
options' vectors is how often they would return the same slate.

- `experimental`, `artsy` and `high_energy` formed a clique (pairwise 0.84 / 0.81 / 0.68).
- Six tiles amounted to roughly **3.5 distinct requests**. A user picking a different
  tile mostly got the same results.

## Coverage and separation trade through the same graph

- **The obvious fix makes it worse.** Splitting a broad option into two raised overlap
  elsewhere (chill/romantic 0.77 → 0.82), because both halves still expand through the
  shared adjacency edges.
- Coverage (every tag reachable from some option) and separation (options differ) move in
  opposite directions, since both run through the adjacency graph. The lever is the
  graph itself: **five edge cuts** took the worst pair from 0.89 to 0.73 with tag coverage
  unchanged.
- **Measure each half of a combined edit separately.** A split plus edge cuts shipped
  together hides which change moved the number.
- **Import the constants, don't retype them.** A hand-retyped weak tier of 0.3 (the real
  value was 0.4) skewed an early run.

## Axis hygiene

Keep mood, category and context as separate axes. An audience/context attribute (e.g.
an identity-specific space) is a context tag, not a mood; putting it on the mood axis
forces it to compete with vibes it is orthogonal to. A related audit finding: the create
endpoint accepted free-text moods while the update endpoint validated against the enum —
the two write paths disagreed on what a valid option was.

## See Also
- [[Starved Tag Triage: Edge, Prompt, or Supply]] — related (the adjacency edges are also the triage lever for starved tags)
- [[Specificity-Adaptive Ranking and Slate Composition]] — related (how the expanded tags feed ranking)
- [[Build the Knobs, Not the Choice]] — related (adjacency weights as a tunable, not a guess)
