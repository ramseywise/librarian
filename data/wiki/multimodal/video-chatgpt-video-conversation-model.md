---
title: Video-ChatGPT Video Conversation Model
tags: [multimodal, concept]
summary: "Video-ChatGPT fine-tunes a LLaVA-style model on 100K video-instruction pairs, training only a linear projection over spatially and temporally average-pooled CLIP frame features, and proposes a GPT-judged video conversation benchmark (all numbers self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-maaz-2024-video-chatgpt.md
  - data/raw/papers/2026-11-08-zhang-2023-video-llama.md
---

# Video-ChatGPT Video Conversation Model

Maaz et al. (ACL 2024) ask whether an LLM can hold detailed conversations about videos and how to evaluate that quantitatively. Their hypothesis is that an adapter over pooled CLIP features, fine-tuned with a high-quality video-instruction set, yields better conversation about time and space than concurrent models.

## Mechanism

- Start from LLaVA (CLIP ViT-L/14 with Vicuna-v1.1 7B). Frame features are average-pooled over space (giving T tokens) and over time (giving N tokens) and concatenated into T+N visual tokens; only a linear projection is updated.
- Data: 100,000 video-instruction pairs, 30% human-assisted and 70% semi-automatic. In a blind test of 50 videos, annotators separated human from semi-automatic pairs only at near chance. Training lasted roughly three hours on eight A100 40GB GPUs for the 7B model over 3 epochs (self-reported).
- It is a sibling of Video-LLaMA, which instead builds a Video Q-Former on BLIP-2; see [[BLIP-2 Q-Former Bridging]].

## Results (self-reported)

- A GPT-3.5 judge scoring 1 to 5 on a test set of ActivityNet-200 videos with human QA pairs puts Video-ChatGPT ahead of Video Chat, LLaMA Adapter and Video-LLaMA (7B variants) for correctness of information. Temporal understanding is its lowest score and ties LLaMA Adapter (self-reported).
- In the ablation, the best average comes from training on the human and semi-automatic data combined (self-reported).
- Switching the judge to the open-source Vicuna-1.5 13B raises Video-ChatGPT's consistency score from 2.37 to 3.09, and the ranking of models is unchanged (self-reported). The extraction leaves the zero-shot MSVD-QA, MSRVTT-QA, TGIF-QA and ActivityNet-QA numbers blank, so none are reported here.

## Limits

- Struggles with subtle temporal relationships in videos over 2 minutes and with small-object details.
- Judge prompts, T, resolution, optimizer and schedule are not given; single run without seeds.
- Swapping the judge shifts absolute scores, and LLaMA Adapter is missing from the open-source judge's comparison.

## See Also
- [[Vision-Language Model Architectures]] — related
- [[LLaVA Visual Instruction Tuning]] — prerequisite-for
- [[BLIP-2 Q-Former Bridging]] — alternative-to
- [[MiniGPT-4 Linear Projection Alignment]] — related
