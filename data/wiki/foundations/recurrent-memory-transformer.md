---
title: Recurrent Memory Transformer (RMT)
tags: [foundations, concept]
summary: RMT passes a few memory tokens from one fixed-size segment to the next on a pretrained transformer, giving linear compute and constant memory; it reached 2M tokens on synthetic fact tasks, though memory is lossy and the tasks are easy.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-bulatov-2023-scaling-transformer-1m-tokens-beyond.md
---

# Recurrent Memory Transformer (RMT)

Bulatov et al. (2023, AAAI 2024 version) add memory tokens to a pretrained transformer. At each step, memory tokens are prepended to a segment, the model runs, and its output memory tokens go into the next segment. Because a single segment sits on the GPU at once, inference memory stays constant and compute grows linearly with input length.

## Setup and results (self-reported)

- A BERT backbone with 512-token segments (499 usable, 10 for memory, 3 special). Training used at most 7 segments with a curriculum that lengthens the task step by step, and evaluation reached 4,096 segments (about 2M tokens).
- Tasks are synthetic bAbI facts hidden in QuALITY filler text: memorize, detect and memorize, and a two-fact reasoning task. Detect-and-memorize is easiest. The text gives no accuracy numbers for these (plots only).
- Training directly on four segments, with no curriculum, neither solved the task nor extrapolated. Once training reached five or more segments, the model generalised almost perfectly to tasks twice as long.
- An analytic FLOP estimate gives RMT 29 times fewer FLOPs than OPT-175B and 295 times fewer than a 125M OPT at 2,048,000 tokens; no run measured this. A measured unoptimised GPT-2 FP32 baseline exhausted an 80 GB GPU at 8K tokens.
- It combines with LoRA and adapters on Pythia-70m (7.30 to 6.97 with one to two segments, from 41.43 for adapters alone), though the table column is labelled loss where the text says perplexity.
- A Lean theorem-proving test gave a modest gain only.

## Limits

- The authors concede the 2M-token result is on specialised synthetic tasks, and the distractor text differs from the facts so the lookup is trivial. No comparison with full attention at long lengths, and no aggregation tasks.
- The authors treat full attention as an upper bound, since RMT sees only compressed memory.
- Extraction inconsistencies: "OPT-135M" appears for the 125M model, a segment size printed as "2028", and a LOSS label against perplexity in the text.
- The backbones are old and small (BERT, GPT-2, and two other small decoder models). Backpropagation through time is costly, and the context sizes it cites for GPT-4 and Claude are out of date.

## See Also
- [[Transformer Architecture]] — prerequisite-for
- [[Artificial Hippocampus Networks]] — alternative-to (compressed state for evicted context)
- [[Unlimiformer]] — alternative-to
- [[Why Context Is Finite]] — related
- [[LM2 Large Memory Models]] — alternative-to (gated memory bank in every block)
- [[Offline Recurrence Sleep for Language Models]] — alternative-to
