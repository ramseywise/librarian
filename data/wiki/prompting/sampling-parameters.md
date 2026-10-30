---
title: Sampling Parameters
tags: [prompting, llm, reference]
summary: Temperature, top_p, max_tokens, stop and frequency/presence penalties — tune temperature or top_p and one penalty, never both; temperature 0 is not deterministic; best-of-n wants temperature ≈ sqrt(n)/10; many reasoning endpoints fix or reject these knobs.
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--04-controlling-output.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--07-prompting-reasoning-models.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--10-adversarial-prompting.md
---

# Sampling Parameters

| Parameter | Effect | Typical use |
|---|---|---|
| `temperature` | Flattens (high) or sharpens (low) the next-token distribution; 0 ≈ top token | Low for extraction, classification, factual QA; higher for brainstorming |
| `top_p` (nucleus) | Sample only from the smallest token set whose mass reaches p | **Tune temperature *or* top_p, not both** |
| `max_tokens` | Hard output cap | Cost/latency control. **A cut-off is not a stop** — check the finish reason |
| `stop` | Strings that end generation server-side | Cheapest way to end on your recognizable end ([[Stop Sequences and Completion Anatomy]]) |
| `frequency_penalty` | Grows with how often a token has appeared | Reduces word-level repetition |
| `presence_penalty` | Flat penalty on any token that appeared | Pushes toward new topics. **Tune one penalty, not both** |

## Caveats

- **Temperature 0 is not deterministic** in practice (batching, floating point). Tests
  must tolerate variation or mock the model.
- **Reasoning models often fix or reject** temperature/top_p; control them with effort
  instead ([[Prompting Reasoning Models]]).
- Provider support differs: penalties and logprobs are OpenAI-style features many APIs
  don't expose.
- Lower temperature is also a factuality mitigation for factual tasks.

## Best-of-n and beam search

- **Best-of-n**: n completions at moderate temperature, keep the best-scoring one. Rule of
  thumb (Berryman & Ziegler): `temperature ≈ sqrt(n) / 10`. At temperature 0 the n
  completions are identical. Score with [[Logprobs as Confidence Signal]] or a judge.
- **Beam search** is the decoding-side cousin: keeps several continuations alive and looks
  a few tokens ahead so the model doesn't paint itself into a corner. More coherent, much
  more compute; hosted APIs rarely expose it.

Repetition traps (a list degenerating into a loop) are mitigated by stop sequences,
repetition detection, penalties or higher temperature ([[Prompts as Document Completion]]).

## See Also
- [[Stop Sequences and Completion Anatomy]] — extends
- [[Logprobs as Confidence Signal]] — extends
- [[Self-Consistency]] — prerequisite-for (needs non-zero temperature)
- [[Prompt Engineering]] — instance-of
