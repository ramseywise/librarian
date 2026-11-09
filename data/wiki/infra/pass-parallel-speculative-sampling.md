---
title: PaSS Parallel Speculative Sampling
tags: [infra, concept]
summary: "PaSS drafts speculative-sampling candidates from the target model itself by appending a few learned look-ahead embeddings, training only those embeddings; with LLaMA 7B and 4 look-ahead tokens it gave up to 30% faster generation with unchanged HumanEval scores (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-08-monea-2023-pass.md
---

# PaSS Parallel Speculative Sampling

Monea et al. (2023, a NeurIPS workshop paper) ask whether speculative sampling needs a second draft model. In PaSS, L learned look-ahead embeddings are appended to the input of a frozen LLaMA 7B, so a single forward pass produces L draft tokens. A second pass checks them under the usual speculative-sampling rejection rule, and a rejected token is resampled from the residual distribution. Only the embeddings are trained, so the added parameters are L x d_emb rather than the K x d_emb of look-ahead heads.

Every model call adds at least one token, which keeps the output distribution unchanged; the paper bounds the speedup at (L+2)/2, lower than the L+1 of classic speculative sampling because each iteration needs two model calls.

## Results (self-reported)

LLaMA 7B, 4 look-ahead tokens unless noted:
- Up to 30% faster on Wikipedia and The Stack completions of 512 tokens.
- HumanEval at temperature 0.1: time falls from 10.52 to 7.17 s with Pass@1 13.2% against 13.4%. At temperature 0.8: 10.15 to 8.17 s with the same 22.5% Pass@10.
- The Stack at temperature 0.2: 8.96 against 12.72 autoregressive. Wikipedia at temperature 0.8: 10.23 against 12.45.
- The gain is larger at lower temperature. A fixed unknown-token look-ahead gave almost nothing (12.25 against 12.52, The Stack, temperature 0.8), so the trained embeddings carry the gain.
- Generation time kept falling until 6 look-ahead tokens (9.66) and was higher at 8 (9.94).

## Limits

- Table 1 gives no time unit, hardware, variance or seeds; only LLaMA 7B and one training set per task.
- The paper reports neither acceptance rates nor tokens per call, and no comparison with a draft-model baseline or Medusa; only autoregressive and fixed-token baselines.
- The gain saturates near 6 look-ahead tokens; the authors name draft quality of parallel generation as the main thing to improve.
- The HumanEval quality claim relies on matching Pass@k scores described as within the margin of error, without an error estimate.

## See Also
- [[Speculative Decoding]] — prerequisite-for (the lossless draft-and-verify scheme PaSS keeps)
- [[TiDAR Diffusion Drafting]] — alternative-to (also drafts with the target model itself)
- [[LLM Inference Economics]] — prerequisite-for (decode latency as the target)
