---
title: Transformer Architecture
tags: [llm, architecture, concept]
summary: The Transformer model architecture (Vaswani et al., 2017) — encoder-decoder stacks of self-attention and feed-forward layers that replaced RNNs/CNNs for sequence transduction, enabling parallelized training and constant-length dependency paths.
updated: 2026-11-19
sources:
  - data/raw/pdfs/2017-06-12-attention-is-all-you-need.md
  - data/raw/papers/2026-11-07-vaswani-2017-attention-all-you-need.md
  - data/raw/papers/2026-11-08-xiao-foundations-llms-ch02-generative-models.md
  - data/raw/papers/2026-11-08-xiao-foundations-llms-ch01-pre-training.md
  - data/raw/papers/2026-11-07-build-a-large-language-model-from-scratch-ch03-coding-attention-mechanisms.md
  - data/raw/papers/2026-11-07-build-a-large-language-model-from-scratch-ch04-implementing-a-gpt-model.md
---

# Transformer Architecture

The Transformer (Vaswani et al., 2017, "Attention Is All You Need") is the first sequence transduction model based entirely on attention, dispensing with recurrence and convolutions. It is the foundation architecture behind all modern LLMs.

## Core Architecture

**Encoder-decoder stacks**, each with N=6 identical layers:

- **Encoder layer**: multi-head [[Self-Attention Mechanism]] + position-wise feed-forward network (FFN), each with residual connections and layer normalization.
- **Decoder layer**: same as encoder plus a third sub-layer performing multi-head attention over the encoder output. Decoder self-attention is masked to prevent attending to future positions.

All sub-layers produce output of dimension d_model = 512.

## Key Components

### Scaled Dot-Product Attention

```
Attention(Q, K, V) = softmax(QK^T / sqrt(d_k)) V
```

Scaling by `1/sqrt(d_k)` prevents dot products from growing large in magnitude, which would push softmax into regions with vanishingly small gradients.

### Multi-Head Attention

Instead of single attention, project Q/K/V h times with different learned projections, attend in parallel, concatenate, and project again:

```
MultiHead(Q, K, V) = Concat(head_1, ..., head_h) W^O
where head_i = Attention(Q W_i^Q, K W_i^K, V W_i^V)
```

Base model: h=8 heads, d_k = d_v = d_model/h = 64. This allows attending to information from different representation subspaces at different positions.

### Three Uses of Attention

1. **Encoder-decoder attention**: queries from decoder, keys/values from encoder output (cross-attention)
2. **Encoder self-attention**: all Q/K/V from previous encoder layer
3. **Masked decoder self-attention**: prevents leftward information flow (auto-regressive property)

### [[Positional Encoding]]

Sinusoidal functions of different frequencies injected at the bottom of encoder/decoder stacks — the model has no recurrence, so position information must be explicitly added. Learned positional embeddings produce nearly identical results.

### Position-wise FFN

Two linear transformations with ReLU: `FFN(x) = max(0, xW_1 + b_1)W_2 + b_2`, with inner dimension d_ff = 2048.

## Computational Properties

| Layer Type | Complexity/Layer | Sequential Ops | Max Path Length |
|---|---|---|---|
| Self-Attention | O(n^2 * d) | O(1) | O(1) |
| Recurrent | O(n * d^2) | O(n) | O(n) |
| Convolutional | O(k * n * d^2) | O(1) | O(log_k(n)) |

Self-attention connects all positions with O(1) sequential operations — faster than recurrent layers when sequence length n < representation dimension d (typical for NLP).

## Training Details

- **Optimizer**: Adam with warmup schedule (linear increase for 4000 steps, then inverse square root decay)
- **Regularization**: residual dropout (P=0.1), label smoothing (epsilon=0.1)
- **Hardware**: 8 NVIDIA P100 GPUs; base model ~12 hours, big model ~3.5 days

## Results

All numbers are the paper's own (self-reported).

