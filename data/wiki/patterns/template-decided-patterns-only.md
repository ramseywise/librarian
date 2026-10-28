---
title: Template Only Decided Patterns
tags: [infra, pattern]
summary: A shared template vendors patterns that have already been decided — templating a scaffold before its upstream research resolves risks shipping a schema the research refutes to every future project, so the research runs first, and if it refutes the pattern, the refutation (as a documented threshold) is what gets templated.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/ai-project-template/docs/prompts/2026-08-05-HOLD-workflow-and-graph-capabilities.md
  - data/raw/claude-docs/ai-project-template/docs/plans/multi-agent-tooling-expansion.md
  - data/raw/repos/ai-project-template/.claude--docs--plans--multi-agent-tooling-expansion.md
  - data/raw/claude-docs/ai-project-template/docs/plans/2026-08-05-workflow-and-graph-capabilities.md
  - data/raw/repos/ai-project-template/.claude--docs--plans--2026-08-05-workflow-and-graph-capabilities.md
---

# Template Only Decided Patterns

A research spawn prompt for adding two capabilities to the ai-project-template — an
orchestrated-workflow scaffold and a knowledge-graph retrieval scaffold — was written and
then placed on **HOLD** with the release condition spelled out in the file header. The
hold itself is the pattern.

## Why hold

Both candidate patterns were being proven out in sibling repos at the time: typed-edge
graph retrieval in librarian (ablation not yet run) and role-contract orchestration in
guacamayo (complete). The template's job is to vendor *decided* patterns:

> Templating a knowledge-graph scaffold before the ablation runs risks shipping a schema
> its own research refutes — and a bad pattern in a template propagates to every project
> scaffolded from it, which is strictly worse than no pattern.

A template amplifies. The cost of a wrong pattern is paid once per rendered repo, which
is why the bar for entry is higher than for any single project.

## A refutation is also templatable

The prompt pre-commits to what happens if the upstream research comes back negative: "If
it refutes typed edges at this corpus size, **that finding is what gets templated** (as a
documented 'don't do this until N pages'), not the schema." The templatable artifact is
then a threshold plus the ablation to run before building — a documented decision, not
code.

## Other rules the prompt encodes

- **Established presumption: `-d`-only, never a genesis question.** Every new toggle
  costs a question in an interview already 11–14 questions long, a row in the render
  matrix, and a maintenance surface. Start from "add it as a non-interview capability"
  and argue only if the evidence overturns it ([[Copier Re-Entry as Capability Path]]).
- **Template the general part, not the instance.** For each upstream pattern, split what
  is general (a role/contract table shape, a findings schema, an edge-type vocabulary)
  from what is repo-specific. "The role contracts are guacamayo-shaped, not general" is a
  legitimate finding.
- **A scaffold that ships an unused type reproduces the bug it was meant to prevent.**
  The upstream orchestration work's central defect was a defined verdict type that both
  ends bypassed. A templated contract must be *load-bearing* — consumed by something —
  or it is decorative and worse than absent.
- **Prior plan docs are findings to reconcile with, not background.** Re-deriving
  questions already answered wastes the research pass.
- **Vendored skills drift silently.** Scaffolded projects cannot reach the global skill
  store, so skills are copied in — and when the global roles change shape, nothing in
  the template notices. The prompt asks for a drift-detection recommendation, not a
  re-sync.

## A confirmed consumer, not a proposal document

A five-phase plan to add frameworks to the template (a role-based multi-agent crew
framework, a second conversational-agent framework, and more) was justified by two
projects' proposal READMEs naming them. Two phases shipped; then the premise broke. One
project was redirected to LangGraph, and a review of what the wider program actually
taught and shipped found the crew frameworks appeared **only in proposal documents** —
curriculum used a no-code workflow tool and Google ADK, and teams shipped plain Python or
no-code flows. The crew-framework phase was marked stale rather than built, and the
dependent sub-item (whose whole design was "repeat that phase's pattern") inherited the
block; independent sub-items stayed startable. The plan was later superseded entirely by
an on-demand capability catalog ([[Capability Catalog with Preconditions]]). Lesson: a
framework named in a proposal is a hypothesis about need, not a consumer; template
infrastructure waits for confirmed use.

## How the held research resolved (2026-08-05 plan)

The research the HOLD asked for came back with a split verdict — **split capabilities by
maturity, not symmetry**:

- **Graph retrieval: no toggle.** The upstream ablation had not yet run, and the template's
  own golden set could not detect a graph win anyway (single-source, single-hop questions).
  The templated artifact became a documented adopt-graph threshold (adopt only when
  multi-hop/associative questions exist and a flat baseline measurably misses them) plus a
  measurability upgrade to the eval scaffold: an expected-set field, an optional multi-hop
  subset, recall@k, and an arm-vs-arm compare. The upstream experiment is
  [[Typed-Graph Retrieval Ablation]].
- **Orchestration: a repo-only reference asset, not a rendered capability.** The *contract
  discipline* generalizes (schema in repo code, a pure decision function, a CLI, a consuming
  skill, a branching gate); the *orchestration* — role names, crew shape — does not. It is
  promoted to a `-d`-only capability only after the source repo completes one full
  produce→consume→gate cycle.
- **Hygiene surfaced by the audit outranked both**: two onboarding criticals and a sync
  script whose guard checked names but not content — see
  [[Name-Only Sync Guards Miss Content Drift]].

## See Also
- [[AI Project Template Scaffold]] — instance-of (the template being gated)
- [[Template Floor Raising]] — related (how template work is otherwise prioritized)
- [[Copier Re-Entry as Capability Path]] — extends (the `-d`-only presumption)
- [[Capability Parity Audit]] — related (the template's verified current state as the baseline)
- [[Sync as Render, Not Copy]] — related (vendored copies that drift)
- [[Deferred Decision Status]] — related (a HOLD with a named release condition is a deferred decision with a trigger)
- [[Typed-Graph Retrieval Ablation]] — related (the experiment the graph threshold waits on)
- [[Name-Only Sync Guards Miss Content Drift]] — extends (the drift-detection recommendation)
