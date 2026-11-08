---
title: MemInsight Attribute Augmentation
tags: [memory, pattern]
summary: "MemInsight has an LLM annotate each memory with attribute-value pairs (ordered by relevance) and retrieves through those attributes; its LoCoMo recall at k=5 is 60.5 against 26.5 for dense retrieval, but answer F1 is only marginally better and the paper's headline percentages do not match its tables (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-salama-2025-meminsight.md
---

# MemInsight Attribute Augmentation

MemInsight (a 2025 preprint) is an annotation and indexing layer, not a memory manager: it trains nothing and has no write or evict policy. An LLM mines attributes and values for each memory (entity-centric or conversation-centric, at turn or session level). In "priority" mode the attributes are ordered by relevance. Retrieval is either comprehensive or refined, by attribute filtering or by embedding the augmentations (FAISS, with Titan Text Embedding v2). The incoming query is also augmented so the attributes to match can be extracted from it.

## Results

- LoCoMo QA recall@5 with Claude-3-Sonnet priority augmentation: an overall 60.5 against 26.5 for the dense-retrieval (DPR) baseline; multi-hop 75.1 against 31.4. Basic (unordered) augmentation gets 48.8 (self-reported).
- Answer F1 on LoCoMo is 30.1 (priority) against 28.7 for DPR, which wins adversarial questions (89.9 against 75.3).
- On LLM-REDIAL movie recommendation (n=200 conversations, Claude-3-Sonnet), attribute filtering retrieves 15 items against 144 for the baseline (about 90% less memory) with comparable recall; recall and NDCG gains are small or absent, and an unnamed LLM judge rates unpersuasive recommendations at 2.0% instead of 16.0% (self-reported).
- 99.14% of Claude-3-Sonnet annotations were judged grounded in the dialogue by DeepEval; Llama and Mistral annotations showed hallucinated attributes in the qualitative figures. Augmentation quality depends on the augmenting model (self-reported).

## Limits

- In ambiguous contexts the generated attributes can turn out vague or generic; results depend on the augmenting LLM, and only text is handled.
- No latency or cost measurement despite the ethics section claiming savings; Mem0, A-Mem and MemGPT are not compared; no variance or significance tests; no memory-update or forgetting evaluation. Models are dated.
- Internal inconsistencies: the abstract's "34% recall" gain does not match Table 2 (60.5 against 26.5 is about 34 points, 128% relative) and the text elsewhere says 35%; the "up to 14%" persuasiveness claim does not clearly match Table 5. The text says it beats baselines on most question types while Table 1 shows DPR winning adversarial ones, and some baseline rows in Table 1 were taken over from other setups and models.

## See Also
- [[Memory Lifecycle]] — prerequisite-for
- [[Memory-Augmented Conversational RAG]] — alternative-to
- [[Index-Time Distillation]] — related (annotating at write time)
- [[Jev-Mem System-One Memory Control]] — related
