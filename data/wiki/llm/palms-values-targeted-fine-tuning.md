---
title: PALMS Values-Targeted Fine-Tuning
tags: [llm, fine-tuning, pattern]
summary: "PALMS fine-tunes GPT-3 on 80 hand-written question-answer samples that match written position statements on eight sensitive topics; human adherence ratings and toxicity improved with model size, with most benchmarks within 1% of base on the 175B model (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-solaiman-2021-process-adapting-language-models-society.md
---

# PALMS Values-Targeted Fine-Tuning

Solaiman and Dennison (NeurIPS 2021) ask whether a small, hand-curated dataset reflecting a predetermined set of values can steer a pretrained language model, by fine-tuning, so that its behaviour on sensitive topics moves toward those values. They hypothesise that it will, more for larger models, without hurting capabilities. PALMS (Process for Adapting Language Models to Society) is a seven-step loop: choose topics, describe the desired behaviour, write prompts, write completions, fine-tune, evaluate, then repeat.

## Setup

- The authors wrote 80 Q&A prompts (70 broad, 10 targeting weaknesses) and commissioned a professional writer for completions of 40-340 words that follow written position statements across eight sensitive-topic categories.
- Eight GPT-3 sizes (125M to 175B) were fine-tuned through the OpenAI fine-tuning API. Each size was compared against its untouched base and against a control variant trained on a corpus of 100 snippets.
- A pilot on the 175B model, with learning rate 30x below the default, found metrics converged around 60 samples.
- Testing used 40 Q&A prompts aimed at weak spots (5 per category) with 3 completions per prompt and model, at length 200 and temperature 0.7. Scoring came from Perspective API toxicity (mean of 4 attributes), human ratings from 1 to 5, and word co-occurrence analysis.

## Results (self-reported)

- In every category human adherence ratings favour the values-targeted models over base and control, with the gap widening as size grows. At the largest sizes the Human Characteristics and Behavior score climbed from 2.55 for base to 4.35; Terrorism shifted least (3.26 to 3.47).
- Mean toxicity falls below base, clearest at the largest size, and the control models land between the two.
- For capability integrity, the 175B values-targeted model stays within 1% of base on most benchmarks; the biggest loss is on 5-digit addition, 88.7 against 90.45 for base.
- For 34 of the 40 test prompts, nothing similar existed in the training set, which the authors take as generalisation from the small dataset.
- The most frequent co-occurring words turn more neutral, yet new biases show up (Tomboy, Heterosexual and Intelligence, for example) and small models still produce terrorism-related words. This used 800 outputs per prompt at top-p 0.8, on gender, religion and race, and is qualitative.
- Anecdotally, an earlier try using samples written by a researcher instead of a professional writer produced poorer output and answers that looked more biased. The authors also guess that fewer examples are needed, linearly, as model size grows exponentially; this was not tested.

## Limits

- The positions encoded come from American English, American law and UN rights statements; the authors present the behaviour as a template, not a universal standard.
- The test prompts cover just Q&A and leading open-ended prompts, a narrow view of behaviour. Toxicity scores have demographic biases of their own, and human rating is subjective.
- The statistical test behind the significance asterisks is not described; one round of iteration, a single run, no seeds stated.
- Capability checks covered just the 175B model and part of the GPT-3 evaluations, leaving out GLUE and SuperGLUE.
- It stays open whether the effect matches stuffing few-shot examples into the context. Appendix J shows that values-targeted outputs remain flawed.
- It predates RLHF-style instruction tuning and is tied to GPT-3-era models.

## See Also
- [[LIMA: Small Curated Instruction Data]] — related (another small hand-curated fine-tuning set)
- [[Continued Pretraining for Domain Adaptation]] — related
- [[Pretraining Data Age, Quality and Toxicity Ablations]] — related (toxicity handled at pretraining time rather than by fine-tuning)
- [[Model Cards]] — related
