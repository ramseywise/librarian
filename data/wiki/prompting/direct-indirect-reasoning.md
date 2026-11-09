---
title: Direct-Indirect Reasoning (DIR)
tags: [prompting, pattern]
summary: Adds indirect reasoning prompts, contrapositive and proof by contradiction, alongside direct reasoning chains and votes over both, improving logical reasoning and mathematical proof tasks.
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-zhang-2024-large-language-models-as-indirect.md
---

# Direct-Indirect Reasoning (DIR)

Models reason forward by default. DIR adds two indirect strategies by prompt: the contrapositive (if the conclusion's negation holds, so does the premise's) and contradiction (assume the claim false and derive an impossibility). Equal numbers of direct (DR) and indirect (IR) chains are voted together, on top of self-consistency, cumulative reasoning (CR) or the MulAD debate method.

## Reported results (self-reported)

Test sets are small and runs single.

- LogiQA, GPT-3.5-turbo, 16 chains, 179 questions: SC-DIR beats SC by 7.2.
- ProofWriter 5-hop, 200 questions: MulAD-DIR with Llama-3-70B 87.5 against 78.0; Gemini-pro 57.0 against 46.0.
- ProofWriter_S (150 hand-selected items): IR alone 50.7 against 17.3 for DR. ProofMath_S (35 items): 82.6 against 57.1. Zero-shot IR 49.3 against 15.3.
- ProofMath, 100 problems: CR-DIR 72.0 against 57.0.
- Removing either the contrapositive or the contradiction instruction degrades IR. Without prompting, models rarely use indirect reasoning (70 questions from each of four datasets).

## Limits

- Gains vary by model; only two logical laws were tried.
- Test sets are 50 to 200 items and runs are single. The DR-versus-IR comparison uses hand-selected subsets chosen to show IR.
- Proofs were judged by 5 graduate students. Dated models; no code release stated.

## See Also

- [[Self-Consistency]] — prerequisite-for
- [[Chain-of-Thought Prompting]] — prerequisite-for
- [[Logic-of-Thought]] — related
- [[Aggregation of Reasoning (AoR)]] — related (both change how sampled chains are combined)
