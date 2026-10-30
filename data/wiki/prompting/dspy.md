---
title: DSPy
tags: [prompting, eval, concept]
summary: DSPy replaces hand-written prompts with signatures and modules that an optimizer compiles against a metric and training set — bootstrapping and ordering few-shot demonstrations, searching instruction wordings, or distilling into weights; worth it only with a multi-step pipeline, a scorable metric and labelled data.
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--08-prompt-optimization.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--06-chaining-and-workflows.md
---

# DSPy

DSPy treats a prompt pipeline as a program:

- **Signatures** declare I/O (`question -> answer`) instead of prose instructions.
- **Modules** (`ChainOfThought`, `ReAct`) implement a prompting strategy over a signature.
- An **optimizer** (teleprompter) *compiles* the program against a metric and a training set.

## What the optimizer does

| Mode | Mechanism | Why it matters |
|---|---|---|
| Few-shot selection | Bootstraps demonstrations from successful runs; chooses which examples and in what order | Directly addresses the few-shot drawbacks — anchoring and spurious order patterns ([[Few-Shot Prompting]]) |
| Instruction optimization | Proposes and searches instruction wordings (MIPRO-style) | Automated version of the manual rewrite loop |
| Fine-tuning | Distills the compiled program into weights | Ends at [[Fine-Tuning as Prompt Compression]] |

**TextGrad** is the nearest alternative: LLM-written critiques ("textual gradients")
propagated backward through a pipeline to revise each component's prompt.

## When to use

A multi-step pipeline ([[Prompt Chaining]]), a metric you can score automatically, and
dozens to hundreds of labelled examples. Skip for one-off prompts or tasks you can't score.
Like every optimizer, it is only as good as the eval behind it ([[Evaluating Prompts]]).

## See Also
- [[Prompt Optimization]] — instance-of
- [[Few-Shot Prompting]] — extends
- [[Prompt Chaining]] — extends
