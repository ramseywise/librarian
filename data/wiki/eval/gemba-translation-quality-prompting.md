---
title: GEMBA Translation Quality Prompting
tags: [eval, llm, pattern]
summary: "GEMBA prompts a GPT model once per translation segment for a quality score and averages segments into a system score; with GPT-4 it topped the WMT22 metrics at system level on three language pairs but only trailed the best metrics at segment level (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-07-kocmi-2023-large-language-models-state-art.md
---

# GEMBA Translation Quality Prompting

Kocmi and Federmann (arXiv 2302.14520, 2023) ask whether LLMs can assess machine-translation quality. GEMBA (GPT Estimation Metric Based Assessment) asks a GPT model, with no examples, for one quality score per segment, with or without a human reference, and takes the mean over segments as the system score. Four prompt templates are used (DA, SQM, stars, classes), and the results are set against the WMT22 metrics using MQM human labels. The authors report that the least constrained template did best.

## Results (self-reported)

Setup unless stated: the WMT22 MQM 2022 test set, covering three language pairs (en-de, en-ru, zh-en), 54 systems and 106k segments, with no few-shot examples.

- Reference-based GPT-4 with the DA prompt tops all WMT22 metrics at system level; the variant without a reference also outscores every other metric, including those that use references. BLEU is the weakest at system level.
- With GPT-4 the stars prompt reached the highest system-level accuracy among DA, SQM and stars (tied with classes, no reference).
- At segment level (en-de), GPT-4 with DA is slightly behind the top metrics; Davinci-003 with DA and no reference has a segment-level tau far below the other top metrics.
- Only GPT 3.5 and larger models could assess quality: Babbage and Curie were near random, and GPT-2 and Ada gave no usable answers.
- More than half of the scores from reference-based GPT-4 with DA are exactly 95; without a reference the share is 60.6% (the body text says 60.5%). The authors conjecture that these ties lower segment-level tau, and state it only as a conjecture.
- Invalid answers were under 1% for almost all model and prompt combinations except SQM, out of 106,758 segments.

## Limits

Only three language pairs; the authors expect weaker results for under-resourced languages. The state-of-the-art result is at system level only, and they want more analysis before it becomes the main tool for judging translation quality. Test data could have been in OpenAI's training data (training cutoff September 2021, test set released December 2022), which they cannot exclude. Prompts were zero-shot; few-shot, fine-tuning, MQM error prompts and document-level context were not tried. Single run with re-prompting randomness, no significance test; GPT-4 details are undisclosed and the API models are deprecated. The 60.6% against 60.5% figure is an internal inconsistency in the paper.

## See Also
- [[LLM-as-Judge Evaluation]] — instance-of (an LLM scoring translations)
- [[GPTScore]] — alternative-to (scoring by token probability instead of a prompted score)
