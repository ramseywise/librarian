---
title: Agensh Orchestrator-Free Agent Scaling
tags: [graph, pattern]
summary: A Microsoft Research harness where peer workers coordinate through a Git workspace, chat and an append-only shared context with no central orchestrator, scaled from 1 to 1,024 agents on ProgramBench tasks.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-zhan-2026-agensh.md
---

# Agensh Orchestrator-Free Agent Scaling

Agensh (Zhan et al., Microsoft Research, an arXiv technical report) claims that many agents can run in one harness without a central orchestrator, and treats agent count as a scaling dimension. All results are the authors' own.

## Mechanism

- **Worker loop:** each agent collects context, claims a sub-task, acts, verifies the result and merges it.
- **Shared pieces:** Gitea provides the Git workspace, Mattermost the chat interface, and a third piece is an append-only board of shared context whose idea comes from DeLM. The board takes typed entries; the paper's prompt calls a FAIL entry for a falsified hypothesis the highest-value one because it stops peers spending budget on it.
- **Motivation:** the paper argues, citing other work, that an orchestrator's capacity limits how far a system can scale. It does not measure this.

## Reported numbers (self-reported)

Setup: model GPT-5.6-sol with high reasoning effort; the single-agent baseline harness is Copilot. Tasks are five from ProgramBench (200 in total) that the authors call hardest: FFmpeg, gromacs, pandoc, PHP-src and ctags. Each is rebuilt from scratch with no internet access, for 6 hours a run, and scored by the canonical kept-tests pass rate.

- Mean pass rate over the 5 tasks climbs with agent count: 19.31% (1 agent), 20.68% (8), 26.52% (32) and 28.78% (128), a gain of 9.47 points, about 49% relative.
- Pandoc, latency: 128 agents reach 30% at 30 minutes, 32 agents at 60 minutes, 8 agents at 90 minutes; one agent stays under 30% for 2 hours.
- On pandoc alone the pass rate goes from 33.89% with one agent to 50.94% with 128 and 55.06% with 1,024 (16 nodes, 64 agents on each).
- Trajectory reading, anecdotal and uncounted: 8 agents agree interfaces, 32 review and withdraw approvals, 128 pick reviewers by experience and settle an integration protocol, and at 1,024 several workers act as integrators.

## Limits

- No cost, token spend, run count or variance; figures look like single runs per cell.
- No ablation: nothing isolates shared context, messaging or the Git workspace, and there is no orchestrator-worker baseline, so the orchestrator-bottleneck claim is cited, not shown.
- Only one benchmark family, one model and one harness are used, and the 1,024-agent point comes from a single task.
- Gains flatten: going to 8 agents adds about 1.4 points, while moving from 128 to 1,024 agents adds 4.12 points at eight times the agent count. Per-agent efficiency, duplicated work and stalled agents are not quantified.
- Disclosed run aids: the single-agent baseline needed a stop hook to use 6 hours, and scaled runs used staggered starts and time reminders.
- According to the extraction, the paper says nothing on using subagents as context firewalls, on separating roles, or on when to avoid multi-agent designs.

## See Also
- [[Multi-Agent Topology Patterns]] — related (a peer topology at scale)
- [[Team of Rivals Critic-Veto Orchestration]] — alternative-to
- [[Harness Anatomy]] — related (shared state and event-driven runtime)
