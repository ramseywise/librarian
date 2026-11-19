---
title: LingBot-World Open-Source World Model
tags: [llm, reasoning-and-planning, concept]
summary: "LingBot-World turns the open 14B Wan2.2 image-to-video diffusion model into an action-controllable world simulator through longer-clip middle-training, action adapters and causal few-step distillation; the real-time variant runs at 16 fps at 480p, with only VBench evidence (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-team-2026-advancing-open-source-world-models.md
---

# LingBot-World Open-Source World Model

The Robbyant Team (preprint, 2026) asks how an open video generator can be turned into a real-time, action-controllable world simulator that remembers for a minute or more, and released openly. Their hypothesis is that three stages give a high-fidelity, high-dynamics, real-time world model: a video prior, long-sequence middle-training conditioned on actions, and causal few-step distillation. Code and weights are released.

## Pipeline

- **Data engine:** captions at three levels (narrative, scene-static, dense temporal) over real footage, game footage and Unreal Engine data.
- **Pre-training:** the starting point is Wan2.2, a 14B image-to-video MoE diffusion model made of two 14B experts (28B in total).
- **Middle-training:** training clips lengthen from 5s to 60s, covering both image-conditioned and video-conditioned generation. The DiT is then frozen and action adapters are finetuned on Plucker camera embeddings plus multi-hot keys fed through AdaLN.
- **Post-training:** a causal block-attention student is built from the high-noise expert and distilled into LingBot-World-Fast using DMD, self-rollout and an adversarial head.
- **Applications:** promptable world events, an action agent built on a Qwen3-VL backbone, and 3D reconstruction.

## Reported results (self-reported)

- On VBench (100 generated videos per model, each over 30 s; which variant was scored is not stated), LingBot-World has the top dynamic degree and imaging quality compared with two rival systems, Yume-1.5 and also HY-World 1.5. Its motion smoothness is 0.9895, just under HY-World's 0.9897 and over Yume's 0.9709; temporal flickering follows the same order.
- LingBot-World-Fast runs at 16 frames per second and 480p with latency below one second on a single GPU node (GPU model unnamed).
- Videos up to ten minutes long are shown, and landmarks reportedly persist after leaving view for 60 s; both claims rest on figures with no metric.

## Limits

- Memory is emergent, with no dedicated module behind it, comes from the context window and is unstable over long simulation; generation length is limited and scenes drift.
- Inference needs enterprise-grade GPUs. The action space is navigation only, with no object-level grounding and one agent.
- The only quantitative evaluation is VBench against two baselines. Genie 3 and Mirage 2 are closed, so there is no benchmark comparison with them (Genie 3 appears only in a feature table). The report gives no training hyperparameters, data sizes or compute.

## See Also
- [[Video Diffusion Models]] — prerequisite-for
- [[DreamerV3 World Model with Fixed Hyperparameters]] — related (a learned world model of another kind)
- [[World Knowledge Model for Agent Planning]] — related
- [[DECKARD LLM-Hypothesized World Model]] — related
