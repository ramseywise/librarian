---
title: "Focused Transformer Crossbatch Training"
tags: [foundations, pattern]
summary: "Focused Transformer trains memory attention with keys from other documents as negatives (crossbatch training) to counter the distraction issue; LongLLaMA 3B reached 94.5% passkey accuracy at 100K tokens (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-06-tworkowski-2023-focused-transformer.md
---

# Focused Transformer Crossbatch Training

When a transformer attends over a large external key-value memory, the paper argues that relevant and irrelevant keys compete for attention. It calls this the distraction issue.

## Mechanism

Under standard training, the positive attention mass fell roughly as 1/d when the model saw the current document plus d-1 others at evaluation (184M-parameter 12-layer model, memory layer 8; self-reported). Crossbatch training adds negative keys drawn from other documents in the batch, trained differentiably with no extra loss. The single added hyperparameter is d, the positive-to-negative context ratio. Training begins with small d (up to 8) since larger values lead the model to disregard its preceding local context, and then moves to d of 64 or more.

LongLLaMA is OpenLLaMA fine-tuned this way at 8k context (3B: 10B tokens; memory layers 6, 12, 18).

## Results (self-reported)

- Passkey retrieval: 94.5% at 100K tokens and 73% at 256K for the 3B model, where the baseline cannot go past 2K.
- Few-shot with longer contexts, 3B: TREC 67.0 at 2K to 73.3 at 8K; WebQS 21.2 to 22.4. At a 4K, 1B-token fine-tuning budget, TREC 60.9 against 57.2 for standard long-context fine-tuning.
- A 16M-token dictionary-lookup task above 92% accuracy.

## Limits

- Evaluation is largely synthetic (passkey, dictionary lookup) and on small models. The extraction notes that the released LongLLaMA uses dense attention over the cache in some layers, not only kNN retrieval.
- TREC demonstrations are few enough at 2K that a class can be missing.

## See Also
- [[Why Context Is Finite]] — prerequisite-for
- [[Unlimiformer]] — alternative-to (kNN-style retrieval over cached keys)
- [[LongMem Side-Network Memory]] — alternative-to
- [[MemLong Retrieval Memory Layers]] — alternative-to
