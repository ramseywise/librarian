---
title: Payload Security Defects at Canon
tags: [infra, llm, pattern]
summary: When a code-gen payload is about to be mirrored into every scaffolded project, its defects must be fixed in the canonical copy first — a mirror multiplies a single-source bug into every downstream consumer, and the fix window closes once copies exist.
updated: 2026-08-03
sources:
  - data/raw/claude-docs/ai-project-template/docs/plans/2026-07-19-agents-skills-sync.md
---

# Payload Security Defects at Canon

Before mirroring a 30-file capability payload into a project template, an audit found
six defects in the canonical copies. The sequencing rule that followed:

> Fix at canon **before** the mirror lands.

The reasoning is arithmetic. A defect in a hand-copied file is one bug. The same defect
in a file that renders into every scaffolded project is one bug per project, discovered
independently, fixed inconsistently — and the canonical copy stays wrong the whole time.
Mirroring is the moment a single-source defect becomes a distributed one.

## The six

| Capability | Defect | Class |
|---|---|---|
| `cap-a2a` | Authentication bypass | Security |
| `cap-batch` | Non-resumable writes | Correctness / data loss |
| `cap-kg` | Cypher injection — needs an allowlist | Security |
| `cap-search` | Per-instance rate limiter race | Concurrency |
| `cap-vision` | Stale `1568px` constant | Version brittleness |
| `infra.md` | Missing `anthropic` dependency | Packaging |

Three distinct failure classes are represented, and only two are security proper. The
list is worth reading as a taxonomy of what accumulates in payload code that is written
once and then only ever copied:

- **Injection at a boundary that looked internal** — the Cypher case. Graph-query
  builders read as templating, not as a query surface, so the allowlist never got
  written.
- **State assumed to be per-process** — the rate limiter is correct for one instance and
  races the moment two exist. Payload code is written against a single-agent mental
  model and then deployed into a fleet.
- **Constants that encode a vendor's current behaviour** — `1568px` was a real API limit
  when written. Hardcoded vendor numbers rot silently; nothing fails, the behaviour just
  drifts out of spec.
- **Dependency declared nowhere** — the payload works in the repo that authored it,
  because that repo already had `anthropic` installed for other reasons. Only a clean
  scaffold reveals it.

## Why the audit happens at mirror time

The defects were not found by a security review. They surfaced because
**preparing to mirror forces a read of every file** — the same forcing function that
makes migrations good bug-finders. Code that is only ever copied is never re-read;
formalizing the copy into a render is the first occasion in the payload's life that
anyone examines all thirty files against a checklist.

This argues for treating the mirror-enablement work as a scheduled audit rather than
plumbing. The plan's own sequencing reflects it: security fixes are a prerequisite step,
not a follow-up issue.

## Surfacing, not just fixing

The parallel contract work requires each capability file to carry **surfaced flags for
security issues, stale constants, and version-brittleness** in its `## Design notes`
section — see [[Capability Runtime-Coupling Tiers]]. Fixing `1568px` once does not stop
the next hardcoded vendor constant; a named section that expects such flags does. The
defect list becomes a standing category in the document format rather than a one-time
cleanup.

## See Also
- [[Sync as Render, Not Copy]] — prerequisite-for (fix before the render lands)
- [[Capability Runtime-Coupling Tiers]] — extends (the contract layer that surfaces flags)
- [[AI Project Template Scaffold]] — instance-of
- [[Safeguards Architecture — Five Protection Layers]] — complements (runtime guards vs payload defects)
