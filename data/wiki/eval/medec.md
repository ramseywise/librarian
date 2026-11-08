---
title: MEDEC
tags: [eval, reference]
summary: A benchmark of clinical notes that are either correct or hold exactly one medical error of five types, with three subtasks (flag, locate, correct); LLMs lead on detection or correction in different ways and two doctors still beat all models.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-08-abacha-2024-medec.md
---

# MEDEC

MEDEC (Ben Abacha and colleagues, 2024) tests whether models can notice and repair errors in clinical text. Each text is either correct or contains one medical error of five types. Subtask A is the error flag, B is extraction of the erroneous sentence, and C is generation of the corrected sentence. The MS subset is built from public MedQA; a second subset (UW) comes from private notes. The test set has 925 texts, 51.3% of them erroneous.

## Results (self-reported unless stated)

Setup: MEDEC test set; the extraction states zero-shot prompt P#1 only for the Claude flagging result, and the doctors annotated a 569-text subset.

- Among the LLMs, Claude 3.5 Sonnet scored highest on flagging errors and on extracting the faulty sentence.
- o1-preview had the best LLM correction aggregate score, ahead of GPT-4 with prompt P#2. The orderings differ between subtasks: Claude leads detection yet comes last on correction, and o1-preview is fourth on detection yet first on correction.
- Two doctors beat every LLM on error-flag accuracy; Doctor #2 also exceeds all LLMs on correction, while Doctor #1 falls below o1-preview and GPT-4. Doctors annotated 569 of the 925 texts while LLMs ran on all 925, so the populations differ.
- o1-preview is much worse on the private UW subset than on the public MS subset.
- o1-preview recall exceeds the doctors on every error type (texts with errors; Diagnosis n=174), which the extraction reads as implying low precision.

## Limits

- Each text holds at most one error and there are only five error types; the dataset is small.
- No sampling settings, seeds or confidence intervals; only two doctors, scored on a different subset than the models.
- Correction is scored by ROUGE-1, BERTScore and BLEURT against one reference; the authors say these miss synonyms and penalise long explanations, and no metric-versus-human agreement is shown.
- The explanations offered for the LLM-doctor gap (a rare task in pretraining data; public MS versus private UW) are untested speculation; contamination of MS, built from public MedQA, was not measured.
- Model sizes come from third-party estimates, and no medically specialised model was run.
- Table 2 gives GPT-4o an aggregate score (0.4682) that disagrees with its own components.

## See Also
- [[MedBrowseComp]] — related (another medical benchmark)
- [[Output Length Confounds Reference Metrics]] — related (reference metrics and long outputs)
