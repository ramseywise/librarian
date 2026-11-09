---
title: Program-Aided Language Models (PAL)
tags: [prompting, llm, concept]
summary: The model writes a program and an interpreter computes the answer — few-shot examples are code with the reasoning in comments, so exact computation (dates, arithmetic) moves out of the token predictor; only safe with a sandbox, and today usually a code-execution tool.
updated: 2026-11-09
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--03-core-techniques.md
  - data/raw/papers/2026-11-06-imani-2023-mathprompter.md
  - data/raw/papers/2026-11-06-yang-2024-number-cookbook.md
  - data/raw/papers/2026-11-07-drori-2022-neural-network-solves-explains-generates.md
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

## MathPrompter: agreement between two expressions

Imani et al. (2023) add a consistency check to program-aided arithmetic. With GPT-3 175B the model writes an algebraic template with variables, produces both an algebraic expression and a Python function for it, evaluates both on random values, accepts when they agree, and votes over several agreeing runs. On MultiArith accuracy went from 78.7 to 92.5 (self-reported, one dataset).

## Number understanding without tools

Yang et al. (2024, NUPA Test) measure GPT-4o on plain arithmetic with no tool. Integer addition is about 100% at 1 to 4 digits, 80% at 5 to 8, 40% at 9 to 14 and 15% at 15 to 20; float addition runs 90, 60, 15 and under 5. "Get digit" on 61 to 100 digit numbers scores 20% against a 10% random baseline (self-reported). The extraction notes the study tests no tool use and no frontier chain-of-thought models, uses different bin sizes per task, and covers 2024-era models. In its small from-scratch tokenizer experiments and a LoRA fine-tune of Llama-3.1-8B, a rule-following chain of thought ran about 17x slower per sample (5.625 vs 0.371 s, an A800, batch 128, 2k context).

## University math by program synthesis

Drori et al. (2022) give Codex (code-davinci-002, temperature 0) each question inside a Python docstring, sometimes with an automatic prefix such as "write a program" or "using sympy", run the generated program and compare its output with the answer. When the first attempt fails, the pipeline retrieves as many as five solved examples from the same course by embedding similarity and adds them to the prompt. On 175 questions (25 per course, drawn from seven courses at two universities), zero-shot Codex solved 71.1% and the full pipeline 81%; a text-davinci-002 baseline answering in prose solved 18.8% zero-shot and 30.8% with few-shot chain of thought. On 90 MATH questions (15 in each of 6 topics) Codex reached 72.2% zero-shot and 81.1% few-shot, against 25.5% and 42.2% for GPT-3 (all self-reported). The 81% includes the 19% of questions that were manually tidied or prompted interactively. The same pipeline also generated explanations and new questions; in a survey of 15 students, generated questions were rated about as difficult as human-written ones and slightly less appropriate. Limits: no image, proof or intractable questions; temperature 0 with one run per question; few-shot examples are added until the output matches the known answer, so that rate uses answer feedback; training-data exposure to public course material is possible (only one course is argued to be unseen); the MATH baseline quoted for comparison comes from a different sample.

## Limits

One dataset, and a failure case where both expressions agree and are wrong, so agreement is not proof.

## See Also
- [[Prompting Technique Selection]] — instance-of
- [[Chain of Thought]] — alternative-to (reasoning as code instead of prose)
- [[Execution Boundaries and Guardrails]] — prerequisite-for
- [[TheoremQA]] — related (benchmark that compares PoT with CoT)
- [[DualDistill Agentic-R1]] — related (student chooses between code and text)
- [[Chain of Code]] — extends (an LM emulator covers lines the interpreter cannot run)
- [[Logic-of-Thought]] — related (code expands logic facts, then appended to the prompt)
- [[Scratchpads and Self-Notes]] — related
- [[Math Word Problem Benchmarks]] — related
- [[ViperGPT Visual Inference via Python Execution]] — related (generated programs call vision modules)
