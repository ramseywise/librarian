---
title: Action Chunking
tags: [foundations, concept]
summary: "A vision-language-action policy infers at 1–10 Hz while robot control runs at 50–1000 Hz, so it emits 25–50 actions per inference and replays them while the next chunk computes — smoother motion bought with blindness to sudden change; plus the discrete-token vs. flow-matching action representations and the planner + VLA split."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/generative-ai--07-agentic-applications--real-time-multimodal-agents.md
---

# Action Chunking

Robot control for household tasks is limited by algorithms more than hardware: a low-cost
dual-arm robot under VR teleoperation (100–200 ms latency) can already do a wide range of
chores; touch sensing and dexterous hands remain real hardware gaps for force-sensitive
work.

## Two layers

- **Long-horizon planning (slow)** answers *what*: "clean the kitchen" → clear the
  counter, load the dishwasher, wipe. Embodied-reasoning models drive this at 0.5–1 Hz with
  a few motion tools; spatial reasoning is strong but fragile over many steps.
- **Vision-language-action (VLA) control (fast)** answers *how*. A VLA is a VLM with action
  output, trained mainly by behaviour cloning. RL-trained VLAs do well on single tasks but
  generalise poorly (one model per task in the published RL run; see
  [[Post-Training for Agents]]).

This is a planning/control split, a different cut from the thinking/speaking split in
[[Fast-Slow Thinking Architecture]].

## Action representations

- **Discrete tokens.** Actions are binned into tokens and decoded like text (the RT-2 /
  OpenVLA line; the open version is a Llama-2 backbone plus a vision encoder, pretrained on a
  multi-robot dataset, then fine-tuned per platform).
- **Continuous trajectories.** Flow matching denoises a smooth trajectory (the π₀ line),
  which suits dexterous work. "Choosing from a menu vs. sketching the curve."

## The chunking mechanism

Control loops run at 50–1000 Hz; VLA inference runs at 1–10 Hz, and an early open VLA at
6 Hz moved jerkily. Action chunking (ACT, 2023) generates **25–50 actions per inference**
(0.5–1 s at 50 Hz) and replays them while the next chunk computes, like video buffering.

The trade-off: longer chunks are smoother but **blind to sudden changes**. Mitigations are
shorter chunks near contact, re-planning on a visual-anomaly trigger, and blending
overlapping chunks. The two-layer design relocates the real-time tension; it does not remove
it.

## Sim2Real

Domain randomisation plus two steps that cannot be skipped: **calibrate the randomisation
range from measured real data** (friction, motor delay — too narrow misses reality, too
wide gives a policy that handles everything and masters nothing), and **align visuals**
(match camera pose, splice in real backgrounds). A published pipeline trained RGB-only PPO to
over 90% in simulation and grasped zero-shot on a real arm, with success dropping sharply on
out-of-distribution objects.

## See Also
- [[Real-Time Multimodal Agents]] — instance-of (the robotics setting)
- [[Fast-Slow Thinking Architecture]] — alternative-to (a different fast/slow split)
- [[Post-Training for Agents]] — prerequisite-for (behaviour cloning and RL for robot policies)
