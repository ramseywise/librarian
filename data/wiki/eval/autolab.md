---
title: AutoLab
tags: [eval, reference]
summary: "A benchmark of 36 long-horizon optimisation tasks run for 2 to 12 hours each; the authors report that persistence in benchmarking, editing and using feedback predicts score better than first-attempt quality, with several models quitting early, and that harness-induced variance can be comparable to model-induced variance (self-reported, correlational)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-xu-2026-autolab.md
---

# AutoLab

AutoLab (Xu et al., arXiv 2606.05080, 2026) measures whether frontier models can do long-horizon optimisation work, meaning executable system and machine-learning engineering tasks where the agent repeatedly benchmarks its own code, edits it and uses the result. It takes its harness (Harbor), its agent (terminus-2) and its task audit rules from [[Terminal-Bench]]. The authors criticise two earlier closed-loop optimisation efforts (AlphaEvolve and an autoresearch project) for relying on bespoke harnesses.

## Main ranking (self-reported)

Setup: terminus-2 in Harbor, 11 flagship models over 36 tasks with three rollouts each, budgets from 2 to 12 hours of wall-clock time; the full evaluation consumed 2,544 hours and 8.60 billion tokens.

- claude-opus-4.6 led with Avg@3 of 0.68, Best@3 of 0.76 and Dominance of 0.93, and gemini-3.1-pro followed at Avg@3 0.50; gpt-5.4 scored 0.36 and grok-4-20 0.35.
- Median steps were 57 for Opus and 12 for gemini-3.1-pro. Score rises with both steps and runtime according to the authors, but only plots show it and no coefficient is given.

## Why runs score zero

The authors inspected 302 zero-score rollouts by hand and sorted them into timeout or context exhaustion, capability gap, instruction violation and other. Three models were timeout-dominated, while gpt-5.4 and grok-4-20 were early submitters. On the CUDA subset, 9 of 12 deepseek-v4-pro trials submitted fewer than 10 actions before the timeout (self-reported). The authors say early stopping largely explains why several proprietary models rank low.

## Harness effect (self-reported)

Setup: three harnesses, 25 CPU tasks, four models, Avg@3. One harness, mini-swe-agent*, is the authors' modified version whose system prompt tells the agent not to submit at the first pass.

- kimi-k2.6 scored 0.21 under pi-mono but 0.64 under the modified mini-swe-agent*, with cost per trial rising from $0.40 to $2.05.
- deepseek-v4-flash reached 0.54 on mini-swe-agent* for roughly $0.07 a trial.
- Model rankings were not transitive across harnesses; for instance gpt-5.4 scored 0.50 on pi-mono, then 0.40 on terminus-2 and finally 0.37 under the modified mini-swe-agent*.

## Run-to-run variance (self-reported)

Setup: appendix stability table. Opus had a mean per-task standard deviation of 0.099. For the four models with a coefficient of variation of at least 0.40, the mean range across trials was 0.28 to 0.34, and the distance from Avg@3 up to Best@3 grew with standard deviation (Pearson r = 0.84). See [[Best-of-k Headline Inflation]] for why the two numbers differ.

## Limits

- The persistence claim depends on correlation plots across models and one trajectory case study, without a controlled test, and Opus's lead is confounded with model identity, steps and tokens. The only intervention is the persistence-prompting harness on four models and 25 CPU tasks.
- The appendix gives opus Avg@3 0.77 and Best@3 0.85, while the main table gives 0.68 and 0.76; the extraction could not reconcile them.
- Three rollouts per cell with large per-task variance; failure labels were manual with no inter-rater check.
- Coverage is measurable auto-research (executable engineering tasks), not scientific discovery generally. Models date from February to April 2026, one default harness was used for the main run, and no open-weight models under 200B parameters were tested.

## See Also
- [[Terminal-Bench]] — prerequisite-for (harness, agent and task audit reused here)
- [[Eval Non-Determinism]] — related (Avg@k against Best@k)
- [[Long-Horizon Execution]] — related (agents that stop early or run out of budget)
- [[NatureBench]] — related
- [[DataSpace]] — related
