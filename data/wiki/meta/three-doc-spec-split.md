---
title: Three-Doc Spec Split
tags: [meta, pattern]
summary: Splitting a monolithic roadmap into scope (what problem, what is out), requirements (what must exist — with stable IDs for requirements, decisions, risks and doc-vs-code contradictions) and roadmap (why this next), plus the directory discipline that dated, Status-stamped research docs are never contracts.
updated: 2026-10-16
sources:
  - data/raw/claude-docs/ai-project-template/docs/research/2026-08-29_diskoe-parity_template-conventions.md
---

# Three-Doc Spec Split

A product-shaped repo (diskoe) restructured its single roadmap document when it had
become "a roadmap + requirements registry + backlog + decision log + risk register in one
file". The split assigns each document one question:

| Doc | Question | Holds |
|---|---|---|
| `design-scope.md` | what problem, what is out of scope? | boundaries |
| `design-requirements.md` | what must exist? | requirement IDs (`PR-*`/`CR-*`/`TR-*`), decisions (`D-`/`DA-`), risks (`RK-`), **doc-vs-code contradictions (`DC-`)** |
| `mvp-roadmap.md` | why this next, what to build? | phases, gates, sequenced `B-` items |

## What is worth copying

- **ID discipline.** Every requirement, decision, risk and contradiction gets a stable
  prefixed ID so plan docs, reviews and commits can cite it without quoting prose.
- **A contradiction register.** `DC-` entries record places where the documentation and
  the code disagree, as first-class items with the same standing as requirements — the
  repo-level analogue of this wiki's `_conflicts.md`.
- **Research vs specs.** `docs/research/` holds dated, `Status:`-stamped audits that are
  *never contracts*; `specs/` holds decisions that are enforced. New projects otherwise
  start with one design doc and no separation between "what was decided" and "what was
  audited."

## When not to

The split earns its complexity only for product-shaped repos with real requirements. Pure
infra or ML-pipeline repos do not need three documents; the template research proposed
gating the stubs on a copier question rather than emitting them unconditionally, and left
open whether that question should fold into `project_type`.

## See Also
- [[DESIGN.md Artifact]] — alternative-to (the single scaffolded design doc this would replace for product repos)
- [[Documentation Boundary — Machine vs Human Docs]] — extends (which of these docs are machine-consumed)
- [[Multi-Repo Claude Organization]] — extends (the research-doc lifecycle, made a directory rule)
- [[Deferred Decision Status]] — related (decision IDs with status)
- [[Plan-Doc Status Enum]] — related (the `Status:` stamp research docs carry)
- [[Prototype Pipeline Handoff Signals]] — extends (when the pipeline should signal the split)
- [[Four-Stage Design Pipeline with Backflow]] — related (the staged process that writes these docs)
