---
title: Vision-Language Model Architectures
tags: [multimodal, comparison]
summary: "Family hub for how vision-language models join an image encoder to a language model: frozen-component bridges, deep fusion, detector-region encoders, jointly scaled encoder-decoders, early-fusion token models, grounding and fine-grained models, video and embodied extensions, with the data and backbone pieces they rely on."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-alayrac-2022-flamingo.md
  - data/raw/papers/2026-11-07-bai-2023-qwen-vl.md
  - data/raw/papers/2026-11-07-chen-2020-uniter.md
  - data/raw/papers/2026-11-07-driess-2023-palm-e.md
  - data/raw/papers/2026-11-07-gao-2023-llama-adapter-v2.md
  - data/raw/papers/2026-11-07-gong-2023-multimodal-gpt.md
  - data/raw/papers/2026-11-07-houlsby-2019-parameter-efficient-transfer-learning-nlp.md
  - data/raw/papers/2026-11-07-li-2023-blip-2.md
  - data/raw/papers/2026-11-07-maaz-2024-video-chatgpt.md
  - data/raw/papers/2026-11-07-peng-2023-kosmos-2.md
  - data/raw/papers/2026-11-07-rebuffi-2017-learning-multiple-visual-domains-residual.md
  - data/raw/papers/2026-11-07-su-2019-vl-bert.md
  - data/raw/papers/2026-11-07-team-2024-chameleon.md
  - data/raw/papers/2026-11-07-tsimpoukelli-2021-multimodal-few-shot-learning-frozen.md
  - data/raw/papers/2026-11-07-wang-2022-git.md
  - data/raw/papers/2026-11-07-zhu-2023-minigpt-4.md
  - data/raw/papers/2026-11-08-chen-2022-pali.md
  - data/raw/papers/2026-11-08-chen-2023-pali-x.md
  - data/raw/papers/2026-11-08-chen-2024-intern-vl.md
  - data/raw/papers/2026-11-08-chen-2024-sharegpt4v.md
  - data/raw/papers/2026-11-08-laurencon-2023-obelics.md
  - data/raw/papers/2026-11-08-multimodal-deep-learning-ch03-multimodal-architectures.md
  - data/raw/papers/2026-11-08-multimodal-deep-learning-ch04-further-topics.md
  - data/raw/papers/2026-11-08-riquelme-2021-scaling-vision-sparse-mixture-experts.md
  - data/raw/papers/2026-11-08-schuhmann-2022-laion-5b.md
  - data/raw/papers/2026-11-08-simeoni-2025-dinov3.md
  - data/raw/papers/2026-11-08-sun-2024-generative-multimodal-models-context-learners.md
  - data/raw/papers/2026-11-08-wang-2024-cogvlm.md
  - data/raw/papers/2026-11-08-zhang-2023-video-llama.md
  - data/raw/papers/2026-11-08-zhou-2020-unified-vision-language-pre-training.md
  - data/raw/papers/2026-11-08-brohan-2023-rt-1.md
---

# Vision-Language Model Architectures

Every model in this family answers one design question: how do image features reach a language model, and which parts train. The per-method pages hold the mechanisms and numbers; this page compares them. Training-recipe stages (what is frozen when) are covered in [[Vision-Language Model Training Families]]; this page is about the connection and the components.

## Families

| Family | Connection | What trains | Pages |
|---|---|---|---|
| Frozen-component bridges | A small module maps frozen image features into a frozen LM | Only the bridge | Frozen (2-token visual prefix), Flamingo (Perceiver Resampler plus tanh-gated cross-attention), BLIP-2 (32-query Q-Former), MiniGPT-4 (one linear layer) |
| Adapter-style tuning | Early-fused visual tokens or LoRA on a frozen LM | About 14M parameters, or LoRA weights | LLaMA-Adapter V2 (bias tuning), MultiModal-GPT (LoRA on OpenFlamingo) |
| Deep fusion | Image tokens get their own weights inside every LM layer | Visual expert (QKV and FFN) | CogVLM |
| Detector-region single stream | Region features and words share one BERT-style Transformer | Whole model, masked prediction | UNITER, VL-BERT, Unified VLP |
| Image encoder plus text decoder | One language-modelling loss on generated text | Encoder and decoder | GIT |
| Jointly scaled encoder-decoder | ViT patch features feed an mT5 or UL2 encoder-decoder | Vision and language together | PaLI, PaLI-X |
| Early-fusion tokens | Images quantised to discrete tokens in one vocabulary | Everything, from scratch | Chameleon |
| Continuous-embedding generative | Image embeddings predicted by regression | Whole model plus a separate pixel decoder | Emu, Emu2 |
| Grounding and fine-grained | Box coordinates as location tokens, higher resolution, OCR data | Staged | Kosmos-2 (GRIT), Qwen-VL |
| Scaled encoder plus middleware | A 5.9B ViT bridged by an LLM-initialised middleware | Staged, contrastive then generative | InternVL |
| Video | Frame features pooled or run through a Video Q-Former | Linear projection or Q-Former | Video-ChatGPT, Video-LLaMA (in the BLIP-2 page) |
| Embodied | Sensor inputs enter as embeddings, or a policy uses a pretrained vision backbone | Policy and encoders | PaLM-E, RT-1 |

