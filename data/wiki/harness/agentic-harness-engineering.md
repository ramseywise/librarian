---
title: Agentic Harness Engineering
tags: [harness, pattern]
summary: A closed loop where an evolve agent edits file-level components of a coding agent's harness using layered trace reports and a change manifest that predicts which tasks each edit fixes or risks.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-07-lin-2026-agentic-harness-engineering.md
---

# Agentic Harness Engineering

Agentic Harness Engineering (AHE, Lin et al., a 2026 preprint) evolves a coding agent's whole harness: system prompt, tools, middleware, memory, skills and sub-agents. The authors' hypothesis is that evolution is limited by observability rather than agent capability, so the method adds structure on three fronts: components as files, experience as layered reports, and decisions as a manifest.

## Loop

The loop runs on the NexAU framework, where a code agent performs k rollouts for every task. An Agent Debugger condenses the traces into layered reports, then an Evolve Agent edits components at file level and records a change manifest listing the fixes it predicts and the regressions it fears. In the next round those predictions are checked, and rollbacks happen per file. The base model stays GPT-5.4; the seed harness, NexAU0, offers a bash tool alone, without skills, middleware or long-term memory.

## Results

Numbers are self-reported by the authors, from one campaign of 10 iterations (about 32 hours) on Terminal-Bench 2, which has 89 tasks; the model is GPT-5.4 at high effort and the timeout one hour.

- Pass@1 rises from 69.7% to 77.0%, above the human-designed and self-evolving baselines the paper compares, though Codex stays ahead on the 30 hard tasks.
- Swapping one evolved component into the seed: memory alone gives the largest single gain and the prompt alone falls below the seed (system prompt, +79 lines, alone scores -2.3 points). Added together, the single-component gains exceed the full gain, which means the components do not combine additively; on the hard tier memory-only beats the full harness.
- The frozen harness, not re-evolved, is tested on the 500 tasks of SWE-bench-verified using GPT-5.4. It posts the top aggregate success, with ACE and TF-GRPO scoring beneath the seed, and uses fewer tokens than the seed does (461k against 526k). The gain over the seed is 0.4 points.
- Manifest quality over 9 rounds: fix predictions have 33.7% precision against 6.5% random; regression predictions 11.8% against 5.6% random, so self-attribution is reliable for fixes and close to blind for regressions.
- Transfer to deepseek-v4-flash shows a gain; within-family gains on other GPT-5.4 reasoning tiers are smaller and non-monotone.

## Limits

- Evolved on Terminal-Bench 2 only; other languages, repository-scale use and human-in-the-loop are untested.
- The step budget and the timeout were tuned for GPT-5.4 at high effort, so any gain on another model blends real portability with that tuning.
- A research prototype, not a full guardrail stack.
- One campaign, no variance or confidence intervals.
- The same base model plays coder, debugger and evolver.
- The extraction's results list omits some exact numbers (for example the baselines' scores), so those are not stated here.

## See Also

- [[Harness Anatomy]] — prerequisite-for
- [[Meta-Harness End-to-End Optimization]] — alternative-to
- [[Harness Subsystem Attribution]] — related (component-level attribution of harness gains)
