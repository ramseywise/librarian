---
title: Position Interpolation
tags: [foundations, concept]
summary: Position Interpolation (PI) extends a RoPE model's context window by scaling position indices down into the trained range instead of extrapolating past it, and recovers a working 8K to 32K window from LLaMA after about 1,000 fine-tuning steps (self-reported).
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-chen-2023-extending-context-window-large-language.md
  - data/raw/papers/2026-11-06-liu-2024-world-model-million-length-video.md
---

# Position Interpolation

RoPE models trained at a window L fail when run beyond it: on LLaMA 7B trained at 2,048 tokens, perplexity on PG19 rose above 1,000 at windows from 4,096 to 32,768. Chen et al. (2023, Meta) instead rescale positions. To run at window L' they map position m to mL/L', so every index falls inside the trained range, and then fine-tune briefly. No weights are added.

## Evidence (self-reported, LLaMA 7B to 65B)

- Without any tuning, PI at 8,192 gives perplexity 16.10 and then 7.12 after 200 steps and 6.95 after 1,000, below the original model's 7.20 at 2,048.
- The effective window, measured by passkey retrieval, reached its target after about 200 steps. Direct fine-tuning to 8,192 grew it only from 2,048 to 2,560 after over 10,000 steps.
- PG19 perplexity kept falling as the window grew under PI (7.23 at 2,048 to 6.77 at 32,768 for the 7B model), while direct fine-tuning regressed.
- The cost is small at short length: perplexity within 2,048 tokens worsens by 0.01 to 0.05 and zero-shot benchmarks lose up to 2% at 8,192, more at longer extension.
- An analytic bound puts interpolation error about 600 times below extrapolation error. This bounds attention scores, not task quality.
- GovReport at 16K: ROUGE-1, ROUGE-2 and ROUGE-L of 60.0, 28.0 and 29.5, compared with 61.3, 32.2 and 33.8 for CoLT5.

## A later recipe

The Large World Model (Liu et al., ICLR 2025) grows a LLaMA-2 7B window in stages (32K, 128K, 256K, 512K, 1M tokens, on 4.8B, 12B, 12B, 3B and 1.8B tokens), raising the RoPE base from 1M to 50M at the last stage, with each stage starting from the previous. It serves 1M tokens with Blockwise RingAttention across a TPU slice (minimum v4-128). Single-needle retrieval is described as near-perfect, and at 1M the multi-needle scores were 0.67, 0.84 and 0.69 against 0.84, 0.97 and 0.84 at 32K (self-reported). MMLU slipped from 0.39 to 0.35 at 1M, which the text's "no negative effects" claim glosses over. Tuning the chat-to-retrieval data mix traded MT-Bench (2.42 to 5.8) against needle accuracy (100% to 31%).

## Limits

- PI applies to RoPE models, and the passkey task is synthetic with a 20% success threshold. No reasoning or multi-hop long-context test. Attention cost at long length is not measured. Models are from 2023.
- The 7B 32,768 model's proof-pile perplexity rose at the longest window (2.24 to 2.48), undiscussed. 65B was extended only to 8,192.
- The LWM results come from 7B models, with 2024-era baselines, and its Table 2 rows added after the paper mix eras. It reports no inference cost curves and no measure of lost-in-the-middle. Its discrete-token vision results trail the state of the art.

## See Also
- [[Positional Encoding]] — prerequisite-for
- [[Why Context Is Finite]] — related
- [[IN2 Training and VAL Probes]] — related (RoPE base suggestion for long-context tuning)
- [[Context Window Budgeting]] — related (nominal versus effective window)
