---
title: Realtime Voice Architecture Reference
tags: [voice, adk, infra, reference]
summary: Numbers and tradeoffs for building a realtime voice agent — cascaded ASR→LLM→TTS vs speech-to-speech, the latency budget in which LLM time-to-first-token dominates, endpointing strategies, domain-specific transcription failure modes, and the regulated-domain constraints (GDPR Art. 9/17/22, health-data hosting) that shape the architecture before any code.
updated: 2026-10-30
sources:
  - data/raw/claude-docs/galactus/docs/research/2026-08-10_voice-tooling_realtime-sota.md
  - data/raw/claude-docs/galactus/docs/research/2026-08-10_voice-tooling_regulated-domain.md
  - data/raw/claude-docs/galactus/docs/plans/2026-08-10-voice-capability-parity.md
  - data/raw/repos/galactus/.claude--docs--plans--2026-08-10-voice-capability-parity.md
---

# Realtime Voice Architecture Reference

Research notes (medium confidence, 2026-08) for a voice scheduling agent in a regulated
health-adjacent domain. The architectural conclusions are the durable part; the latency
figures are a snapshot.

## Cascaded vs speech-to-speech

| | Cascaded ASR → LLM → TTS | Native speech-to-speech |
|---|---|---|
| End-to-end latency | ~400–600 ms | ~200–350 ms |
| Cost | baseline | roughly 10× |
| Text audit trail | yes — transcript is the record | no native text; must be reconstructed |
| Tool calling | mature | weaker |
| Vendor swap | per stage (one-method port) | whole-stack |

For anything that must be **auditable** (scheduling, consent, anything a regulator reads
later) cascaded is the correct choice despite the latency penalty; the transcript is the
compliance artifact, not a byproduct.

## Latency budget

- Conversational threshold: **< 500 ms** feels natural; **> 1500 ms** and the conversation
  collapses (users repeat themselves, talk over the agent).
- Within a **streamed** cascade (stages overlap, endpointing tuned aggressively and
  counted outside the figure), **LLM time-to-first-token (400–800 ms) dominates**; ASR and
  TTS streaming are each ~100–200 ms. In a **fully serial** cascade that waits on a
  500–800 ms VAD silence threshold, endpointing becomes the largest stage and the total
  reaches ~0.95–2.3 s ([[Voice Agent Paradigms]]) — so tune endpointing first, then model tier. Consequence: model tier is the binding constraint —
  a fast small model is not a cost optimisation but a correctness requirement, and
  routing the hard reasoning to a bigger model happens *between* turns, not within one.

## Endpointing (when has the user stopped?)

| Strategy | Accuracy (reported) | Failure |
|---|---|---|
| Acoustic VAD (silence threshold) | ~85–90% | cuts off mid-thought pauses; fires on background noise |
| Semantic endpointing (is the utterance complete?) | ~92–96% | adds a model call to the critical path |
| Model-based turn prediction | highest, least portable | tied to one vendor |

Domain failure modes argue for **hybrid acoustic + semantic**: people pause while reading
out dates, phone-number digit groups and medication lists — exactly the fields a
scheduler must capture — and a pure VAD endpointer splits them.

## Regulated-domain constraints

The existing specs covered PII masking but not compliance *architecture*. Findings:

- **GDPR Art. 9** — health data is a special category: an Art. 6 lawful basis *and* Art. 9(2)
  explicit consent, captured and logged in the call itself.
- **Art. 17 erasure must reach every representation.** Summaries, embeddings, call notes
  and derived fields all contain the data; deleting the recording while a summary survives
  is "dark erasure". Requires traceability from each summary back to its source so a
  deletion can propagate. See [[Data Clusters by Writer and Trust]] for the general shape.
- **Art. 22** (automated decisions with legal effect) is *not* triggered by scheduling but
  is triggered the moment the agent **triages** — so a triage feature is a legal change,
  not a product increment.
- **Data minimisation** — do not transcribe what is not needed; audio redaction is
  mandatory, not optional (contrast [[PII Masking Approaches]] for text).
- **Health-data hosting certification** (e.g. France's HDS) is an *infrastructure*
  requirement on where audio and transcripts rest — it constrains the deployment target,
  not the agent code.

## Evaluation and audit consequences

- **No end-to-end deterministic replay.** The same audio gives the same ASR output but
  different LLM output. Split testing into deterministic checks (tool success,
  infrastructure latency) and statistical ones (task-completion rate, barge-in accuracy).
- **WER does not predict task success.** 20% WER on filler words still books the
  appointment, and 5% WER on the doctor's name does not. Treat WER as a component metric
  and task success as the primary one.
- **The cascaded-vs-S2S verdict is domain reasoning, not tooling reasoning.** The spec
  presents a decision tree with criteria instead of hardcoding "cascaded", so it does not
  mislead the next voice project that is not medical.
- **A clean negative result is worth writing down.** Automated-decision rules do not
  apply to plain appointment scheduling (booking produces no legal or similarly
  significant effect). Saying so explicitly stops someone over-building a human-review
  path. It would apply to triage or eligibility decisions.
- **Audio observability needs a local semantic-convention extension** (`vad.confidence`,
  `asr.confidence_score`, `tts.latency_ms`, …), marked local-until-standardized, because
  the GenAI conventions cover LLM and tool spans but not audio frames.

## See Also
- [[Voice Agent Patterns]] — extends
- [[Duplex Voice Breaks Discrete-Turn Assumptions]] — extends (why the request-response toolkit does not transfer)
- [[PII Masking Approaches]] — extends (text masking vs mandatory audio redaction)
- [[Data Clusters by Writer and Trust]] — extends (erasure must reach every representation)
- [[Safeguards Architecture — Five Protection Layers]] — extends
- [[Voice Agent Paradigms]] — related (the fully serial cascade budget, where the VAD wait dominates)
