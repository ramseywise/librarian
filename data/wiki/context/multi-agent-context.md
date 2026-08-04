---
title: Multi-Agent Context
tags: [llm, agents, context-management, concept]
summary: Sub-agent isolation is the highest-cost context lever — a sub-agent burns 100k tokens and returns 2k, and the discarding of its window is the feature, not a side effect.
updated: 2026-08-04
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--02-context--notes--06-multi-agent-context.md
---

# Multi-Agent Context

> Isolation is the highest-cost context lever. Use it when compression is not enough.

The **Isolate** lever of [[Context Engineering]] — last of the four, because it is the most
expensive.

## Sub-Agent Architectures

Specialized agents handle focused tasks with **clean context windows**, returning condensed
summaries to a lead coordinator.

**The economics are the point.** A sub-agent may burn 100k tokens exploring a codebase and
return a 2k-token summary. The orchestrator pays 2k for work that would have cost it 100k of
its own window — and, more importantly, would have left 98k of exploration debris polluting
the window it needs for synthesis.

```
Orchestrator (holds plan, stays small)
  ├── Sub-agent A: explore subsystem X  ->  2k summary  (spent 80k internally)
  ├── Sub-agent B: explore subsystem Y  ->  2k summary  (spent 60k internally)
  └── Sub-agent C: explore subsystem Z  ->  2k summary  (spent 90k internally)

Orchestrator window: ~6k of findings, not 230k of exploration.
```

**The sub-agent's window is discarded, not merged. That discarding is the feature.**

## Orchestrator-Holds-Plan

The settled default: the **orchestrator owns the plan and the synthesis**; sub-agents own
bounded investigations.

Sub-agents should not decide overall strategy, because each sees only its slice. An agent
that explored one subsystem will **over-weight that subsystem** — it has no basis for
comparison. Cross-cutting judgment requires the window that saw all the summaries.

### What a sub-agent receives

The prompt is the entire interface.

| Gets | Does not get |
|---|---|
| Its specific task, scoped and bounded | The full conversation history |
| The minimum context needed to do it | The overall plan |
| The expected return shape | The other sub-agents' findings |

**That last exclusion is what makes isolation work — and it is also the failure mode.**

## Costs

- **Lost shared context.** Sub-agents can't coordinate, may duplicate work, or reach
  contradictory conclusions from disjoint evidence.
- **Summary is lossy.** Whatever the sub-agent doesn't include is gone. If its judgment
  about relevance was wrong, **the orchestrator never learns what it missed.**
- **Prompt is the whole interface.** An under-specified sub-agent prompt yields an off-target
  investigation, discovered only after it has burned its budget.
- **Token multiplier.** Three sub-agents spending 80k each is 240k of real tokens for 6k of
  visible output. Cheap for the *orchestrator's window*, expensive in absolute spend.

> Try **Compress** before reaching for **Isolate**. Sub-agents are the right answer for
> genuinely parallel, genuinely separable investigation — not for work that a compaction
> would have handled. See [[Context Compaction]].

## Isolation as a Security Boundary

Isolation is also a **containment mechanism**. A sub-agent processing untrusted content —
scraped web pages, user uploads, third-party API responses — has a window that gets
discarded. An injection landing in that window cannot reach the orchestrator except through
the **summary**, which is a narrow, inspectable channel.

**This only holds if the summary is treated as data, not instructions.** A sub-agent summary
interpolated directly into an orchestrator prompt is itself an injection path. See
[[Prompt Injection]].

This is the same structure as the Dual-LLM pattern: a quarantined component reads untrusted
content but cannot act; a privileged component acts but never reads raw untrusted text.

### Skills plus open network access

A high-risk combination. Skills make procedures more capable; network access makes
exfiltration possible. Together they form a data-exfiltration path that is easy to introduce
and hard to retrofit against.

A defensible default posture:

- Skills: **allowed**
- Shell: **allowed**
- Network: **enabled only with a minimal allowlist**, per request, for narrowly scoped tasks

**Assume tool output is untrusted regardless of source.**

## See Also
- [[Memory as Context]] <!-- auto-linked -->
- [[Shared Context Brief]] <!-- auto-linked -->
- [[Why Context Is Finite]] <!-- auto-linked -->
- [[Context Engineering]] — part-of
- [[Tool Design as Context Engineering]] — complements
- [[Context Compaction]] — alternative-to
- [[Prompt Injection]] — mitigates
