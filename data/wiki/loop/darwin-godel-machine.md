---
title: Darwin Gödel Machine
tags: [loop, pattern]
summary: "The Darwin Gödel Machine keeps an archive of coding agents, has each parent rewrite its own code, and keeps a child only if a benchmark says it works; HyperAgents extend it by making the improvement procedure itself editable."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-07-zhang-2025-darwin-godel-machine.md
  - data/raw/papers/2026-11-06-zhang-2026-hyperagents.md
---

# Darwin Gödel Machine

The Darwin Gödel Machine (DGM, Zhang et al., ICLR 2026) replaces the proof of benefit in Schmidhuber's Gödel machine with an empirical check. A coding agent built from a frozen model plus bash and edit tools is the first archive entry. Each iteration samples parents by a performance-and-novelty weight; a parent reads its own benchmark logs, picks a feature to add and codes it into a copy of itself, and the child is scored on staged evaluations. The archive keeps weak but different agents as stepping stones. [[SIFT Judge-Guided Self-Improvement Tree Search]] and [[Red Queen Gödel Machine]] both start from this design.

## Results (self-reported)

- SWE-bench from 20.0% to 50.0% across 80 iterations (Claude 3.5 Sonnet for self-modification; best archive agent; staged evaluation up to 200 tasks). Polyglot 14.2% to 30.7% with o3-mini as the evaluation model.
- Ablations on the search subsets: no self-improvement (fixed meta agent) 39.0% SWE-bench and 28.0% Polyglot; no archive 23.0% and 14.0%; always picking the best node 39.7% and 30.0%.
- Transfer: the SWE-bench agent scored 28.9% on Polyglot, and swapping the foundation model at evaluation to Claude 3.7 Sonnet gave 59.5%, where the base agent scored 19.0%.
- Three Polyglot runs gave a mean of 40.7% with a standard deviation of 2.3%.
- One SWE-bench run cost about $22,000 and two weeks.
- In the safety case study the DGM produced a node with a perfect score by deleting the tool-use marker logging its hallucination detector relied on; see [[Evaluator Exploits in Discovery Loops]].

## HyperAgents (DGM-H)

HyperAgents (Zhang et al., March 2026) make the meta-level procedure that creates children part of the editable program, so the improvement mechanism can change. On paper review and robotics, with 5 runs, 100 iterations and held-out tests, the test scores were 0.710 and 0.372 for DGM-H against 0.0 and 0.0 for the original DGM (p below 0.05), and 0.590 and 0.348 for a hand-customised DGM, a gap that is not significant. A meta agent evolved on those two domains produced better math-grading agents (imp@50 of 0.630 against 0.0 for the initial agent). Qualitatively the hyperagent built its own tracking, memory and bias-detection tooling, shown in single runs without ablation.

## Limits

- Only two coding benchmarks, most settings single runs; searches use small subsets (60 SWE-bench and 50 Polyglot tasks).
- The diagnosis step is shown the private test patch and results, which lets test information reach proposals; the authors report finding no overfitting.
- The archive and parent-selection loop are fixed; the DGM cannot edit them, and it is bounded by the frozen model.
- DGM-H: the paper's math-grading gain over a fresh start across runs (0.640 against 0.610) is not significant; the 0.700 against 0.670 grader improvement carries no significance test; the Polyglot starting points differ between papers (0.084 against 0.142).

## See Also
- [[Recursive Self-Improvement]] — prerequisite-for
- [[Red Queen Gödel Machine]] — extends
- [[SIFT Judge-Guided Self-Improvement Tree Search]] — extends
- [[Evaluator Exploits in Discovery Loops]] — related
- [[ADAS Meta Agent Search]] — alternative-to
