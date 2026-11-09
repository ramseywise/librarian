---
title: LLM Prompting for Mobile UI Screens
tags: [foundations, pattern]
summary: "A 2022 paper converts an Android view hierarchy to HTML and prompts PaLM with at most two exemplars for four screen-language tasks; one example in the prompt delivers most of the improvement, and results are rater-study and benchmark numbers with no agent loop (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-06-wang-2022-enabling-conversational-interaction-mobile-ui.md
---

# LLM Prompting for Mobile UI Screens

The paper (2022) feeds a mobile screen to a language model as text. The Android view hierarchy is traversed depth first and turned into HTML, keeping 4 properties per element. PaLM is prompted with at most 2 exemplars because of a 1920-token limit.

## Four tasks

From a 2x2 taxonomy (who takes initiative, by purpose), the paper tests screen question generation, screen summarization, screen question answering and mapping an instruction to a UI action.

## Results (self-reported)

- **Question generation.** 400 RICO screens, 2 exemplars with chain-of-thought, 931 questions rated by 3 raters each from 17 labelers: grammar 4.98 against 3.60 and relevance 92.8% against 84.1% versus the comparison method.
- **Summarization.** Screen2Words test set (4310 screens), 2 random exemplars, 37 annotators in blind A/B comparison: raters preferred the model's summaries 63.5% of the time over Screen2Words even though automatic metrics were lower (BLEU-1 45.0 against 65.5).
- **Screen QA.** 300 labelled QA pairs on 121 RICO screens, answerable ones scored; 1-shot exact match 65.8% against 36.0% for DistilBERT.
- **Instruction to action.** PixelHelp, 187 instructions; 2-shot with an exemplar from the same app: 80.36 partial / 45.00 complete, against 89.21 / 70.59 for Seq2Act.
- Most of the improvement comes from adding the first exemplar.

## Limits

- No agent loop: each task is a single prompt on one screen.
- Evidence is automatic metrics and rater studies; there is no user study.
- On the action task the prompted model trails the supervised baseline.

## See Also

- [[Computer Use Visual Grounding]] — prerequisite-for
- [[Few-Shot Prompting]] — prerequisite-for
