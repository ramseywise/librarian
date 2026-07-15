---
title: Skill Eval Pipeline (Blind Comparison + Grading)
tags: [eval, pattern]
summary: Three-agent pipeline for A/B testing Claude Code skills — a blind comparator scores two outputs on a rubric without knowing which skill produced them, a grader checks explicit expectations pass/fail with cited evidence, and a post-hoc analyzer unblinds the result to explain why the winner won and suggest concrete improvements to the loser.
updated: 2026-07-14
sources:
  - raw/claude-docs/galactus/skills/skill-eval/comparator/SKILL.md
  - raw/claude-docs/galactus/skills/skill-eval/grader/SKILL.md
  - raw/claude-docs/galactus/skills/skill-eval/analyzer/SKILL.md
---

# Skill Eval Pipeline (Blind Comparison + Grading)

A generic (framework-agnostic, not company-specific) three-agent pipeline for evaluating Claude Code skills against each other or against a defined set of expectations — the mechanism behind "run with-skill vs. without-skill (or old-vs-new) side by side" in [[Claude Workflow System]]'s `/skill-creator` testing loop.

## Why Three Separate Agents

Each agent has a narrow, non-overlapping job, and the split exists specifically to prevent bias:

| Agent | Sees which skill produced which output? | Job |
|---|---|---|
| **Blind Comparator** | No | Judge which of two outputs (A/B) better accomplishes the task |
| **Grader** | N/A (single output) | Check a list of expectations against one transcript/output, PASS/FAIL with evidence |
| **Post-hoc Analyzer** | Yes (runs after the winner is known) | Explain *why* the winner won and generate improvement suggestions for the loser |

## Blind Comparator

Receives two outputs labeled A and B — deliberately without knowing which skill produced which — plus the original task prompt and an optional list of expectations. Generates a task-specific two-dimension rubric on the fly: a **Content Rubric** (correctness, completeness, accuracy) and a **Structure Rubric** (organization, formatting, usability), each scored 1–5 per criterion. Decision order is strict: **primary** = overall rubric score, **secondary** = expectation pass rate (used only as corroborating evidence, never the primary signal), **tiebreaker** = declare a TIE only if genuinely equal — ties should be rare. Output is a JSON file with per-side rubric scores, strengths/weaknesses, and expectation results.

## Grader

Evaluates a fixed list of expectations against one execution transcript and its output files, citing evidence for every verdict — no partial credit, each expectation is strictly PASS or FAIL. PASS requires evidence of *genuine* task completion, not surface-level compliance (e.g. a correct filename with wrong or empty content still fails). The grader has a second, equally important job: **critiquing the evals themselves** — flagging an assertion that would also pass for a clearly wrong output, an important outcome no assertion covers, or an assertion that can't be verified from the available outputs. A passing grade on a weak assertion is treated as worse than useless, since it creates false confidence in the eval suite.

## Post-hoc Analyzer

Runs only after the Blind Comparator has already declared a winner — its job is to "unblind" the result by reading both skills' `SKILL.md` files and both execution transcripts side by side, scoring instruction-following 1–10 for each, and producing prioritized (`high`/`medium`/`low`) improvement suggestions for the losing skill, categorized as `instructions` / `tools` / `examples` / `error_handling` / `structure` / `references`. Priority is explicitly about causal impact — "would this change have changed the outcome of this comparison?" — not just general polish.

**Second mode — benchmark analysis:** the same analyzer agent also has a distinct job when reviewing multi-run benchmark data (not a head-to-head comparison): surface per-assertion patterns (does an expectation always pass/fail regardless of skill? pass with-skill only?) and cross-eval patterns (which eval types are consistently harder or more variable) as freeform, data-grounded observations — explicitly not skill-improvement suggestions and not a repeat of the run's own aggregate summary.

## See Also
- [[Claude Workflow System]]
- [[Anthropic Three-Tier Eval Taxonomy]]
- [[LLM Grader Calibration Insights]]
- [[Grounding Claim Methodology]]
