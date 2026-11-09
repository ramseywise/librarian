---
title: ARES Automated RAG Evaluation
tags: [eval, pattern]
summary: ARES fine-tunes small judges on synthetic data for context relevance, answer faithfulness and answer relevance, then uses prediction-powered inference with a small human set to score RAG systems with confidence intervals.
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-2311-09476v2.md
---

# ARES Automated RAG Evaluation

ARES (Saad-Falcon et al.) asks whether lightweight judges trained on synthetic data plus a small human-labelled set can rank RAG systems accurately, with confidence bounds, on three axes: context relevance (is the retrieved text pertinent), answer faithfulness (is the answer grounded in it) and answer relevance.

## Mechanism

FLAN-T5 XXL generates synthetic query-passage-answer triples from in-domain passages, with positives plus weak and strong negatives. Three DeBERTa-v3-Large binary judges are fine-tuned, one per axis. Prediction-powered inference (PPI) uses a small human preference set to tighten confidence intervals using predictions on a much larger unlabelled set, giving 95% intervals. Systems are then ranked using the midpoints of those intervals.

## Results

Self-reported.
- Mock RAG systems on KILT and SuperGLUE (300-datapoint PPI set): the judge beats RAGAS on context relevance accuracy (the paper gives 59.9 points in Section 5.1 but 59.3 in the introduction, a discrepancy) and on answer relevance; for context relevance its Kendall's tau also exceeds RAGAS.
- 300 annotations beat 1,350 sampled ones (150 per system across nine systems). The margin over a few-shot GPT-3.5 judge that also uses PPI is slight.
- 150 human annotations is the minimum: On NQ context relevance, tau rises from 0.44 with 100 labels to 0.72 with 150.
- AIS (WoW 707 examples, CNN/DM 510): hallucination rates predicted within 2.5 points using 200 annotations.
- Real systems (NQ, WoW, FEVER; BM25/ada/ColBERTv2 with MPT-7b, GPT-3.5, GPT-4 and also Facebook RAG; a single retrieved passage): average tau reaches 0.91 on context relevance and 0.97 on answer relevance, and ground truth fell inside the PPI intervals more than 95% of the time.
- Swapping the human labels for 500 GPT-4 labels cuts tau by between 0.05 and 0.30 in most settings.
- A judge fine-tuned on NQ transfers poorly, with tau of 0.33 on XGLUE, 0.28 on CodeSearchNet and 0.38 on T-Rex.
- Judge and generator need about 32GB of GPU memory.

## Limits

- Needs roughly 150-300 human-labelled datapoints, possibly from domain experts, and a 32GB GPU with hours of fine-tuning.
- English only; the judges fail to generalise to other languages, to text-to-code or to extraction tasks.
- Main benchmarks use mock systems built by sampling negatives; faithfulness could not be tested on KILT/SuperGLUE since hallucination labels were lacking.
- Seeds, significance tests and synthetic-data sizes not stated; the baselines (gpt-3.5-turbo-16k 10/23, RAGAS 0.0.18) are dated.

## See Also
- [[RAG Evaluation]] — prerequisite-for
- [[RAG Eval Metrics Suite]] — prerequisite-for
- [[LLM-as-Judge Evaluation]] — prerequisite-for
- [[Promptagator Few-Shot Synthetic Retrieval Data]] — prerequisite-for (source of its query-filtering step)