- **WMT 2014 EN-DE** (newstest2014): the big model, trained 3.5 days on 8 P100 with the final 20 checkpoints averaged and beam size 4, reaches 28.4 BLEU, over 2 BLEU ahead of every earlier model, ensembles included (ConvS2S ensemble as the baseline).
- **WMT 2014 EN-FR** (newstest2014, big model, dropout 0.1): 41.8 BLEU, a new best for a single model over the MoE baseline, for under a quarter of the previous best's training cost. The base model gets 38.1 on EN-FR after 100K steps (about 12 hours), short of earlier single models; on EN-DE the base model already outscores all earlier models and ensembles at an estimated 3.3e18 FLOPs.
- **Ablations** (base model on the EN-DE newstest2013 dev set, without checkpoint averaging): at fixed computation one head lands 0.9 BLEU below the top setting, and an excess of heads costs quality as well; smaller d_k lowers quality; bigger models and dropout help.
- **English constituency parsing** (WSJ section 23): a 4-layer Transformer gets 91.3 F1 from WSJ data alone and 92.7 F1 semi-supervised on roughly 17M sentences, with little task-specific tuning.
- The sqrt(d_k) scaling is argued, not ablated: assuming independent q and k components of mean 0 and variance 1, dot-product variance rises with d_k.

## The decoder-only block in two textbooks

Xiao and Zhu (*Foundations of Large Language Models*, ch. 2) describe a decoder-only Transformer as a stack of L blocks, each a self-attention sub-layer plus an FFN sub-layer, with a causal mask and a softmax over the vocabulary on top. Raschka's from-scratch LLM book (ch. 3 and 4) codes the same block. Xiao and Zhu run no experiments of their own on these design choices; Raschka's numbers below are his own worked examples.

- **Attention**: Xiao and Zhu write it as softmax(QK^T / sqrt(d) + Mask) V. Raschka scales the scores down by the root of the key dimension so the softmax gradients do not vanish, and masks future positions with -inf before the softmax; on his six-token example this gives the same renormalised weights as zeroing after the softmax and renormalising. He applies dropout to the attention weights after the softmax, in training only, and rescales the survivors by 1/(1-p). In ch. 1 Xiao and Zhu say practical systems set the number of heads to at least 4. See [[Self-Attention Mechanism]].
- **Normalisation placement**: Xiao and Zhu say most LLMs use pre-norm, output = F(LNorm(input)) + input, because it trains deep Transformers more stably than post-norm, which is LNorm(F(input) + input). Raschka likewise uses Pre-LayerNorm and says the original Post-LayerNorm often gives worse training dynamics. Neither shows an experiment; one is in [[Pre-Norm vs Post-Norm and Warm-Up]]. Xiao and Zhu also name RMSNorm as in Llama, which only rescales by the root mean square with no re-centring (see [[Layer Normalization]]).
- **Feed-forward activation**: Raschka uses GELU (tanh approximation, as GPT-2 did) and expands the hidden size 4 times, 768 to 3,072, then contracts it. Xiao and Zhu advise SwiGLU or GeGLU over ReLU in wide FFNs and note that PaLM and Llama use SwiGLU ([[GLU Variants and GELU]]). They add that removing bias terms helps training stability, as in Llama and Gemma.
- **Shortcuts**: in Raschka's five-layer GELU demonstration (layer widths 3,3,3,3,3,1, one input vector [1,0,-1], a target of 0, mean-squared-error loss and seed 123) the mean absolute gradient without shortcuts is 0.00505 at layers.4 and only 0.000202 by layers.0; with shortcuts it is 1.3259 at layers.4 and still 0.2217 at layers.0 (self-reported).
- **Position**: For length generalisation Xiao and Zhu favour relative or rotary schemes over learned absolute embeddings, suggest fine-tuning on longer sequences after pre-training, and describe interpolation or NTK-aware base scaling for stretching RoPE models ([[Position Encodings — Relative, Rotary, ALiBi and CAPE]], [[Position Interpolation]]).
- **Sizes**: Raschka's GPT-2 small configuration has a 50,257 vocabulary, 1,024 context, 768 embedding size, 12 attention heads and 12 layers, dropout 0.1 and no QKV bias; the largest GPT-2 has 25 heads and embedding size 1,600. Xiao and Zhu's model table lists GPT-3 175B with 96 layers, width 12,288 and 96 query heads and 96 KV heads, and Llama3.1 405B with 126 layers, width 16,384, 128 query heads and 8 KV heads (grouped-query attention, see [[Multi-Query and Grouped-Query Attention]]).

## Why It Matters for Agent Engineering

The Transformer is the foundation of every LLM used in agent systems. Understanding its attention mechanism, context window constraints, and computational scaling properties is essential for:
- **Context management**: understanding why context windows have quadratic cost
- **Prompt engineering**: leveraging attention patterns for effective instruction placement
- **Architecture decisions**: when to use encoder-decoder vs decoder-only variants

## Limits

