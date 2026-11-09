---
title: MemoryBank Long-Term Memory
tags: [memory, pattern]
summary: "MemoryBank stores timestamped dialogs with hierarchical event and personality summaries, retrieves them with a dual-tower encoder over FAISS, and updates them with an Ebbinghaus-style decay; its evaluation uses simulated users and never ablates the forgetting rule."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-zhong-2024-memorybank.md
---

# MemoryBank Long-Term Memory

Zhong et al. (AAAI-24) give LLMs a long-term memory that stores, retrieves and updates past dialogue and builds a user portrait for companion use. The store holds timestamped dialogs, LLM-written daily event summaries that are further synthesised into a global summary (the hierarchical event summary), and personality summaries. Retrieval uses a DPR-style dual-tower encoder over a FAISS index.

## Forgetting rule

Updating follows R = e^(-t/S). S, the memory strength, is 1 when a memory is first mentioned; every recall raises S by 1 and sets t back to 0. The authors call the scheme exploratory and highly simplified.

## SiliconFriend evaluation

SiliconFriend is the companion built on the store. It is built around three base models (ChatGPT, ChatGLM, BELLE), the latter two LoRA-tuned on 38k psychological dialogs for 3 epochs on one A100. Evaluation memory is 450 topics, 15 virtual users and 10 days of dialog written by ChatGPT role-playing the users, with 194 manually written probing questions (97 English, 97 Chinese), judged by human annotators; all results below are the paper's own (self-reported) and come from this single evaluation setup.

- English: SiliconFriend-ChatGPT scored highest on response correctness, contextual coherence and ranking score, yet its retrieval accuracy was the lowest among the three variants (self-reported).
- Chinese: the BELLE variant had the highest retrieval accuracy, while the ChatGPT variant scored higher on correctness (0.655) (self-reported).
- Empathy and recall comparisons against ChatGLM appear only as single qualitative examples from real-user conversations on an online platform.

## Limits

- The forgetting mechanism is never ablated, so the contributions list's claim about generalising with and without forgetting has no with/without result in the extraction.
- Quantitative evaluation uses ChatGPT-simulated users over 10 days and 97 questions per language, with no no-memory baseline or other memory method.
- Annotator count and agreement, significance tests, seeds, retrieval top-k, LoRA learning rate and batch size, decoding settings and the ChatGPT version are not reported; no code link.

## See Also
- [[Agent Memory Types]] — prerequisite-for
- [[Memory Decay Weighting]] — related (exponential recency decay)
- [[Memory Lifecycle]] — related
- [[Generative Agents Memory Stream]] — related
- [[Memory-Augmented Conversational RAG]] — related
