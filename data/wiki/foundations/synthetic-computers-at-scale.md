---
title: Synthetic Computers at Scale
tags: [foundations, llm, pattern]
summary: "A pipeline that turns personas into synthetic computers with files, collaborators and a month of simulated work, then distils skills from run retrospectives; the skills lifted a held-out score from 61.6% to 68.6% (self-reported) with no weight updates."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-ge-2026-synthetic-computers-scale-long-horizon.md
---

# Synthetic Computers at Scale

A Microsoft technical report (April 2026) argues that synthetic data for long-horizon productivity agents must supply the working context, not only the task. It builds that context as a whole simulated computer.

## Pipeline

- **Computer creation.** A persona becomes a user profile, then a filesystem policy, then a file plan with a dependency graph; artifacts are written in topological order. 1,000 personas gave 1,000 computers, with file counts rising from about 112 to about 197 per computer on average.
- **Simulation.** Each computer simulates roughly a month of work: 20 working days and 5 deliverables, organised as a weekly plan and one agent session per day, with simulated collaborators. A run averages 2,272 turns over 8.59 hours, compared with 31 turns for a GDPVal task (self-reported).
- **Rubrics.** Built from five repeat runs of one setting and merged by an LLM judge; baseline scores mostly sit between 60% and 80%. Used for evaluation only, not as an RL reward.
- **Retrospectives to skills.** After each run the agent's process is reviewed. One appendix example found cross-document inconsistency across every deliverable, uncorrected collaborator-flagged errors, blank messages late in the run, missing components and a page-count shortfall. Occupation skills are distilled from such reports and given to the agent as external instructions.

## Results (self-reported)

Setup: Claude Code SDK with a Sonnet-class work agent, 900 training and 100 held-out synthetic computers, an Opus-class judge, no seeds or intervals reported.

- Skill-augmented 68.6% against 61.6% baseline (+7.0 points); better on 83 of 100 paired computers.
- Skills from 100, 500 and 900 computers won on 64%, 75% and 83% of test computers; 10 computers gave no gain.
- On GDPVal (220 tasks, pairwise judged), wins/ties/losses were 105/48/67 for the Sonnet-class agent, 104/36/80 for Haiku-class and 99/50/71 for Opus-class; the Haiku-class result is not significant two-sided.

## Limits

- No weights were trained; RL and distillation are proposed future work, so the claim that this is a substrate for agentic RL is argued, not demonstrated.
- Generator, agent and judge are all from one vendor family and the judge is unvalidated against humans. Test and training computers share a persona distribution; no random-skill or generic-skill control.
- The authors concede uniform artifact style, overly clean filesystems and mostly reactive collaborators. The 1,000 simulations are not released, only 100 computers and 500 retrospectives.

## See Also

- [[Post-Training for Agents]] — prerequisite-for
- [[Skill Authoring Discipline]] — related (how skills are written)
- [[Harness Continual Learning]] — related
- [[AutoGym Blueprint-First Verifiable Gyms]] — related
