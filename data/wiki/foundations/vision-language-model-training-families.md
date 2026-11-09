---
title: Vision-Language Model Training Families
tags: [foundations, concept]
summary: "Most VLMs are built by connecting a pretrained vision encoder to a pretrained LLM and training only the connector (a linear map, an MLP or a Q-Former), which is cheap but inherits the LLM's hallucinations and biases; resolution, encoder capacity and visual data matter more than how the two are joined."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-03-bordes-2024-introduction-vision-language-modeling.md
  - data/raw/papers/2026-11-06-han-2023-imagebind-llm.md
  - data/raw/papers/2026-11-06-liu-2023-prismer.md
  - data/raw/papers/2026-11-06-piergiovanni-2023-mirasol3b.md
  - data/raw/papers/2026-11-06-lian-2025-describe-anything.md
  - data/raw/papers/2026-11-06-nassar-2025-smoldocling.md
  - data/raw/papers/2026-11-06-liu-2023-language-quantized-autoencoders.md
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

## Designs from individual papers

Setups differ per paper; each number is the authors' own (self-reported).

| Model | Design | Reported result |
|---|---|---|
| ImageBind-LLM (arXiv 2309.03905) | Trains on image-text pairs only. A frozen ImageBind image encoder feeds a bind network (a linear projection plus 3 residual blocks); the image feature is injected into each word token across all 32 LLaMA layers behind a gate that starts at zero. For audio, video and 3D input at inference, each modality's own encoder is used, with a training-free cache that fetches the closest image features. | One visual token enters the LLM; OCR is weak (IIIT5K 13.9 against 80.17 for BLIP2); MME perception 775.77. |
| Prismer (arXiv 2303.02506, TMLR 2024) | Frozen CLIP ViT and frozen RoBERTa plus six frozen expert models (depth, normal, edge, segmentation, object detection, OCR); about 20% of parameters train. The experts are independent black-box models, not mixture-of-experts layers. | Base model COCO CIDEr 135.1, VQAv2 76.8 after 12.7M pairs; experts add about 6 NoCaps out-of-domain CIDEr and 1 VQAv2 (Large). Training Large took 8 days on 32 V100. |
| Mirasol3B (arXiv 2311.05698, CVPR 2024) | About 3B parameters. An autoregressive audio-video model over time chunks, each compressed to 32 tokens by a Combiner (with a Token Turing Machine variant), joined by cross-attention to a text decoder. | MSRVTT-QA 50.42 against 47.4 for Flamingo 80B; NExT-QA 68.2 at 128 frames, 72.0 at 512, 73.2 at 512 with the Token Turing Machine Combiner (about 30% less memory and 18% less runtime). |
| Describe Anything, DAM-3B (arXiv 2504.16072, ICCV 2025) | Takes a focal prompt: the full image with a mask, plus a crop expanded by alpha=3 with its mask, via a zero-initialised mask patch embedding and gated cross-attention. Data come from a two-stage pipeline: human mask-and-keyword pairs expanded to detailed captions, then semi-supervised self-labelling on SA-1B. | On the authors' own DLC-Bench (892 questions, Objects365 v2 validation, Llama 3.1 8B text-only judge): 67.3% against 61.5 for GPT-4o and 62.5 for o1. Ablation: full image only 48.7, focal crop only 65.4, both with cross-attention 67.3. |
| SmolDocling (arXiv 2503.11576) | 256M parameters: a SigLIP base patch-16/512 encoder (93M) with SmolLM2 135M, pixel shuffle to 64 tokens per patch. Outputs DocTags, an XML-like markup with nested location tags and OTSL tables. Three training stages: frozen encoder, unfrozen, fine-tune. | Full-page text edit distance 0.48 against 0.56 for Qwen2.5-VL 7B on DocLayNet in the authors' harness; 0.35 s per page and 0.489 GB VRAM; layout mAP 0.231 against 0.133 (human 0.82). |
| LQAE (arXiv 2302.00902) | Maps ViT patch embeddings to their nearest entry in the frozen RoBERTa word-embedding table, so an image becomes 256 text tokens and no image-text pairs are needed. A high mask ratio of about 50% is crucial. | 2-way miniImageNet with text-davinci-003 53.97 against 51.3 for Frozen (chance 50%); 5-way 29.04 against 26.26. Swapping in VQ-VAE tokens drops to near zero. |

## Limits

