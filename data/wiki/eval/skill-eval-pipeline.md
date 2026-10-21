---
title: Skill Eval Pipeline (Blind Comparison + Grading)
tags: [eval, pattern]
summary: Three-agent pipeline for A/B testing Claude Code skills — a blind comparator scores two outputs on a rubric without knowing which skill produced them, a grader checks explicit expectations pass/fail with cited evidence, and a post-hoc analyzer unblinds the result to explain why the winner won and suggest concrete improvements to the loser.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/project-g/skills/skill-eval/comparator/SKILL.md
  - data/raw/claude-docs/project-g/skills/skill-eval/grader/SKILL.md
  - data/raw/claude-docs/project-g/skills/skill-eval/analyzer/SKILL.md
  - data/raw/claude-docs/galactus/skills/skill-creator/SKILL.md
  - data/raw/claude-docs/galactus/skills/skill-creator/references/schemas.md
  - data/raw/claude-docs/guacamayo/skills/skill-creator/references/schemas.md
  - data/raw/claude-docs/guacamayo/docs/plans/2026-07-18-skills-refs-evals-norm.md
  - data/raw/repos/guacamayo/.claude--docs--plans--2026-07-18-skills-refs-evals-norm.md
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

## Run discipline (skill-creator)

The vendored `skill-creator` skill wraps the same comparison in an iteration loop:

- **Spawn the with-skill and baseline runs in the same turn** so they finish together. The
  baseline is "no skill" for a new skill, and a snapshot of the old version
  (`cp -r` before editing) for an improvement.
- Draft objectively checkable assertions *while* runs are in flight. Subjective qualities
  are left to human review rather than forced into assertions.
- **Read transcripts, not just outputs.** If every run independently wrote the same helper
  script, the skill should bundle that script.
- Generalise from feedback instead of overfitting the few test prompts. All-caps
  ALWAYS/NEVER is a yellow flag; explain the *why* instead.
- Artifacts follow fixed JSON schemas (`evals.json`, `grading.json`, `benchmark.json`,
  `comparison.json`, …), so iterations can be compared.
- Trigger accuracy is tuned separately (see [[Skill Discovery Failure Modes]]).

## Two-tier eval default

A cross-repo skill audit made this the default in skill-creator, replacing an open-ended
"set up test cases?" prompt:

- **Triggering eval for every skill.** It is cheap and is the default. Each skill gets
  6–9 cases in `evals/evals.json` as `{"input": ..., "expected": true/false}`: 4–6
  positive prompts and 2–3 negative near-misses. It answers *does the description fire
  when it should, and only then?*
- **Behavioral eval only for judgment-shaped skills.** That means fixtures, graded
  assertions and variance runs, the three-agent pipeline above. Procedural skills (lint,
  sync, pipeline runners) get triggering evals only, because a behavioral eval on a fixed
  procedure costs a lot and measures nothing.

The norm went into skill-creator, which loads when a skill is being written. It was not
put in always-on rules. Before it was rolled out, the copies were de-duplicated (see
[[De-Dupe Before You Normalize]]).

## See Also
- [[Eval Harness Anatomy]] <!-- auto-linked -->
- [[System Design — Unified Eval Harness]] <!-- auto-linked -->
- [[project-g Eval Architecture]] <!-- auto-linked -->
- [[Claude Workflow System]]
- [[Anthropic Three-Tier Eval Taxonomy]]
- [[LLM Grader Calibration Insights]]
- [[Grounding Claim Methodology]]
- [[Skill Discovery Failure Modes]] — extends (trigger evals for the description, beside output-quality evals)
- [[Verification Thins Where Blast Radius Widens]] — extends (what happens when only the trigger evals run)
- [[De-Dupe Before You Normalize]] — related (classify skill copies before rolling the eval norm out)
