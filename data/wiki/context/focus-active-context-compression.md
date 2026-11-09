---
title: "Focus Active Context Compression"
tags: [context, pattern]
summary: "Focus gives a coding agent two tools, start_focus and complete_focus, so it can collapse a finished exploration into a short knowledge block and drop the raw messages; a five-instance SWE-bench Lite test cut tokens 22.7% at equal pass count (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-verma-2026-active-context-compression.md
---

# Focus Active Context Compression

Focus is an agent-side compaction scheme: instead of an external process summarizing the history, the agent itself marks the start and end of an exploration and replaces it with a summary.

## Mechanism

Two tools are added to a ReAct loop. `start_focus` opens a phase; `complete_focus` closes it. On completion the agent writes a summary covering what was attempted and what was learned, plus a third part; that phase's raw messages are then deleted and the summary goes into a Knowledge block kept at the start of the context. The context therefore grows during a phase and shrinks at its end, a sawtooth shape (the figure showing it is conceptual, not measured).

The author reports that current models do not compress spontaneously. The configuration that worked used a mandatory workflow, injected reminders and an explicit four-to-six phase structure (explore, understand, implement, verify). The extraction notes that this makes the "full autonomy" wording in the abstract hard to square with a heavily scripted setup.

## Results (self-reported)

SWE-bench Lite, five instances the authors chose as heavy on context, claude-haiku-4-5, A/B against a no-compression agent, persistent bash tool plus a string-replace editor, 150-step cap, success checked in the official Docker harness.
- Total tokens fell from 14,920,555 to 11,526,418 (-22.7%) (self-reported), with 3 of 5 solved in both arms.
- Averages per task: 6.0 compressions per task, 70.2 messages removed; token use 2,984,111 for the baseline and 2,305,284 with Focus (self-reported).
- Savings varied by instance, from -57% (matplotlib and sympy instances) to +110% on one pylint instance, where Focus used more tokens (4.3M against 2.1M, 8 compressions) (self-reported).
- Earlier passive-prompting runs, not tabulated, gave 1-2 compressions and about 6% savings; the aggressive prompt gave 6.0 compressions per task (self-reported).
- The author's reading is that compression frequency and timing matter more than whether to compress. This was not tested in isolation.

## Limits

- N=5, hand-picked instances, one model, no repeated runs and no variance. 3/5 against 3/5 cannot show equal accuracy, and three instances drive the total saving.
- On one iterative task (pylint), compression removed context the agent still needed and it had to explore again.
- The cognitive-tax cost of compressing is asserted, not measured. No ablation separates the reminders from the call-frequency rule.
- The author lists full-benchmark validation, RL with token-cost penalties and structured (artifact-preserving) compression as future work.

## See Also
- [[Context Compaction]] — prerequisite-for
- [[Why Context Is Finite]] — prerequisite-for
- [[AgentFold Context Folding]] — alternative-to (agent-directed folding of history)
- [[Learned Proactive Compaction]] — alternative-to
- [[MemGPT / Letta Virtual Context Memory]] — related
