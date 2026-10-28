---
title: Duplex Voice Breaks Discrete-Turn Assumptions
tags: [voice, llm, pattern]
summary: Every request-response design artifact — framework-selection trees, agent specs, review layers, eval harnesses, PII pre-filters — silently assumes a discrete turn with a stop_reason; realtime duplex voice has no such boundary, so the right move is to scaffold only the graph behind the audio loop, say plainly which half is missing, and generate under constraints rather than generate-and-repair.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/galactus/docs/research/2026-08-10_voice-tooling_spec-gap.md
  - data/raw/claude-docs/galactus/docs/research/2026-08-10_voice-tooling_skill-audit.md
  - data/raw/claude-docs/galactus/docs/research/2026-08-10_voice-tooling_framework-patterns.md
  - data/raw/claude-docs/galactus/skills/new-agent/SKILL.md
  - data/raw/claude-docs/galactus/skills/archived/design-sprint/ARCHIVED.md
  - data/raw/claude-docs/galactus/skills/archived/design-sprint/SKILL.md
  - data/raw/claude-docs/galactus/skills/new-agent/references/framework-selection.md
  - data/raw/claude-docs/galactus/docs/plans/2026-08-10-voice-capability-parity.md
  - data/raw/repos/galactus/.claude--docs--plans--2026-08-10-voice-capability-parity.md
---

# Duplex Voice Breaks Discrete-Turn Assumptions

A five-angle research pass asked whether an existing agent-design toolkit could be reused
for a realtime voice scheduler. The answer was that the toolkit was not *wrong* so much as
built on an axiom voice removes: that there is a turn, and that it ends.

## Where the axiom hides

The spec audit found all ten agent-* specs break on the same point, in different clothes:

| Spec assumes | Duplex reality |
|---|---|
| a `stop_reason` marks the turn boundary | audio is continuous; the user may still be talking |
| stateless functions per call | a persistent connection with per-session state |
| idempotency keys per request | partial hypotheses revised mid-utterance |
| compaction between turns preserves the cache prefix | compaction mid-call invalidates the prefix while audio streams |
| tree-shaped trace spans | concurrent streams (ASR, LLM, TTS) overlapping in time |
| eval trials reset state between runs | a call cannot be reset mid-stream; "step" is undefined |
| PII redaction fires before input reaches the model | partial transcripts are already in context before the redactor sees them |
| tool results are values | tool results are streams |
| uncertainty is binary known/unknown | act on partial evidence and be ready to reverse |
| HITL is a gate before an action | barge-in makes the human simultaneous with the action |

The skill audit found the same at the design-system level: latency tiers of "spinner vs
batch" (voice needs sub-second), termination vs state reset, turn-by-turn simulation that
cannot express overlapping turns, metrics with no barge-in rate or audio dropout, NFRs
with no jitter, codec or concurrency clauses. The REUSE/ADAPT/SKIP verdict was ADAPT: add
a voice stage to scoping, a streaming-loop layer beside the existing orchestration layer, a
voice simulation template, and mandatory audio redaction (see
[[REUSE/ADAPT/SKIP Asset Verdicts]]).

## Two patterns that invert

- **202-and-poll is actively wrong.** The async-job pattern that every API template
  recommends optimises for decoupling; voice needs a persistent connection and sub-500ms
  response. It is not a degraded fit — it is the opposite constraint.
- **Constraints-first, not generate-and-repair.** A deterministic validator survives, but
  the repair loop it feeds cannot run mid-utterance — there is no moment to take the
  output back. Constraints must be satisfied during generation (grammar, allowed slots,
  pre-validated tool arguments), with the validator as a tripwire rather than a corrector.

What *does* survive: a one-method provider port (swap ASR/TTS vendors), the pure graph
behind the turn, and the review subsystem's deterministic substrate.

## The scaffolding rule

The `new-agent` orchestrator encodes the conclusion as its second step: *if the answer is
realtime/duplex, stop scaffolding* — scaffold only the graph behind it, called once per
finalized turn, **and say plainly which half is missing**. Shipping a request-response
skeleton with "voice" in the title is the collapse: it looks complete and cannot work.
The archived sprint skill had reached the same place from the roadmap side — voice is a
separate workstream, not a feature of the general agent track.

## The selection tree's first row, as landed

The galactus `framework-selection` reference now asks the duplex question **first**,
because it is "the only question here that changes the *answer set* rather than choosing
within it." The tell is that no protocol event marks the end of a turn. Three duplex
options replace the request/response three:

- a framework's native bidirectional primitive, when tools and sub-agents are needed on
  that vendor's stack;
- a voice-first realtime API, when voice is the product;
- an external voice runtime plus an agent graph called per finalized turn.

The third is the common case, and it is "a two-component design, not a framework choice":
keep the boundary at the finalized transcript, and **do not put a graph inside the audio
loop**, because the graph's latency is unbounded and the audio loop's is not.

## The amendments, one per restated assumption

The voice capability-parity plan turned the gap analysis into work. Eight of ten agent
specs broke, all on restatements of the *same* request-response assumption. So the work
became amendments plus one new spec, not one new spec on its own. Ordering followed
dependencies: first extend the design-system's five-layer model with a streaming-loop
layer, because new-agent, scope-poc, and three review dimensions all inherit their
assumptions from it. Adapting them before the model was settled would mean adapting them
twice. The amendments:

| Spec | Assumption | Voice amendment |
|---|---|---|
| runtime | stateless requests, no background tasks | the session process is the exception and owns connection lifetime, reconnect, cleanup |
| reliability | idempotency key presumes a replayable turn | a cut-off utterance is **superseded, not retried**. Backoff and circuit breakers carry over unchanged |
| observability | tree-shaped span nesting | session → turn → {asr, llm, tts} with **overlapping** spans (TTS starts before the LLM finishes), plus local audio attributes and an audio retention window |
| eval | reset the environment between trials | no end-to-end deterministic replay: components replay, the pipeline is statistical. **Task success over WER** |
| memory | checkpoint after each plan step | checkpoint at turn boundaries. Erasure covers audio, transcript, *and* derived context |
| tools | none on latency | an in-turn tool call has a latency budget (2s is invisible in chat and fatal on a call). Mitigation: acknowledge out loud while it runs |

Two open problems were recorded as unresolved on purpose rather than given made-up
numbers. First, **barge-in history** has to record what the agent *generated*, what the
user actually *heard* (an offset into the utterance), and the interruption marker. Every
framework serialises this differently, so the spec requires an explicit design and test
coverage of the audit trail, not a format. Second, endpointing thresholds have to be tuned
empirically per domain.

One honest scoping call: the finding with the most leverage (the framework ships a live
streaming runner that the skills never mention) sat upstream in the shared template. So
work confined to this repo would produce a showcase that was internally consistent while
everything else still sent voice projects to the wrong framework. That trade was accepted
and logged as a risk with likelihood **High, accepted** rather than left implicit.

## See Also
- [[Voice Agent Patterns]] — extends (the BIDI/session patterns this gap analysis is about)
- [[Realtime Voice Architecture Reference]] — prerequisite-for (the latency and architecture numbers behind the constraints)
- [[HITL and Interrupt Patterns]] — contradicts (gate-shaped HITL vs simultaneous barge-in)
- [[REUSE/ADAPT/SKIP Asset Verdicts]] — instance-of
- [[Capability Runtime-Coupling Tiers]] — extends (duplex is the missing first row of the framework-selection tree)
- [[Streaming Output Scrubbing]] — extends (redaction on a stream rather than before input)
