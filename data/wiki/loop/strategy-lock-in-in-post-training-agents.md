---
title: Strategy Lock-In in Post-Training Agents
tags: [loop, concept]
summary: "A study of coding agents running post-training jobs finds they refine execution but rarely change their training strategy (2.1% of adjacent runs), and that a single human instruction to switch beat the agent's own continuation in forked runs."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-lim-2026-what-missing-ai-post-training.md
---

# Strategy Lock-In in Post-Training Agents

Lim et al. (Tsinghua, arXiv 2608.19072, preprint, 2026) analyse autonomous agents that post-train a small model under a fixed time budget. They report that an agent settles on a default training strategy that depends on the agent, not the task. Their summary is that execution loops close but strategy loops remain open.

## Observations (self-reported)

- **Corpus.** 1,338 PostTrainBench trajectories (seven benchmarks, four base models, three harnesses, each given 10 hours on one H100) containing 5,111 verified training experiments. Only 814 trajectories had a recognised initial strategy; labels came from rule-based scripts and an LLM, checked by the authors.
- **Lock-in.** In 3,557 adjacent training pairs only 74 (2.1%) switched strategy. By harness, switch rates were 4.5% (Claude Code), 1.6% (Codex CLI) and 0.4% (OpenCode). Claude Code chose full SFT by default in 71.9% of cases; Codex CLI chose PEFT in 89.5%.
- **Experience helps execution.** Setup: Opus 4.6 in Claude Code, three runs each on Qwen3-1.7B-Base, evaluated on GSM8K, HumanEval and AIME 2025. With a journal, skill library and evaluator agent the gap to the official instruct model shrank by 75.1%, versus 48.6% for the same agent alone. It accepted all 22 execution-level suggestions and none of the 21 strategy-level ones. Dropping the evaluator agent cost the most (56.8% of the gap).
- **Human instruction.** In forked runs (one trajectory per benchmark, same remaining budget), a single mid-run instruction to switch raised GSM8K by 17.44 points (from 47.76 to 65.20 by moving from SFT to GRPO) and HumanEval from 52.0 to 62.8. A plain "reconsider" prompt left every fork on SFT.
- **Compute.** Roughly 90% of GSM8K's gain arrived before half the token budget was spent; on AIME, about 14M more tokens bought a single extra solved problem.
- **Proposal.** Insert an explicit continue-or-switch decision after every evaluation.

## Limits

- Controlled tests use one base model, three benchmarks, three runs and 10 hours on 4 A800s. Forks use one trajectory per benchmark, with branch point and alternative chosen by the authors after the fact: this shows a better route existed, not which is best.
- AIME has 30 problems, 3.33 points each, so its gains sit within noise. 733 of the 5,111 experiments lack an algorithm label.
- The fork training signal is proposed, not tested. The design is observational and case-study, not a controlled causal test. Newer models were excluded for noise or contamination, and one reported run showed reward hacking including edits to the evaluation interface.

## See Also
- [[Loop Engineering]] — prerequisite-for
- [[Recursive Self-Improvement]] — related
- [[Post-Training for Agents]] — related (the agent as post-trainer, not the methods)
