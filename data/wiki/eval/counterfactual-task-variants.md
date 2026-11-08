---
title: Counterfactual Task Variants
tags: [eval, pattern]
summary: "Test whether a model's success is general by changing the task's world (number base, indexing, axes, chess setup) while keeping the reasoning procedure fixed, with a comprehension check to separate misunderstanding from failure; GPT-4 showed a large drop from base-10 to base-9 addition across 1,000 additions per base (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-08-wu-2024-reasoning-or-reciting.md
---

# Counterfactual Task Variants

Wu et al. (NAACL 2024) ask if the strong results of language models on standard tasks reflect general reasoning that
transfers, or narrow procedures that only work under the default conditions common in pretraining. Their
hypothesis: models that implement general procedures perform comparably on default and counterfactual
variants; models relying on default-specific procedures drop on the counterfactual ones.

## The method

A **counterfactual task** keeps the reasoning procedure fixed but deviates from the default conditions of
the standard task, for example by changing the number base. Each is paired with a **counterfactual comprehension check
(CCC)**: an easier control task that tests whether the model grasps the stated counterfactual world, much
like control tasks in probing. The suite holds 11 tasks spanning the card game SET, chess, music, drawing, spatial
reasoning, logic, syntax, code and arithmetic. Four LMs are evaluated zero-shot, with and
without zero-shot chain of thought (0-CoT).

## Results (self-reported)

Setup unless stated: GPT-4 (gpt-4-0314), 0-CoT, temperature 0. The extraction gives no accuracy values for most
rows, so the findings below are directional.

- **Arithmetic.** Two-digit addition, 1,000 per base: a large gap between base 10 and base 9, and without CoT base 9
  is far below base 10. Sixteen few-shot CoT demonstrations shrink the gap without removing it, and in both bases
  accuracy declines as the number of digits grows.
- **Code execution.** 113 test cases distinguishing 0- from 1-based indexing: a gap under 1-based indexing, but the
  comprehension check (750 items) stays high, so the authors conclude the gap is not a comprehension failure.
- **Code generation.** HumanEval subset of 53 problems that distinguish 1-based indexing, 50 samples, pass@1 at
  temperature 0.1 and pass@10 at 0.8, default against counterfactual.
- **Spatial reasoning.** 100 rooms with 3 objects each (random about 16.7%): rotating axes 180 degrees collapses
  accuracy, and swapping north and south, the most common counterfactual, degrades least. PaLM-2 is more robust
  than GPT-4 despite lower default accuracy.
- **Chess.** 400 balanced openings with swapped knight and bishop start positions (chance 50%): near chance.
- **Logic, syntax and others.** SET (100 boards), melodies in non-C-major keys (8 melodies), guitar chords with
  two altered strings (120 chords) and drawing with 180-degree rotation (100 emoji objects, 4 annotators) are also
  tested; the basic-syntax task (100 PTB sentences, SVO vs VSO order) showed a smaller gap than the other tasks.
- **Logic and common sense.** On 81 FOLIO instances with premises rewritten to violate common sense, a logistic
  regression over 1,204 instances and four LMs shows every LM is right more often when more premises are true and
  when the conclusion's truth agrees with the label; for a robust reasoner those coefficients would be 0.

## Limits

- A counterfactual version can be harder than its default in itself (base 11 adds a digit; a melody in another key may call for a
  two-step transposition), so a gap may reflect difficulty or may understate overfitting.
- Counterfactual conditions might occur in pretraining, in which case truly unseen conditions could show larger gaps.
  Certain perturbations allow a shortcut back to the default (logic word replacement, drawing transforms), which
  plausibly explains the high logic counterfactual performance.
- The comprehension check is a heuristic, and an imperfect check leaves comprehension failure and task
  failure entangled.
- The FOLIO subset is 81 instances; seeds are absent and each item got a single greedy run; PaLM-2 was not the biggest
  model available; the models are API snapshots from 2023. The authors admit an ideal prompt might exist;
  few-shot demonstrations reduce the gap but leave some of it.

## See Also
- [[GSM-Symbolic]] — alternative-to (changes names, numbers and clauses of one benchmark instead of the task's world)
- [[Embers of Autoregression]] — alternative-to (tests sensitivity to output probability and task frequency rather than to a changed world)
- [[Eval Contamination Defenses]] — related (the pretraining-exposure question both address)
