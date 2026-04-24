# Design Sprint Framework — SKILL.md

## Purpose

Run a structured design sprint for any use case, producing a full set of planning artefacts: problems, pain points, insights, opportunities, HMW statements, technical solutions, workstream clusters, and a dependency-mapped initiative backlog.

Based on the IDEO / Stanford d.school HMW methodology adapted for cross-functional engineering team planning. Output is a buildable backlog with cross-team ownership, not just a set of ideas.

---

## When to use this skill

- Starting a new product, feature, or platform initiative from scratch
- A team needs shared understanding before committing to a quarterly backlog
- You need to map cross-functional dependencies across FE, BE, AI Eng, and Ops
- A stakeholder has asked "what should we build and in what order?"

---

## Inputs required before starting

Ask the user for these if not already provided:

1. **Use case** — what product, feature, or problem space are we designing for?
2. **Known constraints** — market, language, tech stack, team roles available
3. **Any existing data** — user research, ticket data, prototype learnings, production metrics
4. **Scope boundary** — what is explicitly out of scope?

---

## Output artefacts

Produce all seven artefacts in sequence. Each builds on the previous.

---

## Phase 1 — Deconstruct

Produce a 4-quadrant analysis of the use case:

**Problems** — specific, causal chains not just symptoms. Format: what happens → what it causes → implication for the system.

**Pain points** — operational friction for users or agents. Each pain point must have a one-line implication (what does this mean for how we build?).

**Insights** — non-obvious findings from data, prototypes, or analogous systems. Each insight must name its source (research, prototype, benchmark, analogy). Prioritise insights that challenge default assumptions.

**Opportunities** — reframe each problem/pain point as a design space. Format: "designing X that does Y → implication: Z".

Output as a markdown table with columns: Area | Finding | Implication.

---

## Phase 2 — How Might We (HMW)

Reframe each finding from Phase 1 as a HMW question.

Rules:
- State the problem, not the solution
- Avoid suggesting a solution in the question
- Keep it broad and outcome-oriented
- Phrase positively (not "reduce X" but "make X feel Y")
- One HMW per finding

Output as a list grouped by source quadrant (Problems / Pain Points / Insights / Opportunities).

---

## Phase 3 — Technical solutions

For each HMW, produce:
- **What is required to solve this** — one sentence, no implementation detail
- **Technical solution headline** — concrete, named approach (e.g. "Two-stage hierarchical classifier: LLM routes to 15 categories → fine-tuned classifier resolves within it")

Output as a table with columns: HMW | What's required | Technical solution headline.

---

## Phase 4 — Workstream clustering

Group all technical solutions into clusters using three lenses:

**WHO** — end-user or agent facing. Main audience is a human interacting with the system directly. Owner: FE Engineers.

**WHERE (BE)** — session state, context injection, data APIs, infrastructure. Owner: BE Engineers.

**WHERE (AI)** — classification, RAG pipeline, embeddings, hallucination prevention, personalisation. Owner: AI Engineers.

**WHERE (data)** — content ingestion, metadata enrichment, freshness, corpus quality. Owner: AI Engineers.

**WHY** — feedback loops, observability, eval harness, initiatives that enable other teams. Owner: AI Eng + Ops Engineers.

**WHERE (Ops)** — infrastructure, provisioning, CI/CD, security, managed services. Owner: Ops Engineers.

Note items that span multiple clusters — these become cross-team interface points.

Output as a table with columns: Cluster | Owner | Technical solution | HMW it solves.

---

## Phase 5 — Initiative definition

Group workstream clusters into 5–7 named initiatives. Each initiative must:

- Have a clear name in the format: Initiative "X"
- Have a one-sentence description of what it builds and why
- List the components it owns (from Phase 4)
- List the engineering roles required
- Note cross-initiative dependencies explicitly

Rules:
- No initiative should be blocked by another initiative that hasn't started
- The first initiative to start should have zero external dependencies
- Phase 2 initiatives depend on Phase 1 initiatives being stable — make this explicit
- Always include a Platform & Security Foundation initiative if auth, PII, or infra is needed

Output as a structured list, one block per initiative.

---

## Phase 6 — Dependency mapping

For each initiative, produce a dependency graph as an HTML artifact with:

- One card per component (node)
- Card content: bold title, description, needs (inputs), enables (outputs), role badge
- Arrows between cards showing dependency direction (what must exist before what)
- Colour coded by role: FE = blue, BE = pink, AI Eng = amber, Ops = green, External dep = grey
- Cross-initiative dependencies shown as grey external dep nodes

Produce one graph per initiative, not a single dense graph.

---

## Phase 7 — Owner backwards map (optional)

If the user specifies their ownership areas, backwards map from those areas to:
- Which problems, pain points, insights, and opportunities they own
- Which HMW statements they are responsible for answering
- Which technical solutions they need to define
- What cross-team interfaces they need to negotiate early

Output as a card grid grouped by ownership area, each card showing: area tag, problem/insight/opportunity, HMW, technical solution, relevant tags.

---

## Quality checks before completing

Before delivering any phase output, verify:

- Every HMW is outcome-oriented, not solution-prescribing
- Every technical solution has a concrete named approach, not a vague direction
- Every initiative has at least one clear cross-team dependency named
- No phase 2 initiative has zero dependencies on phase 1 work
- The platform / security / infra foundation is represented if the use case requires auth, data storage, or external APIs
- If the use case involves multiple markets or languages, multilingual requirements are called out explicitly as day-one decisions not future migrations

---

## Tone and format

- Be specific. Use real numbers, benchmarks, and named tools where they exist.
- Cite analogous systems or prior art where relevant.
- Never produce a generic output that could apply to any use case — every finding should be grounded in the specific context provided.
- Ask for clarification before starting if the use case is underspecified.
