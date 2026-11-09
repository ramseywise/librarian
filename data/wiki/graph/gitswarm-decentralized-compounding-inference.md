---
title: GitSwarm Decentralized Compounding Inference
tags: [graph, pattern]
summary: "GitSwarm has identical workers coordinate only through a shared, branchable Git repo in which every commit declares the earlier work it drew on; on a 50-task ProgramBench subset it scored 79.4% against 65.1% for one agent prompted to keep going (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-shah-2026-gitswarm.md
---

# GitSwarm Decentralized Compounding Inference

Shah et al. (arXiv 2610.04862, October 2026, preprint without a venue). No central planner and no assigned roles. Identical workers run without waiting on one another, each in its own isolated worktree, up to a concurrency cap; every episode ends as a contribution, a nomination or an abstention. The harness only schedules and validates.

## Mechanism

- **Commits carry two kinds of parent.** Each commit has a physical Git parent and a mandatory `informed_by=` list naming the semantic sources it used. A worker can therefore inherit one branch while using discoveries from other branches, with no merge. The graph's edges are the Git-parent edges plus one extra edge for each `informed_by` source beyond the parent.
- **Two read-only views, neither assigns work.** `gs_dashboard` reports the remaining budget, how many workers are running, and the nomination count. `gs_inflight` is a shared log where a worker states its scope plus success and abort criteria before it edits anything.
- **Decentralised readout.** Workers nominate candidates and the harness takes the commit with the most nominations, with a deterministic tie-break. Nomination records sit outside the computation graph. This readout is used for the benchmarks, not the research tasks.

## Results (all self-reported)

- ProgramBench (a stratified 50-task subset of 200 tasks; workers are Codex GPT-5.5-high, 5 at a time, with budgets between 100 and 500 charged episodes): 79.4% for the swarm against 65.1% for "Forced Codex" (one agent re-prompted to keep going) at similar compute. The score climbed from 73.1% at a budget of 100 to 79.4% at 500; returns diminished and input-token cost grew with repository size.
- IMOProofBench-Advanced, 30 proof problems, one run: GPT-5.5-high workers solved 30 of 30 (28 at budget 20, 30 at budgets 40 and 80). The authors say Best-of-N with an oracle verifier also reaches the ceiling at lower token use, so this does not show a unique advantage.
- Research tasks, each with its own setup. Residual Matrix Transformer (12 Codex workers, 72 h, 8 H200 GPUs, a cap of 350M parameters, 1.3B training tokens): the two swarms finished with 2.890 and 2.894 on held-out loss (the reference: 3.147). Four of the six final changes originated on other branches; an idea about previous-token memory that had failed was taken up again 49.5 h later and turned into a temporal mixer. Looped Transformer (12 workers, 48 h, runs not finished at writing): dev loss 3.187 versus 3.265 for the reference; 74% of the negative results were cited afterwards. NanoChat (20 workers, 16 GPUs, 5-minute training clock, first 24 active hours): validation bits per byte dropped from 0.993 to 0.905; 70.1% of negative research commits were cited afterwards.
- Reuse, measured from traces: 99.9% of eligible ProgramBench episodes and 96.2% of proof episodes reference prior work; ProgramBench contributions get built on 94.7% of the time, proofs 44.4%. Git-parent ancestry accounts for only about a quarter of the graph.
- Roles appear without being assigned: proof episodes spent on selection grow from 44.2% of the total at budget 20 to 69.7% at 160, and roughly one ProgramBench worker in six abstains as redundant. Of 1,421 abstention traces that could be adjudicated, 94.9% were judged justified, yet abstainers still consume 6 to 7% of ProgramBench tokens.
- Design comparison on 9 ProgramBench dev tasks (GPT-5.5-medium, budget 50, 3 seeds): the asynchronous design scored 62.06% in 38.0 min and synchronous waves 63.11% in 49.3 min; decentralised nomination scored 62.06%, a central selector 64.40% (34.9 min) and a central aggregator 58.19%. The authors say three seeds is too few for a conclusion either way.

## Limits

- The gains are not causally tied to the design; the authors state that showing persistence, branchability or `informed_by` caused them would need a matched-run intervention, which was not run. A worker declares `informed_by` itself, so it proves nothing about influence, and trace-based reuse shows only observed use.
- The perfect proof result is one run. The ProgramBench set is a 50-task subset; the design comparisons use three seeds and do not establish equivalence.
- The single-agent comparators on the research tasks spent more tokens than the swarm's budget, the seeded run starts from earlier research, and the NanoChat runs being compared use different starting checkpoints and GPU counts.
- The harness still schedules, validates and reads out, so "decentralised" refers to intellectual control only. Nobody has yet evaluated at matched compute over a long horizon. Model names are as printed in the paper.
- The extraction did not read several appendices and warns that some figure text may be missing.

## See Also
- [[Graph Topology Primitives]] — prerequisite-for
- [[CAID Centralized Asynchronous Isolated Delegation]] — alternative-to (central manager over isolated workers)
- [[Knowledge Graph as Shared Agent Memory]] — related
- [[Multi-Agent Topology Patterns]] — prerequisite-for
