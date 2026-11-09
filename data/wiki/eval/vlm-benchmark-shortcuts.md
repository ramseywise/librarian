---
title: VLM Benchmark Shortcuts
tags: [eval, concept]
summary: "Vision-language benchmarks can be passed without seeing: a model of all-zero weights scores 100% on caption-pair tests when ties go to the first, correct, caption; for one question type in the original VQA, 'yes' is right 98% of the time; exact-match VQA accuracy under-scores free-form answers; and CHAIR misleads on long outputs."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-03-bordes-2024-introduction-vision-language-modeling.md
---

# VLM Benchmark Shortcuts

Bordes et al. (arXiv 2405.17247, 2024) list the ways vision-language benchmarks reward
something other than looking at the image. Each one is a check to run before trusting a
score. The model-building side is in [[Vision-Language Model Training Families]].

## The argmax tie

Many compositional benchmarks ask the model to choose the correct caption out of a pair. If
both captions score the same, `argmax` returns the first one, and datasets often list the
correct caption first. **A model whose weights are all zero can then score 100%.** Fix: break
ties with a small random epsilon, or count ties separately.

## Language priors

Some benchmarks can be answered from the question alone. In the original VQA, "yes" is right
98% of the time for one question type. Winoground and EqBen are built to
penalise text-only shortcuts; ARO, Crepe, VL-CheckList and SugarCrepe are reported to be
open to them.

## Metric strictness

- **VQA accuracy** matches strings exactly, so it under-scores generative models that answer
  correctly in their own words, and formatting tricks distort comparisons. Mañas et al.
  propose an LLM judge instead ([[LLM-as-Judge Evaluation]]).
- **Selective prediction** scores coverage at a fixed risk: whether the model abstains rather
  than answer wrongly. Use it where a wrong answer costs more than no answer.

## Hallucination metrics

CHAIR counts objects mentioned but absent from the image. It is unreliable for long outputs and
only works on COCO images, which training sets often contain. The alternatives are POPE (binary
"is there a X?" polling), GPT-4-based scoring (GAVIE, CCEval, MMHal-Bench) and human review.

## Others

- In a controlled synthetic test that moved an object left or right, VLMs answered spatial-relation
  questions at chance level.
- Measured bias can come from the evaluation set itself, through label quality that varies by
  group or image sources that differ by group. CLIPScore is only as good as the CLIP model
  behind it.

The general version of these checks is in [[Eval Metric Interpretation Pitfalls]].

## Limits

The source is a May 2024 survey, not a measurement study: the shortcuts above are reported from
the works it cites, and its authors concede that many benchmarks have severe limitations and
that there is no holistic way yet to judge the quality of multimodal data. The model line-up it
describes has since moved on.

## See Also
- [[Vision-Language Model Training Families]] — prerequisite-for
- [[Eval Metric Interpretation Pitfalls]] — related
- [[LLM Judge Biases]] — related (the judge that replaces exact match has its own biases)
- [[POPE Object Hallucination Probing]] — instance-of (polling probes)
- [[MMBench]] — instance-of (CircularEval)
- [[SEED-Bench]] — instance-of (likelihood-scored options)
- [[Visual Instruction Tuning and Tool-Using VLMs]] — related (compares the models these benchmarks score)
- [[Visual Question Answering Benchmarks]] — related
- [[MMMU]] — related
- [[MM-Vet]] — related
