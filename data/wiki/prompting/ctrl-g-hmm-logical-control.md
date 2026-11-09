---
title: Ctrl-G HMM Logical Control
tags: [prompting, pattern]
summary: Ctrl-G distills a hidden Markov model from the LLM, compiles a logical constraint to a DFA, and reweights next-token probabilities by the chance of satisfying the constraint; it reached full constraint success on text editing, but needs logit access and a distilled model per LLM.
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-zhang-2024-adaptable-logical-control-large-language.md
---

# Ctrl-G HMM Logical Control

Ctrl-G constrains an LLM to satisfy logical constraints, such as required keywords or an exact length, without retraining the LLM for each constraint. Three parts work together: an HMM distilled from the LLM, a DFA compiled from the constraint, and a decoding rule that multiplies the LLM's next-token probability by the HMM's estimate that the constraint can still be satisfied. The paper writes this as p_ctrl-g proportional to p_lm times p_hmm(constraint | prefix). The cost is O(nmh²) in the paper's notation (self-reported).

## Reported results

All are (self-reported), with TULU2-7B as the controlled model unless noted.

- Text editing: 100% constraint success, while GPT-4 tops out at 60%.
- Human-evaluated overall satisfaction (fluent and constraint-satisfying), averaged over the K, L and K&L settings: 79% against 24% for GPT-4.
- CommonGen (GPT2-large, compared with GeLaTo, not TULU2-7B): BLEU-4 of 31.5 against 29.0.
- A human evaluation reports Kendall's W of 0.449.

## Comparison with grammar-constrained decoding

The paper's section 3.3 contrasts Ctrl-G with grammar-constrained decoding such as [[Outlines Guided Generation]]. The extraction notes that the paper runs no structured-output or grammar-decoding baseline, so this is argued, not measured.

## Limits

- An HMM must be distilled for every LLM.
- Logit access is needed, so closed API models are out.
- No head-to-head against grammar-decoding libraries.
- Comparisons with GPT-4 differ in access: GPT-4 is prompted, Ctrl-G controls decoding.

## See Also
- [[Structured Output]] — prerequisite-for
- [[Outlines Guided Generation]] — alternative-to
- [[Length Limits Are a Fit Layer, Not a Prompt]] — related
- [[Logits Masking and Grammar-Constrained Generation]] — alternative-to
