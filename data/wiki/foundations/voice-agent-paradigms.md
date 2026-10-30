---
title: Voice Agent Paradigms
tags: [foundations, voice, comparison]
summary: "Cascaded (VAD → ASR → LLM → TTS), end-to-end omnimodal, and full-duplex voice agents differ in one thing — how far each gets from VAD's assumption that conversation happens in discrete turns — and all three coexist as trade-offs; the cascade's serial latency budget is about 1–2 s before queueing multiplies it."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/generative-ai--07-agentic-applications--real-time-multimodal-agents.md
---

# Voice Agent Paradigms

Three paradigms coexist in production. A newer one does not simply replace an older one.
The question that separates them is **how far each gets from the assumption that
conversation happens in discrete turns**.

| Paradigm | Shape | Turn-taking |
|---|---|---|
| **Cascaded** | VAD → ASR → LLM → TTS, separate models | VAD guesses turns from silence |
| **End-to-end omnimodal (Omni)** | One model listens, thinks and speaks | Still turn-based, still VAD-driven |
| **Full-duplex** | Listens and speaks at once, deciding many times a second whether to speak, listen, stop, interrupt or call a tool | No turns at all |

## Cascaded: the latency budget

Fully serial, short reply, no reasoning:

| Stage | Typical latency |
|---|---|
| VAD end-of-speech (silence threshold) | 500–800 ms |
| ASR | 50–200 ms (200–500 ms on constrained hardware) |
| LLM time to first token | 100–500 ms (5–10 s with reasoning) |
| LLM first short segment | 100–300 ms |
| TTS first segment | 200–500 ms |
| **Total** | **≈ 0.95–2.3 s**; above about 2 s people get restless |

**Queueing multiplies it**: latency ≈ idle latency × 1/(1 − utilisation), so 2× at 50%
load and 5× at 80%. Voice servers cannot run hot.

**Full-chain streaming** makes each stage emit early (ASR while the user speaks, the LLM
split into speech-ready chunks at punctuation, TTS chunk by chunk). The real overlap is
limited: ASR overlaps the user's speech, and the tail of LLM output overlaps TTS and
playback. **Speculative generation** starts the LLM on a stable partial transcript, cancels
or corrects if it changes, and holds playback until the turn is confirmed; frameworks
support it, but commit, invalidation and rollback are still yours to implement. No amount
of streaming removes **the turn decision itself** — that is what
[[Semantic Turn Detection]] addresses.

## End-to-end omnimodal

One model lets paralinguistics (emotion, prosody, ambient sound) flow through the latent
space instead of being squeezed into text, and cuts latency. It costs more training data and
is harder to debug.

**End-to-end wins on latency, not necessarily accuracy.** In a *self-cascade*, the same
model transcribes to structured text, then reasons over it. When the answer depends on
*what was said*, self-cascade matches or beats end-to-end, especially for models with weak
perception; when it depends on *how it was said*, end-to-end wins. So the winner is
predictable from the task: what matters is what information the bottleneck carries, and
adding paralinguistic markers to the intermediate text narrows the gap. A support line that
must capture order numbers exactly is content-determined, so a (self-)cascade is as accurate
and more debuggable.

Mechanism notes from the published models: native-audio APIs add barge-in and asynchronous
function calls (the model keeps talking while a tool runs); a Thinker/Talker split on MoE
raises throughput but not first-packet latency, which comes from the talker's
multi-codebook autoregression and a causal codec (about 234 ms). The remaining flaw: Omni
still takes turns, so a user pausing mid-number gets cut off.

## Full-duplex

Full-duplex drops the turn assumption, as simultaneous interpretation does. One design
models two audio streams (user and self) plus an inner-monologue text stream, so overlap and
interruption need no special logic (about 200 ms end to end). Another argues that
interactivity belongs *inside* the model rather than in a VAD harness, working in ~200 ms
micro-turns with audio, video and text interleaved and speaking up unprompted; its reported
turn-switch latency is about 0.40 s against about 1.18 s for a turn-based realtime API.
Production systems at large scale now wait while the user thinks, backchannel and translate
live.

The arc: VAD guesses turns from silence → streaming perception guesses them from meaning →
full-duplex has no turns, so barge-in handling largely disappears from the architecture. The
practical consequences for request-response tooling are in
[[Duplex Voice Breaks Discrete-Turn Assumptions]].

## Serial vs streamed budgets

The table above is a **fully serial** cascade with endpointing inside the budget, where the
VAD silence wait (500–800 ms) is the largest stage. A **streamed** cascade overlaps the
stages and counts endpointing separately; there LLM time-to-first-token (400–800 ms)
dominates and the end-to-end figure is ~400–600 ms ([[Realtime Voice Architecture Reference]]).
Both are true; quote the configuration with the number.

## See Also
- [[Real-Time Multimodal Agents]] — instance-of (the voice setting)
- [[Semantic Turn Detection]] — extends (replacing VAD's silence guess)
- [[Fast-Slow Thinking Architecture]] — extends (adding reasoning without adding latency)
- [[Realtime Voice Architecture Reference]] — extends (the streamed cascade budget)
- [[Voice Agent Patterns]] — extends (implementation patterns for a voice agent)
- [[Duplex Voice Breaks Discrete-Turn Assumptions]] — extends (what full-duplex breaks downstream)
