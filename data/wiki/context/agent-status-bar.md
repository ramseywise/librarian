---
title: Agent Status Bar
tags: [context, context-management, agents, pattern]
summary: "A short, code-maintained, key-value block the harness appends at the end of the context every turn (counters, time, TODO, environment, errors) — it works because in-context learning is closer to lookup than aggregation, so distilled state beats raw history; it is lossy and trusted almost unconditionally, so its accuracy must be monitored."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--02-context-engineering--notes--02-context-anatomy.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--02-context-engineering--notes--05-compression-compaction.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--02-context-engineering--notes--04-retrieval.md
---

# Agent Status Bar

A small structured block the **harness** appends at the *end* of the context on every
turn — the live dashboard, as distinct from the system prompt, which is the fixed manual.
Part of the runtime-injection layer in [[Context Anatomy]].

```xml
<agent_status>
- phone_call: 3 invocations (merchant: 3/3 max)
- Current time: 2025-09-14 10:30:45
- TODO: [1] Cancel plan (in_progress)
</agent_status>
```

## Why It Works: Distill, Don't Retrieve

**In-context learning behaves more like retrieval than reasoning.** Attention finds an
existing record easily ("what is in record 37?") but is poor at *aggregating* across the
window in one forward pass ("how many records match?"). An agent told "call each merchant
at most 3 times" miscounts its own calls; put "this is call #3 to this merchant (3/3)" in
the tool result or status bar and the violation disappears.

The status bar is the **distillation layer** raw attention lacks: it turns a conclusion
that had to be reasoned over the transcript into one that can be looked up. Its position
at the end puts it next to the tokens being generated.

The same idea recurs at two other scales: [[Context-Aware Compression]] *replaces* raw
records with distilled conclusions, and [[Index-Time Distillation]] applies it to a corpus
(statistics and rules computed before any query arrives).

## Evidence

From a course synthesis of a published study (11 models, ~24k evaluations):

- Weak models gain 40–54 points; a 2B model *with* a status bar matched a frontier model
  *without* one.
- Strong models keep accuracy and cut reasoning tokens by 80–90%.
- Without a status bar, reasoning effort per query grows with context length; with one, it
  stays flat.
- Key–value entries (`Items: 9 (Pass 7, Defect 2)`) beat the same facts written as prose.

## Three Rules

1. **Maintain it in code, not with an LLM.** A ~20-line regex matched ground truth; a
   frontier model summarising the whole history at once did *worse than no status bar*.
   If an LLM must be involved, have it extract items one at a time and aggregate in code.
2. **It is a lossy projection.** Delete raw history only if the bar covers every question
   that will be asked. When a question needed triple intersections and the bar stored only
   pairs, accuracy collapsed (100% → 7.6% in one experiment). Treat a new question type as
   a schema change.
3. **Monitor its accuracy as a first-line metric.** Models trust it almost unconditionally:
   errors under ~10% are tolerated, larger ones are worse than having no bar. Source it
   only from real observations — if an attacker can write to it, it is an injection channel
   (see [[Context Failure Modes]]).

## Contents Worth Carrying

- A TODO plan (fewer iterations and fewer missed subtasks in the course lab)
- Per-event side-channel data: timestamps, time since last reply
- Environment: cwd (updated after `cd`), OS, shell
- Per-tool call counters — "call #3 for `read_file`" prompts a change of strategy
- Detailed errors with fix hints (recovery rose from ~60% to ~95% in one lab)
- The available-skills list

## Update Strategy

| Strategy | When | Cost |
|---|---|---|
| **Replace** the old status each turn | Short trajectories, or a large status | Cache lost only for the last few turns; one unambiguous status |
| **Append** a new status each turn | Frequent updates, long trajectories | Fully cache-friendly; stale copies the model must ignore |

Claude Code's `<system-reminder>` is the append variant. See [[Cache-Stable Context Layout]].

## Readings Need a Strategy

Raw timestamps alone barely move pass rates (~2–3 points) on time-sensitive tasks.
Pairing them with a short operating rule ("deliver when time is short; investigate slow
calls; route around hard blockers") lifted pass rates from roughly 10% to 40–50% across six
models. Time sense has three axes:

- **Urgency** — match effort to the clock
- **Persistence** — distinguish permanent blockers from transient ones (don't retry a 410
  five times)
- **Vigilance** — treat anomalies as evidence (a 5 s call that should take 500 ms; a 1 ms
  empty success)

A status bar that reports *external* facts the model could not infer (test results, render
checks, real system state) is the "interaction" axis of test-time compute — beyond longer
reasoning or more samples.

## See Also
- [[Context Anatomy]] — extends (the runtime-injection layer, placed last)
- [[Structured Context and Schemas]] — instance-of (a state schema maintained by code)
- [[Context-Aware Compression]] — alternative-to (adds distilled conclusions vs replacing raw records)
- [[Index-Time Distillation]] — extends (the same idea applied to a corpus)
- [[Context Failure Modes]] — prerequisite-for (a writable status bar is an injection channel)
