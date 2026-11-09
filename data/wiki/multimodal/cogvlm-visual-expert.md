---
title: CogVLM Visual Expert
tags: [multimodal, concept]
summary: "CogVLM keeps a frozen Vicuna-7B and adds, in every layer, a trainable visual expert (separate QKV and FFN for image tokens), arguing deep fusion avoids both shallow-alignment weakness and forgetting from training the LLM directly (all numbers self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-wang-2024-cogvlm.md
---

# CogVLM Visual Expert

Wang et al. (2024) ask whether deep fusion, instead of shallow alignment, lets a pretrained LLM gain strong visual understanding while keeping its NLP ability. Shallow alignment means mapping image features into a frozen LM's input embedding space through a Q-Former or linear layer.

## Mechanism

- Frozen Vicuna-1.5-7B, frozen EVA2-CLIP-E ViT and a two-layer SwiGLU MLP adapter. In every layer a **visual expert** adds its own QKV matrix and FFN applied only to image tokens, initialised from the LLM.
- The expert doubles parameters but keeps FLOPs the same, and the authors claim text-only input reproduces the original LLM behaviour.
- Pretraining runs in two stages over about 1.5B image-text pairs and 40M grounding images; SFT then produces the CogVLM-Chat and CogVLM-Grounding variants.

## Results (self-reported)

- MMLU falls to 24.9 after 2500 steps of training the language part directly on LAION, which the paper reads as catastrophic forgetting. It also cites a 87.3% NLG drop for PaLM-E 8B.
- Ablation on VQAv2 (6,000 iterations, batch 8,192): tuning only the MLP adapter (140M trainable) is clearly worse than the expert; tuning all LLM parameters plus adapter (6.9B) gets 78.9 against 80.0 for the expert (6.6B trainable). An expert at every 4th layer is only slightly worse; random initialisation is worse than LLM initialisation (self-reported).
- Swapping the 4.4B encoder for a 300M one lowers TextVQA by 2.5 points; letting visual tokens attend bidirectionally is slightly worse, and an added image SSL loss brings no gain (self-reported).
- Zero-shot NoCaps val OOD CIDEr 132.6 against 130.6 for GIT2 with 1.5B against 12.9B pretraining pairs; zero-shot Flickr CIDEr is 94.9, a margin of 9.1 over Qwen-VL (self-reported).
- CogVLM-Chat scores 82.3 on VQAv2, 70.4 on TextVQA and 91.2 on ScienceQA; its POPE is 87.9, MMBench 77.6, SEED 72.5, MM-Vet 51.1 and MMMU 41.1. CogVLM-Grounding RefCOCO val 92.76 against 92.64 for UNINEXT-H, and best on 5 of 9 grounding splits (self-reported).
- Pretraining compute is 230.1 PFLOPS-days against 453 for PaLI-17B (self-reported).

## Limits

- No text-only benchmark after training backs the no-NLP-loss claim; only the direct-training baseline is shown.
- Many chat-table VQA numbers come from datasets used in SFT, so those results are not zero-shot.
- The paper gives no seeds, variance, hardware or wall-clock figures; SFT mixture sizes are not given; ablations are 6,000 iterations at matched trainable size in one setting.
- MathVista is 35.2 in the text and 34.5 in the table.

## See Also
- [[Vision-Language Model Architectures]] — related
- [[BLIP-2 Q-Former Bridging]] — alternative-to
- [[MiniGPT-4 Linear Projection Alignment]] — alternative-to
- [[Qwen-VL Fine-Grained Perception VLM]] — alternative-to
- [[PaLM-E Embodied Multimodal Language Model]] — related
