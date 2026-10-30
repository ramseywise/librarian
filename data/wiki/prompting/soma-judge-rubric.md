---
title: SOMA Judge Rubric
tags: [prompting, eval, pattern]
summary: Write LLM-judge rubrics as Specific questions on an Ordinal, level-described scale across Multiple Aspects — never tell the judge it is grading its own work, split Goldilocks questions into separate axes, put the rubric before the content, and treat scores as relative.
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--09-evaluating-prompts.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--prompt-library.md
---

# SOMA Judge Rubric

A rubric recipe from Berryman & Ziegler for judge prompts in [[Evaluating Prompts]].

| | Rule | Why |
|---|---|---|
| **S**pecific questions | "Did it pick the heating system?" — not "Is this right?" | A generic question is as hard as the task and more ambiguous |
| **O**rdinal scale | 1–5 with every level described | Yes/no hides degrees; undefined levels drift between runs and let the judge hold ambitious answers to a stricter bar than safe ones |
| **M**ulti-**A**spect | Score each dimension separately, e.g. **intent** (right plan?) vs **execution** (carried out correctly?) | One composite score lets the judge silently switch criteria |

A widely used code-assistant chat product split its judge into **RTC**: relevance, truth,
completeness.

**Avoid Goldilocks questions** that fold "enough" and "not too much" into one axis ("is
the length right?") — split into "complete?" and "concise?".

## Framing and placement

- **Never let the model know it is grading its own work.** Self-grading is pulled two ways:
  forum-style pretraining data is not known for objective self-reflection, and RLHF
  trains deference at any hint of doubt. Frame the output as another system's.
- **Rubric before content** — the judge reads once, left to right
  ([[Prompts as Document Completion]]), so state the aspects first, then the example.
- Output per-aspect scores as JSON so they can be aggregated.

## Interpreting scores

- **Scores are relative.** "81% correct" means little alone; "B is judged correct more
  often than A" is the valid claim.
- **Calibrate against humans** — several annotators, not one. The bar: adding the model
  (temperature 0) to the annotator pool does not increase disagreement (e.g. Kendall's τ).
- Reasoning models make strong judges ([[Prompting Reasoning Models]]); pairing a judge
  with a prompt rewriter yields an optimizer ([[Prompt Optimization]]).

## See Also
- [[LLM-as-Judge Evaluation]] — extends
- [[Evaluating Prompts]] — instance-of
- [[Prompt Optimization]] — prerequisite-for
