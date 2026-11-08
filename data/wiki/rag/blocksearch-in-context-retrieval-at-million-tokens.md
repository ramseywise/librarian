---
title: BlockSearch In-Context Retrieval at Million-Token Scale
tags: [rag, concept]
summary: A small LLM trained to pick gold documents out of a long in-context corpus collapses near a million tokens because attention to the gold document dilutes; scaling scores by log N and routing to a shortlist recover most of a dense retriever's recall.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-gollapudi-2026-can-language-models-actually-retrieve.md
---

# BlockSearch In-Context Retrieval at Million-Token Scale

BlockSearch is the authors' name for a Qwen3-0.6B model fine-tuned to read a corpus of independent documents (block-sparse mask, each document labelled with a four-digit code) and emit the code of the matching one. It is the test bed for asking whether long-context models can subsume a retriever. Numbers are the paper's (self-reported) unless noted; MS MARCO, 400 queries, Recall@1.

## Reported results

- **Collapse.** 95.8% at N=500 documents (about 45k tokens), against 95.5% for a dense retriever on the same backbone, but 0.2% at N=10,000 (about 0.95M tokens), where the dense retriever scores 20.2%. A prompted Gemini-3-flash given no task training falls from 95.0 to 16.2 across that range.
- **Mechanism the authors measured.** Measured at layer 19 over 100 queries (median), the gold document's slice of the attention output shrinks from 0.91 to 0.01 as N grows from 500 to 10,000, while total output magnitude shrinks only about 36%. An additive attention sink barely helps (0.2 to 2.5).
- **Fixes.** Rescaling the pre-softmax scores with log N (SSMax) and routing to a top-B document shortlist (B=256, layer 16) together reach 20.0 in the prose; dense scores 20.2. Routing alone gives 78.5 against 79.5 on HotpotQA. Decode latency at N=10k is 0.84 s routed against 4.51 s unrouted.
- **LIMIT lexical benchmark** (N up to 10,000, 1,000 queries): the method scores 0.135 and the same-backbone dense retriever 0.029; the authors say the gain still declines with N.
- **Synthetic scores overstate.** A concurrent 4B model with near-perfect needle-in-a-haystack scores gets 16.0 on MS MARCO at 10k documents, where dense scores 20.2.
- **Memory.** The KV cache for 10k documents is about 101 GiB against about 20 MB for a dense index.

## Limits

- Only two small backbones were tried (0.6B and 0.36B), with one query sample per corpus size; corpus capped at N=10,000, documents at 300 tokens, documents independent with a block-sparse mask rather than full attention.
- Retrieval-only training costs general ability (MMLU 40.2 to 33.6). On the indirect-relevance set OBLIQ every variant is near zero. Hybrid search, rerankers and production ANN are not tested.
- Internal inconsistencies: SSMax at N=10k is 17.8 in the text and 16.5 in Table 2; the combined result is 20.0 in the text and 20.5 in Table 2.

## See Also
- [[RAG Reranking]] — related
- [[Two-Tower Retrieval with logQ Correction]] — related
- [[Contextual Retrieval]] — related
