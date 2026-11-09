---
title: Self-RAG Reflection Tokens
tags: [rag, concept]
summary: "Self-RAG fine-tunes one LM to emit special tokens that decide when to retrieve and critique passages and its own output, with the critique labels inserted offline by a distilled critic; the paper's results and ablations are summarised with their setups."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-2310-11511v1.md
---

# Self-RAG Reflection Tokens

Self-RAG (Asai et al., 2023) trains a single language model to retrieve on demand, generate, and critique. The authors' hypothesis is that retrieving a fixed number of passages every time hurts versatility and quality. **Reflection tokens** are special vocabulary items (Retrieve, IsRel, IsSup, IsUse) the LM generates to signal that retrieval is needed and to grade its output.

## Mechanism

- **Training.** Llama 2 7B and 13B generators are fine-tuned with a plain next-token loss on instruction data that was enriched offline: a Llama2-7B critic, distilled from GPT-4 labels, inserts the reflection tokens and the retrieved passages. No critic runs at training or inference time.
- **Inference.** The model first predicts a Retrieve token, then handles K passages in parallel; segments are chosen by beam search, scored on the segment's token probability plus a weighted sum of critique-token scores. The weights and a retrieval threshold can be changed at inference, so behaviour is customisable without retraining. The default retriever is Contriever.

## Results (self-reported)

Setups differ per row; most are the 13B model compared with Ret-Llama2-chat 13B or Ret-ChatGPT.

- On ALCE-ASQA zero-shot, SELF-RAG 13B has higher citation precision than Ret-ChatGPT, but does not win on string exact match (31.7 against 32.8 for Ret-Llama2-chat 13B).
- It beats retrieval-augmented baselines on PopQA's long-tail subset and by a large margin on PubHealth; on ARC-Challenge, Ret-ChatGPT scores 75.3.
- On biography generation (FactScore), SELF-RAG 13B beats Ret-Llama2-chat 13B; the 7B model scores 81.2.
- Llama2-FT 7B, trained on identical data minus the reflection tokens, does worse than SELF-RAG 7B on PopQA.
- Ablations (7B, 50k training instances; ASQA on 150 instances): always retrieving the top-1 passage lowers PopQA accuracy, and training without the critic collapses ASQA.
- Only 2% of correct SELF-RAG predictions on TriviaQA and PopQA are not in the provided passages (baseline printed as Alpaca 30B).

## Limits

- Training data is capped at 150k instances and the authors say scale curves are still rising; joint retriever training is left for later because off-the-shelf retrievers are weak for open-ended generation.
- Output can still lack full support from its citations. On factual precision SELF-RAG 7B sometimes edges out the 13B model, which the paper puts down to shorter outputs.
- Toolformer, SAIL and CoVE figures come from their papers, not re-runs; ablations use small samples with no seeds or significance tests; optimizer, seeds and several test-set sizes are not stated.

## See Also
- [[Agentic RAG — Advanced Patterns]] — related (the Self-RAG against CRAG comparison)
- [[RL for Retrieval Policies]] — related (Self-RAG as a policy without online rollouts)
- [[ADAPT-LLM Learned RET Token]] — alternative-to (also teaches the LM when to retrieve)
- [[CRAG Retry Logic]] — alternative-to
- [[PopQA and Popularity-Gated Adaptive Retrieval]] — related
- [[Auto-RAG Autonomous Iterative Retrieval]] — alternative-to
- [[Adaptive-RAG Query Complexity Routing]] — alternative-to
