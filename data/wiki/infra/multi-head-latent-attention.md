---
title: Multi-Head Latent Attention
tags: [infra, concept]
summary: "Multi-head latent attention (MLA) caches one low-rank key-value latent per token plus a small decoupled position key, shrinking the cache far more than grouped-query sharing; DeepSeek-V2 pairs it with DeepSeekMoE and reports large cache and throughput gains over its dense predecessor."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-07-deepseek-ai-2024-deepseek-v2.md
---

# Multi-Head Latent Attention

DeepSeek-AI's DeepSeek-V2 report introduces MLA as an attention mechanism with low-rank joint compression of keys and values. Each token's hidden state is projected down to a latent c_t^KV (W^DKV h_t), and keys and values are recovered by up-projections (W^UK, W^UV); only the latent is cached. RoPE cannot be applied to the compressed keys without blocking the absorption of the up-projection into the query projection, which would force prefix keys to be recomputed. MLA therefore carries RoPE on extra multi-head queries and one shared key (decoupled RoPE) and caches the latent plus that key, a total of d_c plus d_h^R elements for each token in each layer. The report states this as an argument and gives no ablation of the choice.

## What the report measures

- Cache size: with d_h = 128, a compressed dimension d_c of 4 d_h (512) and a rope dimension d_h^R of 64, the cache works out to about 9/2 d_h per layer-token, which the report equates to GQA with 2.25 groups. The count is in elements, not bytes.
- MoE ablations: MLA used 14% (small, about 16B total parameters, 1.33T tokens) and 4% (large, about 250B total, 420B tokens) of the MHA cache; the arms differ in activated parameters (21.5B MLA against 25.0B MHA at large scale) (self-reported).
- Quality: large MoE, MLA scores 50.7 against 46.6 for MHA on BBH (3-shot); in the small MoE, MLA trails MHA on C-Eval (50.9 against 51.6) but leads on BBH, MMLU and CMMLU (self-reported).
- Dense 7B comparison at 1.33T tokens: MHA 45.2, GQA with 8 groups 41.2, MQA 37.9 on 5-shot MMLU (self-reported); the report uses this to argue that MLA avoids the quality cost of sharing heads.
- Whole-model headline: DeepSeek-V2 (236B total, 21B active, 60 layers, 2 shared plus 160 routed experts with 6 active) cuts the cache by 93.3% and reaches 5.76x the maximum generation throughput of dense DeepSeek 67B on one node of 8 H800 GPUs with FP8 weights and a 6-bit average KV cache; throughput exceeds 50K tokens/s for generation and 100K tokens/s for prompt input (self-reported). Training costs 42.5% less per trillion tokens (172.8K against 300.6K H800 GPU hours).
- Other model results from the same report: 78.5 on 5-shot MMLU at 21B activated parameters, 38.9 length-controlled AlpacaEval 2.0 win rate and 8.97 MT-Bench for the RL chat model, and 128K context via YaRN with 1000 steps at 32K (self-reported).

## Limits

- The 93.3% and 5.76x figures are measured against dense DeepSeek 67B and bundle MLA with MoE sparsity, FP8 weights and a 6-bit quantised cache; there is no full-scale ablation isolating MLA's efficiency.
- The MLA-against-MHA quality ablation runs at two scales with different token budgets and activated parameters per arm; single runs, no seeds.
- Throughput is taken on the request mix of the DeepSeek 67B service; batch size, utilisation and kernel details are absent, and apart from one prompt-throughput figure prefill and decode are not separated.
- Hyperparameters and data sizes for the RL stage are not given. The authors concede the model cannot learn new facts after pretraining, may hallucinate, is weak outside Chinese and English, and handles text only.

## See Also

- [[Multi-Query and Grouped-Query Attention]] — alternative-to
- [[DeepSeekMoE Fine-Grained Expert Segmentation]] — related (the feed-forward half of DeepSeek-V2)
- [[Self-Attention Mechanism]] — prerequisite-for
- [[Prefix Caching]] — related
