---
title: NoiserBench Beneficial and Harmful RAG Noise
tags: [rag, concept]
summary: "NoiserBench tests seven kinds of synthetic noise added to a gold passage; the authors report three types (semantic, datatype, illegal sentence) beat gold-only context while counterfactual noise collapses accuracy, whereas a separate study found no noise setting above the gold ceiling."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-wu-2024-pandora-s-box-or-aladdin.md
  - data/raw/papers/2026-11-08-leto-2024-toward-optimal-search-retrieval-rag.md
---

# NoiserBench Beneficial and Harmful RAG Noise

Wu et al. (2024 preprint) ask whether noise in retrieved documents is always harmful. They define seven linguistically grouped noise types: **beneficial** (semantic, datatype, illegal sentence) and **harmful** (counterfactual, supportive, orthographic, prior). NoiserBench builds 4-option multiple-choice items from eight QA datasets with gold evidence plus synthetic noise documents, gold placed in the middle of 5 documents, and evaluates eight LLMs without examples under a base prompt, with the gold evidence alone, and with gold evidence plus each noise type in turn.

## Results (self-reported)

Setup: Llama3-8B-Instruct and Qwen2-7B-Instruct, 7-dataset weighted average accuracy, compared with Golden Only.

- Illegal-sentence noise beats Golden Only on both models; semantic noise beats it on Llama3-8B and only marginally on Qwen2; datatype noise barely beats it on Llama3-8B. Effects are often 1-3 points and many single cells fall below Golden Only.
- Counterfactual noise collapses accuracy; supportive and orthographic noise (ratio 0.3) fall below Golden Only.
- On RGB (300 samples, eight LLMs) counterfactual noise cuts the average to 25.42 against 72.20 for Golden Only; semantic noise helps the larger models but hurts the small ones (62.30 average). Most of the big illegal-sentence gain comes from Llama2-13B, which moves from 29.33 to 72.33.
- Wilcoxon signed-rank p-values for the beneficial types are below 0.05. With illegal-sentence noise, gradient attention on the gold document is 0.67 against 0.28 under counterfactual noise; a manual check of 100 samples per dataset found clearer reasoning in 37 beneficial-noise cases against 31.

## Retrieval-side counter-evidence (Leto et al.)

Leto et al. (2024 preprint) use frozen BGE-base with graph ANN, ColBERTv2, and Mistral-7B-Instruct or Llama-2-7b-chat on ALCE-style ASQA, NQ and QAMPARI.

- (Self-reported.) Mistral on ASQA peaks in EM recall at k = 10; citation recall peaks at k = 5 and citation precision falls as k grows.
- Letting ANN search recall@10 slip to 0.7 loses just 2-3% of gold-document recall (self-reported), yet it is the gold-document recall that drives QA quality, not the ANN figure; on NQ, Mistral's citation recall goes from 75.0 with gold recall 1.0 down to 60.8 at 0.5 (self-reported).
- Adding noise documents lowers EM recall (Mistral 50.7 to about 40-44 with decile noise, self-reported); no noise setting surpasses the gold-only ceiling, which disagrees with Cuconasu et al. 2024.

## Limits

- Wu et al.: noise is synthetic (random words, URLs), the gold passage is always present, the multiple-choice layout, with its Uncertain option, may reward well-formatted outputs, and the mechanism analysis is preliminary. Decoding settings and seeds are not reported; a caption and a table row are inconsistent (79.71 against 79.63).
- Leto et al.: one dense retriever for the ANN experiments, 7B readers, a single run per condition at temperature 1, no ANN latency or memory measured, and noise effects on citation metrics inconsistent.
- The two studies differ in setup (synthetic noise on multiple choice against retrieved neighbours on open QA), so the disagreement is flagged, not resolved. Leto et al. contradict only the claim from Cuconasu et al.

## See Also
- [[Knowledge Conflicts Taxonomy]] — related (counterfactual noise)
- [[Lost in the Middle]] — related
- [[Vector Database Comparison]] — related (ANN recall trade-off)
- [[Self-RAG Reflection Tokens]] — related
