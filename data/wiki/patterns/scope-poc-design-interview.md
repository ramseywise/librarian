---
title: Scope-POC Design Interview
tags: [llm, pattern]
summary: A five-tier system-design interview that produces a DESIGN.md answering *what* to build — idempotent over its own output, ratifying rather than adopting inherited decisions, and treating "I don't know" as a recordable answer instead of a blocker.
updated: 2026-08-03
sources:
  - data/raw/claude-docs/ai-project-template/skills/scope-poc/SKILL.md
---

# Scope-POC Design Interview

`/scope-poc` is the middle stage of the ai-project-template pipeline
([[Project Discovery Conversation]] → `/scope-poc` → `/project-genesis` → copier). Its
output is `DESIGN.md`.

The load-bearing separation: **`/scope-poc` answers WHAT to build; `/project-genesis`
answers HOW** (infrastructure). *"Don't conflate them — many design sessions happen weeks
before the scaffold is run."* Design and infrastructure are different conversations at
different times.

## The five tiers

| Tier | Covers |
|---|---|
| 1 — Problem and actors | Current workaround, 5-minute demo target, who uses it, what the AI specifically does |
| 2 — System boundaries | Auth, data sources, output destinations, fresh-vs-layering, MCP exposure |
| 3 — AI design | What data it reasons over, whether the MVP actually needs RAG, evaluation metrics, the naive baseline |
| 4 — Constraints | Data classification, multi-tenancy, operator model, load/latency/spend, observability |
| 5 — MVP scope | Thinnest valuable slice, top risks, what breaks first, explicit non-goals |

*"Have a real conversation (not a rigid checklist read aloud)... Skip a question if the
answer is obvious from context already given."*

## Ratify, don't adopt

Step 0 scans for pre-existing answers — `roadmap.md`, milestone files, plan docs, an
existing `DESIGN.md`, a `PROJECT-PROFILE.md` from discovery. A real dry-run
(see [[Skill Pipeline Dryrun Testing]]) found literal
scaffold parameters (`vector_backend=postgres`, `primary_chat_agent=lg_agent`) written
verbatim in a milestone's "done when" clause.

Every pre-answered decision is surfaced as a one-line checkpoint — *"your roadmap resolved
X on \<date\> — confirm, or reopen?"*

> *"Skipping the re-interview is right; skipping the user's consent is not. A user who
> never said 'yes, LangGraph' out loud will not feel ownership of the scaffold that assumes
> it."*

This failure was observed live. The same discipline governs consuming the Project Profile:
pre-filled fields are ratified individually, never silently adopted. The profile is *"a head
start, not a shortcut"* — it pre-fills the "what" while the "how" and constraints still get
the full interview.

## Idempotent over its own artifact

*"Re-running is cheap and expected."* A later run reads the existing DESIGN.md, ratifies
what's resolved, and interviews only the gaps — **never starting a fresh file when one
exists**. Same in-place-update discipline as the upstream Project Profile.

## The three independent axes

Agent-shaped projects open with an explicit disambiguation, because users *"reliably
collapse these into one anxiety"* — verbatim from a live session: *"should this be a Vercel
agent, LangGraph, or Supabase/Firebase?"*

| Axis | The question |
|---|---|
| Agent framework | How the AI code is written (LangGraph/ADK in Python, Vercel AI SDK in TS) |
| Database / identity | Where data lives, who users are (Supabase / Postgres / Firebase) |
| Deployment | Where it runs (Vercel, Railway/cloud, local) |

Stating their independence *plainly, before any technical question* is the intervention. A
related rule: **never bundle a governance gate (budget/approval pending) with a technical
choice in the same question.**

## Questions that resist scaffold defaults

Several tier questions exist specifically to stop the template's defaults from answering on
the user's behalf:

- **Does the MVP itself need retrieval?** Extraction pipelines, automation, and services
  reading through another system's API usually don't. The answer drives whether `rag_agent`
  *"and its heavy embedding dependencies belong in the render at all."*
- **What's the naive baseline?** What happens with a lookup table, keyword search, or human
  checklist — and what must the AI beat, by how much? *"Most AI projects fail at planning,
  not modeling — a project that can't name its baseline can't demonstrate value over it."*
- **What breaks first?** An adversarial read-back of the stated design: which component
  fails first as usage grows, what the failure looks like *to a user* (slow? wrong answer?
  silent staleness?), who would notice, and the cheap mitigation. Distinct from the risk
  question — Q13 asks what the POC should *prove*, this asks what the architecture will
  *cost you*.

Evaluation answers are captured as concrete metric targets (metric, target, how measured),
because they become `evals/targets.yaml` in the generated project — *"not just prose"* —
where `make eval-gate` fails on regression. At least one row derives from each top risk and
one from the naive baseline. See [[Golden Set Mechanics]] and [[Eval-Driven Development (EDD)]].

## Tier defaults are decisions, not unknowns

Load, latency, and spend have per-complexity-tier defaults (weekend sprint → demo-scale,
demo-tolerance latency, free tier only; semester → real projections with alerting) that are
**offered rather than demanded as numbers**.

A volunteer accepting the default is a **resolved** answer, recorded as
`<value> (weekend-sprint tier default, unvalidated)`. It is explicitly *not* parked as an
Open Question — because Open Questions block the G1 gate, and an accepted default is a
decision. Parking happens only when the user says the number matters *and* doesn't know it.

This is the rare case where a defaulted answer is deliberately recorded as settled; the
provenance annotation is what makes that safe.

## Observability is conditional-mandatory

*"The scaffold ships tracing; this asks what it's for."* Normally one or two lines. But when
data classification is `restricted` or `secret`, asking what must be redacted before
reaching a trace or log becomes **non-optional** — a trace backend is scaffolded by default,
so *"a silent default here has an irreversible failure mode."* Same category as
`human_approval`.

## Rationale authoring rule

In the Key Decisions table, *"a rationale that only records provenance ('set at scaffold
time', 'from design.yaml') is not a rationale — it says what happened, not why."* Every
hand-authored row names a real alternative and the cost of not taking it. If none was
considered, write *"no alternative considered"* — *"that is itself useful signal at
review."* Machine-generated rows between the `design-table` markers are exempt, since they
render `design.yaml` and provenance is the correct content there.

## Handoff

Step 7 maps DESIGN.md answers onto `/project-genesis` questions (AI approach → `project_type`,
actors → `primary_users`/`primary_chat_agent`, data classification → `data_sensitivity`,
system boundaries with an external user + own backend → `frontend_backend_topology`).
Anything still open is answered interactively during genesis.

## See Also
- [[Specification by Example]] <!-- auto-linked -->
- [[Project Discovery Conversation]] — prerequisite-for
- [[Deferred Decision Status]] — extends (status semantics for the Key Decisions table)
- [[AI Project Archetypes]] — extends (archetype pre-fills Tier 3)
- [[Asked vs Derived Scaffold Variables]] — prerequisite-for (Step 7 hands off to the genesis interview)
- [[AI Project Template Scaffold]] — prerequisite-for
- [[NYC-DSSG Project]] — instance-of (DSSG platform context block)
- [[Golden Set Mechanics]] — extends
- [[Skill Pipeline Dryrun Testing]] — extends (asserts which questions this skill skips and which it must still ask)
