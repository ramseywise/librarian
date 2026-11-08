---
title: Embers of Autoregression
tags: [eval, concept]
summary: "The behavioural patterns that result from a model being optimised for next-word prediction, such as sensitivity to output probability and task frequency; on a subset of the original tasks OpenAI o1-preview improved but still did better when the output was more probable, and used more thinking tokens on low-probability outputs (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-08-mccoy-2024-when-language-model-optimized-reasoning.md
---

# Embers of Autoregression

McCoy et al. (2024 preprint) use the phrase **embers of autoregression** for behavioural traces left by having been
trained to predict the next word. The framing is **teleological**:
analyse the system through the pressures that shaped it. Their earlier 2023 paper
(arXiv 2309.13638) supplied the tasks, datasets and the results for the non-o1 models.

## The o1 question

Does OpenAI's o1-preview, a model optimised for reasoning, still show sensitivity to output probability
and task frequency? The authors hypothesise that optimising for reasoning could soften the constraints that come with
next-word prediction, but note o1 was probably also trained on next-word prediction, so those effects
could remain.

## Method

The model o1-preview-2024-09-12 (default settings) was tried on part of the 2023 task set and set beside results
reported earlier (Claude 3, Gemini 1.0, Llama 3, GPT-3.5, GPT-4). For each output-probability bin and for common
versus rare task variants, the comparison covers accuracy and median thinking tokens; two extra harder variants are
included so that accuracy does not hit a ceiling. Thinking-token counts act as a second measure of difficulty.

## Results (self-reported, o1-preview; most numbers are in figures and not given)

- For shift-cipher decoding, o1's accuracy is higher in the highest output-probability bin than in the lowest.
- On acronyms, accuracy was almost the same for the common (first-letter) and rare (second-letter) variants, yet the
  rare one drew far more thinking tokens.
- Across all four output-probability tasks, o1 used more thinking tokens on low-probability outputs.
- On the standard datasets (five task pairs), o1 is far better than the other LLMs on rare variants and scores
  similarly on common and rare, which the authors say may be a ceiling effect.
- On the harder variants (sorting where every word starts with "i", and shift-cipher examples of medium or low
  probability), the common variant is solved more accurately by o1 than the rare one.

In the authors' overall reading, o1 is better in quantity yet retains its sensitivity to output probability and
some sensitivity to how common the task is.

## Limits

- Only a subset of tasks was run, excluding large datasets because of o1's cost per example; only o1-preview was
  tested, and the other models' results are copied from 2023.
- o1's internals are not public, so the explanations offered for probability sensitivity are speculation; only
  the number of thinking tokens is visible, not the chain of thought itself.
- Ceiling effects on the standard datasets limit conclusions about task frequency.
- The paper gives no example counts, run counts, prompts or significance tests, and most values appear only in figures.

## See Also
- [[Counterfactual Task Variants]] — alternative-to (changes the task's world instead of probing probability and frequency)
- [[Prompting Reasoning Models]] — related (o1-style reasoning models)
- [[Eval Error Bars and Sample Size]] — related (the paper reports no counts or tests)
