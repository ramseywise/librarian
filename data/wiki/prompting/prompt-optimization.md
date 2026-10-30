---
title: Prompt Optimization
tags: [prompting, eval, concept]
summary: Treat the prompt as a versioned artifact searched against a fixed eval set and metric — by hand (cheapest layer first, one change at a time), by an LLM proposer (APE, OPRO, meta-prompting) or by a framework (DSPy, TextGrad); an optimizer without a metric is just a rewriter.
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--08-prompt-optimization.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--07-prompting-reasoning-models.md
---

# Prompt Optimization

```
template v1 → run on eval set → score → propose changes → template v2 → keep if it beats …
```

The proposer can be a human, an LLM, or a framework. What matters is the same in every
case: **a fixed eval set, a metric, and a record of every version** ([[Evaluating Prompts]]).

## Prompts as versioned artifacts

- Version the **template**, not the rendered string ([[Prompt Templates and Variables]]).
- Store it like code (repo or registry) with ID, version, the model it was tuned on and its
  eval score. **Pin the model version** — prompts are not portable across models.
- **Diff behaviour, not text**: a one-word change can move scores; regression-test every edit.
- Log production I/O per prompt version — tomorrow's eval set and optimizer training data.

## LLM as proposer

- **APE** (Zhou et al., 2022): an LLM drafts candidate instructions from input/output
  demonstrations, each is scored on the target model (e.g. by log-probability of correct
  outputs), winners are resampled. It found a zero-shot CoT trigger that beat "Let's think
  step by step" on arithmetic benchmarks.
- **OPRO** (2023): the LLM optimizer sees past prompts and their scores in context.
- **Prompt-OIRL**: offline inverse RL to pick query-dependent prompts.
- Gradient-based search (AutoPrompt, prefix and prompt tuning) needs model access and
  borders on [[Fine-Tuning as Prompt Compression]].

The lesson is not the magic phrases — model-specific and dated — but that **search
against a metric beats intuition** once you have one.

## Meta-prompting (two senses)

1. **Structure-oriented prompting** (Zhang et al., 2024): give an abstract solution
   *template* for a class of problems instead of worked examples. Token-efficient, avoids
   example anchoring ([[Few-Shot Prompting]]), behaves like zero-shot; degrades on
   genuinely novel domains.
2. **A model writing prompts** — the common sense in practice: a strong (often reasoning,
   [[Prompting Reasoning Models]]) model drafts a system prompt or critiques and rewrites
   one given failing cases; vendor prompt generators/improvers do this. The
   evaluator–optimizer loop automates it: a judge scores and writes feedback, a meta-prompt
   turns feedback into a revised prompt. Generated prompts are **a first draft, not a
   result** — they must still win on the eval.

## Frameworks

[[DSPy]] compiles signature-and-module programs against a metric (few-shot selection,
instruction search, distillation); TextGrad propagates LLM-written critiques ("textual
gradients") back through a pipeline. Worth it for multi-step pipelines with a scorable
metric and dozens to hundreds of labelled examples; skip for one-off prompts.

## Manual checklist

1. Find the **failure category** in eval results — format, missing context, wrong
   reasoning, instruction ignored.
2. Fix the **cheapest layer first**: instruction clarity → missing context → ordering →
   examples → CoT → splitting the task ([[Prompt Chaining]]) → stronger model → fine-tuning.
3. **Change one thing at a time** and re-score.
4. **Keep the losers** so you don't retry them.

## See Also
- [[Evaluating Prompts]] — prerequisite-for
- [[DSPy]] — extends
- [[Fine-Tuning as Prompt Compression]] — alternative-to
- [[Prompt Templates and Variables]] — extends
