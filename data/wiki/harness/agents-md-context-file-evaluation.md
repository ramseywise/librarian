---
title: AGENTS.md Context File Evaluation
tags: [harness, concept]
summary: A study of repository context files (AGENTS.md, CLAUDE.md) on SWE-bench Lite and a new benchmark, CtxBench; the files did not significantly raise success and raised cost by about 20%.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-gloaguen-2026-evaluating-agents-md.md
---

# AGENTS.md Context File Evaluation

Gloaguen et al. (ETH Zurich and LogicStar.ai, a preprint dated September 2026) test whether repository-level context files help coding agents. They also build CtxBench: 138 instances from 5,694 pull requests in 12 Python repositories that commit their own AGENTS.md or CLAUDE.md. Codex running GPT-5.2 built the benchmark, writing the tests and task descriptions too; 25 of 138 tests were hand-edited.

## Setup

Four agent-and-model pairs were run: Claude Code on Sonnet-4.5, Codex on GPT-5.2, Codex on GPT-5.1 Mini, and Qwen Code on Qwen3-30B-Coder. Two benchmarks: CtxBench, and SWE-bench Lite with 300 tasks across 11 repos. One sample per agent per instance; significance by Cochran-Mantel-Haenszel test. Conditions: no file, an LLM-generated file, a developer-written file (CtxBench only).

## Results (all self-reported)

- Context files did not significantly improve success, and LLM-generated files raised cost by about 20% on SWE-bench and 23% on CtxBench. p=0.87 (SWE-bench, none against LLM), 0.37 and 0.21 on CtxBench (none against LLM, none against developer).
- LLM-generated files lowered success by 0.5 points (SWE-bench) and 2 points (CtxBench) on average, with drops in 5 of 8 settings, and added 2.45 and 3.92 steps.
- Developer-written files gained 2.4 points over none (not significant) and beat LLM-generated ones (p=0.038).
- Overviews in the file did not reduce the steps before the agent first touched a gold-patch file.
- Agents followed the instructions: when uv was mentioned it ran 1.6 times per instance, versus under 0.01 otherwise; repo-specific tools ran 2.5 times versus under 0.05 (trace analysis with an LLM judge).
- On SWE-bench, LLM files increased reasoning tokens: 22% for GPT-5.2, and for GPT-5.1 Mini 10%.
- A stronger model's generated file changed success by +2% on SWE-bench and -3% on CtxBench.
- With every other markdown doc and the docs folder deleted, LLM-generated files improved success by 2.7 points on CtxBench, averaged over three models (Qwen3-30B, GPT-5.2 and GPT-5.1 Mini).
- Section removal, GPT-5.2 only: dropping the testing section cut CtxBench cost from $0.4715 to $0.3730 (p=0.023) with accuracy 68.12% to 66.67% (p=0.80).

The authors suggest omitting LLM-generated files for now, and keeping human-written ones to what the README lacks, evaluated before adoption.

## Limits

- Python only; only task resolution is measured, not efficiency or security. Only root-level AGENTS.md and CLAUDE.md files were tested, not nested files or skills.
- Single sample per instance; CtxBench is small (standard errors near 4 points), so the 2.4-point developer-file gain is within noise.
- CtxBench tests and descriptions were LLM-generated, making it about 15% easier than SWE-bench.
- The models tested (Sonnet-4.5, GPT-5.2) are now dated.
- Table 5 labels CtxBench as "PLAN-BENCH", a labelling inconsistency in the paper or extraction.

## See Also

- [[Harness Engineering]] — prerequisite-for
- [[Skill Authoring Discipline]] — related
- [[Natural-Language Agent Harnesses]] — related
