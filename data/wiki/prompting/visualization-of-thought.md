---
title: Visualization-of-Thought (VoT)
tags: [prompting, pattern]
summary: A zero-shot prompt asking the model to draw the state after each reasoning step, which helps GPT-4 on text-grid spatial tasks but gives mixed or no gain on small models.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-wu-2024-mind-s-eye-llms.md
---

# Visualization-of-Thought (VoT)

VoT appends the instruction "Visualize the state after each reasoning step" to a zero-shot prompt, so thought and a drawn state (a 2D grid built from emoji or special characters) alternate. Comparisons were zero-shot CoT, a "no visualization" instruction, and GPT-4V on an image of the same grid. Tasks: natural-language navigation (200 generated 3x3 maps), visual navigation (route planning and next-step prediction over 496 maps) and visual tiling (796 questions).

## Reported results (self-reported)

- GPT-4 1106-preview, temperature 0: route planning completing rate 40.77 against 37.02 for CoT and success rate 14.72 against 9.48; next-step prediction 55.28 against 48.61; tiling 63.94 against 54.15; natural-language navigation 59.00 against 54.00 for CoT and 35.50 without visualization. The CoT comparison on navigation had p below 0.16; the paper reports significance against the other baselines.
- Text-grid GPT-4 beat GPT-4V on the image version (tiling 54.15 against 49.62 under CoT); the authors suggest a grid-grounded LLM can outperform a multimodal model here.
- Visualisations are often wrong: state accuracy was 26.48 (visual navigation) and 24.25 (tiling), while decision accuracy given an accurate picture was 65.16 and 77.20.
- VoT lost on a ring-navigation variant that reduces to modular arithmetic: 49.5 against 52.5 for CoT (200 instances, ring of 12).
- Llama3-70B gained on route planning (19.90 to 30.24) and navigation (26.00 to 32.50) but not tiling; GPT-3.5 and Llama3-8B showed mixed or no gain.
- Telling GPT-4 to use ascii-art raised complete tracking to 98.5 (the authors conjecture, untested, that code-comment ascii-art in pretraining explains it).

## Limits

- The authors say the work only scratches the surface, depends on emergent ability in advanced models, and is prompt-sensitive; only 2D grids were tested.
- Absolute performance is low (route-planning success 14.72 with VoT). Tested models were limited to a GPT-4 preview snapshot, its vision variant, GPT-3.5 and Llama3; greedy single runs; no frontier reasoning models. GPT-4 against GPT-4V compares a text grid with an emoji image, so it is not a clean multimodal test.
- The extraction could not read the tracking-rate figure, so those values are omitted. No cost or token comparison. The "mind's eye" framing is an analogy; internals are not probed.

## See Also

- [[Chain-of-Thought Prompting]] — prerequisite-for
- [[Zero-Shot Chain-of-Thought]] — prerequisite-for
- [[MVoT Multimodal Visualization of Thought]] — extends
