---
title: GPT-4 Technical Report and Predictable Scaling
tags: [llm, pretraining-and-data, concept]
summary: "OpenAI (2023) report GPT-4 exam and benchmark results and fit scaling curves on runs with 1,000x to 10,000x less compute to predict its final loss and a HumanEval pass-rate metric, while withholding architecture, size, hardware, compute and dataset details (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-openai-2023-gpt-4-technical-report.md
---

# GPT-4 Technical Report and Predictable Scaling

GPT-4 is a Transformer-style multimodal model taking images and text and producing text. It was trained to predict next tokens on public and licensed data and afterwards tuned with RLHF. The report keeps back the architecture, model size, hardware, training compute, how the dataset was built and the training method, so the paper's own experiments are evaluations of the model and scaling-law extrapolation from smaller models. The stated hypothesis is that when infrastructure and optimisation behave the same way at every scale, the final loss and some capabilities can be forecast accurately from runs using 1,000x to 10,000x less compute. All figures are self-reported.

## Predictable scaling

Two fits were made on smaller models trained the same way:

- **Loss.** `L(C) = aC^b + c`, a power law with an irreducible term, forecast the final loss of GPT-4 on an internal code dataset (next-word loss on OpenAI's codebase, which was excluded from training), using models trained with up to 10,000x less compute. The forecast was made soon after the run began.
- **Capability.** a power law in compute C, with the negative expected log pass rate equal to alpha times C raised to the power -k, forecast HumanEval results on a subset of its problems, using models with up to 1,000x less compute. The forecasts were recorded before training ended. Excluding the 15 hardest problems, the rest were grouped into 6 difficulty buckets, and GPT-4 came in under the forecast on the easiest one.

On the Inverse Scaling Prize task Hindsight Neglect, GPT-4 breaks the pattern of accuracy declining as models grow (the five models ada, babbage, curie, gpt-3.5 and gpt-4 appear only in Fig 3).

## Exam and benchmark results

- Simulated Uniform Bar Exam (run by Casetext and Stanford CodeX; single run): roughly the top 10% of test takers, against the bottom 10% for GPT-3.5.
- 5-shot MMLU 86.4% against 70.0% for GPT-3.5 (base model; contamination about 0.6%). 0-shot HumanEval 67.0% against 48.1% (contamination 25%, non-contaminated score 65.58%). GSM-8K 92.0% with 5-shot chain of thought, with part of the GSM-8K training set in the pre-training mix; the authors say to read it as between true few-shot transfer and benchmark-specific tuning.
- MMLU translated with Azure Translate (3-shot): GPT-4 exceeds the English-language state of the art in 24 out of 26 languages; English GPT-4 is 85.5% in that figure.
- Competitive programming is weak: Codeforces rating 392, Leetcode hard 3 of 45.
- Averaged across the multiple-choice parts of the exams, base and RLHF models land close together (73.7% and 74.0%), so exam ability mostly comes from pre-training; per-exam differences are wide (AP Microeconomics 90.0 base against 76.7 RLHF; GRE Quantitative 57.5 against 67.5).

## RLHF effects and safety

- In a blind comparison with one sampled response each, labelers chose GPT-4 over GPT-3.5 for 70.2% of 5,214 user prompts.
- After RLHF, TruthfulQA mc1 reaches about 60%, up from roughly 30% for an earlier version; the base GPT-4 improves only a little over GPT-3.5.
- The pre-trained model is well calibrated (ECE 0.007 on an MMLU subset) and post-training hurts it (ECE 0.074).
- Safety mitigations combine extra safety prompts in RLHF with RBRMs, which are zero-shot GPT-4 classifiers; given the prompt, the policy's output and a rubric written by people, they supply an extra reward signal. They cut disallowed-request answers by 82% against GPT-3.5 (internal challenging prompt set). Separately, on RealToxicityPrompts the GPT-4 launch model is toxic 0.73% of the time against 6.48% for GPT-3.5.
- More than 50 domain experts red-teamed the model. In the ARC autonomy test, early versions of GPT-4 could not effectively copy themselves, gather resources or avoid being shut down.

## Limits

- Training cannot be reproduced from the report; the authors give the competitive landscape and safety as reasons.
- The scaling evidence is a single point against a fit of smaller models; Figs 1 and 2 print no numeric loss values, the HumanEval forecast only covers problems that every model solved at least once, and the authors say some capabilities remain hard to predict.
- One run per exam, with non-final snapshots (Feb 23 for free response, Dec 16 for USABO); answer letters were extracted differently in some runs; percentiles for AMC 10/12 are extrapolated from 2021 score distributions.
- Exam questions appeared in the pre-training data; BIG-bench turned out to be mixed into training and was dropped; the GSM-8K and MATH training sets were part of the pre-training mix; RLHF data was not checked for TruthfulQA or exam contamination. The substring contamination check can give false negatives and positives.
- Free-response grading used 1-2 contractors with no inter-rater statistics; there are no seeds, confidence intervals or significance tests.
- Vision is shown only through qualitative examples. Known weaknesses: hallucination, reasoning errors, limited context, no learning from experience, a knowledge cutoff of September 2021, jailbreaks, and refusals that can exacerbate bias. Safety work is mainly in English and takes a US-centred view, and system card examples are cherry-picked.
- The ARC test used early versions without fine-tuning, not the final model. The report is a March 2023 snapshot.

## See Also

- [[GPT-3 and Few-Shot In-Context Learning]] — prerequisite-for
- [[RLHF Pipeline]] — prerequisite-for
- [[Open Pretrained Model Reports Comparison]] — related (reports that disclose setups GPT-4 withholds)
- [[Eval Contamination Defenses]] — related
