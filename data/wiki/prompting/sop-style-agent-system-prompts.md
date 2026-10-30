---
title: SOP-Style Agent System Prompts
tags: [prompting, harness, pattern]
summary: Write a long agent system prompt as an ordered procedure with per-stage exception branches, not an unordered rule pile — in a Tau-Bench ablation, flattening the same rules into a list cut task success by more than 30% while tone changes barely mattered.
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--02-prompt-anatomy.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--README.md
---

# SOP-Style Agent System Prompts

A long agent system prompt is an operating manual for a capable new hire. Bojie Li's
Tau-Bench ablation (*AI Agents in Depth*, Experiment 2-4: airline and retail support)
isolates which properties of that manual matter:

| Change (all else fixed) | Effect |
|---|---|
| Tone swapped (neutral → bombastic → emoji-casual) | Little change |
| **Same rules flattened from an ordered procedure into an unordered list** | **Success fell >30%**; "verify identity before refund" was skipped |
| Tool descriptions removed (signatures kept) | Tool-call errors up 45% |

## The rules

- **Write an SOP, not a rule pile.** Numbered stages (validate → classify → preprocess →
  execute → verify), each with its exception branches. The model can tell which stage it is
  in and what applies there, instead of searching hundreds of rules for one that fits.
- **Ablate before rewriting.** When an agent underperforms, switch off one component at a
  time and see what moves.
- **Make business rules executable.** "Choose the billing type that fits the task" behaves
  differently every run. Each edge needs a decision rule (e.g. commission only when an
  existing bill is negotiated down, never on refunds or cancellations; "savings" computed
  only from the current bill). Product owners settle these rules; engineers encode them
  faithfully and don't invent business logic. The model then spends its reasoning only on
  the parts that need judgment.
- **Few-shot placement.** 2–3 boundary-covering examples when rules can't capture the
  target (style, report format, tone); skip them when the task is easy to state. Put them
  in the system prompt or as synthetic first-turn messages, and keep them **byte-stable** —
  per-request "most relevant" examples break the prompt cache ([[Few-Shot Prompting]],
  [[Context Anatomy]]).
- **Tool descriptions are load-bearing** (the 45% row) — see
  [[Tool Definitions as Prompts]].
- **Explain why**, and skip SHOUTING: modern models follow instructions more literally, so
  CRITICAL/MUST tends to cause over-application rather than compliance
  ([[Prompt Engineering]]).

## See Also
- [[Prompt Engineering]] — instance-of
- [[Tool Definitions as Prompts]] — extends
- [[Few-Shot Prompting]] — extends
- [[Harness Anatomy]] — extends (the system prompt as one harness component)
