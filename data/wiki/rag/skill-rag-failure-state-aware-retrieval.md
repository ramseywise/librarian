---
title: "Skill-RAG Failure-State-Aware Retrieval"
tags: [rag, pattern]
summary: "Skill-RAG gates retrieval with a hidden-state probe and, after a failed retrieval, routes to rewrite, decompose, focus or exit skills; it beat Probing-RAG by 6 to 14 accuracy points on out-of-domain multi-hop sets (self-reported) and added little in-domain."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-06-wei-2026-skill-rag.md
---

# Skill-RAG Failure-State-Aware Retrieval

Skill-RAG (2026 preprint) puts a probe on the generator. A per-layer MLP reads the model's hidden states and predicts whether the model already knows the answer; when it does not, retrieval runs. If retrieval then fails to help, a prompt-based router selects one of four skills: query rewrite, question decomposition, evidence focus, or exit (stop retrieving and answer). Retrieval is BM25. Generators are Gemma2-9B, Qwen3-8B and Llama3-8B. The probe is trained on NQ, TriviaQA and HotpotQA (3,000 examples from each); out-of-domain tests use 500 examples each from MuSiQue and 2Wiki.

## Results (self-reported)

- Out-of-domain gains over Probing-RAG: Gemma2 +6.1 accuracy on MuSiQue and +13.6 on 2Wiki; Qwen3 +6.4 accuracy and +5.3 EM on MuSiQue, +9.5 and +6.4 on 2Wiki.
- In-domain gains are under 1.1 accuracy points, with under 0.08 retrieval rounds saved.
- The exit skill saved 1.42 rounds for 0.6 accuracy lost, on 2,660 hard cases.
- Llama3 on HotpotQA (Table 1): Skill-RAG EM 23.1, DRAGIN 31.9.

## Limits

- Internal inconsistency: the prose gives a 22% MuSiQue exit rate while Table 2 gives 28%.
- Requires white-box access to hidden states, so it does not apply to API-only models.
- BM25 only; open 7B to 9B models only. The probe threshold and the retrieval budget are not reported.
- The four-skill claim rests on a t-SNE plot. The router's own LLM call is not counted in the cost.

## See Also
- [[Hidden-State Hallucination Probes]] — related
- [[The Augmentation Gate]] — related
- [[RAGate Adaptive Augmentation Gate]] — alternative-to
- [[Agentic RAG — Advanced Patterns]] — prerequisite-for
