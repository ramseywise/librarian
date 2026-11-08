---
title: AutoScientists Self-Organizing Teams
tags: [harness, pattern]
summary: "AutoScientists runs a decentralised team of research agents over a shared state with a noise-aware promotion gate; its gain over a single agent is domain-dependent and every removed mechanism hurts on at least one task."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-gao-2026-autoscientists.md
---

# AutoScientists Self-Organizing Teams

AutoScientists (Gao, Fang and Zitnik, a May 2026 preprint) replaces a single autoresearch agent with a team that organises itself: analysts and experiment agents read and write shared state, including a ledger of dead ends, and results are promoted only when they clear a noise-aware gate (the extraction describes a two-standard-deviation rule).

## Findings (self-reported)

- BioML-Bench, 24 tasks, Claude agents, 4 hours on one GPU per task (3 analysts, 6 experiment agents): 74.40% mean leaderboard percentile against 66.07% for a single-agent autoresearch loop. Drug discovery gained most (64.52 against 46.16, n=9); protein engineering was tied at 96.97; imaging differences were inside the standard error.
- nanochat: reached a validation bpb of about 0.978 in 34 experiments against 65 for the single agent (per experiment, not wall-clock). Starting from the team's own champion, it accepted 7 of 93 experiments while the single agent accepted none of 100; one run each.
- Seeded with a strong protein-fitness baseline, it found an extension that lifted average Spearman from 0.657 to 0.700 over 217 assays, tuned on one assay.
- Ablations on four tasks (one run per condition): removing analysts, cross-agent sharing or self-organisation each hurt somewhere, and the damaging component differed by task. Without shared state, five of six independent agents rediscovered the same first win within two experiments.
- Crew size is task-dependent; 14 agents was worse than 9 on every task tested.

## Limits

- Table S3 has a caption mismatch in the extraction.
- Run-to-run spread is moderate (nanochat final bpb SD 0.0010 over three runs; hERG SD 0.020).
- On BioML-Bench the other baselines are published figures from a different protocol (CPU only, eight hours); just the single-agent loop and Biomni were re-run under the team's setting.
- The 3.25x parallel speed-up is a projection, because agents actually ran one after another. Cost is also higher than the main text implies.

## See Also
- [[Multi-Agent Topology Patterns]] — prerequisite-for
- [[Long-Horizon Execution]] — prerequisite-for
- [[AiScientist File-as-Bus]] — alternative-to
- [[Harness Continual Learning]] — related
