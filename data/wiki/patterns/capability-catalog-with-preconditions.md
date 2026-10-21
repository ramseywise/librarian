---
title: Capability Catalog with Preconditions
tags: [infra, pattern]
summary: "A scaffold's derivation rules answer \"given these answers, what renders?\" but cannot answer the reverse — \"given this repo, what can still be added?\" — because a default expression is a function, not a relation; a declared catalog of addable capabilities with `requires`/`sets`/`conflicts_with`, CI-checked against the template, turns add-later into a three-bucket filter."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/ai-project-template/docs/plans/2026-07-19-genesis-lifecycle-architecture.md
  - data/raw/repos/ai-project-template/.claude--docs--plans--2026-07-19-genesis-lifecycle-architecture.md
---

# Capability Catalog with Preconditions

The ai-project-template's `/add-capability` skill carried a hand-maintained table mapping
8 capabilities to `-d` answers, against 54 derived variables, with nothing verifying it.
Asked *"why can't I add X?"*, the skill could only say "the template can't scaffold it" —
when often the real answer was "add a TypeScript backend first."

## The reverse-derivation problem

Forward derivation is what `copier.yaml` does: `project_type=rag` →
`include_rag_agent=true`. The reverse question is not expressible there, because a
`default:` expression is a **function, not a relation**. Three options were weighed:

| Option | Verdict |
|---|---|
| Keep the hand table | Drifts; already covered 8 of ~20 addable toggles |
| Compute it — flip each derived bool, re-render, diff the file set | Correct but N renders slow, and answers "what changes", not "what is meaningful" |
| **Declare it** — a catalog with preconditions | Chosen, with the computed form as the CI check |

## The catalog shape

One entry per addable capability, shipped into every rendered repo so the skill reads it
locally months after genesis:

```yaml
split_service:
  label: Split frontend/backend
  sets: {frontend_backend_topology: split_service, include_frontend: true}
  requires: {has_typescript: true, primary_backend_language: [both]}
  conflicts_with: {ts_agent_framework: vercel_ai_sdk}
  adds: [frontend/, backend/src/middleware/auth.py]
```

`+` in `sets` marks an additive multiselect merge (`agent_tools: +mcp`), so adding one
item does not clobber the existing list.

Detection becomes a **filter, not a lookup**: evaluate each entry's `requires` against
`.copier-answers.yml` and report *addable now*, *already on*, and *blocked by
<precondition>*. The third bucket is the real win — it tells the user what to do first.

## Why not copier validators

Preconditions are **guidance at the front door, not invariants**. A `-d` override that
violates one may be exactly what CI wants. On the enforcement ladder (hooks > skills >
CLAUDE.md) this is skill-tier: strong enough to be read, weak enough to be overridden. A
documented-but-unenforced conflict (`split_service` vs a specific TS agent framework)
lives in the catalog's `conflicts_with`, not in a structural copier rule.

## The CI check

A cheap audit script asserts every `sets:` key exists in `copier.yaml`, every value is in
that variable's `choices`, and every entry with `adds:` paths has a matching `_tasks`
prune line. That catches the "dead flag" class — a toggle that documents a capability the
template cannot produce.

## See Also
- [[Copier Re-Entry as Capability Path]] — extends (the mechanism the catalog fronts)
- [[Capability Parity Audit]] — related (have/partial/gap, but for the template's roadmap rather than one repo)
- [[Asked vs Derived Scaffold Variables]] — prerequisite-for (the forward derivations the catalog inverts)
- [[Template Only Decided Patterns]] — related (only decided capabilities get a catalog entry)
- [[AI Project Template Scaffold]] — instance-of
