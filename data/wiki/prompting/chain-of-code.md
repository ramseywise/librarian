---
title: Chain of Code
tags: [prompting, pattern]
summary: "The model writes reasoning as code; a Python interpreter runs each line and an LM emulator fills in lines that fail to execute (semantic helpers), giving 84 on BIG-Bench Hard against 72 for CoT in the paper (self-reported, text-davinci-003)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-li-2023-chain-code.md
---

# Chain of Code

Chain of Code (CoC; Li et al., 2023) extends [[Program-Aided Language Models (PAL)]]. The model writes a program for the task, including lines that call undefined helper functions for fuzzy steps (for example deciding whether a phrase is sarcastic). A Python interpreter executes the program line by line while keeping program state. When a line raises an error or cannot run, an LM emulator is asked to predict that line's output, and the prediction is written back into the state. The final answer is read from the resulting state.

## Reported results

- BIG-Bench Hard, 23 tasks, text-davinci-003: CoC 84, CoT 72, direct prompting 55 (self-reported). The paper puts the average human rater at 68.
- Ablations on the same setup: interpreter-only 48 and LM-only 57 (self-reported), so the mix beats both halves.
- On NLP-style tasks CoC ties CoT (74 vs 74, self-reported); gains concentrate on algorithmic tasks.
- CoC loses to CoT on the Ruin Names task (self-reported).

## Safety note

The paper executes model-written code as though it were benign. Anyone reusing the idea needs the sandboxing described in [[Execution Boundaries and Guardrails]].

## Limits

- One model family (text-davinci-003 headline); no later models on the headline table.
- Tasks are benchmark suites; no deployment-style evaluation.
- Emulator output is unchecked, so a wrong emulated line propagates into later lines.

## See Also
- [[Program-Aided Language Models (PAL)]] — prerequisite-for
- [[Chain of Thought]] — prerequisite-for
- [[Execution Boundaries and Guardrails]] — related (sandboxing generated code)
- [[Self-Consistency]] — related (a vote over several sampled programs is a natural combination, not tested here)
