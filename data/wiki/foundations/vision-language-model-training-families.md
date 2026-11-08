---
title: Vision-Language Model Training Families
tags: [foundations, concept]
summary: "Most VLMs are built by connecting a pretrained vision encoder to a pretrained LLM and training only the connector (a linear map, an MLP or a Q-Former), which is cheap but inherits the LLM's hallucinations and biases; resolution, encoder capacity and visual data matter more than how the two are joined."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-03-bordes-2024-introduction-vision-language-modeling.md
---

# Vision-Language Model Training Families

Bordes et al., *An Introduction to Vision-Language Modeling* (arXiv 2405.17247, 2024), is an
introduction rather than a survey, and nearly all its numbers are reported from the cited
papers. Cite the primary paper for any figure.

## What trains

The useful question for any VLM is **which parts are frozen**.

| Model | Frozen | Trained | Reported cost |
|---|---|---|---|
| Frozen | the 7B language model | vision encoder and linear map, from scratch | — |
| MiniGPT-4 | vision encoder and Vicuna | one linear projection, in two rounds | ~10 h on 4 A100s |
| BLIP-2 | both pretrained models | a ~100–200M-parameter Q-Former | — |
| LLaVA 1.5 | not stated | MLP projector, instruction-tuned | ~1 day on 8 A100s |
| Monkey | the encoder | LoRA plus a resampler; tiles the image to raise resolution | — |

Training from scratch is the expensive path: the guide says contrastive models have used
hundreds to thousands of GPUs, though it estimates a well-curated contrastive run need not
exceed 64 (about 10K USD). Reusing a pretrained LLM saves that compute, but **the VLM can
inherit the LLM's hallucinations and biases**, and correcting them can add overhead.

## Parameter-efficient adaptation

When full fine-tuning is too costly the guide groups the options into four: LoRA (and QLoRA,
which trains LoRA weights through a frozen 4-bit model), prompt methods (visual prompt tuning
adds under 1% trainable input parameters), adapters (with weight sharing, VL-adapter rivals full fine-tuning)
and mapping methods. A per-feature linear map makes the sequence as long as the number of
visual features; MAPL fixes that by pooling into a few learnable query tokens.

## What matters most

- **Resolution, encoder capacity and visual pretraining data** move results most; the choice
  of connector matters much less (reported from MM1).
- **Concept frequency:** zero-shot accuracy on a concept follows its frequency in the training
  set, and that frequency can be counted in advance with a recognition model run over the data.
- **Data hygiene:** deduplicate (saves compute, reduces memorisation); model-generated labels
  inherit the labeller's misses; synthetic-caption gains cap out because generated captions
  lack diversity.
- **Data loading** is an overlooked bottleneck; randomly masking image tokens speeds training.

## What the guide does not cover

Nothing on choosing which parts to freeze for a new domain, no
hyperparameters, no memory figures, no minimum dataset sizes and no in-training evaluation.
It is a May 2024 snapshot: the 224×224 norm and the model line-up have dated.

## See Also
- [[VLM Benchmark Shortcuts]] — extends (how these models are evaluated, and how that fails)
- [[Real-Time Multimodal Agents]] — related (VLMs under a latency budget)
- [[Contrastive Self-Supervised Pretraining]] — prerequisite-for (the contrastive objective behind CLIP-style encoders)
- [[Computer Use Visual Grounding]] — related
