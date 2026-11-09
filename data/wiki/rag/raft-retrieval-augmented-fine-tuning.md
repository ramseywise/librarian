---
title: "RAFT Retrieval-Augmented Fine-Tuning"
tags: [rag, pattern]
summary: "RAFT fine-tunes a model on questions paired with one golden document plus distractors, and with no golden document for a fraction of examples, with chain-of-thought answers that quote the source; LLaMA2-7B beat domain fine-tuning and RAG baselines on four of five in-domain sets (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-06-zhang-2024-raft.md
---

# RAFT Retrieval-Augmented Fine-Tuning

RAFT trains a model for a fixed document set, like preparing for an open-book exam. For a fraction P of training questions the prompt holds the question, the golden document and distractor documents; for the remaining 1 minus P it holds distractors only. Both are labelled with a chain-of-thought answer that quotes the source between quote markers. The authors give memorization as the reason for the no-golden fraction and distraction in top-k results as the reason for distractors. The method is supervised fine-tuning and does not depend on the retriever. Main runs use one golden document and four distractors.

## Results (self-reported)

LLaMA2-7B-chat base. Scores are listed per dataset as PubMed, HotPot, HuggingFace, Torch Hub and TensorFlow, in that order:

- RAFT: PubMed 73.30, HotPot 35.28, HuggingFace 74.00, Torch Hub 84.95, TensorFlow 86.86.
- Domain-specific fine-tuning (DSF) alone: PubMed 59.7, HotPot 6.38, HuggingFace 61.06, Torch Hub 84.94, TensorFlow 86.56. DSF with RAG added at test time: PubMed 71.6, HotPot 4.41, HuggingFace 42.59, Torch Hub 82.80, TensorFlow 60.29.
- Base LLaMA2-7B with RAG: PubMed 58.8, HotPot 0.03, HuggingFace 26.43, Torch Hub 08.60, TensorFlow 43.06.
- GPT-3.5 with RAG: PubMed 71.60, HotPot 41.5, HuggingFace 29.08, Torch Hub 60.21, TensorFlow 65.59.
- Adding RAG to the fine-tuned model helped only on PubMed. GPT-3.5 with RAG beat RAFT on HotPot (41.5 against 35.28), and RAFT's margin over DSF on Torch Hub and TensorFlow is 0.01 and 0.30.
- Training with distractors made the model more robust to the number of documents at test time than training with the golden document alone.

## Limits

- Internal inconsistencies: the text says the best golden fraction is 80% but the reported optima are 40%, 60% and 100%; the best number of training distractors differs between the text and the Figure 6 caption (NQ three against four, HotPot one against two), and the caption mentions three domains while two are plotted.
- Evaluation is in-domain only, on the same document sets used for training. Only LLaMA2-7B was fine-tuned.
- Metrics are not defined; no variance. NQ and TriviaQA numbers appear only in plots and are missing from Table 1.
- The authors say base LLaMA2's answering style does not match the ground truth, so part of the gain may be style alignment. PubMed gains are small, attributed by the authors to yes/no questions.
- LLaMA-2 era; no long-context models tested.

## See Also
- [[RA-DIT Dual Instruction Tuning]] — alternative-to
- [[RankRAG]] — related
- [[RAG Architecture Selection]] — prerequisite-for
- [[Agentic RAG — Advanced Patterns]] — prerequisite-for
