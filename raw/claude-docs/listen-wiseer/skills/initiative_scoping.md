# Initiative Scoping — SKILL.md

## Purpose

Take a named initiative from a design sprint (or any other source) and produce a
Linear-ready technical backlog: failure modes, HMWs, research section, task backlog
with acceptance criteria and t-shirt sizes, dependency graph, and Linear hierarchy.

The answer quality initiative in the help-assistant project is the reference example
for this skill. Every structural decision here is grounded in that output.

---

## When to use this skill

- A named initiative exists (from a design sprint, a brief, or a planning meeting)
  and needs to be broken into buildable tasks before sprint planning
- You need to cross-reference existing research docs, phase plans, or prototype
  findings to gap-check a backlog before it is committed
- You need to produce a Linear-ready structure (initiative → projects → issues)
  with blocking relationships between issues
- An engineer needs to present their initiative to the team with full context:
  why we are doing this, what we already know, what we are building, and what
  could go wrong

---

## Inputs required before starting

Ask for these if not already provided:

1. **Initiative name and one-line goal** — what does this initiative deliver?
2. **Known failure modes** — what are the distinct ways the system currently fails
   in this area? Aim for 3–5. Each should be named as a pattern, not a symptom
   (e.g. "corpus quality → coverage without noise" not "bad retrieval")
3. **Brief or requirements doc** — paste or reference the relevant sections
4. **Existing assets** — prior prototypes, research docs, phase plans, analogous
   systems. These are used to gap-check the backlog.
5. **Team roles available** — FE / BE / AI Eng / Ops / Analytics
6. **MVP scope** — what is explicitly in vs out for the first delivery?

---

## Output structure

Produce all five sections in order.

---

## Section 1 — Failure modes and HMWs

For each known failure mode, produce a row in this table:

| # | Failure mode | Pain point | HMW |
|---|---|---|---|

Rules:
- Failure mode name follows the pattern: `root cause → observed symptom`
  e.g. "context augmentation → personalisation", "reactive monitoring → proactive grounding"
- Pain point is one sentence: what the user or agent experiences when this fails
- HMW is outcome-oriented, not solution-prescribing, phrased positively
- Every subsequent task in the backlog must trace back to at least one failure mode

Also state the core problem in one paragraph: why this initiative is the enabling
layer for the product objectives it serves.

---

## Section 2 — Research

Three sub-sections:

### Existing internal assets
Table with columns: Asset | Status | Relevance

Include: prior prototypes, production systems being replaced, datasets, codebases,
benchmark baselines. For each, state explicitly whether it can be reused directly,
adapted, or only used as reference — and why.

### Libraries and tools under consideration
Table with columns: Layer | Option | Notes

Cover every technical layer: embedding model, retrieval, reranking, vector store,
agent graph, evaluation, tracing, session storage, query rewriting. For each option
note the key trade-off (cost, latency, data residency, GPU requirement, etc.).

Flag the tracing backend decision explicitly — it affects multiple tasks and is
often decided by default rather than intentionally.

### Technical unknowns and roadblocks
Two sub-sections:

**Technical unknowns** — decisions that must be made before implementation begins
and that are currently unresolved. Format: one bullet per unknown, stating what
the unknown is and what it blocks.

**Roadblocks and dependencies** — table with columns:
Dependency | Blocks | Owner | Status

Flag the highest-risk dependency explicitly. For most AI initiatives this is data
access (historical ticket data, golden dataset source). Without it the eval harness
has no baseline and the MVP has no measurable definition of done.

---

## Section 3 — Task backlog

### Initiative goal
One paragraph: what does done look like? Include 3–5 measurable criteria that
constitute the MVP definition of done (e.g. hallucination rate <5%, hit rate ≥60%,
citation coverage 100%).

### One task block per task

Each task follows this exact structure:

```
### Task N — [descriptive name]
*Failure mode: [which failure mode(s) this addresses]*

**Goal:** One sentence — what problem does this task solve?

**Deliverable:** What exists when this task is done? Be concrete.
A running service, a validated model, an agreed schema document, a dataset.
Not "implement X" — "X running in production doing Y".

**Key work:**
- Bullet list of the major implementation steps
- Each bullet is a concrete action, not a category
- Include library/tool choices where they are already decided
- Flag cross-team interface points explicitly

**Risks and questions:**
- What could go wrong or block this task?
- What decisions are still open that affect this task?
- What cross-team alignment is needed before this task can be completed?

**Size: S / M / L / XL**
```

T-shirt size guide:
- S — one engineer, less than a week, few unknowns
- M — one engineer, one to two weeks, some unknowns or cross-team coordination
- L — one or two engineers, two to four weeks, significant unknowns or
  sequential dependencies
- XL — multiple engineers, more than a sprint, major architectural decisions
  or blocked on external dependencies