- ImageBind-LLM has no ablations, only image-only quantitative evaluation, a confounded PandaGPT comparison (LLaMA against Vicuna) and unstated k and alpha. Internal inconsistency noted by the extraction: the abstract says 3M cached features and the body says 1M.
- Prismer needs all six experts at inference; its ablations use a reduced setup (3M pairs, 224px, BASE, single runs, differences of tenths of a point). The extraction notes the per-expert reading is unverified because the table's colour coding was lost.
- Mirasol3B comparisons are not controlled; ablations use a 1.15B model with half the steps; the streaming claim is untested; subtitle or ASR text is left to future work. The extraction notes some reference author names were inferred and that a "0.75%" masking ratio is probably a typo.
- Describe Anything: the benchmark and data pipeline come from the same authors, the benchmark questions are seeded by vision-language models including GPT-4o (also a baseline), and it needs a mask as input. Internal inconsistency noted by the extraction: stage-1 region counts are 603k and 202k in one place and 684k and 226k in a table caption.
- SmolDocling shows failure modes (missing tags, endless repetition), has no ablation of staging or of DocTags against Markdown, and needed a near-full pretraining run (64 A100 for 4 epochs). Internal inconsistencies noted by the extraction: the SynthDocNet size is 250K in the text but 375K in Table 1, and the code-language count is 56 on one page but 57 on another.
- LQAE is, in the authors' words, far from state-of-the-art; classification only; it mixes language-model sizes (GPT-3.5 against about 6B) and uses ImageNet-derived train and test data. Internal inconsistencies noted by the extraction: the Table 2 caption wording on class labels and chance level is garbled, and a Table 3 row carries a Davinci label that does not fit the rest.

## See Also
- [[VLM Benchmark Shortcuts]] — extends (how these models are evaluated, and how that fails)
- [[Real-Time Multimodal Agents]] — related (VLMs under a latency budget)
- [[Contrastive Self-Supervised Pretraining]] — prerequisite-for (the contrastive objective behind CLIP-style encoders)
- [[Computer Use Visual Grounding]] — related
- [[MoE-LLaVA and MoE-Tuning]] — instance-of (a sparse mixture-of-experts vision-language model)
- [[Mixture-of-Transformers]] — instance-of (per-modality weights with global attention)
- [[DoRA Weight-Decomposed Low-Rank Adaptation]] — related (a LoRA variant)
- [[Visual Instruction Tuning and Tool-Using VLMs]] — extends (compares LLaVA, Emu, SPAE and tool-composition systems)
- [[LLaVA Visual Instruction Tuning]] — instance-of (linear and MLP projector instruction tuning)
- [[Emu Generative Pretraining in Multimodality]] — instance-of (regressed visual embeddings with a diffusion decoder)
- [[SPAE Semantic Pyramid AutoEncoder]] — instance-of (frozen LLM reads images as vocabulary words)
- [[MedGemma 1.5 Medical Vision-Language Model]] — instance-of (domain adaptation of a general VLM)
- [[Diffusion and GAN Image Generation]] — related
- [[Contrastive and Masked Vision-Language Pretraining]] — instance-of (per-method pages and family comparison)
- [[CLIP Contrastive Language-Image Pretraining]] — instance-of
- [[ALIGN Noisy Alt-Text Dual Encoder]] — instance-of
- [[SigLIP Sigmoid Loss for Language-Image Pretraining]] — instance-of
- [[Florence UniCL Vision Foundation Model]] — instance-of
- [[ALBEF Align Before Fuse]] — instance-of
- [[BLIP Bootstrapped Captioning and Filtering]] — instance-of
- [[SimVLM PrefixLM Pretraining]] — instance-of
- [[ViLT Patch Projection Vision-Language Transformer]] — instance-of
- [[ViLBERT Co-Attention Two-Stream Pretraining]] — instance-of
- [[ImageBind Emergent Cross-Modal Alignment]] — instance-of
- [[VIOLET Masked Visual-Token Modeling]] — instance-of
- [[MERLOT Multimodal Script Knowledge]] — instance-of
- [[InstructBLIP Instruction-Aware Query Transformer]] — instance-of
- [[MultiInstruct Multimodal Instruction Benchmark]] — instance-of
- [[LENS Frozen LLM with Vision Modules]] — instance-of
- [[DreamLLM Interleaved Comprehension and Creation]] — instance-of
- [[Segment Anything SAM and SA-1B]] — related (segmentation foundation model)
- [[Swin Transformer Shifted Windows]] — related (vision backbone)
- [[DALL-E and Parti Autoregressive Text-to-Image]] — related (token-based image generation)
- [[Speech and Audio Generation and Recognition]] — related (audio counterpart)
- [[Donut OCR-Free Document Understanding]] — related
- [[MERLOT Reserve Audio-Video-Text Pretraining]] — related
- [[Depth Anything Monocular Depth from Unlabeled Data]] — related
- [[Visual Question Answering Benchmarks]] — related
- [[LXMERT]] — related
- [[RA-CM3 Retrieval-Augmented Multimodal Modeling]] — related
- [[Vision-Language Model Architectures]] — related
- [[Flamingo Gated Cross-Attention VLM]] — instance-of
- [[Frozen Visual Prefix Few-Shot Learning]] — instance-of
- [[GIT Generative Image-to-Text Transformer]] — related
- [[OBELICS Interleaved Web Document Dataset]] — related
- [[Multimodal Fusion and Multipurpose Models]] — related
- [[CogVLM Visual Expert]] — related
- [[PaLI and PaLI-X Jointly Scaled VLMs]] — related
- [[Chameleon Mixed-Modal Early Fusion]] — related
