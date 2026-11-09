---
title: "ALMA Meta-Learned Memory Designs"
tags: [memory, pattern]
summary: "ALMA has a meta agent write memory designs as code and keep them in an open-ended archive; with a small agent the learned designs averaged 12.3% against 6.1% with no memory over four text-game benchmarks, and they transferred to a larger agent (self-reported), while some hand-built designs scored below no memory."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-xiong-2026-learning-continually-learn-meta-learning.md
---

# ALMA Meta-Learned Memory Designs

ALMA (a 2026 preprint) searches over memory designs instead of hand-building one. A design is a triplet of update process, storage structure and retrieval process, written as code against two interfaces (general_update and general_retrieve) and composed from sub-module layers that can chain and hold their own databases. A meta agent (GPT-5) samples up to five designs from an archive, reads their code, interaction logs and scores, proposes and implements a new design, and gets up to three debug retries. Search is open-ended, in the style of an archive tree, rather than always expanding the current best. The run uses 11 learning steps and 43 designs. Memory is first collected with the agent denied memory access, then deployed either static (frozen) or dynamic (updating after each task); learning uses static mode.

## Results

Setup: ALFWorld, TextWorld, Baba Is AI and MiniHack; designs learned and tested with a GPT-5-nano agent, mean over 3 deployment runs. All figures are self-reported.

- Overall average 12.3% against 6.1% with no memory; the best hand-built baseline was 8.6 (trajectory retrieval).
- Transfer: designs learned with GPT-5-nano and tested with GPT-5-mini reached 53.9% against 41.1% with no memory; trajectory retrieval reached 48.6 and a reasoning-bank design 40.1, below no memory.
- Some human designs hurt: with GPT-5-nano on TextWorld, trajectory retrieval scored 2.7 and G-Memory 2.1 against 5.4 with no memory.
- Open-ended against greedy search on ALFWorld (one benchmark, same budget): 87.1 against 77.1 with GPT-5-mini; with GPT-5-nano 12.4 against 11.9.
- Cost: $0.09 end to end across benchmarks, counting only GPT-4o-mini and embedding calls, with 1,319 retrieved tokens per query against 9,149 for trajectory retrieval.
- Learned designs specialised: fine-grained fact stores (affordance and spatial graphs) for object-goal games, abstract strategy libraries and plan synthesis for the harder-reasoning ones.

## Limits

- Single benchmark for the search ablation; baselines were not tuned per domain; designs are learned per foundation model. Adding collected experience did not improve success monotonically.

## See Also
- [[Memory Architecture]] — prerequisite-for
- [[ADAS Meta Agent Search]] — related (meta agent writes agent code in an archive)
- [[Self-Learning Agents]] — related
