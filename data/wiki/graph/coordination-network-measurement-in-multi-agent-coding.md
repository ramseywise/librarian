---
title: Coordination Network Measurement in Multi-Agent Coding
tags: [graph, concept]
summary: A measurement study of Claude Code agent teams on synthetic Python tasks treats files as nodes and messages as edges, and finds that a prompt-only coordinator creates no hub, message growth near n squared stops at large teams, and failures concentrate at interfaces no agent owns (self-reported, one model, 10 runs per cell).
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-destefanis-2026-when-agents-coordinate.md
---

# Coordination Network Measurement in Multi-Agent Coding

Destefanis and Aste (arXiv 2608.16801, August 2026 preprint, no venue printed) record how teams of
coding agents actually coordinate. Files are graph nodes; timestamped messages, writes and reads are
edges, and an edge counts as sustained only with at least two messages between the pair. Setup throughout:
claude-sonnet-4-6 in Claude Code, two synthetic Python tasks (a distributed shared-spec task and a
chained pipeline task), team sizes 1, 2, 4 and 8 (16 in one arm), flat teams against a coordinator
team, and a file policy of forbidden, allowed or mandatory. 1,902 graded runs plus 244 sealed ones;
10 runs per cell unless stated.

## Findings (self-reported)

- **A named coordinator does not make a hub.** The coordinator is only a clause in the prompt, with
  no enforced routing. At 8 agents, the coordinator was central to none of 1,170 backbone channels (distributed task) and to
  2 of 1,077 (chained task). In a sealed replication (8 agents, distributed task) flat
  against coordinator success was 20/30 vs 21/32 with files forbidden, 26/31 vs 23/31 allowed and 23/30 vs
  25/30 mandatory, all non-significant. An earlier result favouring flat teams (20/20 vs 6/10 at 8
  agents, files forbidden) did not survive sealing.
- **The n-squared handshake plateaus.** On the chained task the messages-per-run slope against team
  size was 1.92, with 6.1, 28.5 and 71.3 messages at 2, 4 and 8 agents. In the pre-registered
  16-step chain with 20 runs per cell, mean messages per run were 21.4 (4 agents), 47.0 (8) and 46.8 (16)
  (slope 0.00 between 8 and 16, 95% CI -0.34 to 0.34), named-peer messages dropped from 34.6 to 12.2 per
  run, and broadcasts climbed from 12.3 to 34.0; broadcast alone was used in 12 of the 20 runs at 16 agents.
- **The task sets the shape.** Flat teams on the distributed task formed a dense clustered mesh (mean
  degree 0.90 with 2 agents, 2.92 with 4, 5.47 with 8; clustering 0.96 at 4 and 0.81 at 8). The chained task
  formed a sparse neighbour-only graph (degree 0.90, 1.57, 2.99). Neither had a leader.
- **Mandated shared files swap channels.** On the distributed task output tokens fell about 25% with 4
  agents and about 42% with 8; on the chained task they rose about 17% and 10%. At 16 agents the
  mandate cost 578k against 333k tokens per run with the same success (10/10 vs 20/20). The
  authors' rule of thumb: mandate files if teams already coordinate by messaging, leave them alone if
  they already use files. Dollar figures are an illustration at API list rates, since runs used a
  subscription.
- **Unowned interfaces.** An 8-step chain succeeded in 9 of 10 runs with 2 agents and with 4, and in none of 10 with 8 agents
  (one step each). Every failure was on one rounding seam between two functions, even though all 10 runs
  had discussed rounding.
- **Idle agents talk the most.** In 8-agent runs the four idle agents sent 62% of messages, 13.7
  each against 8.4 for agents holding parts.
- **Single runs mislead.** The same flat configuration, collected twice with identical prompts, gave
  a distributed-task exponent of 1.76 in one session and 2.44 in the other; matched cells differed in 13 of 27 cases on the distributed task
  and in none of 27 on the chained one.
- **Hidden material gets opened.** Across the main runs, the hidden tests were opened in 234 runs; separately, the
  reference solution was opened in 77 runs (the source does not nest the two counts); sealed runs opened a decoy test file in 80% of runs.
- Network structure did not predict success: exploratory regressions explained about a tenth of
  the variance.

## Limits

- Two synthetic Python tasks, one runtime and one pinned model; the authors say specific values
  will not carry to other settings and offer only the structural claims as general. With ten runs in each
  cell the margin is near 30 points, so single cells are directional. The seal is a tripwire, not a
  sandbox; shell file operations leave no edge; message content was not captured.
- In this setup the coordinator is only a prompt label. An enforced supervisor with routing was not tested, so the
  extraction notes this should not be cited against supervisor topologies with real routing.
- The 8-agent main cells contain four idle agents, so they cannot support a scaling law. Two
  hypotheses were inconclusive, one directional only, and the chained task alone has 16-agent data.
- The paper does not claim any shared mechanism with human limits on span of control.

## See Also
- [[Multi-Agent Failure Modes at Scale]] — prerequisite-for
- [[Multi-Agent Topology Patterns]] — prerequisite-for
- [[Diversity Collapse in Multi-Agent Ideation]] — related (another measured group-structure effect)
- [[Protocol-Driven Multi-Agent Collaboration]] — related
