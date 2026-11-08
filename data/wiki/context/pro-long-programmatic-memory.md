---
title: PRO-LONG Programmatic Memory
tags: [context, concept]
summary: PRO-LONG keeps a lossless append-only log of everything an agent observes and does, and lets a coding agent read it back with grep, Python and file tools; it raised pass@1 on ARC-AGI-3 and NetHack over the same agent without a log (self-reported).
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-fox-2026-pro-long.md
---

# PRO-LONG Programmatic Memory

Fox et al. (Duke, 2026) argue for a fidelity-tractability tradeoff: shrinking what is saved at write time makes reading easier but can discard details whose relevance only shows later. Their answer is to write everything and make the read side programmable.

## Mechanism

- **Write.** Every observation, action and outcome is appended to a log file, uncompressed.
- **Read.** The agent is a coding agent with a shell. It searches the log with grep, runs Python over it, reads line ranges, and may write or edit files in its workspace.
- The accessed context (what sits in the prompt, roughly 100K to 1M tokens) stays small while the accessible record (10M or more) grows.

## Results (self-reported)

ARC-AGI-3 uses 25 public games with a cap of 500 actions and high reasoning effort.
- Against the same coding agent with no log, pass@1 rose by 15.7 to 21.0 points over three models (GPT-5.5 41.2 against 24.0, with five runs for PRO-LONG).
- Against specialised harnesses it came near at lower cost: 41.2 against 45.1 pass@1 for one at 5.8 times fewer billed tokens, and 82.1 against 84.4 best@2 for another at 4.2 times fewer. The authors rescored the competitors.
- Tool ladder on GPT-5.5: read only 23.1, adding grep 27.2, Python 38.3, write and edit 41.2.
- Lowering the compaction threshold from 244K to 64K tokens left PRO-LONG at 44.3 (within its interval) while the no-log agent fell steadily. Clearing the workspace each call gave 40.7 against 41.2 for PRO-LONG, and 19.9 against 24.0 without a log.
- NetHack (BALROG progression, fixed seed, five-episode lifetimes, with the log carried between episodes): GPT-5.6 with Codex (ten lifetimes) reached a mean best@5 of 24.5% against 13.5% without the log. Kimi with Mini-SWE (fifteen lifetimes) reached 11.3% against 5.1%.

## Limits

- Two game benchmarks only. No conversational or preference memory, and no head-to-head run against semantic or vector retrieval; Mem0-style systems are discussed but not run.
- Five or fewer runs on ARC, two on Claude Code, and single runs at several ablation points. Best@5 of 60.1 against pass@1 of 41.2 shows large run-to-run variance.
- Cost ratios depend on the authors' rescoring and weighting of billed tokens. Several competitors have no replicates, and one cost covers only retained runs.
- The log is within-task history, not knowledge shared across tasks, and the NetHack seed is fixed. A coding agent with a shell is required, and logs reached 320K lines.

## See Also
- [[Context Compaction]] — alternative-to (lossless log against lossy summary)
- [[Scroll Event Log and Eviction Index]] — related (same append-only log, plus an eviction view)
- [[Coding Agents as Long-Context Processors]] — related
- [[Memory as Context]] — related
