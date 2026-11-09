---
title: ModernBERT Encoder Backbone
tags: [foundations, concept]
summary: ModernBERT is an encoder-only model with RoPE, GeGLU, alternating global and local attention and unpadding, trained on 2T tokens with 8192-token context, evaluated as a fine-tuned backbone for retrieval, code and classification.
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-warner-2024-smarter-better-faster-longer.md
---

# ModernBERT Encoder Backbone

Warner et al. ask whether an encoder-only model built with LLM-era architecture, large-scale data and hardware-aware design can outdo BERT-era encoders at retrieval, classification and code while running faster and using less memory, with native 8192-token context.

## Mechanism

ModernBERT-base (149M) and -large (395M) use RoPE, GeGLU, pre-norm, alternating global and local attention and full unpadding, built with the FlexBERT modular framework. Training is masked language modelling with a 30% mask over 2T tokens, of which 1.719T are at sequence length 1024 and 300B extend it to 8192. Each backbone is evaluated by fine-tuning on GLUE, MS MARCO retrieval (single-vector DPR and multi-vector ColBERT), the MLDR long-document benchmark and CoIR code tasks.

## Results

Self-reported; single run per cell.
- BEIR (15 datasets, nDCG@10, MS MARCO fine-tune): the base DPR average narrowly beats GTE-en-MLM-base; it leans on TREC-COVID (72.1 vs 49.7), which the authors say is an important factor. ColBERT-style training (810k samples, KL distillation from BGE-M3) beats the other base encoders.
- MLDR English out of domain: trained on short MS MARCO only, the base DPR model is worse than GTE-en-MLM-base; fine-tuning on MLDR closes the gap. ColBERT-style checkpoints are far ahead without long-context fine-tuning.
- GLUE dev: the base model outperforms DeBERTaV3-base and is the first MLM-trained model to do that; large is second to DeBERTaV3-large. CodeSearchNet: base beats all base encoders.
- Efficiency on one RTX 4090 with synthetic 8192-token documents: for long-context input the base model's throughput is 2.65x that of the next-fastest encoder (3x for large), and batches twice as big fit.
- Alternating global/local attention matched global-only downstream at 100B tokens while faster. Training loss of ModernBERT-large plateaued at a learning rate of 5e-4, so it was rolled back and the final 800B tokens ran at 5e-5.

## Limits

- English only; web-heavy data; MLM-only objective; only data scaling explored.
- The authors do not explain the long-context single-vector gap to GTE-en-MLM.
- No seeds or significance tests; efficiency on one GPU with synthetic data; GTE-en-MLM GLUE numbers come from its paper.
- It is a backbone, not an embedder: retrieval numbers reflect the authors' MS MARCO recipe.

## See Also
- [[RAG Retrieval Strategies]] — related
- [[GTR Large Dual Encoders]] — related (earlier dense-encoder backbone study)
