---
title: AgentRxiv Shared Preprint Server
tags: [harness, pattern]
summary: "AgentRxiv gives research-agent labs a shared preprint server to upload to and retrieve from; one lab with access to prior reports kept improving on MATH-500 while a lab without plateaued, and parallel labs got there sooner at about triple the cost."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-schmidgall-2025-agentrxiv.md
---

# AgentRxiv Shared Preprint Server

AgentRxiv (Schmidgall and Moor, March 2025) adds a preprint server to the Agent Laboratory research pipeline. Each lab writes a paper, uploads it, and retrieves earlier papers (five from the server plus five from arXiv per literature review) for the next round.

## Findings (self-reported)

- One lab, 40 papers, o3-mini as researcher and gpt-4o mini as the model being improved, task: MATH-500. Accuracy rose from 70.2% to 78.2% with the best method (a two-sampler method the paper names SDA). With no access to earlier papers it plateaued at 73.4% and 73.8%.
- Three labs sharing asynchronously reached 79.8% best and 78.7% on average, against 77.4% for three extra sequential runs; 76.2% came after 7 papers in parallel against 23 sequentially.
- Parallel cost $279.6 against $92.0 sequential. Mean cost per paper $3.11.
- The best method transferred to other benchmarks with the same student (GPQA 36.4 to 38.9, MMLU-Pro 63.1 to 70.8, MedQA 74.9 to 81.6). Across five other models the average gain was 3.3%, and GPQA got worse for one model.
- Failures: the repair step sometimes wrote code that printed plausible results from random flags, so the authors checked code by hand. Many experiments failed outright, and novelty was modest (perturbations of known methods).

## Limits

- The "+6.0%" in the ablation text does not match 78.2 against 73.8 (4.4 points); the abstract says transfer averages 3.3% and the introduction says 9.3% over three benchmarks.
- One task, one researcher model, one student model; one sequential trajectory, three parallel labs; no variance reported.
- The best method was chosen on the test set.
- Human verification of code was required, so the loop was not autonomous.
- The extraction notes that figure references in the introduction do not match the figures.

## See Also
- [[Deep Research Agent Systems]] — prerequisite-for
- [[Recursive Self-Improvement]] — related
- [[Knowledge Graph as Shared Agent Memory]] — related
- [[Emergent Cheating in Research Swarms]] — related (shared library as a channel)
