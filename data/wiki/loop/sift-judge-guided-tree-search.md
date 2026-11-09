---
title: SIFT Judge-Guided Self-Improvement Tree Search
tags: [loop, pattern]
summary: "SIFT puts a cheap pairwise LLM judge in front of the expensive benchmark run, ranks candidate agents with a Bradley-Terry fit, and spends full evaluation only on the top nodes of a self-improvement tree."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-fu-2026-self-improvement-fast-tree-search.md
---

# SIFT Judge-Guided Self-Improvement Tree Search

SIFT (Self Improvement via Fast Tree-search, Fu et al., a September 2026 preprint) starts from the Darwin Gödel Machine style of self-improving coding agent: a tree of agent variants, each produced by an LLM editing its parent's code. Its observation is that nearly all the cost sits in scoring a node on the benchmark, so it adds a cheaper first filter.

## Mechanism

- A pairwise LLM judge compares two candidate agents and states which looks better. Up to ten judge calls are made per node.
- A regularised Bradley-Terry model is fitted to the wins and losses, and the resulting ranks decide which node becomes the next parent.
- Full benchmark evaluation is kept for the most promising nodes only.
- Expansion, judging and evaluation run as an asynchronous pipeline, with speculative expansion of nodes that are judged but not yet evaluated. The paper reports that the pipeline accounts for most of the speed-up.

Cost per call, as the paper tabulates it for 50 Polyglot tasks (self-reported): a full evaluation is about $6.0 and 2.6 CPU-hours, an expansion about $0.12, and one judge call about $0.044.

## Results (self-reported, single runs)

- On Polyglot-225, with a 30B Qwen3-Coder model doing the coding, SIFT scored 31.1% with one judge and 32.0% with another, against 30.5% for HGM, 27.1% for DGM and 25.1% for SICA. The paper reports 224 CPU-hours against 347 for HGM.
- With o3-mini as coding model, 35.1% within 30 expansion steps; three repeats range from 32.0% to 35.6%.
- TerminalBench: the judge-selected agent scored 36.7% on repeated full evaluation against 28.1% for the top accuracy-selected agent, though it scored lower on the 50-task search subset.
- Judge quality: Spearman 0.72 and 63.2% per-verdict agreement with measured outcomes. A weaker judge keeps the global ordering but is worse at the top (recall of the true top five 3 of 5 against 4 of 5). Showing the judge full files beat showing diffs (Spearman 0.68 against 0.40).

The authors suggest a tiered judge: cheap for bulk comparisons, strong for the frontier. That judge is stronger than the coding model it steers, which bears on [[Harness Updating vs Harness Benefit]], where evolver strength mattered little for updating.

## Limits

- One search run per condition; no variance across independent searches.
- Table 3 lists the o3-mini run as 20 steps, $86.8, 59 CPU-hours and 2.1 hours, while the text gives 42 CPU-hours for the 35.1% run. Table 2 also carries a "judge None" row.
- The HGM comparison figures come from another paper's setup.
- The judge is imperfect: the best-ranked group still contains weak agents.

## See Also
- [[Recursive Self-Improvement]] — prerequisite-for
- [[Bradley-Terry Preference Model]] — prerequisite-for
- [[Loop Scorekeeper]] — prerequisite-for
- [[Harness Updating vs Harness Benefit]] — related (evolver capability)
- [[AI Research Preference Model]] — alternative-to
- [[Rehearse Focused Outcome Memory]] — alternative-to
- [[Darwin Gödel Machine]] — prerequisite-for
