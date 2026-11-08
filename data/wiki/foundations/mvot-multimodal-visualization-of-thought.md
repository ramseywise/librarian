---
title: MVoT Multimodal Visualization of Thought
tags: [foundations, pattern]
summary: "MVoT interleaves generated images with text steps during reasoning (Anole-7B with a token discrepancy loss), scoring 92.95, 95.14 and 85.60 on Maze, MiniBehavior and FrozenLake (self-reported), but plain CoT does better on the two easier tasks."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-li-2025-imagine-while-reasoning-space.md
---

# MVoT Multimodal Visualization of Thought

MVoT (Li et al., 2025) lets a multimodal model draw its intermediate state. After each text step the model generates an image of the new spatial state (grid position, object layout) and conditions the next step on it. The base is Anole-7B, fine-tuned with a token discrepancy loss intended to keep generated image tokens close to the right visual tokens.

## Reported results

- Maze 92.95, MiniBehavior 95.14 and FrozenLake 85.60 (self-reported; spatial-reasoning tasks).
- Plain CoT scored higher on two of the easier tasks, so visual steps are not uniformly better (self-reported).

## Limits

- Three small grid-world tasks and one 7B base model.
- The extraction notes inconsistent MiniBehavior grid sizes between sections.
- Image generation per step adds latency and tokens; cost is not the headline.

## See Also
- [[Chain of Thought]] — prerequisite-for
- [[Prompting Reasoning Models]] — related
- [[Tree of Thoughts]] — related (another way to extend the reasoning trace beyond plain text)
