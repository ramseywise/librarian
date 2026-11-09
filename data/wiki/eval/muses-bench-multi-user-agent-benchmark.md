---
title: Muses-Bench Multi-User Agent Benchmark
tags: [eval, concept]
summary: A benchmark of 19 models acting as one shared agent for several users with different authority, covering conflicting instructions, prompt-level access control over turns, and meeting scheduling.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-yang-2026-multi-user-large-language-model.md
---

# Muses-Bench Multi-User Agent Benchmark

"Multi-User Large Language Model Agents" (Yang et al., Stanford, KAUST, UT Austin and MIT, arXiv preprint, April 2026) argues chat templates and training assume one principal, so models deployed for several users with different authority prioritise unstably, leak protected information as turns accumulate and coordinate inefficiently. The paper combines a benchmark with a position and offers no defence. The benchmark name appears once, in a table caption.

## Setup

19 models (13 proprietary, 6 open-weight), temperature 1.0, simulated personas with authority levels 1 to 10, multi-user input serialised into one user role in three formats. Run counts and cost are not stated. Scenarios: instruction following (1,298 execution and 304 selection scenarios, 2 to 10 users); access control (216 scenarios; the prompt tells the model to reject strictly when a user lacks authorisation; privacy is one minus leakage, utility is delivery to authorised users); meeting scheduling (216 scenarios, half full and half partial disclosure).

## Reported numbers (self-reported, Table 2)

- Best averages: Gemini-3-Pro 85.6, Claude-Sonnet-4.5 82.6.
- Privacy against utility: Claude-Sonnet-4.5 77.3 and 97.5; GPT-5.1 98.6 and 60.3; GPT-5.2 100.0 and 61.2; Gemini-3-Flash 88.7 and 90.6. Only Gemini-3-Pro (98.6 and 73.9) is high on both.
- Conflict lowers execution: Claude-Haiku-4.5 drops from 0.86 when aligned to 0.62 under conflict, and GPT-OSS-120B from 0.64 to 0.50.
- Over 10 rounds Claude-3.5-Haiku privacy falls from above 0.95 to below 0.75 after four rounds.
- Meeting success is mostly 50 to 65%, lower under partial disclosure, and falls as group size grows from 2 to 20.
- Qwen3-4B-IT reaches 83.8 on selection F1 but only 57.9 on execution.
- Serialisation format and attack type (fake authorisation, pressure, role-play) change privacy and utility little, which the authors read as interaction complexity being the bottleneck.

## Limits

- Simulated users, 10-round interactions, 2025-era models.
- No defence or external enforcement baseline is tested. The extraction marks "enforce outside the model" as its own inference; the paper only lists policy enforcement with tool calls and logs as future work.
- Serialising into a single user role is a confound, since no model natively supports multi-user messages.
- The extraction notes text and table mismatches in section 5.2: GPT-OSS-120B meeting success 77.3 in text against 58.9 in the table, Grok-3-Mini privacy and utility 99.7 and 59.0 against 99.6 and 60.1, and GPT-OSS-120B utility 94.4 against 94.8. Table values are used above.

## See Also
- [[LLM-as-a-Verifier]] — related
- [[Execution Boundaries and Guardrails]] — related (prompt-only access control tested here)
