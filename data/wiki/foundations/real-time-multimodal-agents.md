---
title: Real-Time Multimodal Agents
tags: [foundations, voice, concept]
summary: "Voice dialogue, computer use and robot control are the three settings where continuous input and a strict output time budget make multimodality hard — and all three are moving the same way, from serial pipelines toward end-to-end models and a fast/slow division of labour, with irreversible actions needing a gate."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/generative-ai--07-agentic-applications--real-time-multimodal-agents.md
  - data/raw/repos/learn-ai-engineering/generative-ai--07-agentic-applications--README.md
---

# Real-Time Multimodal Agents

Static image and document understanding is ordinary agent work, and image or video
*generation* is just a tool call. The hard cases are the ones where input arrives
continuously and output has a time budget: **voice**, **GUI operation** and **robot
control**. Each extends the loop in [[Agent Fundamentals]] under a latency constraint.

## The common thread

| | Serial bottleneck | End-to-end move | Fast/slow split | Still open |
|---|---|---|---|---|
| Voice | VAD → ASR → LLM → TTS | Omni models, then full-duplex | Interaction model + background reasoner | Debuggability of end-to-end models |
| Computer use | Screenshot → think → click | — | Voice model + slow GUI agent | Per-step latency, continuous video |
| Robotics | Plan → act | Vision-language-action models | Planner + VLA with action chunking | Cross-task generalisation, data |

- **Voice** — [[Voice Agent Paradigms]] (cascaded, omnimodal, full-duplex) and
  [[Semantic Turn Detection]], the streaming-perception fix for VAD's silence guess.
- **Thinking under a latency budget** — [[Fast-Slow Thinking Architecture]].
- **Computer use** — [[Computer Use Visual Grounding]].
- **Robotics** — [[Action Chunking]] and VLA action representations.

## Speech synthesis: imperfection on purpose

Perfectly fluent TTS sounds machine-made, because human pauses and fillers signal thinking
and uncertainty. The proposal is to **let the LLM decide prosody** by emitting control
tokens (a thinking pause with a filler, a searching cue, emotion, speed, a sigh or a small
laugh). Only the LLM knows whether it is mid-hard-problem or whether the user is impatient.
TTS becomes a generator that takes text plus control tokens. Two ways to build it: a
proprietary TTS with native control tokens (flexible, needs a dedicated team), or voice
cloning with a **reference library** — two dozen short clips covering emotion × speed ×
style, chosen by the control tokens so timbre stays consistent. Against no control tokens
(robotic) and a single reference clip (monotone), the multi-clip library came close to a
human agent.

## Observing an end-to-end voice model

Log the input audio, the event tokens and any inner-monologue or text stream, and replay
through a self-cascade (the same model transcribing first) to localise an error to
perception or to reasoning.

## Irreversible actions need a gate

Every fast/slow design lets the fast path act before the slow path checks — speak then
correct, click then look, step then look. Whatever is irreversible has to be gated
outside the model ([[Execution Boundaries and Guardrails]]).

## See Also
- [[Agent Fundamentals]] — prerequisite-for (the loop these settings extend)
- [[Voice Agent Paradigms]] — extends (the voice setting)
- [[Fast-Slow Thinking Architecture]] — extends (the shared division of labour)
- [[Computer Use Visual Grounding]] — extends (the GUI setting)
- [[Action Chunking]] — extends (the robotics setting)
- [[Post-Training for Agents]] — extends (voice SFT, robot-policy RL)
- [[Realtime Voice Architecture Reference]] — extends (build-time numbers for a voice agent)
- [[Voice Agent Patterns]] — extends
