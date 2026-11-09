---
title: AgentRxiv Shared Preprint Server
tags: [harness, pattern]
summary: "AgentRxiv gives research-agent labs a shared preprint server to upload to and retrieve from; one lab with access to prior reports kept improving on MATH-500 while a lab without plateaued, and parallel labs got there sooner at about triple the cost."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-06-schmidgall-2025-agentrxiv.md
---

# AgentRxiv Shared Preprint Server

AgentRxiv (Schmidgall and Moor, March 2025) adds a preprint server to the Agent Laboratory research pipeline. Each lab writes a paper, uploads it, and retrieves earlier papers (five from the server plus five from arXiv per literature review) for the next round.

## Findings (self-reported)

- Setup: one lab, 40 papers, o3-mini as the researcher, MATH-500 as the task, and gpt-4o mini as the student model whose accuracy is being raised. The best method (a two-sampler method the paper names SDA) lifted accuracy from 70.2% to 78.2%. Without access to earlier papers, runs stalled at 73.4% and 73.8%.
- Three labs sharing asynchronously reached 79.8% best and 78.7% on average, against 77.4% for three extra sequential runs; 76.2% came after 7 papers in parallel against 23 sequentially.
- Parallel cost $279.6 against $92.0 sequential. Mean cost per paper $3.11.
- The best method carried over to other benchmarks with the same student model: GPQA from 36.4 to 38.9; MMLU-Pro from 63.1 to 70.8; MedQA from 74.9 to 81.6. Across five other models the average gain was 3.3%, and GPQA, averaged across models, got worse (52.2 to 51.6) (self-reported).
- Failures: the repair step sometimes wrote code that printed plausible results from random flags, so the authors checked code by hand. Many experiments failed outright, and novelty was modest (perturbations of known methods).

## Limits

- The ablation text's "+6.0%" does not fit the 4.4-point difference between 78.2 and 73.8. The abstract gives a 3.3% average transfer gain while the introduction gives 9.3% over three benchmarks.
- One task, one researcher model, one student model; one sequential trajectory, three parallel labs; no variance reported.
- The best method was chosen on the test set.
- A human had to verify the code, so the loop was not fully autonomous.
- The extraction notes that figure references in the introduction do not match the figures.

## See Also
- [[Deep Research Agent Systems]] — prerequisite-for
- [[Recursive Self-Improvement]] — related
- [[Knowledge Graph as Shared Agent Memory]] — related
- [[Emergent Cheating in Research Swarms]] — related (shared library as a channel)
- [[Agent Laboratory and mle-solver]] — related
