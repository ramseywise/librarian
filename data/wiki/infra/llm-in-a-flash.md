---
title: LLM in a Flash
tags: [infra, concept]
summary: "A method for running a model larger than DRAM by keeping weights in flash and loading only the feed-forward neurons that are active, using windowing and row-column bundling; up to 4x CPU, 7x Metal and 20x GPU speedup over naive loading when half the model fits (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-alizadeh-2023-llm-flash.md
---

# LLM in a Flash

Alizadeh et al. (Apple, arXiv 2312.11514, preprint, 2023) target models that do not fit in DRAM. The weights stay in flash and are read on demand, so the cost to cut is the number of bytes and the number of separate reads per token.

## Mechanism

- **Sparsity first.** The method only works where the feed-forward layers are mostly inactive per token. The paper reports sparsity of 97% for OPT, 95% for a relufied Falcon and 90% for a Llama 2 variant with a FATReLU activation.
- **Predictor.** A low-rank predictor reads the current layer's attention output and guesses which neurons will fire, so only those are fetched. The paper contrasts this with the Dejavu predictor, which works from earlier input. Reported error is about 5% false negatives and about 7% false positives, with little accuracy change (Arc Easy 66.1 to 66.2).
- **Windowing.** DRAM keeps the neurons that were active over the last k tokens, and each new token loads only the increment.
- **Row-column bundling.** An up-projection column and its matching down-projection row are stored together, so one read returns twice the data.
- A negative result: bundling neurons that tend to co-activate did not help.

## Reported results

Headline claim: models up to twice the size of DRAM run with up to 4x CPU, 7x Metal and 20x GPU speedup over naive loading (self-reported). Setup: about half the model held in DRAM, batch size 1, C4 validation data, 128 prompt tokens and 256 generated tokens.

For OPT 6.7B per-token latency (Table 3, naive against the full method): CPU 3182 ms against 669 ms, and an RTX 4090 GPU 2218 ms against 84 ms (self-reported). In the M1 Max breakdown (OPT 6.7B, 16-bit, half the memory) I/O latency falls from 2196 ms for the naive read to 87 ms in the final row (self-reported).

## Limits

- Batch size 1 only, and only models with ReLU-type sparsity.
- Only about half the model is held in DRAM; total energy use is higher than a fully resident model.
- The naive baseline uses a "best theoretical" I/O figure, and the 4-bit phone case is projected, not measured.
- Internal inconsistencies noted by the extraction: the Table 2 tick columns are ambiguous, and the 164 ms row cannot be matched to any named technique; Persimmon latency is 1041 in Table 3 and 1090 in Table 5.

## See Also
- [[LLM Inference Economics]] — prerequisite-for (the memory and latency levers this sits among)
- [[MoE Expert Offloading]] — alternative-to (the same flash-or-host-memory problem for expert layers)
- [[BitNet b1.58 Ternary Weights]] — alternative-to (shrinking the weights instead of paging them)
- [[Scaling Axes and Customer-Triggered Cost Cliffs]] — related
