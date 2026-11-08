---
title: Position Bias Calibration (MEC, BPC, HITLC)
tags: [eval, llm, pattern]
summary: "Three calibrations for pairwise LLM judges whose verdicts flip with answer order: sample evidence-first judgments (MEC), average over both orders (BPC), and send high-entropy cases to humans (HITLC); on 80 Vicuna questions they lifted GPT-4 agreement with a three-author majority from 52.7% to 62.5% without humans (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-08-wang-2024-large-language-models-not-fair.md
---

# Position Bias Calibration (MEC, BPC, HITLC)

Wang et al. (ACL 2024) ask whether GPT-4 and ChatGPT, used as pairwise judges, are sensitive to the order in which two responses are shown, and whether that sensitivity can be calibrated away. The probe is the **conflict rate**: the share of cases where the same judge gives a different verdict after the two responses swap places.

## The bias

All figures are self-reported, on the Vicuna benchmark (80 questions) with the vanilla template.

- With ChatGPT as judge, reordering the responses lets Vicuna-13B beat ChatGPT on 66 of 80 queries.
- Under GPT-4, Vicuna-13B's win rate against ChatGPT is 51.3% when listed first and 23.8% when listed second, so GPT-4 leans to the first slot. Under ChatGPT the same pair gives 2.5% listed first and 82.5% listed second, a lean to the second slot.
- ChatGPT's conflict rate for Vicuna-13B against ChatGPT is 82.5%, and 52.5% against Alpaca-13B, both higher than GPT-4's on the same pair.
- GPT-4's conflict rate falls to 5.0% for Vicuna against the much weaker Alpaca-13B; conflicts concentrate where the score gap is 1 or less.

## The three calibrations

1. **Multiple Evidence Calibration (MEC).** The judge writes evaluation evidence before it gives scores, and k such samples are drawn.
2. **Balanced Position Calibration (BPC).** Each candidate is judged in both positions across two runs and the scores are averaged.
3. **Human-in-the-Loop Calibration (HITLC).** The examples with the highest **Balanced Position Diversity Entropy (BPDE)**, the entropy of win/tie/lose outcomes over all 2k evaluations from both positions, go to human annotators.

## Results (self-reported)

Reference label: the majority of three annotators, who were the authors; 80 questions, ChatGPT versus Vicuna-13B responses.

- GPT-4 accuracy rose from 52.7% (vanilla template) to 62.5% when MEC with k=3 was combined with BPC with k=3; ChatGPT rose from 44.4% to 58.8% (kappa 0.06 to 0.31).
- MEC (k=6) alone gave GPT-4 60.9%, below the 62.5% of MEC plus BPC at similar sample count. The extraction reads this as position balancing mattering beyond sample count.
- Evidence-first prompting with a single sample lifted ChatGPT from 44.4% to 52.6%.
- Sending 20% of examples to humans: GPT-4 reached 73.8% (kappa 0.56); ChatGPT reached 71.3%, which the authors match to the human average of 71.7% (kappa 0.54), with annotation cost cut from $30 to $18.3 (39%).
- Switching ChatGPT from the scoring to the comparing template moved vanilla accuracy from 44.4% to 50.2% (conflict rates 82.5% and 50.0%); with MEC plus BPC the two gave 58.8% and 60.0%.
- Gains from MEC plateaued beyond k=3 for ChatGPT (values read from a figure); temperatures of 0.6 and 1.0 worked and the authors call 0.2 and 1.4 sub-optimal.

## Limits

The authors did not investigate the causes of the bias. One benchmark, one model pair for human labels, and two judges only. The reference is a vote among three authors. Each annotator's accuracy is scored against that vote, and HITLC reuses the vote as its human correction, which makes the HITLC figures optimistic. Single annotators land between 68.8 and 76.3% accuracy, above the best calibrated judge working alone (62.5%). There are no significance tests or intervals, and with 80 questions one example moves a score by 1.25 points. Models are unversioned 2023 API snapshots.

## See Also
- [[LLM Judge Biases]] — prerequisite-for (position bias, measured and calibrated)
- [[LLM-as-Judge Evaluation]] — prerequisite-for (a calibration for the pairwise judge)
- [[J1 Reinforcement-Learned Judge]] — alternative-to (a training-time consistency reward against order flips)
- [[Judge Calibration (TPR, TNR and Corrected Pass Rate)]] — related (accuracy against human labels, a different calibration)
- [[Self-Consistency]] — related (sampling several judgments and aggregating)
