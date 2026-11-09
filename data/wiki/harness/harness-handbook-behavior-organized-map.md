---
title: Harness Handbook Behavior-Organized Map
tags: [harness, pattern]
summary: A generated, source-linked three-level map of a harness codebase plus a shared-state register view, used to find every code site a behaviour change touches before planning an edit.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-wang-2026-harness-handbook.md
---

# Harness Handbook Behavior-Organized Map

The Harness Handbook (Wang et al., a July 2026 preprint) targets one problem in evolving agent harnesses: finding every code site that a behavioural change request touches, which the authors call the bottleneck. It builds a map organised by behaviour rather than by file layout, using static analysis plus LLM structuring.

## Structure

- L1 is a system overview, L2 describes stages or components, and L3 holds units with locators into the code.
- A cross-stage state-register view lists each shared state variable with all of its read and write sites. In one walkthrough on Terminus-2 a single Boolean flag appeared in 7 places across 3 functions; this is an anecdote from one trace.
- The repo stays the authority. A locator at L3 has to resolve to current code, otherwise its entry is frozen and left out; what the handbook holds is an index of locations, not source code. Whenever a diff is non-empty, a resync limited to that scope runs.
- The reading workflow, Behavior-Guided Progressive Disclosure, reads L1 and L2 to choose stages, follows the register view for coupled stages, opens just the relevant L3 entries, expands along the call graph and checks the result against the live repo. A site enters the plan only once verified.

## Results

All numbers are self-reported by the authors. Setup: planner DeepSeek-V4-Pro in a read-only environment, 30 requests per harness, three LLM judges, and a win is counted only if one harness leads by 3 points or more on a weighted score out of 100.

- Plan-quality win rate with the handbook against exploring the repo directly: Codex 38.3% vs 28.3%, Terminus-2 45.6% vs 26.7%.
- Planner tokens per request fell from 0.102M to 0.089M for Codex and 0.058M to 0.053M for Terminus-2; the count includes handbook and source context but not handbook construction.
- Measured against reference plans from Opus 4.8 and GPT-5.5 (these are not ground-truth edits), recall, precision and F1 improved in all 24 comparisons, F1 gains of 5.0 to 18.8 points; Codex gains against the GPT-5.5 reference were small.
- Slices are tiny (10 requests per type per harness).
- Scale: Terminus-2 is 6 files and 103 functions (20 stages, 10 registers); Codex is 2,267 files and 34,363 functions (140 stages, 62 registers).

## Limits

- Two harnesses, one planner model, LLM judges and LLM-written reference plans; no significance tests.
- Plans are scored, not executed as working patches.
- Construction and resync cost is excluded from the token comparison.
- No comparison against simpler baselines such as repo maps, AGENTS.md or code search.
- The extraction notes the paper's evidence concerns generated behaviour-to-code maps, not AGENTS.md entry files, and the paper does not discuss earlier findings on generated context files.

## See Also

- [[Harness Anatomy]] — prerequisite-for
- [[Progressive Disclosure and Skill Packs at Library Scale]] — related (progressive disclosure applied to skills)
- [[AGENTS.md Context File Evaluation]] — related (flat context files, contrasted with this navigable tree)
- [[Harness Continual Learning]] — related
