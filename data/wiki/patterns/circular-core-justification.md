---
title: Circular Core Justification
tags: [infra, pattern]
summary: "A template's always-on surface is suspect when each component is justified only by another component in the same chain (agent calls MCP tool → MCP tool calls retrieval service → service needs a corpus index) — that chain is a demo welded in as infrastructure, and the fix is to derive the real core from requirements every project shares and demote the chain to a per-shape example."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/ai-project-template/docs/plans/2026-07-17-template-core-redesign.md
  - data/raw/repos/ai-project-template/.claude--docs--plans--2026-07-17-template-core-redesign.md
  - data/raw/claude-docs/ai-project-template/docs/plans/2026-07-16-genesis-dryrun.md
  - data/raw/repos/ai-project-template/.claude--docs--plans--2026-07-16-genesis-dryrun.md
  - data/raw/claude-docs/ai-project-template/docs/plans/2026-07-12-puffin-integration.md
  - data/raw/repos/ai-project-template/.claude--docs--plans--2026-07-12-puffin-integration.md
---

# Circular Core Justification

> *"The core is circular, not minimal."*

A review of the ai-project-template asked why retrieval, a vendored reference library,
and an MCP server were part of every render. Tracing each default's help text found a
loop of self-reference rather than a base requirement:

- MCP defaults on because the example agents call the project's own MCP retrieval tool.
- The retrieval service ships because it is the service the MCP tool calls.
- The corpus pipeline (named `core/`) ships unconditionally because the retrieval service
  needs an index.

Net effect: a workflow or API-backend project received a corpus pipeline, a vector
index, a retrieval REST service, and an MCP server whose only tool searched sample
articles — none requested. The chain is a working end-to-end example, which is valuable;
but **an example belongs on the project-shape axis, not in the core**.

## How it was caught in practice

A live dry-run on a real pipeline-shaped project (transcript → extract → score →
persist) rendered a chat/RAG product — FastAPI `/chat`, guardrail → retrieve → generate
graph, coffee-machine sample data. The user's reaction, *"it shouldn't be rag agent or lg
agent, it should start with clients, nodes etc."*, matched what an independent shape
review concluded. Everything the MVP needed was missing; most of what rendered was dead
weight.

## The fix: derive the core from shared requirements

List what *every* project needs, each tied to a concrete choice already wired through the
repo — toolchain (one ruff config → hooks + pre-commit + CI), layout, config contract,
service boundary (app factory, `/health`, versioned `/api/v1/*`), eval gate (design
targets → `targets.yaml` → CI), governance (`data_sensitivity` → hard rules + infra tags),
agent guardrails, docs discipline. Everything not in that table is either:

1. **a shape example** — exactly one per `project_type`, or
2. **a capability** added mid-project through [[Copier Re-Entry as Capability Path]],
   never asked at genesis.

Two diagnostics that generalize:

- **A misnamed directory hides the loop.** Calling corpus machinery `core/` made the RAG
  stack read as base infrastructure. But the literal fix (rename it `corpus/` and gate it
  on the RAG toggle) was rejected: the default chat agent's retrieval and the
  always-shipped eval imported it too. What shipped was `core/` as an always-present ETL
  home with `core/pipelines/corpus/` gated on *any retrieving agent* — see
  [[Gate Coupled Features on the Producer, Not the Label]].
- **"Both" as a default is the same smell.** Defaulting to both agent frameworks gave
  every chat project two dependency sets and two Makefile families. A new project needs
  one working example chosen for it, with the other a re-render away.

## See Also
- [[Gate Coupled Features on the Producer, Not the Label]] — extends
- [[Template Only Decided Patterns]] — related (what may enter the template at all)
- [[Template Floor Raising]] — contradicts (the case for making shared capabilities default-on)
- [[REST-First, MCP as Adapter]] — extends (the boundary decision the de-circularized core adopted)
- [[Copier Re-Entry as Capability Path]] — extends (where demoted components come back from)
- [[AI Project Template Scaffold]] — instance-of
