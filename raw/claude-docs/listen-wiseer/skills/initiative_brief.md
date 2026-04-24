---
name: initiative_brief
description: "Write a structured initiative brief for a new product or platform initiative. Covers the HMW framing, existing assets, technical unknowns, roadblocks, task backlog with sizing and ownership, dependency summary, and open questions. Use when a design sprint has produced workstream clusters and you need to convert them into an actionable brief document for sprint planning."
---

Write an initiative brief for: $ARGUMENTS

## Before starting

Check what inputs are available:
- If a design sprint output (HMW statements, workstream clusters, initiative definitions) exists — read it and use it as input
- If no prior design sprint — ask for: (1) initiative name and goal, (2) known constraints, (3) existing assets, (4) team roles available, (5) scope boundary

---

## Brief structure

Produce the brief in this order. Present each section and ask for confirmation before continuing.

### 1. Why — the HMW

- 2–3 core failure modes or pain points the initiative solves
- One HMW statement per failure mode
- North star connection: how this initiative enables a measurable product outcome

### 2. Research — existing assets, libraries, unknowns, roadblocks

**Existing internal assets**: what is already built or available that is relevant. Include prior prototypes, existing data sources, and production baselines with their metrics.

**Libraries and tools under consideration**: for each layer (embedding, retrieval, reranker, vector store, agent graph, evaluation, tracing), list options with tradeoffs. Be specific: latency numbers, cost, GPU requirements, data residency concerns.

**Technical unknowns**: list each open technical question with what it blocks if unresolved.

**Roadblocks and dependencies**: table with columns: Dependency | Blocks | Owner | Status.

### 3. What — backlog

**Initiative goal**: one paragraph. What gets built, for whom, and how success is defined.
**Definition of done for MVP**: bullet list of measurable acceptance criteria.

Then 6–9 tasks, each with:
- **Goal**: what this task achieves
- **Deliverable**: concrete artifact (running service, agreed document, validated dataset)
- **Key work**: 4–6 bullet points of the actual work
- **Risks and questions**: open questions and risks specific to this task, not generic
- **Size**: XS / S / M / L / XL

### 4. Summary table

| # | Task | Size | Key dependency | Owner |

### 5. Critical path

One paragraph naming the 2–3 hardest sequential dependencies. Identify the single highest-risk dependency.

### 6. Open questions requiring answers before sprint planning

Numbered list. Each question names who must answer it.

---

## Quality rules

- Every task deliverable must be a concrete artifact, not "complete implementation of X"
- Every risk must be specific to this initiative — no generic "scope creep" risks
- Dependencies between tasks must be explicit — if Task 5 needs Task 2's output, say so
- Technical unknowns that are day-one blockers must be called out as such
- Multilingual or multi-market requirements must be flagged as day-one decisions
- Data access dependencies (ticket data, CMS, API access) are almost always the highest-risk — call them out first
