---
title: MultiMedQA and Med-PaLM
tags: [eval, benchmark]
summary: "MultiMedQA combines six medical QA datasets with a new 3,173-question consumer set and a clinician and lay rating framework; Flan-PaLM 540B reached 67.6% on MedQA and instruction prompt tuning (Med-PaLM) cut clinician-rated potentially harmful answers from 29.7% to 5.9% on 140 questions (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-singhal-2023-large-language-models-encode-clinical.md
---

# MultiMedQA and Med-PaLM

Singhal and colleagues (Nature 2023) ask how well PaLM and Flan-PaLM answer medical questions and how to evaluate answers beyond multiple-choice accuracy. **MultiMedQA** combines six existing datasets with a new set of 3,173 consumer questions (HealthSearchQA) and a pilot human-evaluation framework with clinician and lay axes. **Med-PaLM** is Flan-PaLM 540B aligned to consumer medical QA by **instruction prompt tuning**: a soft prompt, shared across the medical datasets, is learned from 65 clinician-written exemplars and placed before the task prompt.

## Multiple-choice results (self-reported)

Setup: Flan-PaLM 540B with few-shot, chain-of-thought and self-consistency prompting.

- MedQA (4-option, 1,273 test questions): 67.6%, above the prior best of a 2.7B model; 5-option: 62.0%. MedMCQA dev-test: 57.6%. PubMedQA: 79.0% against 78.0% for a single human rater. MMLU professional medicine 83.8%, clinical knowledge 80.4%.
- Self-consistency (11 chain-of-thought decodes, temperature 0.7) improves MedQA by over 7% against few-shot but lowers PubMedQA. Chain-of-thought alone gave no gain on MedQA, MedMCQA or PubMedQA.
- Scaling from 8B to 540B roughly doubles accuracy; Flan-PaLM 540B beats the 62B model by over 14% and the 8B by over 24%. Instruction tuning lifts the 8B model on PubMedQA by over 30%.
- Selective prediction: with 41 decodes, setting aside the 45% of MedQA questions with the weakest agreement among decodes lifts accuracy on the remainder to 82.5%.

## Long-form human evaluation (self-reported)

Setup: 140 consumer questions, drawn as 100 from HealthSearchQA, 20 from LiveQA and 20 from MedicationQA, with nine clinician raters with one rating per answer; five lay raters in India for helpfulness.

| Axis | Flan-PaLM | Med-PaLM | Clinicians |
|---|---|---|---|
| Aligned with scientific consensus | 61.9% | 92.6% | 92.9% |
| Potentially harmful | 29.7% | 5.9% | 5.7% |
| Inappropriate or incorrect content | 16.1% | 18.7% | 1.4% |
| Omission of important information | 47.6% | 15.3% | 11.1% |
| Lay raters found helpful | 60.6% | 80.3% | 91.1% |

Med-PaLM contained more incorrect content than Flan-PaLM. Evidence of correct knowledge retrieval was 97.8% for clinicians, 76.3% for Flan-PaLM and 95.4% for Med-PaLM.

## Limits

- One rater per answer and 140 questions; the rating axes are a subjective pilot and the harm scale is not validated for this use.
- English only, and multiple choice is easier than clinical workflows. The bias evaluation is narrow. The effect of prompt tuning on multiple-choice accuracy is only preliminary.
- Possible memorisation of datasets (the supplement reports minimal overlap). Weights and code are not released, so Med-PaLM is not reproducible.

## See Also
- [[PubMedQA]] — related (one of its six source datasets)
- [[Self-Consistency]] — prerequisite-for (voting over sampled reasoning paths, also used as a deferral signal)
- [[Medprompt]] — related (a prompting route to medical benchmark accuracy)
- [[MEDEC]] — related
