---
title: RT-1 Robotics Transformer
tags: [multimodal, concept]
summary: "RT-1 is a real-time Transformer policy for language-instructed robot manipulation: an ImageNet-pretrained EfficientNet conditioned on an instruction embedding through FiLM, TokenLearner compression, and discretised actions, trained by behaviour cloning on about 130k real episodes (all numbers self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-brohan-2023-rt-1.md
---

# RT-1 Robotics Transformer

Brohan et al. (RSS 2023) ask whether a single real-time Transformer policy with high capacity, trained on large and varied real-robot demonstrations, can carry out hundreds of language instructions and cope with new tasks, distractors and backgrounds. They hypothesise that generalisation comes from broad task-agnostic training combined with a high-capacity architecture, and that varied data counts for more than a larger quantity. The model is an embodied policy built from vision-language components: a pretrained image backbone, a sentence encoder and a Transformer.

## Mechanism

- Six past images go through EfficientNet-B3, pretrained on ImageNet, which is conditioned on an instruction embedding from the Universal Sentence Encoder using FiLM layers initialised as identity.
- TokenLearner compresses 81 tokens per image to 8, and 48 tokens enter an 8-layer decoder-only Transformer. It outputs 11 action dimensions discretised to 256 bins plus a mode variable.
- Training is behaviour cloning on successful teleoperated demonstrations: about 130k episodes, over 700 instructions, 13 robots, 17 months. Control runs at 3 Hz.

## Results (self-reported)

- On real mobile manipulators RT-1 succeeds on 97% of the seen instructions (over 200), 76% of unseen ones (24 points ahead of the next-best baseline), 83% of distractor tasks and 59% of background tasks, against baselines retrained on the same data (self-reported).
- Across realistic kitchen scenarios the overall score is 70% for RT-1 and 55% for BC-Z XL (self-reported).
- Dropping a quarter of the tasks while retaining 97% of the data harms generalisation about as much as shrinking the dataset by 49% (self-reported).
- With 518k simulated pick trajectories mixed into the real data, real-world success on objects seen only in simulation climbs from 23% to 87%, and on real objects moves from 92% to 90% (self-reported). Blending 209k Kuka bin-picking episodes with RT-1 data at 2:1 takes bin picking from 22% to 39% and costs 2 points on the classroom evaluation (self-reported).
- On SayCan long-horizon tasks RT-1 executes 67% successfully in each of the two kitchens, while in the second kitchen Gato achieves 0% and BC-Z 13% (self-reported).
- Ablations: continuous Gaussian actions lower seen-task success to 68%; dropping ImageNet pretraining costs 33 points on unseen tasks; conditioning actions autoregressively gave no gain and inference time grew from 15 ms to 36 ms (self-reported).
- Inference gets 2.4x faster from TokenLearner and 1.7x faster from token reuse, inside a sub-100 ms budget for control at 3 Hz (self-reported). The original 1.2B Gato takes 1.9 s per inference on the robot, so the baseline was shrunk to 37M parameters.
- A simulator with 551 tasks gives a rough ranking of real policies and serves for choosing checkpoints; no correlation coefficient is given.

## Limits

- Imitation learning cannot surpass the demonstrators, and generalisation is limited to combinations of seen concepts, not new motions; evaluation kitchens resemble training and the tasks are not very dexterous (authors).
- The paper omits the optimizer, learning rate, batch size, step count, hardware and seeds, and gives neither variance nor per-cell trial counts.
- The authors retrain the baselines on their own data and scale them to similar size, so the comparison is between architectures and not complete systems.
- Inconsistent counts in the paper: 21 unseen tasks in one section and 53 in the appendix; 200+ seen tasks against 744.
- Dataset and weights are not stated as released.

## See Also
- [[Vision-Language Model Architectures]] — related
- [[SayCan Affordance-Grounded Skill Selection]] — prerequisite-for
- [[PaLM-E Embodied Multimodal Language Model]] — related
- [[RoboCat Self-Improving Robot Generalist]] — related
