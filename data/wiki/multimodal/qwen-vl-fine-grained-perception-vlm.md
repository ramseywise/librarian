---
title: Qwen-VL Fine-Grained Perception VLM
tags: [multimodal, concept]
summary: "Qwen-VL pairs an OpenCLIP ViT-bigG and a 256-query cross-attention adapter with Qwen-7B, trained in three stages on caption, box and OCR data to add grounding and text reading to a vision-language generalist (all numbers self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-bai-2023-qwen-vl.md
---

# Qwen-VL Fine-Grained Perception VLM

Bai et al. (2023) ask how an open LLM can be given detailed visual perception across captioning, VQA, text reading and grounding. They hypothesise that a higher input resolution, an adapter that compresses while keeping position information, and training data with caption-box and OCR content outperform coarse generalists of comparable size.

## Mechanism

- Visual receptor: OpenCLIP ViT-bigG followed by an adapter that is one cross-attention layer with 256 learnable queries, passing features to Qwen-7B. Image, box and ref special tokens form the input-output interface; the grounding data and format follow Kosmos-2 with minor changes.
- In stage 1 the ViT and adapter learn from 1.4B cleaned image-text pairs, using 224px inputs (about 1.5B samples over 50,000 steps at batch size 30720). In stage 2 all parts train on seven tasks at 448px. Stage 3 instruction-tunes the LLM and adapter with 350k dialogues, yielding Qwen-VL-Chat.
- At 448px in the ViT, window attention produced a clearly higher loss than global attention for similar speed (9 versus 10 seconds per iteration), so global attention stayed (self-reported).

## Results (self-reported)

- Zero-shot Flickr30K CIDEr 85.8, above Flamingo-80B (Karpathy test, greedy) (self-reported).
- VQAv2 79.5, OKVQA 58.6, GQA 59.3 with open-ended greedy decoding; TextVQA 63.8 against 50.7 for InstructBLIP (self-reported).
- The 7B model scores 89.36 on RefCOCO val, which tops Shikra-13B (87.83) but trails UNINEXT-H (92.64) (self-reported).
- On MME, Qwen-VL-Chat gets 1487.58 for perception and 360.71 for cognition, and 645.2 (English) and 401.2 (Chinese) on TouchStone, which uses GPT-4 as judge (self-reported).
- After stage 2, MMLU is 50.7, compared with 49.9 for the intermediate Qwen-7B checkpoint it started from, so text ability did not erode (self-reported).

## Limits

- The paper gives no compute, hardware, wall-clock time, seeds or significance tests, and its in-house data (220M pairs plus text corpora) is neither released nor described.
- The ablations on adapter queries and window attention run on a ViT-L/14 and appear only as loss curves, with no benchmark scores.
- Zero-shot VQA improves even though stage 1 contains no VQA data; the paper remarks on this without analysing it.
- Training began from an intermediate Qwen-7B checkpoint rather than the released model.
- Speech, video, scaling and image generation are named as future work.

## See Also
- [[Vision-Language Model Architectures]] — related
- [[Kosmos-2 Grounded Multimodal LLM]] — extends
- [[BLIP-2 Q-Former Bridging]] — alternative-to
- [[CogVLM Visual Expert]] — alternative-to
