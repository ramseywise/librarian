---
title: "GPT From Scratch: Block, Weight Tying and Shortcuts"
tags: [llm, architecture, concept]
summary: "Raschka's from-scratch GPT-2 small build: causal multi-head attention coded step by step, pre-LayerNorm blocks with GELU feed-forward and shortcuts, and why the module-by-module model counts 163M parameters instead of 124M (weight tying)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-build-a-large-language-model-from-scratch-ch01-understanding-llms.md
  - data/raw/papers/2026-11-07-build-a-large-language-model-from-scratch-ch03-coding-attention-mechanisms.md
  - data/raw/papers/2026-11-07-build-a-large-language-model-from-scratch-ch04-implementing-a-gpt-model.md
---

# GPT From Scratch: Block, Weight Tying and Shortcuts

Raschka's *Build a Large Language Model (From Scratch)*, chapters 3 and 4, implement the decoder-only architecture described on [[Transformer Architecture]] in PyTorch. The chapters use toy sizes and untrained weights; every number below is a worked example unless marked reported.

## Attention, coded in four steps (chapter 3)

1. Simplified self-attention without trainable weights.
2. Scaled dot-product attention with learnable query, key and value matrices. Dividing the scores by sqrt(key dimension) is meant to stop softmax gradients vanishing. Raschka prefers `nn.Linear` to `nn.Parameter(torch.rand)` for these projections, citing its initialisation.
3. Causal attention: future positions are masked with `-inf` before softmax, which gives the same renormalised weights as zeroing after softmax and renormalising (second row [0.5517, 0.4483, 0, ...] both ways, on a 6-token example with d_in=3, d_out=2). Dropout on the attention weights applies after softmax and only in training; at 50% the survivors are scaled by 2 so the average influence is unchanged (later GPT training uses 0.1 or 0.2, per Raschka). The mask lives in a `register_buffer`, so it follows the model between devices.
4. Multi-head attention, first as a wrapper over causal heads (two heads, d_out=2 give a four-dimensional context vector per token), then as a weight-split class using one projection and a view/transpose split. He argues the second is more efficient and measures nothing.

Reported sizes for comparison: smallest GPT-2 has 12 heads, a 768-wide embedding and a 1,024-token context; the largest has 25 heads and embedding size 1,600.

## The block and the model (chapter 4)

The GPT-2 small configuration has vocabulary 50,257, context 1,024, embedding 768, 12 heads, 12 layers, dropout 0.1 and no QKV bias.

- **LayerNorm** adjusts activations to mean 0 and variance 1 across the feature dimension, with learned scale and shift; `unbiased=False` in the variance matches GPT-2's TensorFlow weights.
- **Pre-LayerNorm:** normalisation applied ahead of the attention and feed-forward layers, each wrapped in a shortcut. Raschka says the original transformer's Post-LayerNorm often trains worse and shows no experiment.
- **Feed-forward:** the 768-wide input grows fourfold to 3,072 and shrinks back, using the tanh-approximation GELU that GPT-2 used.
- **Shortcut connections** add a layer's input to its output. Setup: a small GELU network of five layers (sizes [3,3,3,3,3,1]) fed the single input [1,0,-1] with target 0, MSE loss, seed 123. Without shortcuts the mean absolute gradient is 0.00505 at layers.4 but only 0.000202 at layers.0; with them layers.0 keeps 0.2217 against 1.3259 at layers.4.
- `generate_text_simple` takes the last `context_size` tokens, the last position's logits, a softmax and an argmax (greedy decoding). Untrained, it produces gibberish ("Hello, I am Featureiman Byeswickattribute argue", 6 new tokens, seed 123).

## Parameter count and weight tying

With a separate output head, the assembled model counts 163,009,536 parameters rather than 124M. Dropping the output head's parameters, which is what weight tying amounts to (GPT-2 reuses the token embedding as its output layer), leaves 124,412,160, the GPT-2 small figure. In float32 the 163M model needs 621.83 MB (parameters x 4 bytes). Raschka keeps the layers separate because, he reports from experience with no data shown, they trained and performed better than tying. The chapter also notes that the 124M figure corrects the 117M printed in the GPT-2 report.

## Context numbers from chapter 1

Raschka restates GPT-3 figures from secondary sources: 96 transformer layers and 175 billion parameters, against six repeated encoder and decoder blocks in the original transformer; 300 billion of 499 billion listed tokens used in training (reason unstated); CommonCrawl (filtered) at 410B tokens and 60% of the mix; a $4.6 million cloud-credit estimate; and a Lambda Labs estimate of 355 V100-years. Chapter 1 also says LLaMA's data added Arxiv papers at 92 GB and StackExchange code Q&A at 78 GB.

## Limits

- Architecture only: the model is untrained, and chapter 3 uses toy dimensions (3 in, 2 out, 6 tokens) so outputs stay readable.
- Nothing is timed or measured for memory, so the efficiency case for the weight-split attention is an argument only. The gradient demo is one toy net, one seed, one input.
- The preference for untied heads and for Pre-LayerNorm is the author's claim without data.
- GPT-3 figures in chapter 1 are secondhand, and the cost estimate is cited by link rather than derived.
- The extraction records a figure mis-reference in the text (4.18 for 4.8) and a pointer saying weights are loaded in chapter 6 (the book's own numbering).

## See Also
- [[Transformer Architecture]] — prerequisite-for
- [[Self-Attention Mechanism]] — prerequisite-for
- [[Pre-Norm vs Post-Norm and Warm-Up]] — related (the normalisation placement Raschka adopts)
- [[Byte Pair Encoding and Sliding-Window Batches]] — prerequisite-for (the input this model reads)
- [[Pretraining a Small GPT: Loss, Perplexity and Overfitting]] — extends
