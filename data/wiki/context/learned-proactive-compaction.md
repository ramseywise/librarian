---
title: Learned Proactive Compaction
tags: [context, concept]
summary: "A coding agent can be trained to call compact() itself, at a seam rather than at a length limit; AutoCompact reports 39.6% vs 30.4% on SWE-bench Verified (self-reported), but the like-for-like 16K gain is 38.0% vs 28.8%, and most of the lift survives even when the compaction calls are skipped."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-02-zhang-2026-autocompact.md
---

# Learned Proactive Compaction

Most agents compact when the window fills: a length trigger fires at a fixed threshold and a
summariser rewrites the history ([[Context Compaction]]). **Proactive compaction** makes the
trigger a decision the agent takes. The agent has a `compact()` action; calling it replaces
earlier history with a summary under a fixed header, while the original task stays untouched.

AutoCompact (Zhang et al., arXiv 2610.02163, 2026) trains that decision instead of prompting
for it. The authors report that putting compaction rules in the prompt left the base model
almost never calling the action.

## Three decisions, supervised separately

Compaction is split into **when** (the trigger), **what** (the working state the summary keeps)
and **how to continue** (the first action after the summary). Training runs in two stages:

1. **Judge-guided SFT.** A strong model watches on-policy runs and keeps, replaces or repairs
   each compaction decision. The corrected version is what actually executes, so the
   follow-up actions match the corrected summary. Of 1,052 corrected trajectories, about half
   fixed what the summary kept; the rest split between trigger and continuation.
2. **Outcome RL** on a binary task reward, joint over coding and compaction. The trajectory is
   cut where the prefix gets rewritten, and every segment shares one advantage.

RL raised compaction use from 44% to 59% of tasks and cut summaries that dropped key state
from 3.1% to 0.2%, with no reward aimed at compaction (self-reported).

## Reading the numbers carefully

All rows: Qwen3-Coder-30B-A3B-Instruct in one terminal REPL scaffold, SWE-bench Verified,
averages of three runs, no intervals (self-reported).

| Comparison | Pass rate |
|---|---|
| Base, full 256K history | 30.4% |
| AutoCompact SFT→RL, 256K | 39.6% |
| Base vs AutoCompact, 16K forced threshold with fallback (AutoCompact may also compact early) | 28.8% vs 38.0% |
| AutoCompact checkpoint with its compact() calls skipped, top budget | 37.7% |

The headline compares across windows; the like-for-like pair is the 16K one. The checkpoint
still scores 37.7% when its compaction calls are skipped, so most of the 9.2-point gain (about 7.3)
remains without compacting. The paper also notes that its RL stage trained coding and compaction
together, so the 7.4 points RL added over SFT cannot be credited to compaction alone. Against that skipped-calls
checkpoint, executing compaction is ahead by 19.9% at a $0.10 budget and by 1.9% at $4.00.

Covering the state and naming a next step does not make a summary coherent: one SFT summary
recorded an unresolved syntax error and then proposed finishing. Check summaries for
self-consistency, not only for coverage.

## Limits

One scaffold, one base model, coding benchmarks only, three-run averages without intervals;
RL trained on 32K sequences but was evaluated at 256K. Costs are estimated from token prices.

## See Also
- [[Context Compaction]] — prerequisite-for
- [[Long-Horizon Execution]] — related (where compaction decides whether a run survives)
- [[Compression Strips the Epistemic Frame]] — related (what a summary loses)
- [[Context Failure Modes]] — related
- [[Context-Aware Compression]] — alternative-to
- [[Agentic Context Management (ACM)]] — alternative-to
