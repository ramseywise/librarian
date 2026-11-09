---
title: BLIP-2 Q-Former Bridging
tags: [multimodal, concept]
summary: "BLIP-2 bridges a frozen image encoder and a frozen LLM with a 188M-parameter Q-Former of 32 learned queries, pretrained in a representation stage and then a generative stage (all numbers self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-li-2023-blip-2.md
  - data/raw/papers/2026-11-08-zhang-2023-video-llama.md
---

# BLIP-2 Q-Former Bridging

Li et al. (2023) ask whether vision-language pretraining gets cheaper when a small trainable module links an image encoder and an LLM, both kept frozen. They hypothesise that training the Q-Former in two stages, representation learning and then generative learning, narrows the gap between modalities more than an image-to-text generation loss used alone.

## Mechanism

- The **Q-Former** is a lightweight transformer with learnable query vectors that act as an information bottleneck between the frozen encoder and the frozen LLM. It has 188M parameters, is initialised from BERT-base with random cross-attention, and uses 32 queries.
- Stage 1 attaches it to a frozen ViT and optimises three objectives, ITC, ITG and ITM. In stage 2 a single fully connected layer turns its outputs into soft prompts for a frozen OPT or FlanT5 model.
- Pretraining uses 129M images with CapFilt synthetic captions.

## Results (self-reported)

- Zero-shot VQAv2 test-dev with ViT-g and FlanT5-XXL (12.1B parameters in total) beats Flamingo-80B by 8.7 points while training 54 times fewer parameters than Flamingo's 10.2B (self-reported).
- With OPT-6.7B, zero-shot VQAv2 test-dev is 52.6, below Flamingo-80B at 56.3 (self-reported). On OK-VQA the best FlanT5-XXL variant scores 44.7 against 50.6; the authors guess Chinchilla 70B holds more knowledge than FlanT5-XXL 11B (self-reported).
- Skipping stage 1 lowers zero-shot VQA substantially and OPT then suffers catastrophic forgetting (numbers only in a figure, ViT-g, 80k iterations) (self-reported).
- In COCO retrieval fine-tuning, including ITG alongside ITC and ITM raises text-to-image R@1, going from 67.2 to 68.3 (self-reported).
- On a single 16-GPU A100 (40GB) machine the largest model finishes stage 1 in under six days and stage 2 in under three (self-reported).
- A stronger image encoder or a larger LLM both improve zero-shot VQA, and FlanT5 beats OPT (self-reported).

## Downstream use

Video-LLaMA runs each frame through BLIP-2's frozen ViT-G/14 and Q-Former, then adds a Video Q-Former that carries frame position embeddings, plus a parallel Audio Q-Former over a frozen ImageBind encoder. Linear layers on both branches produce soft prompts for a frozen Vicuna or LLaMA. The vision branch trains on WebVid-2M and CC595k captions and is then instruction-tuned. The audio branch trains only on visual-text data and relies on ImageBind's shared embedding space to accept real audio at inference. The paper shows only example conversations: no benchmark, baseline comparison or ablation.

## Limits

- No gain from in-context examples, which the authors attribute to pretraining on a single image-text pair per sample.
- Answers can be wrong through inaccurate knowledge, a faulty reasoning path or out-of-date information, and the model inherits LLM risks such as bias and privacy leakage.
- The zero-shot gains are single runs, with no seeds.
- The trainable-parameter figure differs by table: 188M in Table 1, 103-108M in Table 2 and 1.1-1.2B in the fine-tuning tables, with no explanation.
- Video-LLaMA (per its extraction): early-stage prototype, weak on long videos, inherits LLM hallucination, no quantitative evaluation, most hyperparameters and dataset sizes unstated, and its audio branch is never shown real audio paired with text.

## See Also
- [[Vision-Language Model Architectures]] — related
- [[Frozen Visual Prefix Few-Shot Learning]] — related
- [[Flamingo Gated Cross-Attention VLM]] — alternative-to
- [[MiniGPT-4 Linear Projection Alignment]] — extends
- [[Vision-Language Model Training Families]] — related
- [[BLIP Bootstrapped Captioning and Filtering]] — prerequisite-for
- [[ALBEF Align Before Fuse]] — prerequisite-for
- [[InstructBLIP Instruction-Aware Query Transformer]] — extends
- [[LENS Frozen LLM with Vision Modules]] — related
