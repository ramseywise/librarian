---
name: scope-initiative
description: "Take a named initiative and produce a Linear-ready technical backlog: failure modes, HMWs, research section, task backlog with acceptance criteria and t-shirt sizes, dependency mapping, and Linear hierarchy. Use when an initiative is named and agreed on."
disable-model-invocation: true
allowed-tools: Read Bash Grep Glob WebSearch Write
---

Scope the following initiative into a Linear-ready backlog: `$ARGUMENTS`

## Inputs (ask if not provided)

1. **Initiative name + one-line goal**
2. **Known failure modes** — 3-5 distinct ways the system currently fails (patterns, not symptoms)
3. **Brief or requirements doc**
4. **Existing assets** — prototypes, research, analogous systems
5. **Team roles available**
6. **MVP scope** — in vs out

## Sections

1. **Failure modes & HMWs** — table: # | Failure mode (`root cause -> symptom`) | Pain point | HMW. Every subsequent task traces to at least one failure mode.
2. **Research** — existing assets (reuse/adapt/reference), libraries per layer, technical unknowns (what each blocks), roadblocks + dependencies table.
3. **Task backlog** — initiative goal + MVP definition of done. Per task: goal, deliverable (concrete, not "implement X"), key work bullets, risks/questions, size (S/M/L/XL).
4. **Summary table + critical path** — # | Task | Failure mode | Size | Key dep | Owner | MVP? Plus: week-1 decisions, highest-risk dependency, tasks that must be designed together.
5. **Open questions** — numbered, each names who must answer. Categories: data access, infra, product, ownership, policy, phasing.
6. **Linear hierarchy** — Initiative → Projects (workstreams) → Issues (tasks) with acceptance criteria (Given/When/Then + metric + integration criterion) and blocking relationships.

## Task constraints

- Every deliverable is concrete (running system, document, dataset) — not "implement X"
- Every task traces to at least one failure mode
- T-shirt sizes: S (<1wk, few unknowns), M (1-2wk, some unknowns), L (2-4wk, significant unknowns), XL (>sprint, major decisions)
- Day-one decisions (embedding model, schema, vector store) appear first in critical path
