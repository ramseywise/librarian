---
title: MeMo Memory as a Model
tags: [memory, pattern]
summary: "MeMo fine-tunes a small memory model on question-answer 'reflections' generated across a document corpus and lets a frozen LLM query it; it beats retrieval baselines on two of three benchmarks and ties on the third, at hundreds of GPU-hours of training per corpus (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-quek-2026-memo.md
---

# MeMo Memory as a Model

MeMo (a 2026 preprint) puts knowledge into the weights of a small fine-tuned "memory model" and has a frozen "executive" LLM ask it questions. The extraction stresses that this is knowledge integration over a static document corpus, not agent experience: there are no agent trajectories. The closest comparison is distilling a corpus into weights versus retrieval over raw documents.

## Mechanism

A pipeline generates question-answer reflections from groups of documents, including cross-document synthesis (its Step 5), and the memory model is fully fine-tuned on them. The executive queries it in structured multi-turn exchanges (one grounding turn, seven entity-ID turns and eight answer-seeking turns, up to 16 exchanges in all). Merging models is offered for incremental updates.

## Results

- 14B memory model (Qwen2.5-14B-Instruct) with a Qwen2.5-32B executive: NarrativeQA 26.85% against 21.39% for HippoRAG2; MuSiQue 48.30 against 42.17; BrowseComp-Plus 54.22 against 56.11 for HippoRAG2, so it loses there with this executive. With Gemini-3-Flash, NarrativeQA is 53.58% against 26.62% for the best baseline (self-reported). Qwen runs average 3 runs; Gemini is a single run.
- Adding distractor documents (1x) drops NV-Embed-V2 and HippoRAG2 by 6.22 points on BrowseComp-Plus; MeMo changes by +0.55 there and -1.77 on MuSiQue. With no distractors at all, HippoRAG2 (62.33) is ahead of MeMo (53.67).
- Removing the cross-document synthesis step (1.5B memory model, 3 runs) drops NarrativeQA from 24.00 to 6.37 and MuSiQue from 42.90 to 24.17 (self-reported).
- Training cost: generating the reflection data took about 240, 200 and 150 GPU-hours, and training the 14B model about 180, 150 and 90, for BrowseComp-Plus, NarrativeQA and MuSiQue.
- Merging two models for an incremental update uses 33% less compute but accuracy drops sharply. Qwen goes from 26.85 down to 15.81, and Gemini goes from 53.58 down to 34.47. Structured querying beats single-turn: 54.22 against 32.56 on BrowseComp-Plus. LoRA is worse than full fine-tuning (48.78 against 54.22).

## Limits

- Authors concede upfront training per corpus, variation across domains and model families, a capacity bound on a fixed-size memory model, and quadratic data-generation growth.
- Not shown: any agent or experience setting, streaming corpora, forgetting, or wall-clock latency. Corpora are at most 5.3k documents. There is no full-context baseline, and tokens and compute are not matched; the claim that retrieval cost does not depend on corpus size is stated but never measured.
- The extraction notes that training data is generated per question group from the evaluation corpus, which the extraction reads as nearer to an oracle grouping than to something deployable (its reading, not a limit the authors state).
- Internal inconsistency: Section 5 says 105 documents per NarrativeQA text but a footnote says 10. On BrowseComp-Plus the margins over some baselines fall within noise.

## See Also
- [[Memory Forms Taxonomy]] — prerequisite-for
- [[Index-Time Distillation]] — related (distilling at write time instead of into weights)
- [[Designed Memory vs Raw-Record Search]] — related
- [[LM2 Large Memory Models]] — alternative-to (memory inside the weights of one model rather than a separate memory model)
