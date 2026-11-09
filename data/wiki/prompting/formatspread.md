---
title: FormatSpread
tags: [prompting, concept]
summary: "Meaning-preserving changes to prompt format (casing, separators, spaces, enumeration) move few-shot accuracy by up to 76 points on LLaMA-2-13B; FormatSpread estimates the min-max spread across formats with a bandit under a budget, without model weights (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-07-sclar-2023-quantifying-language-models-sensitivity-spurious.md
---

# FormatSpread

Sclar, Choi, Tsvetkov et al. (ICLR 2024) ask how much accuracy changes under formatting choices that keep the meaning of a prompt, and how to measure that cheaply. They argue that reporting one format is misleading.

## Method

A hand-written grammar generates formats that mean the same thing by varying descriptor casing, separators, spaces and enumeration style. The paper samples formats for 53 Super-NaturalInstructions tasks and runs few-shot prompts on LLaMA-2, Falcon and GPT-3.5, then reports **performance spread**, the best metric minus the worst over plausible formats. **FormatSpread** treats format selection as a bandit problem and uses Thompson sampling under an evaluation budget, needing only black-box access. An **atomic change** alters one constant, such as a space, separator, casing or item format.

## Results

All figures are the paper's own (self-reported); setups differ per row.

- Equivalent formats shift accuracy by up to 76 points for LLaMA-2-13B, and by about 10 on average (few-shot, 50+ tasks, several models). Larger models, more shots and instruction tuning do not remove the sensitivity.
- Pairwise format ordering is preserved across models only slightly above chance (LLaMA-2-7B against 13B).
- GPT-3.5 shows a spread up to 56 points over 320 formats, at under 10 USD per task (53 tasks, exact prefix matching).
- Budget: with 51,200 evaluations over 320 formats (20 per round, 5 trials, 31 tasks), Thompson sampling lands within 1 point of the true spread, a naive search within 4 and UCB within 11. On one task with 2,500 test examples, 5% of the search space estimates spread within 2 points.
- Monotonic triples of atomic changes occur no more often than chance would give, which makes local search ineffective. Spread is not explained by prompt length.
- Top 100 principal components of LLaMA-2-7B prompt embeddings identify the format at 0.98 accuracy or more (10 formats, 31 tasks, XGBoost).
- One constant edit lifts a single task from 0.043 to 0.826 accuracy (probability ranking, model not named in the table).

## Limits

- Some "equivalent" formats look odd to people; parsing choices create unusual strings in under 20% of cases.
- Instructions and inputs are short; only casing, separators, spaces and enumeration change, and wording, instructions and examples are held fixed.
- Spread measured over 10 formats is a lower bound that rises with more formats, and no noise floor or confidence interval is given for it.
- GPT-3.5 is scored by prefix matching and LLaMA by ranking, so their medians cannot be compared; LLaMA-2-70B ran 4-bit quantized.
- The models are LLaMA-2, Falcon-7B and GPT-3.5-Turbo, all few-shot; the 31-task analyses draw on a task set the paper does not fully name.

## See Also
- [[Benchmark Prompt Format Sensitivity]] — related (the same effect on benchmark scores)
- [[Prompt Order Sensitivity and Entropy Probing]] — related
- [[Few-Shot Prompting]] — prerequisite-for
- [[Evaluating Prompts]] — prerequisite-for
