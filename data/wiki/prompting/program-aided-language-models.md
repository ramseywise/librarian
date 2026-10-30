---
title: Program-Aided Language Models (PAL)
tags: [prompting, llm, concept]
summary: The model writes a program and an interpreter computes the answer — few-shot examples are code with the reasoning in comments, so exact computation (dates, arithmetic) moves out of the token predictor; only safe with a sandbox, and today usually a code-execution tool.
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--03-core-techniques.md
---

# Program-Aided Language Models (PAL)

Gao et al. (2022). Follows the tokens rule of [[Prompts as Document Completion]]: **don't
ask the model to do what code does reliably.** Arithmetic, date maths and string
manipulation are sub-token or exact-computation tasks the model does poorly.

## Mechanism

The few-shot examples are **code with the reasoning in comments**, so the model's
completion is itself a program:

```python
# Q: 2015 is coming in 36 hours. What is the date one week from today in MM/DD/YYYY?
# If 2015 is coming in 36 hours, then today is 36 hours before.
today = datetime(2015, 1, 1) - relativedelta(hours=36)
one_week_from_today = today + relativedelta(weeks=1)
answer = one_week_from_today.strftime('%m/%d/%Y')
# Q: {question}
```

The app runs the completion and reads a variable (`answer`). The model does the
decomposition; Python does the computation.

## Caveats

- **`exec` on model output is acceptable only in a sandbox** ([[Execution Boundaries and Guardrails]]).
- Today this is usually a **code-execution tool** rather than a hand-built prompt — the
  same idea delivered via [[Tool Definitions as Prompts]].
- The general principle — move deterministic work out of the model — recurs throughout the
  wiki, e.g. [[Length Limits Are a Fit Layer, Not a Prompt]].

## See Also
- [[Prompting Technique Selection]] — instance-of
- [[Chain of Thought]] — alternative-to (reasoning as code instead of prose)
- [[Execution Boundaries and Guardrails]] — prerequisite-for
