---
title: ShareGPT4V Detailed Caption Data
tags: [multimodal, concept]
summary: "ShareGPT4V replaces short captions with long GPT4-Vision captions (100K directly, 1.2M from a distilled captioner) in both pretraining and SFT of a LLaVA-1.5-style 7B model, and reports gains from caption quality alone (all numbers self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-chen-2024-sharegpt4v.md
---

# ShareGPT4V Detailed Caption Data

Chen et al. (2024) ask whether replacing short, low-quality captions with long, detailed GPT4-Vision captions improves modality alignment, in both pretraining and supervised fine-tuning (SFT). Their hypothesis is that existing captions impede vision-language alignment.

## Mechanism

- GPT4-Vision captioned about 100K images using a base prompt together with a prompt specific to each data source. Those captions fine-tune **Share-Captioner**, a general caption model that then captioned 1.2M further images (**ShareGPT4V-PT**), taking around 44 A100 GPU days. GPT4-Vision captions average 942 characters against 52 for COCO and 54 for BLIP-LCS.
- A 7B model in the LLaVA-1.5 style is pretrained on the 1.2M captions with the second half of the vision encoder unfrozen, then fine-tuned (SFT) on the 665K LLaVA-1.5 mixture, in which 23K GPT4-Vision captions replace its 23K detailed-description items.

## Results (self-reported)

- Replacing just the detailed-description captions in SFT lifts LLaVA-7B by 222.8 on MME perception and by 2.7 on MMBench; the replacement is 14.5% of LLaVA's SFT data and 3.5% of LLaVA-1.5's (self-reported).
- ShareGPT4V-7B reaches 1943.8 on MME (perception 1567.4, cognition 376.4), which is 95.6 more than Qwen-VL-Chat-7B, itself trained on 1.4 billion samples; it also gets 68.8% on MMBench and 69.7% on SEED image (self-reported).
- Ablation against LLaVA-1.5-7B: using the data in SFT only adds 31.4 MME perception points and in pretraining only adds 46.5; both is best (self-reported).
- Same images, different captions: using ShareGPT4V-PT captions in place of BLIP captions for the 558K pretraining images takes MMBench from 66.2 up to 68.3 while SEED-I climbs from 66.9 to 68.9, while BLIP captions give only minor gains over baseline (self-reported).
- Unfreezing the second half of the vision encoder is worth 52.2 MME perception points over keeping it frozen; gains from caption scale saturate beyond about 1000K captions (read from a plot) (self-reported).

## Limits

- The evidence comes from the LLaVA-1.5 recipe at 7B, with a 13B baseline; the authors say a new architecture is not the goal.
- Captions come from a proprietary teacher; the paper reports no hallucination or factuality audit, the only check is a preference test on 100 samples with 10 volunteers, who judged Share-Captioner on par with the teacher.
- Runs are single and unseeded, so gains of about a point cannot be told apart from noise; some competitor numbers are re-implemented.
- The SFT swap mixes a quality change with a distribution change. Training details are not stated, and a dialog figure shows two characters confidently misidentified, which the paper does not discuss.

## See Also
- [[Vision-Language Model Architectures]] — related
- [[LLaVA Visual Instruction Tuning]] — prerequisite-for
- [[MiniGPT-4 Linear Projection Alignment]] — related (also repairs short captions with detailed ones)
- [[LAION-5B Open CLIP-Filtered Image-Text Dataset]] — related
