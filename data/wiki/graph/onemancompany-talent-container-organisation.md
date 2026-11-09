---
title: OneManCompany Talent Container Organisation
tags: [graph, concept]
summary: "OneManCompany (OMC) organises heterogeneous agents as a company, with a manager tree plus dependency DAG, an explore-execute-review loop and portable Talent identities; it reports 84.67 percent on PRDBench but ablates none of its components (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-yu-2026-skills-talent.md
---

# OneManCompany Talent Container Organisation

Yu et al. (arXiv 2604.22446, April 2026, preprint, authors' own system). OMC frames a multi-agent team as a company: a human CEO supplies requirements, a founding team (HR, EA, COO, CSO) runs it, and employees are agents of different kinds.

## Mechanism

- **Task graph.** A hierarchical manager tree plus dependency edges. Decomposition edges make a strict tree, dependency edges can cross sibling branches, and the whole must remain a DAG, enforced by cycle detection when an edge is added. A supervisor sets decomposition granularity and employee assignment.
- **Explore, execute, review (E2R).** Five actions: decompose, assign, recruit, review, iterate. The paper calls it MCTS-inspired in structure only: there are no rollouts and no UCB, review is the supervisor explicitly accepting or rejecting, and the policy is the supervisor LLM rather than a learned one.
- **Review gate with AND semantics.** A node resolves only when all children resolve, and a task moves from completed to accepted only after supervisor review, so dependents are not unblocked by an unchecked result. Rejection triggers re-decomposition.
- **Safeguards.** Seven invariants (crash recovery, acyclicity, one running task per employee, idempotent scheduling, termination of review, and completeness of cascades and dependencies), a review limit of 3 rounds before escalation, a 3,600 s task timeout, a cost budget that pauses work, and a deadlock detector. The extraction describes the "formal guarantees" as arguments about the design that come with no checkable proof.
- **Talent and Container split.** Each employee's identity (portable: principles, role prompts, skills, tools) lives apart from the runtime that executes it (LangGraph, Claude Code or a script), joined by six typed interfaces. Recruitment goes through a talent market that HR queries, with human CEO approval of the shortlist. HR reviews employees every three projects, with a performance plan after three consecutive failures. Self-evolution edits Talent artefacts, not weights, and is not ablated.

## Results (self-reported)

- PRDBench, 50 project-level tasks, official DEV mode (one-shot document, no feedback): 84.67% success, 15.48 points above the best baseline, at $345.59 for the 50 tasks (about $6.91 per task). The team consisted of recruited Claude Code employees plus a founding agent, built with LangGraph, running on Gemini Flash Lite Preview.
- Baselines in the same table were copied from PRDBench, not rerun; from lowest to highest: Gemini CLI 11.29, Claude Code 56.65, CodeX 62.09, GPT-5.2 62.49 and Claude-4.5 minimal 69.19. Baseline cost is not reported.
- Case studies are single runs: a GitHub trend report about $4.48, an audiobook $1.57, a research survey $16.26.

## Limits

- The authors concede the only quantitative evaluation is PRDBench, no non-coding benchmark exists, self-evolution is not ablated, and cost is high.
- The extraction notes that the tree, the review gate and the mixed-model team were never ablated; there is no single-agent control on the same backend; baselines were copied with their cost unknown; each task ran once with no variance; and a human approves the shortlist, so the organisation is only semi-self-organising. Convergence depends on human judgment.
- Internal inconsistency: Table 2 labels the system with Gemini 3.1 Flash Lite Preview while the setup text says Gemini 2.1; the Figure 12 caption says 18 deliverables where the figure label says 17. Model names will date quickly.

## See Also
- [[Graph Topology Primitives]] — prerequisite-for
- [[Multi-Agent Topology Patterns]] — prerequisite-for
- [[Harness Orchestration]] — related
- [[Graph Governance and Attribution]] — related