- Only two translation tasks and one parsing task are tested; the authors leave language modelling and other modalities as future work.
- Each configuration has a single run, with no seeds or significance testing.
- For the EN-FR big model the abstract and Table 2 print 41.8 BLEU while section 6.1 prints 41.0; the paper never reconciles them, and this page quotes 41.8.
- FLOPs come from GPU time and nominal capacity rather than measurement, and perplexities are per wordpiece, so they cannot be set beside per-word numbers.
- The interpretability evidence for attention consists of hand-picked examples.
- Xiao and Zhu's chapter has almost no experiments of its own; its figures are borrowed from other work or illustrative, and its model table (Table 2.2) is a late-2024 to early-2025 snapshot. The extraction flags, from an outside-knowledge check it marks as unverified in the text, that the table lists Gemma2 as 37B and gives Llama2-70B, Falcon and Mistral-7B equal query and key-value head counts. Its pre-norm and bias-removal statements carry no experiment.
- Raschka's examples use toy sizes, a fixed seed and a single input, his pre-norm statement is made with no experiment, and the extraction notes a figure-number slip in the text (4.18 for 4.8).

## See Also
- [[Self-Attention Mechanism]] — extends
- [[Positional Encoding]] — prerequisite-for
- [[Batch Normalization]] — prerequisite-for (layer norm in Transformer is the successor)
- [[Neural Probabilistic Language Model]] — prerequisite-for (word embeddings that Transformers build on)
- [[Pre-Norm vs Post-Norm and Warm-Up]] — extends
- [[LSTM Forget-Gate Bias and Vanishing Gradients]] — related (the recurrent models it replaced)
- [[Encoder Tokens, Position and Attention Scaling]] — extends
- [[Recurrent Memory Transformer (RMT)]] — instance-of
- [[Gist Tokens]] — instance-of
- [[Mixture-of-Transformers]] — extends (per-modality weights with shared attention)
- [[Multi-Head Latent Attention]] — extends (low-rank key-value cache)
- [[RWKV Linear-Time Recurrent Language Model]] — alternative-to (attention-free recurrent formulation)
- [[Cut Cross-Entropy]] — extends (loss layer for large vocabularies)
- [[UL2 Mixture of Denoisers]] — related (a pretraining objective mix on the encoder-decoder transformer)
- [[Conformer Convolution-Augmented Transformer for ASR]] — related
- [[Code Encoder and Encoder-Decoder Pretraining]] — extends
- [[Edge Probing and Layer Localisation in BERT]] — related (layer-wise probing of a Transformer encoder)
- [[Attention Head Roles, Pruning and Faithfulness]] — related (analyses of what attention heads do)
- [[Mixture-of-Experts Routing and Scaling]] — extends
- [[Tensor, Pipeline and Data Parallelism for Large Transformers]] — related
- [[BERT Masked-LM Pretraining and Its Refinements]] — extends (encoder-only pretraining)
- [[T5 Text-to-Text Transfer Transformer]] — extends (encoder-decoder transfer study)
- [[Scaling Laws: Kaplan, Chinchilla and Error Landscapes]] — related
- [[Recurrent-Depth Latent Reasoning (Huginn)]] — extends
- [[Word2vec: CBOW, Skip-gram and Negative Sampling]] — related
- [[LSTM: Constant Error Carousel and Gated Memory Cells]] — related
- [[GPT-3 and Few-Shot In-Context Learning]] — extends
- [[Open Pretrained Model Reports Comparison]] — extends
- [[Qwen and Qwen2.5 Technical Reports]] — related (open-weight decoder family reports)
- [[GPT From Scratch: Block, Weight Tying and Shortcuts]] — instance-of (a from-scratch decoder-only implementation)
- [[Byte Pair Encoding and Sliding-Window Batches]] — related (how text becomes the model's input tokens)
- [[Transformer-XL Segment Recurrence]] — extends
- [[Mamba Selective State Space Model]] — alternative-to
- [[GLU Variants and GELU]] — extends (feed-forward non-linearity variants)
- [[Layer Normalization]] — prerequisite-for
- [[Position Encodings — Relative, Rotary, ALiBi and CAPE]] — extends
- [[Encoder-Decoder Translation Before the Transformer]] — prerequisite-for
- [[Attention for Neural Machine Translation (Bahdanau, Luong, Decomposable)]] — prerequisite-for
- [[Tied Input and Output Embeddings]] — extends
- [[Back-Translation at Scale]] — related
- [[Vision Transformer ViT Patch Tokens and Scaling]] — extends
- [[Hugging Face Transformers Library and Model Hub]] — extends (a library implementing the Transformer behind one tokenizer, model and head API)
