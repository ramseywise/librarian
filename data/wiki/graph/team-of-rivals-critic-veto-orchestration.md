---
title: Team of Rivals Critic-Veto Orchestration
tags: [graph, pattern]
summary: A vendor case study of planners, executors and critics with strict roles, where critics hold a veto against pre-declared acceptance criteria and tool calls run in a remote executor that returns only schemas and summaries.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-vijayaraghavan-2026-if-you-want-coherence-orchestrate.md
---

# Team of Rivals Critic-Veto Orchestration

The Team of Rivals paper (Vijayaraghavan et al., Isotopes AI, a vendor; arXiv preprint, January 2026) argues reliability comes from how agents are organised, not from a stronger single agent. The authors built and evaluated their own system, so the numbers below are self-reported.

## Mechanism

- **Roles:** planners, executors and critics hold strict roles with opposing incentives.
- **Veto, not vote:** a critic has hierarchical veto and checks work against acceptance criteria declared in advance. The paper's phrase is "errors should die in committee".
- **Context firewall:** agents write code, a remote executor runs it against real data, and only schemas and summaries return to agent context.
- **Different models:** the paper puts critics on models other than the writers', aiming at what it calls cognitive diversity.
- **Why not naive sub-agents:** the paper argues that sub-agents cannot see sibling work, so one assuming a December fiscal year-end and another March hand the parent conflicting outputs with no visible assumptions. It cites Cognition's analysis for this and does not test it.

## Reported numbers (self-reported)

- **Production sessions:** 522 financial-analysis sessions. 130 (24.9%) passed first time; the inner loop recovered 344 (337 via Code Critique, 7 via Chart Critique); Output Critique rescued a further 7; and 41 (7.9%) were rejected by users, giving 92.1% (481/522) overall. "Success" means the user did not disapprove, and there is no control arm on those sessions.
- **Controlled comparison:** one task, reconciling 9 invoices against a QuickBooks Online expense report with a $40 discrepancy. A single agent was right in 6 of 10 trials (60%) and confident in all 10. Asking it to self-verify, 5 trials, flipped 3 from correct to incorrect. The multi-agent arm scored 90% (18/20) in 4.2 minutes against 1-2. Neither arm has its model named in the paper.
- **Cost:** over the 392 sessions that needed recovery, recovery cost an additional 38.6% in credits and 21.8% in active time. Level 3 sessions are 28% of sessions and 68% of recovery credits. Cost is in unitless credits.
- **Catch rates:** Among sessions reaching it, Code Critique catches 86.0% of errors and Chart Critique 1.8%; Output Critique catches 14.6% of the 48 sessions that got that far. The Code and Chart critics fired on disjoint sessions (385 and 7), which the authors read as support for orthogonal critics.
- **Projection:** adding a fourth critic equal in strength to Output Critique would lower the escape rate from 7.9% to 6.7%; this is projected, not tested.

## Limits

- Finance tasks only; no public benchmark or dataset; n=10 and n=20 with no confidence intervals; transcripts are only a short link.
- There is no ablation. Nothing removes the planner, swaps in a critic from the writer's own model, or sets veto against voting, so the cognitive-diversity claim stands untested; the benefit of the context firewall is likewise never isolated.
- The 522-session success is user approval, not ground truth, and critic false positives are not measured. The authors concede finance-only scope, cost at scale, sequential latency per critic layer and a floor of about 7% escapes.
- The baseline is one agent set against a council of critics, never sub-agents, so the argument against naive fan-out is not tested.
- The extraction notes that the paper's baseline error rate of 75% matches the 24.9% clean first pass, and that the 90 against 60 percent result is one task with unnamed models and should not be cited as general.

## See Also
- [[Multi-Agent Topology Patterns]] — related
- [[Verification Loops]] — related (self-verification degraded accuracy in the paper's one controlled task)
- [[Multi-Agent Failure Modes at Scale]] — related
- [[Harness Orchestration]] — related
