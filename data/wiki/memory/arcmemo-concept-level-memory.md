---
title: ArcMemo Concept-Level Memory
tags: [memory, pattern]
summary: "ArcMemo stores reusable abstract concepts distilled from solved puzzles instead of raw solutions or one running summary, and on a 100-puzzle ARC-AGI-1 subset it lifts an o4-mini baseline from 55.17 to 59.33, a gain the paper's own variance numbers make fragile (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-ho-2025-arcmemo.md
---

# ArcMemo Concept-Level Memory

ArcMemo (a 2025 preprint) keeps lifelong memory as modular, abstract concepts extracted from reasoning traces, rather than as instance-level solutions or a single rewritten summary. The authors argue that instance entries are of little use for problems that only look different from earlier ones; the extraction notes that raw instance memory is never tested as its own arm.

## Setup common to the results

ARC-AGI-1, using 100 puzzles drawn at random from the public validation split, with o4-mini at medium effort. Results average 3 runs at oracle@2, and the memory is frozen after being seeded from 160 hand-written solutions. Two formats are compared: a program-synthesis format (PS) and a second format (OE, which the source does not expand). The comparators are no memory and a re-implementation of Dynamic Cheatsheet (one rewritten summary).

## Results

- Official score at retry 0: no memory 55.17, cheatsheet 57.67, OE 56.67, PS 59.33 (+7.5% relative) (self-reported). PS is the only design above the baseline at every compute scale tested.
- The gain sits near the noise. Run-to-run spread is 3.18 for the no-memory baseline and only 0.29 for PS. At the second retry the baseline reaches 69.00, PS 70.83, and the cheatsheet comparator 71.33, which is higher than PS (all self-reported, 100-puzzle ARC-AGI-1 subset, 3 runs averaged, oracle@2). The paper says memory matters less as inference compute grows.
- Selecting a subset of memory per problem: removing the selection step gives 55.17 at retry 0 against 59.33 with it, and uses many more tokens (self-reported).
- Attribution check by the authors on 10 puzzles that differed between arms: 40% of the cheatsheet's new solves traced to its content, against 100% for PS without selection (self-reported, 10 puzzles); the authors say causation cannot be concluded.
- Continual update during evaluation (OE, updated every 10 problems): helps at retry 2 (67.67 to 70.00) but is slightly lower at retries 0 and 1 (56.67 to 56.00; 65.67 to 65.00) (self-reported).
- Embedding retrieval of memory scored lower than the chosen selection on o3-mini (0.26 to 0.22; self-reported, setup as given in the source).

## Limits

- Only 100 ARC-AGI-1 puzzles and 3 runs; the authors concede this limits the visible size of gains. ARC-AGI-2 was not run, and one main model was used.
- Headline comparisons use a frozen memory built from human-written solutions rather than the agent's own experience, and only the OE format was used when memory was updated continually.
- Deciding which traces to keep requires feedback at test time (test cases); traces judged wrong are discarded.
- Compute is matched on attempts, not tokens: memory runs use more output tokens and the extra abstraction and selection calls are not obviously charged.
- Transfer is argued from the design (Figure 1) and not tested directly; memory is flat, with no consolidation, and the update order matters.
- A small specificity experiment (n=10) shows a trade-off: more detailed concepts solved more puzzles (4 of 10 at the highest detail) yet were harder to retrieve.

## See Also
- [[Memory Lifecycle]] — prerequisite-for
- [[Designed Memory vs Raw-Record Search]] — related (raw record versus designed memory)
- [[MemCollab Contrastive Cross-Model Memory]] — alternative-to (another abstract-entry memory, built from cross-model contrast)
- [[Memory Transfer Learning in Coding Agents]] — related (abstraction level and transfer)
