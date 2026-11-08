---
title: Query-Only Test-Time Training (qTTT)
tags: [foundations, concept]
summary: qTTT caches the key/value states of a long prompt and then takes a few gradient steps on the query projection alone, on the model's own context, to counter score dilution in softmax attention; with Qwen3-4B it beats a FLOP-matched thinking budget on LongBench-v2 and ZeroScrolls (self-reported).
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-bansal-2025-let-s-not-just-put.md
---

# Query-Only Test-Time Training (qTTT)

Bansal et al. (2025) argue that long-context failure comes from **score dilution**: with static softmax attention, many distractor tokens that score close to the needle take attention mass away from it. Generating more thinking tokens does not help, because those tokens use the same attention and can put on the needle at most their own attention mass.

## The argument

- Lemma 2.2: if m distractors score within a margin Δ of the needle, the needle's attention weight is bounded by 1/(1+m·e^−Δ).
- Lemma 2.3: holding the needle's attention mass fixed as context length T grows needs a logit gap that grows like log T.
- The authors conclude that a useful inference-time method has to change the query-key similarity, for example by updating queries, not sample more tokens.
- The theory is first-order, covers a single attention layer, and gives a worst-case bound rather than a measurement.

## The method

1. One prefill pass caches keys and values.
2. A few gradient steps update only the query projection W_Q, with a next-token loss over random spans taken from the context.
3. The gradient moves a query toward the needle key, and Lemma 3.2 says the margin rises with the step size.

Because keys and values stay fixed, the cache is reused and the cost is dominated by prefill. On an A100, an 8B model at 128K tokens takes 354 s for prefill and 375 s with qTTT (self-reported latency, no accuracy at that length).

## Results (Qwen3-4B, one run per setting, self-reported)

- LongBench-v2, six subsets, FLOP-matched (thinking budget 8,192 tokens against k=128 and 32 qTTT steps): in-context 27.0, thinking 33.5, qTTT 39.6.
- ZeroScrolls, eight datasets: in-context 18.4, thinking 23.9, qTTT 32.5.
- Synthetic bank-transaction needle task at 9,560 tokens: thinking accuracy 1.0%, qTTT 8.4%, with attention mass on the target 0.04 and 0.25.
- Splitting the same budget over samples hurts: self-consistency over 32 samples averaged 19.8 on LongBench-v2.

## Limits

- Single runs, no confidence intervals, and sample sizes are not stated. The learning rate is tuned per dataset, and high or low rates fail badly.
- On the shortest synthetic length, qTTT trailed thinking mode on bank transactions, 28.0 to 36.0. Gains depend on the task and are smaller on summarization, and on GovReport Qwen3-32B with qTTT scored under plain in-context use (26.0 against 26.7).
- Only Qwen3 models from 1.7B to 32B were tried, and synthetic contexts reach about 10K tokens. No comparison with RAG, compression or other test-time-training variants.
- The claim that dilution is the main cause rests on a correlation with attention mass and a no-RoPE ablation, neither of which excludes other causes.

## See Also
- [[Self-Attention Mechanism]] — prerequisite-for
- [[Context Failure Modes]] — related (the failure it targets)
- [[Doc-to-LoRA]] — alternative-to (both move context information into weights at inference)
- [[Why Context Is Finite]] — related
