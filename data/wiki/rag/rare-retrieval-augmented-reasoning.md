---
title: "RARE Retrieval-Augmented Reasoning"
tags: [rag, pattern]
summary: "RARE adds two retrieval actions and a retrieval-based factuality scorer to rStar-style tree search; on medical QA with LLaMA 3.1 8B it averaged 73.84 against 70.56 for rStar (self-reported), at roughly 300 times the tokens of chain-of-thought."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-06-tran-2024-rare.md
---

# RARE Retrieval-Augmented Reasoning

RARE (arXiv 2412.02830, preprint) extends the rStar Monte Carlo tree search reasoner with retrieval. Two new actions join the search: A6 issues several retrieval queries for the current step (multi-query retrieval), and A7 retrieves for each generated sub-question. A factuality scorer called RAFS rates candidate reasoning paths with the same backbone model, using retrieved evidence to check each statement. Retrieval uses ColBERT over the MedCorp corpus.

## Results (self-reported)

- Ablation on 250 MedQA samples, LLaMA 3.1 8B: rStar 70.0, rStar plus RAFS 71.4, plus A6 72.4, plus A7 71.2, plus A6 and A7 73.2, full RARE 74.8.
- Averages over the medical benchmarks, LLaMA 3.1 8B: chain-of-thought scored 62.76 and rStar 70.56. Retrieval baselines were MedRAG (64.81) and i-MedRAG (71.21). RARE scored 73.84.
- At 70B, RARE scored 84.51 against 83.57 for GPT-4o.
- Token use: about 400 for chain-of-thought, 92.6k for rStar and 119.9k for RARE.
- RAFS agreement with expert labels was 85.14% on 10 questions (about 100 statements).

## Limits

- Only LLaMA-family backbones are tested. No latency or dollar cost is given, only token counts.
- There is no retriever ablation, so the contribution of ColBERT versus the search actions is not separated.
- The significance claim (p<0.01) states no number of runs.
- The scorer and generator are the same model, and the factuality scores of competing paths sit close together in the examples (1.0, 0.625, 0.6).
- Ablation uses 250 samples from one dataset.

## See Also
- [[Agentic RAG — Advanced Patterns]] — prerequisite-for
- [[RAG Retrieval Strategies]] — related
- [[Self-Reasoning Retrieval-Augmented Model]] — alternative-to
- [[CRAG Corrective Retrieval Evaluator]] — alternative-to
