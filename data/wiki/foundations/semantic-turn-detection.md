---
title: Semantic Turn Detection
tags: [foundations, voice, concept]
summary: "Replacing VAD's silence threshold with streaming perception that judges end-of-turn from meaning plus acoustics — why VAD + segmented ASR fails on latency, information and accuracy, the two streaming paths, and the label-leakage bug where the fix was causal re-labelling, not a new architecture."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/generative-ai--07-agentic-applications--real-time-multimodal-agents.md
---

# Semantic Turn Detection

A cascaded voice agent ([[Voice Agent Paradigms]]) decides the user has finished speaking
with voice-activity detection: a silence threshold. VAD plus segment-by-segment ASR has
three built-in problems:

1. **Latency.** VAD cannot predict the future; it can only wait for silence.
2. **Information loss.** VAD emits one bit. Emotion, hesitation, background sound and the
   difference between "uh-huh" as acknowledgement and as interruption are gone.
3. **Accuracy.** Independent segments lose context. If "smith" in an email address lands in
   its own segment it can be transcribed as "miss"; "around two o'clock" became "around
   midnight" in one experiment.

A silence threshold alone fails in **both directions**, because pauses *within* a turn
(reciting a phone number) often run longer than gaps *between* turns.

## What streaming means

A **causal or chunked encoder** that needs only the audio already received, plus
**incremental decoding**. A whole-window encoder (one that needs a 30-second window) cannot
stream however its decoder works. Streaming ASR without an LLM (RNN-T, streaming Conformer)
is old and powers live captions.

## Two newer paths

- **LLM-based streaming perception.** An LLM backbone post-trained to consume a continuous
  audio stream sees the whole conversation, not VAD fragments, so it can learn names and
  terms in context and use world-knowledge priors. It emits **acoustic event tokens**
  alongside text: speech start/end (a joint semantic and acoustic judgment), interrupt,
  emotion, laughter, noise.
- **Turn detection inside the recogniser.** Lighter: a LoRA on a small streaming ASR model
  that weighs semantics and silence together.

## The label-leakage lesson

In one such turn detector, the decision wavered. The cause was **the labels, not the
architecture**: end-of-turn labels had been annotated using audio from *after* the decision
point, which an online model can never see. Re-labelling with only causal information fixed
it. It is the same "data over architecture" result as in [[Post-Training for Agents]], and a
form of temporal leakage — the label knew something the model would not know at prediction time ([[Tabular ML Leakage Taxonomy]]).

Semantic turn detection patches the turn framework; it does not remove it. Full-duplex
models do.

## See Also
- [[Voice Agent Paradigms]] — extends (the turn decision streaming cannot remove)
- [[Realtime Voice Architecture Reference]] — alternative-to (hybrid acoustic + semantic endpointing numbers)
- [[Duplex Voice Breaks Discrete-Turn Assumptions]] — prerequisite-for (why turns are an assumption at all)
- [[Tabular ML Leakage Taxonomy]] — instance-of (temporal leakage: labels built from information the online model cannot see)