### Task ordering rules
- Tasks that are prerequisites for everything else (schema decisions, model
  selection, data access) go first regardless of size
- Day-one decisions that are expensive to change later (embedding model,
  vector store, metadata schema) must be called out explicitly in the critical path
- Post-MVP tasks are included in the backlog but clearly labelled — they inform
  architecture decisions even if not built immediately

---

## Section 4 — Summary table and critical path

### Summary table
Columns: # | Task | Failure mode | Size | Key dependency | Owner | MVP?

### Critical path
One paragraph naming:
- The week-1 decisions that block everything else
- The highest-risk external dependency
- Any tasks that must be designed together even if delivered sequentially
- The threshold condition for any post-MVP tasks that are conditional on
  production data (e.g. "introduce CRAG only if escalation rate >20%")

### Linear project grouping
Table mapping Linear projects to task numbers and failure modes.
Each Linear project should be a coherent workstream a single sub-team could own.

---

## Section 5 — Open questions

Numbered list of questions that must be answered before sprint planning can
happen meaningfully. Format each as a direct question to a named role or team.

Categories to cover:
- Data access (blocking for golden dataset and intent taxonomy)
- Infrastructure (GPU, vector store, ops provisioning)
- Product decisions (unsupported scenario list, automation boundary)
- Ownership (API contracts, cross-team interfaces)
- Policy (data residency, GDPR, PII handling)
- Phasing (what ships in MVP vs iteration 1)

---

## Linear hierarchy

Map the output to Linear as follows:

```
Initiative (Linear initiative)
  └── Project 1 — [workstream name]  (Linear project)
        ├── Issue: Task N — [name]   (Linear issue)
        │     - Description: goal + deliverable
        │     - Acceptance criteria: measurable conditions from deliverable
        │     - Estimate: t-shirt size
        │     - Blocking: [Task M] (if applicable)
        └── Issue: Task M — [name]
  └── Project 2 — [workstream name]
        └── ...
```

### Acceptance criteria format
For each issue, acceptance criteria follow the format:
- Given [condition], when [action], then [measurable outcome]
- Include at least one metric-based criterion where possible
  (e.g. "hit rate ≥60% on golden dataset", "zero wrong-market answers on test set")
- Include at least one integration criterion
  (e.g. "API contract agreed and documented with BE before FE starts")

### Blocking relationships
An issue blocks another when the blocked issue cannot be started without it.
Distinguish from soft dependencies (informed by, but not blocked):
- Hard block: Task 4 cannot start until Task 2 is merged
- Soft dependency: Task 9 threshold values are informed by Task 12 results
  but Task 9 can start with conservative placeholder values

---

## Gap-checking against research docs

When the user provides existing research docs, phase plans, or prototype findings,
cross-reference them against the backlog before finalising:

1. List every solution and dependency named in the docs
2. Check each against the backlog tasks — is it covered, partial, or missing?
3. Flag gaps explicitly: what is in the docs but not in the backlog?
4. Add missing items as tasks or sub-tasks, citing the source doc

This step is what separates a backlog built from first principles from one that
is genuinely grounded in what the team already knows. Common gaps:

- Query transformation strategies named in research but missing from backlog
  (multi-query / RAG-Fusion, step-back prompting)
- Tracing backend decisions made in research but not carried into task specifications
- History / context management patterns described in phase plans but not scheduled
- Router eval datasets described as discrete artefacts but merged into the main
  golden dataset task
- Memory statistics injection described in MemGPT-pattern research but absent
  from the generation task

---

## Quality checks before completing

- Every task traces back to at least one named failure mode
- Every deliverable is concrete — a running system, a document, a dataset —
  not "implement X"
- Every task has at least one risk or open question
- The week-1 decisions are named and sequenced before everything else
- Post-MVP tasks are present in the backlog and architecture is compatible with them
- Day-one decisions that are expensive to change (embedding model, vector store,
  metadata schema) appear in the first sprint
- The highest-risk external dependency is named, its owner is identified, and
  the consequence of it not being resolved is stated
- Linear grouping produces workstreams a single sub-team could own without
  needing to coordinate with every other team on every issue
- Acceptance criteria are measurable, not descriptive

---

## Relationship to the design sprint skill

The design sprint skill (SKILL.md in this same directory) produces the planning
artefacts that feed into this skill:
- Phase 5 of the design sprint produces named initiatives
- Phase 7 produces the owner backwards map

This skill takes a single initiative from Phase 5 and produces the full technical
backlog and Linear structure. Run the design sprint first, then this skill for
each initiative that needs a detailed backlog.

If no design sprint has been run, this skill can be used standalone — the failure
modes and HMWs in Section 1 serve the same purpose as phases 1–3 of the design
sprint, scoped to a single initiative rather than the full problem space.
