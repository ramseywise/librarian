---
title: Offline Recurrence Sleep for Language Models
tags: [foundations, pattern]
summary: "Before evicting old tokens from the KV cache, a hybrid state-space/attention model runs several offline recurrent passes over them to update its fast weights, so later answers need one forward pass; the benefit shows on synthetic reasoning tasks at small scale and is a latency shift, not a compute saving (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-lee-2026-do-language-models-need-sleep.md
---

# Offline Recurrence Sleep for Language Models

The paper (a 2026 preprint) treats a hybrid model, with attention over a bounded window plus a recurrent state-space layer whose state acts as fast weights, as having a "wake" mode and a "sleep" mode. At sleep time, before KV-cache entries are evicted, the model loops N times over that context, updating the recurrent state through a learned local rule trained end to end. At wake time the model answers in a single forward pass with no explicit retrieval or chain of thought. The idea is to spend compute while idle so the evicted context is still usable.

## Results (synthetic tasks; seed counts not given)

- Rule 110 cellular automaton with a 4-layer GDN-attention hybrid (eviction length 24, 32 steps): about 10% accuracy with no loop, about 20% with 2 loops and above 30% with 3 to 4 loops (self-reported, read from a figure).
- GSM-Infinite on Jet-Nemotron 2B (L=2000, 1,600 held-out examples): adding 6 loops moves 6-operation accuracy from 0.742 to 0.812, and 8-operation accuracy from 0.351 to 0.388 (self-reported).
- Ouro 1.4B plus 6 Jet layers, 4 loops: 0.419 to 0.615 (6-operation) and 0.210 to 0.272 (8-operation) (self-reported).
- With a sliding window of 512, 2-operation problems go from 0.596 to 0.905, which the paper calls a 52% improvement (self-reported).

## Limits

- Tasks are synthetic and models modest in scale. Training cost grows about linearly with the number of loops and is described as unstable and slow.
- The benefit is lower latency at wake time, not lower total compute. No analysis of forgetting, interference or multiple sessions, and no comparison with retrieval or compaction. No seed counts or variance; failure claims hold only under a fixed training-token budget. A depth-of-reasoning task (Depo) is reported as curves only.

## See Also
- [[Delta-Mem Fixed-Size State Memory]] — alternative-to
- [[Context Compaction]] — alternative-to
- [[Recurrent Memory Transformer (RMT)]] — related
- [[Memory Forms Taxonomy]] — prerequisite-for
