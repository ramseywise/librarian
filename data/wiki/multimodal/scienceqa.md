---
title: ScienceQA
tags: [multimodal, concept]
summary: "ScienceQA is 21,208 K-12 multimodal science questions with annotated lectures and explanations; few-shot GPT-3 with chain of thought is the best model and gold explanations in the prompt lift it to 94.13 (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-lu-2022-learn-explain.md
---

# ScienceQA

Lu et al. (NeurIPS 2022) build a multimodal science question benchmark with annotated lectures and explanations to test whether language models gain from generating a chain of thought, both when fine-tuned and when prompted. Questions are scraped from IXL Learning, cleaned and split 60:20:20. Language models see a generated caption (maximum 16 tokens) in place of the image. A chain of thought here is a flow of sentences revealing premises and conclusion; the notation QCM->ALE means question, context and options in, answer then lecture then explanation out.

## Results (self-reported)

- The best model is few-shot GPT-3 with chain-of-thought prompting (text-davinci-002, 2 shots, temperature 0), though the gain over answering directly is a modest 1.20 points. Humans, with three AMT workers per question, beat every model.
- Fine-tuned UnifiedQA-base gains from generating a lecture and explanation (QCM->A is 70.12). With chain-of-thought output it matches the version without it using 40% of the training data.
- Question-only and caption-only blind baselines are near random (caption only 39.87 against chance 39.83), run on the Top-Down model without the options.
- Upper bound: GPT-3 given the gold lecture and explanation in the prompt reaches 94.13 against 75.17 for QCM->ALE. Predicting lecture and explanation before the answer lowers GPT-3 to 73.6 (on 1,000 test examples).
- Picking in-context examples from the same topic does not beat random picks, scoring 74.58 when matched by category and 75.10 when matched by skill.

## Limits

- Captions describe diagrams badly, and no experiment tests GPT-3 or UnifiedQA with the caption removed.
- GPT-3 tables use one in-context example set; error bars appear only in one figure and there are no significance tests.
- The upper bound reflects leakage of the solution and not accuracy a model could achieve. Human accuracy was measured with crowd workers, not experts.
- One source (IXL), English, non-commercial licence; the GPT-3 engine has been deprecated.

## See Also
- [[Visual Question Answering Benchmarks]] — related
- [[Multimodal Chain-of-Thought]] — prerequisite-for
- [[MMMU]] — extends (a harder, college-level successor)
