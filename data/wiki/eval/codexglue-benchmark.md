---
title: CodeXGLUE Code Understanding and Generation Benchmark
tags: [eval, code, benchmark]
summary: "CodeXGLUE bundles 10 code tasks over 14 datasets with CodeBERT, CodeGPT and encoder-decoder baselines and an evaluation platform; its metrics are overlap-based, not execution-based, and its baselines are about 125M-parameter models (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-lu-2021-codexglue.md
---

# CodeXGLUE Code Understanding and Generation Benchmark

Lu and colleagues ask whether one GLUE-style benchmark of diverse code tasks, with baselines and a platform, can speed up research on code intelligence. The introduction implies the hypothesis that a diversified benchmark does for code what ImageNet and GLUE did for vision and language.

## What it contains

- 10 tasks over 14 datasets (8 existing, the rest new), arranged into four groups by input and output type: code to code, text to code, code to text and text to text.
- Named datasets include BigCloneBench and POJ-104 (clone detection), Devign (defect detection), PY150 and Github Java Corpus (completion), CONCODE (text-to-code), Bugs2Fix (repair), CodeSearchNet (search, cloze and summarisation; see [[CodeSearchNet Challenge]]) and Microsoft Docs (documentation translation).
- Cloze test comes in two forms: CT-all uses a filtered vocabulary of 930 candidate tokens, CT-maxmin uses only the candidates max and min.
- Three baselines: CodeBERT (encoder), CodeGPT (GPT-style, released with the paper; CodeGPT-adapted starts from GPT-2 and continues training on code) and an encoder-decoder initialised from CodeBERT. Models are about 125M parameters.

## Findings (self-reported, one run per cell)

- CodeGPT-adapted is the best completion baseline overall (PY150 and Github Java Corpus, scored by token accuracy and line-level edit similarity) and also leads the text-to-code baselines on CONCODE.
- On clone detection CodeBERT is ahead of RoBERTa (F1 96.5 on BigCloneBench, MAP 84.29 on POJ-104). On defect detection (Devign, random 80/10/10 split) its margin over TextCNN is slight.
- Normalising function and variable names lowers CodeSearchNet Python MRR: CodeBERT starts from 0.869 before normalisation (its normalised score is not given in the extraction) and RoBERTa falls from 0.809 to 0.419.
- CodeBERT is best on summarisation overall and beats RoBERTa on cloze; the CodeBERT-initialised encoder-decoder is best on Java-C# translation (1,000 test pairs).
- Repair exact match stays very low (Bugs2Fix small and medium).

## Limits

- The paper supplies baselines only, typically one run per table cell, without seeds, variance or significance tests, and leaves most fine-tuning hyperparameters unstated.
- The models are small and from the BERT and GPT-2 era, so the numbers sit far below later code language models.
- Scoring relies on overlap (BLEU, CodeBLEU, edit similarity, exact match), and text-to-code has no functional tests. Compare execution-based sets such as [[APPS Coding Challenge Benchmark]].
- The authors note limited languages and missing tasks (idiom mining, bug localisation, test generation, program synthesis), and that CodeBERT ignores code structure.
- Absolute scores on repair (about 10% exact match) and defect detection (about 62% accuracy) are low.
- The authors drew their own random Devign split because none is official, and say nothing about duplicate leakage.

## See Also
- [[CodeSearchNet Challenge]] — prerequisite-for
- [[APPS Coding Challenge Benchmark]] — alternative-to
- [[Spider Text-to-SQL Benchmark]] — related
