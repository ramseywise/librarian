---
title: Procedural Graphs
tags: [harness, pattern]
summary: "A procedural graph stores an agent's learned workflow as a small editable graph whose local neighbourhood is turned into guidance for a ReAct solver, and a gated loop evolves it from success and failure traces."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-lu-2026-procedural-graphs.md
---

# Procedural Graphs

Procedural Graphs (Lu et al., a September 2026 preprint) keep experience as an explicit graph of steps instead of retrieved trajectories. Nodes are actions; edges have four relation types and carry a condition, guidance text and pitfalls. Most graphs have 7 to 17 nodes, with one benchmark (BFCL) at 131.

## Mechanism

- Online: the active node is found by exact match on the agent's last action, the neighbourhood within two hops goes to a guidance model, and the resulting text is added to the solver's prompt. The solver stays free to ignore it. If matching fails, the whole graph is used.
- Offline evolution: contrast good and bad traces, propose add or delete edge edits, commit an edit only if the validation score is at least the current one, and keep a memory of rejected edits.

## Findings (self-reported)

- Six benchmarks, four models, against six memory baselines: first or joint first in 21 of 24 settings (19 wins, 2 ties, 3 losses against the strongest baseline). HotpotQA margins were tiny (-0.90 to +1.30).
- Local guidance beat injecting the raw graph or the full graph; full-graph guidance dropped ALFWorld to 54.48 from 81.53. Guidance still raised total tokens, though solver steps fell.
- Starting from only Start and End, gated evolution matched or beat a hand-built graph. A hand-built expert graph lowered MultiChallenge success from 87.50 to 58.93; one ungated static update lowered it to 53.57; the gated iterative loop reached 92.86.
- EnterpriseArena (up to 132 months): full-horizon survival rose from 44.0 to 58.0 for one model, 6.0 to 34.0 and 26.0 to 40.0 for two others. A ten-round trace on 20 episodes per split reached 85.0% test survival against 0.0%; the authors report the returned graph, not the best round (95.0%), to avoid selecting on test.

## Limits

- Table 2 and the ablations use one model and small splits (56 samples for MultiChallenge, 44 for GDPval); one run per cell.
- With 20 episodes per split, single accept or reject decisions turn on one or two episodes.
- The guidance model and refiner share the solver's LLM; weak-solver and strong-refiner is untested; transfer across solvers is untested.
- The judge is a model that is also among the solvers.
- The extraction did not read the 24-method comparison or the EnterpriseArena table.

## See Also
- [[Harness Engineering]] — prerequisite-for
- [[Harness Continual Learning]] — related
- [[Knowledge Graph as Shared Agent Memory]] — related
- [[Verification Loops]] — related
