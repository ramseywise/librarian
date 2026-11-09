---
title: "AgentFold Context Folding"
tags: [context, pattern]
summary: "AgentFold lets a web agent fold its own history at two scales each turn, condensing one step or consolidating a range into one block, keeping context near 7k tokens over 100 turns on BrowseComp (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-ye-2025-agentfold.md
---

# AgentFold Context Folding

AgentFold treats the agent's context as a workspace to edit, not a log to append to or a transcript to re-summarize in full each step.

## Mechanism

At step t the context holds the question, the tool list, summaries of older steps at several scales, and the newest interaction in full. On each step the model produces its reasoning, a folding directive, a rationale and a tool call. The directive names a range of steps and a summary.
- Granular condensation folds just the previous step into one summary entry.
- Deep consolidation merges the latest interaction and earlier summaries into one coarse block, which lets a run of failed attempts collapse into a single conclusion.

Training data comes from a pipeline that builds folded trajectories on a web-agent question set, with rejection sampling to drop format breaks, then plain supervised fine-tuning of a 30B mixture-of-experts model (3B active). Prompting alone did not reliably produce the structured output.

## Results (self-reported)

- Over 100 turns the average context went from roughly 3.5k to 7k tokens (200 BrowseComp trajectories, 100-turn cap, 128k window; self-reported).
- Benchmark scores for the SFT-only model, 100 tool-call cap: BrowseComp at 36.2, BrowseComp-ZH at 47.3, GAIA at 67.0 (text-only subset) and WideSearch at 62.1 (item-level F1) (self-reported). The baseline figures were taken from other papers and leaderboards.
- At turn 100 the context is reported as over 84k tokens smaller than a ReAct context, read off a plot. A 500-turn run kept context mostly under 20k tokens, with no accuracy given (self-reported).
- A worked example that assumes 1% of a detail is lost at each re-summarization leaves 36.6% of it after 100 steps. This is illustrative, not measured.

## Limits

- No ablation separates folding from the SFT data or base model, and there is no head-to-head against full-history summarizers; the paper only argues against them.
- More than a fifth of tasks ran into the 100-turn limit with the context still near 7k tokens, so the turn limit rather than context space was what constrained them.
- No latency, cost or fold-error analysis; folds are irreversible and nothing measures how often a needed detail is dropped. Single runs on large benchmarks, three trials on small ones, no variance.
- The memory saving (about 7GB per instance) is an estimate.

## See Also
- [[Context Compaction]] — prerequisite-for
- [[Focus Active Context Compression]] — alternative-to
- [[AdaCoM Learned Context Manager]] — alternative-to
- [[Context Window Budgeting]] — related
