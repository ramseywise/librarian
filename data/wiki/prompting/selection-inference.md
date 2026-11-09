---
title: Selection-Inference
tags: [prompting, pattern]
summary: "Split multi-step logical reasoning into alternating Selection calls (pick facts) and Inference calls (derive one new fact from only those facts), so each step depends on the last; the paper reports a 7B model beating larger baselines on 10 tasks (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-creswell-2022-selection-inference.md
---

# Selection-Inference

Creswell, Shanahan and Higgins (arXiv v1, 2022) ask whether replacing one long chain of reasoning with alternating Selection and Inference calls improves accuracy and yields a trace that is causal and inspectable. Their starting observation is that language models do single-step inference well and chain steps poorly, checked on 50 logical reasoning tasks.

## Mechanism

Frozen Gopher-family models are prompted few-shot in two roles. The **Selection** module picks facts or rules from the context by scoring each context sentence with the model's log-likelihood. The **Inference** module sees only that selection, not the question, and writes one new fact, which is appended to the context. The loop runs for a fixed number of steps and the last inference is the answer. A variant fine-tuned on ProofWriter single steps is also tested.

A **causal reasoning trace**, in the paper's sense, is one in which every step is derived from, and relies on, the step before.

## Results

All numbers are the paper's own (self-reported).

- Setup for the first group: a frozen Gopher-family 7B model with 5-shot prompts and no fine-tuning, scored by generative exact match over ten tasks: bAbI tasks 1, 2, 3, 15 and 16, plus ProofWriter OWA at depths 0, 1, 2, 3, 5 with Unknowns removed. Selection-Inference on the 7B model beats the same model prompted plainly, the same model with chain-of-thought prompts, and the plain and chain-of-thought 280B baselines. The abstract's headline is over 100% improvement against the equivalent plain baseline.
- Fine-tuned Selection-Inference on ProofWriter beats the prompt-engineered version, which scored 57.93%, and the baselines (7B fine-tuned on single steps). A Selection model fine-tuned for 4x10^4 steps keeps high accuracy across depths.
- In multi-choice scoring the plain 7B model beats the plain 280B model; the authors speculate the larger model has stronger priors.
- Gopher 280B, 5-shot, on 38 multi-choice logic tasks, is only modestly above chance. On a 2WikiMultiHop dev subset, models degrade when Wikipedia paragraphs are added.

## Limits

- Selection is where the method mostly fails, and without labelled intermediate steps the failures are hard to count.
- There is no halting mechanism, so the number of steps is fixed and only the final inference is scored.
- Every needed fact is presumed to sit in the context, and nothing is retrieved.
- The tasks are deductive with a few inductive ones, and the method ran on 10 of the 50.
- Prompt engineering has trouble with multi-step selection and with rules that take several arguments, and the lead narrows as ProofWriter depth increases.
- There are no seeds or repeated runs, and neither temperature nor learning rate is given.
- The Gopher models are not public, and this source is arXiv v1, so figures may differ in the ICLR 2023 version.

## See Also
- [[Chain-of-Thought Prompting]] — prerequisite-for (the baseline it is compared against)
- [[Prompt Chaining]] — prerequisite-for
- [[Compositionality Gap]] — related (the failure it targets)
- [[Iterated Decomposition]] — related (select-then-generate pipelines refined by hand)
- [[RuleTaker]] — related (fine-tuned alternative on synthetic rule theories)
