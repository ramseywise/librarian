---
title: VeriHarness Agentic Verification
tags: [harness, pattern]
summary: A same-model verifier with workspace and evidence tools audits ten rollouts of a long-horizon task, resolves disputed claims, challenges shared errors and revises the best rollout.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-zhang-2026-veriharness.md
---

# VeriHarness Agentic Verification

VeriHarness (Zhang et al., an October 2026 preprint) has the generating model verify its own long-horizon artifacts, without reference answers or rubrics, from a pool of N=10 rollouts. Three roles act in turn:

- A **disagreement resolver** checks claims that are in dispute against evidence from the environment.
- A **consensus challenger**, in a separate context, hunts for errors the rollouts share and for omitted requirements.
- A fresh-context **adjudicator** chooses one rollout as the base and drafts a plan for revising it.

The authors' motivation is that agreement between rollouts does not guarantee correctness. In a pool analysis (APEX-Agents, Opus, 1,692 claims), 34% of consensus values were wrong, and disputed claims contained a correct candidate 74% of the time while the most frequent value was right only 47% of the time (self-reported).

## Results

All numbers are self-reported. Setup: five document, spreadsheet and code workspace benchmarks (APEX-Agents v1.0 with 480 tasks, Workspace-Bench Lite, WorkBuddy, SpreadsheetBench 2, JobBench); each of two models, Claude Opus 4.8 and Gemini 3.5 Flash, serves both as generator and as verifier; all methods draw on one frozen pool of 10 rollouts; each score averages 3 verifier runs, and the benchmarks are averaged unweighted.

- Selection by itself adds 4.4 points over a lone rollout with Flash (from 47.2 up to 51.6); with Opus the gain is 4.1 points, taking it from 49.6 up to 53.7. Adding revision lifts the gains to 6.2 for Flash and 6.4 for Opus.
- Average baselines with Flash: majority vote scores 47.5; a best-of-N judge 47.3; a pairwise tournament 49.1; and LLM-as-a-Verifier, 49.5; and an agentic verifier that can reach the environment but follows no protocol scores 49.4, which by the authors' account recovers about half of the gain only. The selection oracle is 62.7.
- Ablation (Opus, full harness with revision), scores by variant: 54.3 with the resolver alone, 52.6 with the challenger alone, 56.1 with both, 53.8 without skills, and 55.3 with one merged context.
- Selection gain is +0.6 on 154 unanimous pools and +6.1 on 262 disputed ones.
- Verifier cost per task for selection is $1.44 with Flash and $3.92 with Opus, and revision multiplies it roughly threefold.
- Self-evolving the skill library on held-out subsets (single run): +11.0 on APEX-Agents from an empty library.

## Limits

- Authors concede the cost of 10 rollouts, no per-rollout score, same-model verification only and added latency.
- Document, spreadsheet and patch workspace tasks only; compared with the single-rollout mean, not a cheaper self-check or retry loop.
- The paper gives neither confidence intervals nor significance tests, and its graders are largely LLM judges.
- Evolution experiments use development-set grader feedback. Skills are human-authored.
- The extraction notes baseline costs are partly estimates.

## See Also

- [[Verification Loops]] — prerequisite-for
- [[LLM-as-a-Verifier]] — alternative-to (the strongest baseline in the comparison)
- [[Self-MoA Single-Model Aggregation]] — related
- [[Effective Feedback Compute]] — related