## Design axes the pages show

- **Bridge versus fusion depth.** The bridge family keeps the LLM untouched and trains little: BLIP-2 reports far fewer trainable parameters than Flamingo (self-reported), MiniGPT-4 trains one layer, and CogVLM argues a per-layer visual expert beats tuning only an adapter at matched trainable size (self-reported). The textbook chapter classes fusion as early, joint or late; see [[Multimodal Fusion and Multipurpose Models]].
- **Forgetting.** CogVLM reports MMLU falling to 24.9 when the language part is trained directly on LAION; PaLM-E reports an unfrozen 84B model losing much of its language ability, with the loss shrinking at 562B (all self-reported). Qwen-VL reports MMLU holding after multimodal training (self-reported).
- **Where the gain comes from.** Several pages credit data over architecture: MiniGPT-4's 3,500 detailed descriptions fix unnatural output, and ShareGPT4V swaps in long captions while keeping the recipe (all self-reported). See [[ShareGPT4V Detailed Caption Data]], [[OBELICS Interleaved Web Document Dataset]] and [[LAION-5B Open CLIP-Filtered Image-Text Dataset]].
- **The vision backbone.** InternVL scales the encoder and reports gains even with plain MLP glue, so part of its advantage is the encoder alone (self-reported). Backbones appear in [[DINOv3 Gram Anchoring Self-Supervised Backbone]] and [[V-MoE Sparse Mixture of Experts for Vision]].
- **Output side.** Chameleon and Emu generate images; Kosmos-2 and Qwen-VL generate box tokens; most other models only emit text.

## What the evidence does not settle

- Numbers across pages come from different benchmarks, judges and training data, so no ranking is given here. Several papers report single runs without seeds, and many competitor comparisons are not like for like (starred benchmarks saw their training annotations).
- The claim that GPT-4-style abilities come from a stronger LLM is untested in the MiniGPT-4 paper.

## Limits

- This hub covers only the group of papers compiled with it. Existing pages for LLaVA, InstructBLIP, ViLBERT and others are linked below but not re-summarised.

## See Also
- [[Vision-Language Model Training Families]] — related
- [[Frozen Visual Prefix Few-Shot Learning]] — instance-of
- [[Flamingo Gated Cross-Attention VLM]] — instance-of
- [[BLIP-2 Q-Former Bridging]] — instance-of
- [[MiniGPT-4 Linear Projection Alignment]] — instance-of
- [[LLaMA-Adapter V2 and MultiModal-GPT Parameter-Efficient Visual Tuning]] — instance-of
- [[CogVLM Visual Expert]] — instance-of
- [[Region-Based Single-Stream VLP (UNITER, VL-BERT, Unified VLP)]] — instance-of
- [[GIT Generative Image-to-Text Transformer]] — instance-of
- [[PaLI and PaLI-X Jointly Scaled VLMs]] — instance-of
- [[Chameleon Mixed-Modal Early Fusion]] — instance-of
- [[Kosmos-2 Grounded Multimodal LLM]] — instance-of
- [[Qwen-VL Fine-Grained Perception VLM]] — instance-of
- [[InternVL Scaled Vision Encoder with QLLaMA]] — instance-of
- [[Video-ChatGPT Video Conversation Model]] — instance-of
- [[PaLM-E Embodied Multimodal Language Model]] — instance-of
- [[RT-1 Robotics Transformer]] — instance-of
- [[Emu Generative Pretraining in Multimodality]] — instance-of
- [[LLaVA Visual Instruction Tuning]] — instance-of
- [[Multimodal Architectures Survey (Image-Text)]] — related
- [[Multimodal Fusion and Multipurpose Models]] — related
