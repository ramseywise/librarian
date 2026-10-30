---
title: Computer Use Visual Grounding
tags: [foundations, llm, concept]
summary: "How a GUI agent turns a screenshot into a click — Set-of-Mark labelling, structured DOM/accessibility indexing (prefer it whenever structure exists) and direct coordinate prediction with aspect-ratio-matched rescaling — plus the observation-interface fix for dynamic screens and why per-step efficiency is now the bottleneck."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/generative-ai--07-agentic-applications--real-time-multimodal-agents.md
---

# Computer Use Visual Grounding

A computer-use agent runs a perceive–think–act loop: screenshot, a multimodal model
outputs a thought and an action, execute, wait, screenshot again. Each cycle takes 2–5 s.
The design axes are the action space, visual grounding and the model.

**Action space.** A reference tool set has three tools: a `computer` tool (mouse moves,
clicks, drags, scroll with modifiers, typing, key presses, screenshot, cursor position,
wait), a persistent `bash` session (completion detected with a sentinel string, with a
timeout), and a string-replace file editor with view/create/insert/undo, which is safer
than overwriting whole files (see [[Tool Design as Harness Surface]]).

## Three grounding routes

| Route | How | Use when |
|---|---|---|
| **Set-of-Mark** | A segmentation model numbers screen regions; the model answers "click [7]" | No structure available: native desktop apps, games |
| **Structured element indexing** | Read the DOM or accessibility tree, number the interactive elements, draw boxes and send an element list | **Whenever structure exists.** Most accurate and stable; does not save tokens |
| **Coordinate prediction** | The model outputs (x, y) directly | Canvas or WebGL, models trained for GUI grounding |

Labelling turns fill-in-the-blank into multiple choice. All three still struggle with small
elements and dense screens, so keep both an indexed path and a vision fallback and pick the
route per model.

**Resolution matters for coordinates.** A model trained at a few fixed resolutions should
get a screenshot scaled to the trained resolution with the **closest aspect ratio**, and its
coordinates mapped back. A 2560×1440 screen maps to 1366×768, so (683, 384) maps back to
(1280, 720). Squashing 16:9 into 4:3 shifts every prediction.

## Dynamic screens: the observation interface

Screenshot loops assume a static screen and miss video, toasts and meeting audio. An
observation-interface middleware (no retraining) adds keyframe capture gated by pixel diff
then a small model, speech transcription gated by volume, and a **one-sentence text
narration of each captured frame** that stays in memory after the image is evicted. The
narration does most of the work: +17 to +48 points across eight models, largest on voice
tasks. Too many image tokens hurt some newer models, so components are chosen per model.

## Mobile

The action space is accessibility APIs plus gestures, where the same (x, y) can be a tap, a
long press or the start of a swipe. The real blocker is ecosystem: platforms earn from
attention (ads, recommendations, impulse buys) and a goal-directed agent skips all of it —
a structural conflict of interest, not just CAPTCHAs.

## Efficiency is now the bottleneck

Benchmark success has climbed from about 20% toward human level, but agents take many more
steps than humans and per-step latency *grows* with context, so a seconds-long human tweak
takes an agent minutes. There is no systematic fix yet; agents cannot predict their next
action while the current one runs. The workaround is to decouple a fast voice front from
the slow GUI agent ([[Fast-Slow Thinking Architecture]]).

## See Also
- [[ACI (Agent-Computer Interface)]] — extends (the interface design discipline, applied to screens)
- [[Real-Time Multimodal Agents]] — instance-of (the GUI setting)
- [[Fast-Slow Thinking Architecture]] — extends (talking while acting)
- [[Tool Design as Harness Surface]] — prerequisite-for (the computer/bash/editor action space)
