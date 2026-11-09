---
title: "Chain-of-Note"
tags: [rag, pattern]
summary: "Chain-of-Note has the reader write a short note on each retrieved document before answering, in one of three note types; fine-tuned LLaMa-2 7B gained about 7.9 EM when all five documents were noisy (self-reported), at roughly 20 times the decoding time unless hybrid training is used."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-06-yu-2023-chain-note.md
---

# Chain-of-Note

Chain-of-Note (CoN; arXiv 2311.09210, EMNLP 2024) changes the reader, not the retriever. Given k retrieved documents, the model first writes one reading note per document and then answers. There are three note types: the document answers the question; the document gives context that the model combines with its own knowledge; or all documents are irrelevant and the model has no knowledge of its own, so it answers "unknown". Training notes came from GPT-4 on 10K NQ questions, with a small human check, and LLaMa-2 7B was fine-tuned on them (learning rate 5e-6, batch size 128, 3 epochs). The retriever is DPR over Wikipedia with five passages.

## Results (self-reported)

- Fully noisy documents (LLaMa-2 7B, subsets where DPR retrieved a gold document, noise built by hand): average EM rose by 7.94 over plain retrieve-then-read (NQ 34.28 to 41.83). The gain shrinks as noise falls: +3.18 at 80%, about +2 at 60% to 20%, and +2.72 at 0%.
- Full test sets, LLaMa-2 7B: average EM 48.49 to 50.46 (+1.97).
- GPT-4-1106 prompted zero-shot, substring accuracy: average 63.1 for retrieve-then-read, 64.4 with chain-of-thought and 65.7 with CoN. On TriviaQA, GPT-4 without retrieval scored 74.2, close to CoN at 74.6.
- RealTimeQA questions after the model's pretraining cutoff: rejection rate 6.1 to 13.0 while EM stayed 15.6 to 15.7.
- Per-example decoding time (8 A100 GPUs): 0.61 s for retrieve-then-read, 12.02 s for CoN and 0.61 s for hybrid training, where half of training uses the standard prompt without notes and only that prompt is used at inference. On the NQ curve hybrid scored 36.3 EM at 100% noise against 41.8 for CoN.

## Limits

- Internal inconsistency: the abstract and text claim a +10.5 rejection-rate gain on real-time questions, but Table 4 gives 6.1 to 13.0, which is +6.9.
- The text says both systems fell below the no-retrieval model at 100% noise, but the compared numbers come from different evaluation sets (full test versus subsets), as the extraction notes.
- One trained size (LLaMa-2 7B), notes from NQ only, DPR and Wikipedia only, synthetic noise, no seeds or significance tests.
- The authors concede note generation is slow because it is sequential. False refusals on answerable questions were not measured.
- Hybrid training is shown only on an NQ curve and a timing table.

## See Also
- [[Dense Passage Retrieval (DPR)]] — prerequisite-for
- [[RA-DIT Dual Instruction Tuning]] — related
- [[Sufficient Context Autorater]] — related (also targets abstaining on insufficient context)
- [[Self-Reasoning Retrieval-Augmented Model]] — alternative-to
- [[Agentic RAG — Advanced Patterns]] — prerequisite-for
