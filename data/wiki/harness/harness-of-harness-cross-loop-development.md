---
title: Harness-of-Harness Cross-Loop Development
tags: [harness, pattern]
summary: HoH wraps an unchanged coding-agent harness in repeated Planner, Developer and QA Tester loops that carry both the code and the QA evidence from loop to loop.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-yan-2026-harness-harness.md
---

# Harness-of-Harness Cross-Loop Development

Harness-of-Harness (HoH, Yan et al., a September 2026 preprint, Shanghai AI Laboratory) leaves a coding agent's own harness unchanged and wraps it in a cycle of Planner, Developer and QA Tester roles that repeats. Two things persist between loops: artifact state (the code) and evidence state (QA findings), and the authors credit that carry-over for the gains over one pass. Information kept only in an invocation's interaction history is lost when it ends, so plans, reports and histories are saved to the filesystem and exposed through a concise categorised index, a progressive-disclosure design rather than a dedicated memory module.

## Results

All numbers are self-reported, with one valid run per task-condition cell and no controlled seeds. HoH@3 means three loops.

- GameCraft-Bench (45 of 140 tasks, 0-100 score): Codex with GPT-5.5 improves from 49.58 to 71.52, OpenCode with DeepSeek-V4-Pro from 26.90 to 48.98, and Pi with MiniMax-M3 from 42.16 to 58.78.
- FrontierSWE, scored by mean reward on 15 of its 17 tasks: the gains are 0.31 to 0.54 for Codex, 0.23 to 0.31 for OpenCode and 0.26 to 0.55 for Pi. Five of 15 Codex tasks stay at 0.00 in every loop.
- ProgramBench test pass rate, first loop to last: Codex goes 60.41 then 66.50; OpenCode 45.27 then 57.56; Pi 35.83 then 52.68.
- Budget control (Codex, GameCraft, 45 tasks): a plain "continue developing" prompt in the same session reaches 49.58, 54.99 and 58.24 over 1 to 3 passes at 2.59M, 4.56M and 6.33M tokens per task, against 59.71, 64.84 and 71.52 for HoH at 2.88M, 5.67M and 8.41M.
- Removing one channel from full HoH@3 (71.52): no plan update 63.39, no evidence feedback 65.23, and no warm start, meaning a rebuild from empty at every loop, 63.67. Only that last ablation raised token use, to 11.12M.
- Ten loops (Codex, FrontierSWE): a dominance measure goes from 39.33% at three loops to 72.67% at ten against 27.33% for vanilla in the same pool; the same HoH@3 reads 71% in a different pool, so the figure depends on the comparison pool.
- Case study: a first-person shooter built over 70 loops across about 6 days left 16 of 81 recorded issues open; a further 17 issues were reopened when a later change broke behaviour that had been verified. No control.

## Limits

- One run per cell; bootstrap intervals resample tasks, not generations. No dedicated limitations section.
- Benchmarks are subsets, and the QA stage uses the same model as the developer without a test of that.
- Compaction against context reset is never compared; each role is a fresh invocation.
- The extraction flags a table showing lower FrontierSWE tokens for HoH@3 than vanilla as odd and unexplained.
- Model names are dated 2026 releases.

## See Also

- [[Harness Orchestration]] — prerequisite-for
- [[Long-Horizon Execution]] — related
- [[Verification Loops]] — related (independent QA role)
- [[Proposer-Reviewer and Sidecar Gating]] — related
