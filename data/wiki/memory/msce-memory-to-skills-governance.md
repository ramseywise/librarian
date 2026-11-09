---
title: "MSCE Memory-to-Skills Governance"
tags: [memory, pattern]
summary: "MSCE promotes procedural policies from layered memory into a skill library only with evidence from repeated episodes and a positive gain, and gates skill use by a reliability score; on EvoAgentBench its ablations rank flat retrieval worst and skill crystallization the most consistent component (self-reported, single run, vendor authors)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-06-tang-2026-memory-skills.md
---

# MSCE Memory-to-Skills Governance

MSCE (a 2026 preprint by authors from MemTensor (MemOS), per the extraction) builds skills from governed memory rather than distilling them straight from raw trajectories. The authors' stated worry is that a skill taken directly from raw trajectories may fit them too closely and fire in unsuitable situations.

## Mechanism

Memory has three layers: L1 grounded step traces, L2 procedural policies and L3 declarative environment cognition. A skill library sits downstream, each skill carrying a trigger, procedure, verification, boundary, evidence anchors, guidance and a reliability score. A policy is promoted to a skill only when it has evidence from at least two distinct episodes and a gain above zero. Skills move from probationary to active when reliability passes 0.6 and are archived below 0.2. Step values come from backfilling the reward, weighted by an LLM score of how faithful the agent's self-reflection is.

## Results

Setup: EvoAgentBench, GPT-5.2 backbone on the OpenClaw runtime, identical tools, budgets and task order for every method, Pass@1; a single run with small per-domain task counts. All figures are self-reported.

- Swapping MSCE for Flat Memory, a single unlayered store searched directly with neither gating nor skills, costs 15.38, 16.00 and 19.23 Pass@1 points on information retrieval, math and software engineering respectively.
- Removing skill crystallization costs 6.15 to 11.54 points and raises cost in every domain; dropping value calibration also lowers Pass@1 and increases cost everywhere.
- Against the strongest non-MSCE baseline, gains are 4.61 (information retrieval), 4.00 (math) and 15.39 (software engineering) points; on code it ties a skill-evolution baseline.
- Several baselines score below the vanilla agent in places (for example 26.92 against 38.46 on software engineering), which the extraction reads as naive memory or skill reuse sometimes hurting.
- Gains grow with accumulated experience, +13.84 to +17.00 points from none to full, and cross-domain transfer adds +2.56 to +5.13.

## Limits

- The authors call the values, gains and reliability heuristic governance signals, not causal credit estimates; five operators are prompted LLMs, and one runtime and backbone were used.
- No seeds, intervals or significance tests appear although the text says "significantly"; the Flat Memory arm also removes gating and L3, so the comparison confounds several factors, and raw trajectories, insights and skill files are not separate arms.

## See Also
- [[Memory Lifecycle]] — prerequisite-for
- [[Memory Forms Taxonomy]] — prerequisite-for
- [[Recuris Experiential and Working Memory]] — related (skill libraries and when they are invoked)
