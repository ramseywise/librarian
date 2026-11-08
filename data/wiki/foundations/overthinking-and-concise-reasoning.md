---
title: Overthinking and Concise Reasoning
tags: [foundations, concept]
summary: "Longer reasoning is not better reasoning: o1-like models spend thousands of extra tokens on easy questions after a correct first answer, and several methods (self-training, length caps, token-complexity thresholds) trade a small accuracy loss for large token savings."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-chen-2024-do-not-think-that-much.md
  - data/raw/papers/2026-11-06-lee-2025-how-well-do-llms-compress.md
  - data/raw/papers/2026-11-06-nayab-2024-concise-thoughts.md
---

# Overthinking and Concise Reasoning

## The overthinking observation

Chen et al. (2024) examine o1-like models (QwQ-32B-Preview and DeepSeek-R1). On the question "2+3" they report 1,953% more tokens than a conventional model (self-reported). More than 92% of cases already contained a correct first solution (self-reported), with later solutions mostly re-checking it. Their fix is SimPO self-training on shorter self-generated answers: on MATH500 tokens fell 48.6% while accuracy moved from 93.0 to 92.8; on AIME24 accuracy dipped from 46.7 to 43.3 (self-reported).

## Token complexity

Lee et al. (2025) argue accuracy depends on how many tokens the reasoning uses, not on the format. A threshold classifier on that length reaches about 90% (the introduction claims 94%) (self-reported). Prompting for brevity (BeConcise) cut tokens 1.2x to 1.4x against an oracle bound of 3.2x to 11.2x, and routing with a verifier approached the bound (self-reported). Non-reasoning models only.

## Length-capped CoT

Nayab et al. (2024) cap zero-shot chain-of-thought at a word budget (CCoT). Llama2-70b on GSM8K: 36 with plain CoT, 37 at a 30-word cap and 41.77 at a 100-word cap, with time falling from 30.09 s to at most 23.86 s (self-reported). Results were mixed on Falcon-40b and it failed on small models.

## Limits

- Chen: maths and science only; the text and Figure 7 disagree on the level-1 efficiency figure.
- Lee: the 90% vs 94% classifier figures differ between sections.
- Nayab: several table inconsistencies; models are 2023 vintage and the cap is a prompt, not enforced.
- None of the three tests the same model, so the savings are not comparable across rows.

## See Also
- [[Prompting Reasoning Models]] — prerequisite-for (effort settings are the practical dial)
- [[Chain of Thought]] — prerequisite-for
- [[Inverse Scaling in Test-Time Compute]] — related (longer reasoning lowering accuracy)
- [[DeepConf Confidence-Filtered Voting]] — related
- [[Price Reversal in Reasoning-Model Costs]] — related
- [[Scaling Axes and Customer-Triggered Cost Cliffs]] — related
