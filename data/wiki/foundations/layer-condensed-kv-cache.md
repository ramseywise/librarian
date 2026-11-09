---
title: Layer-Condensed KV Cache
tags: [foundations, concept]
summary: "The Layer-Condensed KV Cache pairs every layer's queries with the keys and values of only the top layer, so one layer's KV is cached; it reports up to 26x throughput against a standard Transformer but costs about 3x pretraining time and was checked for quality only at 1.1B (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-wu-2024-layer-condensed-kv-cache-efficient.md
---

# Layer-Condensed KV Cache

Wu and Tu (2024) pair the queries of all layers with the keys and values of the top layer only. Only one layer's KV is cached or computed, and the key and value projections of the other layers are dropped. Masking the attention diagonal stops a layer depending on itself, and the first token receives zero-valued placeholder KV.

## Training and prompt handling

Training runs n bottom-up iterations in parallel, each using the previous iteration's top-layer KV. Back-propagation covers only the last b=2 iterations, and m=7 forward-only iterations were enough. The paper has a theorem that this matches sequential training when enough iterations are used. A few "warmup" layers keep standard attention; the best placement split them between bottom and top (1.1B, w=2, dev perplexity 7.381 against 7.668 all-bottom and 9.098 all-top, fine-tuned from a pretrained initialisation). Prompts cannot be encoded in parallel: the prompt is iterated m+b=9 times.

## Results (self-reported)

- Headline: up to 32x larger batch and 26x higher throughput for 1B-30B models. The 26x belongs to the 30B model run with CPU offload on one RTX 3090 (batch 4 against 83); without offload on an A100 the gains are 3.0x for 7B and 7.7x for 30B, each with w=2. Setup: Hugging Face Transformers with FlashAttention-2, FlexGen-style end-to-end throughput.
- Quality, 1.1B models pretrained on 100B SlimPajama tokens with the TinyLlama recipe: dev perplexity 9.219 (TinyLlama), 9.265 (w=10), 9.746 (w=2); average of seven zero-shot tasks 46.65, 46.84 and 45.45.
- At about equal batch size the model is still faster (7B on A100, 141.10 against 367.56 tokens/s at w=2); the paper says the cause is unclear.
- It combined with StreamingLLM for lower latency in the paper's setup.

## Limits

- Pretraining took about 3x as long as the baseline (2.77x at w=2); the authors suggest initialising from a pretrained model.
- Quality was measured only at 1.1B on 100B tokens at 2048 context, with small zero-shot commonsense tasks; 7B and 30B were throughput-only.
- Prompt-heavy tasks lose throughput because encoding is iterative; the paper suggests long-generation uses.
- Tested on Hugging Face with FlashAttention-2, not a production server; no paged attention and no comparison with GQA or MQA.
- The extraction notes that the memory bars in Figure 5 show smaller savings than the headline figures.

## See Also
- [[KV Cache Reduction Methods]] — prerequisite-for (the family it belongs to)
- [[YOCO Decoder-Decoder Architecture]] — alternative-to (also keeps a single global KV layer)
- [[Self-Attention Mechanism]] — prerequisite-for (the per-layer attention it changes)
