---
title: Transformer-XL Segment Recurrence
tags: [llm, architecture, concept]
summary: "Transformer-XL caches the previous segment's hidden states as extra keys and values and uses a relative positional encoding, so a self-attention language model reaches beyond a fixed-length context without context fragmentation."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-dai-2019-transformer-xl.md
  - data/raw/papers/2026-11-08-khandelwal-2018-sharp-nearby-fuzzy-far-away.md
---

# Transformer-XL Segment Recurrence

Dai, Yang, Yang et al. ask whether a self-attention language model can learn dependencies longer than a fixed context window without context fragmentation (segments of fixed length cut with no regard for sentence or semantic boundaries, leaving early symbols without context), and also evaluate faster.

## Mechanism

- **Segment-level recurrence:** the previous segment's hidden states are held fixed (stop-gradient) and cached; keys and values for the next segment also cover them, extending its context. Gradients never leave the current segment.
- **Relative positional encoding:** a sinusoidal relative encoding R takes the place of absolute position embeddings, with learned global biases u and v (one pair, shared everywhere) and distinct key matrices for content and for position.
- **Relative Effective Context Length (RECL):** defined over a group of models, it gauges the benefit of a long context as the relative gain over the best short-context model, restricted to the r hardest examples. It builds on the effective-context-size idea of Khandelwal et al.

## Results (all self-reported, single runs)

- WikiText-103: the 257M Large model (attention length 384 train, 1600 eval) reaches 18.3 test perplexity against 20.5 for the contemporary 247M Adaptive Input model; the 151M Standard model gets 24.0.
- enwik8: a 24-layer 277M model (attention length 784 train, 3,800 eval) reaches 0.99 bits per character, which the paper calls the first below 1.0, against 1.06 for the 64-layer 235M model of Al-Rfou et al. A 12-layer 41M model reaches parity with the 64-layer vanilla Transformer using 17% of its parameters (12-layer Al-Rfou, 44M, scores 1.11).
- text8: 1.08 bits per character with enwik8 hyperparameters and no tuning. One Billion Word: single-model state of the art moves from 23.7 to 21.8 (Large, 0.8B), a task with no long-term dependency. Penn Treebank: 54.52 perplexity among models without two-step finetuning (24M parameters).
- Ablation, One Billion Word (20 layers, about 0.3B, 400K steps): without recurrence perplexity rises from 25.2 to 27.1, while using the Shaw et al. encodings instead gives 25.7. On WikiText-103 (128M, backpropagation length 128), lengthening attention to 500 lowers perplexity from 27.02 to 26.77, while models lacking recurrence get nothing from longer attention.
- RECL at r = 0.1 for the 151M models is 900 words: 80% above recurrent networks and 450% above the Transformer (LSTM 400, QRNN 500, vanilla Transformer 128).
- Against the vanilla Transformer from Al-Rfou et al., evaluation is up to 1,874 times quicker at attention length 3,800 and 363x quicker at 800 (one GPU, per-token time).

## What an LSTM language model uses of its context

Khandelwal et al. disturb the earlier context of a trained AWD-LSTM language model at test time (truncating, permuting, dropping, replacing) and track how dev perplexity rises (mean of 3 seeds, PTB and Wiki). Effective context size, the tokens needed to land within 1-2% perplexity of unlimited context, is roughly 200; on PTB the 1% threshold is only crossed past 150 tokens, and on Wiki past 250. Local word order matters just within the latest 20 tokens, global word order within the latest 50. Deleting content words 5 tokens back raises perplexity about 65%, against 17% for random removals. Targets that only far context can supply (Cfar, past the latest 50 tokens) suffer 12% when all distant context is removed. A neural cache helps copying, yet harms about 36% of PTB words (20% of Wiki) that context cannot supply.

## Limits

- The Transformer-XL PDF carries no appendices, so the optimiser, learning rate and batch size, depth and width for most models, number of training steps, hardware and the formal RECL definition are all absent.
- Results are single runs with no seeds or significance tests; the Adaptive Input baselines are concurrent work and the Large models exceed most baselines in size.
- R is a fixed sinusoid without learnable parameters, and no clipping of relative distance is mentioned. The word-level results use adaptive softmax and adaptive inputs, which is not ablated.
- Khandelwal et al. apply perturbations only at test time, so the losses are upper bounds; one architecture and two small datasets confound model and data effects; token-level analysis only; dev sets only; no attention models.

## See Also

- [[Transformer Architecture]] — prerequisite-for
- [[Recurrent Memory Transformer]] — related (another recurrence over segments)
- [[Deep Character-Level Transformer with Auxiliary Losses]] — prerequisite-for
- [[Adaptive Input Representations]] — related (contemporary baseline)
- [[Efficient Attention Approximations]] — related (a recurrence method in Tay et al.'s taxonomy)
