---
name: design-sprint
description: "Run a full design sprint for any use case — deconstruct problems and pain points, generate HMW statements, define technical solutions, cluster into workstreams, map dependencies, and produce an initiative backlog. Use when starting a new product, feature, or platform initiative from scratch."
disable-model-invocation: true
allowed-tools: Read Bash Grep Glob WebSearch Write
---

Run a full design sprint using IDEO / Stanford d.school HMW methodology for: `$ARGUMENTS`

## Inputs (ask if not provided)

1. **Use case** — product, feature, or problem space
2. **Known constraints** — market, language, tech stack, team roles
3. **Existing data** — research, ticket data, prototypes, production metrics
4. **Scope boundary** — what is explicitly out of scope

## Phases

1. **Deconstruct** — problems, pain points, insights, opportunities. Table: Area | Finding | Implication.
2. **HMW statements** — reframe each finding as a How Might We question. Outcome-oriented, not solution-prescribing.
3. **Technical solutions** — for each HMW: what's required + concrete named technical approach.
4. **Workstream clustering** — group by WHO (FE), WHERE-BE, WHERE-AI, WHERE-data, WHY (observability), WHERE-Ops. Note cross-cluster items.
5. **Initiative definition** — 5-7 named initiatives. Each: name, one-sentence goal, components, roles, cross-initiative dependencies. First initiative has zero external deps.
6. **Dependency mapping** — HTML artifact per initiative: cards with title, description, needs, enables, role badge. Color-coded by role.

## Quality constraints

- Be specific to the use case — no generic outputs that could apply to anything
- Use real numbers, benchmarks, and named tools where they exist
- Cite analogous systems or prior art
- If multilingual requirements exist, call them out as day-one decisions
