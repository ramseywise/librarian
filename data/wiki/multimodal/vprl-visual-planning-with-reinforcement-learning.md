---
title: VPRL Visual Planning with Reinforcement Learning
tags: [multimodal, concept]
summary: "VPRL plans in pure image sequences: a video-pretrained model generates the next-state image, and a GRPO stage rewards moves that shorten the path to the goal; on three small grid-navigation tasks it averages 80.6 exact match against 53.6 for text SFT (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-06-xu-2025-visual-planning.md
---

# VPRL Visual Planning with Reinforcement Learning

Xu et al. (arXiv 2505.11409, ICLR 2026) ask whether a model can plan with images alone, with no text in the reasoning. The paper positions visual planning as an addition to language reasoning rather than a substitute for it.

## Mechanism

- Backbone: LVM-7B, trained only on images and video, with a VQGAN tokenizer (256 tokens per image). At each step the policy generates the next image; a rule-based dynamics interpreter parses the action from the image change.
- Stage 1 (policy initialisation) trains on random-walk trajectories, with the target sampled from all valid next states. It gives no planning skill (EM 11.1 / 9.6 / 0.5 on the three tasks) but keeps entropy from collapsing; without it, GRPO advantages go to zero.
- Stage 2 is GRPO over G candidate next images. The progress reward gives +1 when a valid move shortens the breadth-first-search distance to the goal, 0 when a valid move does not, and -5 for an invalid move.

## Results (self-reported)

Setup: FrozenLake, Maze and MiniBehavior synthetic grids; evaluation from the initial state only; no seeds or error bars. Baseline is Qwen2.5-VL-7B supervised on the same data.

- Average exact match 80.6 for VPRL against 53.6 for text SFT; per task 91.6, 74.5 and 75.8. Plain supervised visual planning (VPFT) gets 75.4, 59.0 and 33.8.
- Gemini 2.5 Pro (thinking mode, prompted) averages 43.7 EM, Gemini 2.0 Flash with CoT 12.8; Qwen2.5-VL-7B prompted gets 0.7 (direct) and 3.7 (CoT).
- FrozenLake by grid size (250 environments each): Gemini 2.5 Pro falls from 98.0 to 38.8 between 3x3 and 6x6; VPRL from 97.6 to 82.4.
- Text-side GRPO on Qwen2.5-VL-7B (FrozenLake) reaches 54.4 or 60.1 EM against 68.6 for SFT; the authors blame a modality gap. Generated text layouts mismatch the true layout 25.7% (coordinates) or 22.3% (ASCII) of the time.
- Among failed trajectories, the fraction containing an invalid action is lower for VPRL (36.9, 25.1, 29.6 on the three tasks) than for VPFT (60.6, 73.7, 78.3).
- Larger unseen grids stay hard: FrozenLake 7x7 EM 20.4 (VPFT 9.6), Maze 7x7 10.0, MiniBehavior 9x9 0.4.
- Visual planning averages 1082.5 generated tokens, about 3 times Qwen CoT (298.3) and 6 times Gemini 2.0 Flash CoT (171.2).
- Supplying true images in place of the model's own generated ones moves FrozenLake EM only from 91.6 to 92.1; the authors attribute artifacts to the tokenizer.

## Limits

- Authors concede: only LVM-7B was used; image generation adds inference cost; the interpreter that reads the dynamics is rule-based and works pixel by pixel on grayscale grids; failures remain (agents vanishing, teleporting, walking through walls).
- The extraction notes: only small synthetic grids; the reward uses breadth-first search with privileged access to the environment, so it is not learned; no confidence intervals; out-of-distribution EM is at most 20.4; the text-RL comparison was reward-limited in one setup; Gemini was prompted, not trained; MiniBehavior grids were 7x7 and 8x8 with duplicated layouts. The models are from 2025.
- The extraction decoded concatenated table columns from the header and could not view the figures.

## See Also
- [[Visual Instruction Tuning and Tool-Using VLMs]] — related
- [[MVoT Multimodal Visualization of Thought]] — related (also reasons with generated images)
- [[Multimodal Chain-of-Thought]] — related
