---
title: Agentless Localize-Repair-Validate
tags: [harness, pattern]
summary: "Agentless solves repository issues with a fixed three-phase pipeline of hierarchical localization, sampled patch repair and test-based selection, with no agent loop, and reports 32.00% on SWE-bench Lite at $0.70 per issue."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-xia-2024-agentless.md
---

# Agentless Localize-Repair-Validate

Agentless (Xia et al., 2024) is a counterweight to autonomous coding agents: the model never chooses its next action. A fixed pipeline localizes the fault, samples candidate patches and picks one by running tests. It is a useful baseline when judging whether a harness's agent loop earns its cost; see [[Repository-Level Coding Benchmarks]] for the benchmarks involved.

## Pipeline

1. **Localize** hierarchically: files first, then classes and functions, then edit locations.
2. **Repair** by sampling several patches in a diff format at the chosen locations.
3. **Validate** by generating reproduction tests, running them with existing regression tests, and re-ranking candidate patches by the results.

## Results (self-reported)

- 96 of 300 issues (32.00%) on SWE-bench Lite with GPT-4o at an average of $0.70 per issue, the paper's headline.
- A selection ladder across the patch-choice steps rose from 77 to 81 to 96 resolved issues, and the paper names the reproduction-test step (81 to 96) as the largest single gain. If any of the 40 sampled patches counted, 126 issues (42.0%) would be solvable, so re-ranking is the stated headroom.
- Of 213 generated reproduction tests, only 94 also verified the ground-truth fix, so the tests are a noisy selector.

## Limits

- The extraction notes a StarShip file-level localization figure of 90.7% in the table against 90.0% in the text.
- Results are on SWE-bench Lite with one model; the extraction does not report variance across sampled runs.
- Reproduction tests that do not discriminate correct patches weaken the selection step.
- The cost comparison mixes baselines that use different models, and only some tools list a cost.

## See Also
- [[Repository-Level Coding Benchmarks]] — related
- [[Verification Loops]] — related
- [[InfCode Adversarial Test-Patch Refinement]] — related
