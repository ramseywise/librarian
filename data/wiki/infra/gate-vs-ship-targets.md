---
title: Gate vs Ship Make Targets
tags: [infra, pattern]
summary: Two compound make targets with different autofix policies — `gate` is the dev loop where `--fix` is allowed, `ship` runs the same checks strictly so the committed diff is the reviewed diff — plus the companion rule that any check needing external credentials skips without them and fails loudly when they are present.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/ai-project-template/docs/research/2026-08-29_diskoe-parity_template-conventions.md
  - data/raw/claude-docs/kiez/docs/env.md
---

# Gate vs Ship Make Targets

A mature project's Makefile separated two compound targets that most repos conflate:

| Target | Composition | Autofix | Purpose |
|---|---|---|---|
| `gate` | `type-check lint test build db-drift` | allowed (`--fix`) | the inner dev loop; make it green fast |
| `ship` | the same gates, strict | **none** | what runs before a PR — *so the committed diff is the reviewed diff* |

The reason to forbid autofix in `ship` is reviewability, not strictness for its own sake:
if the pre-PR target rewrites files, the diff a reviewer reads is not the diff the author
wrote, and the formatter's edits land unreviewed. The template already had every
constituent target; what it lacked was the composite alias and the policy split, which is
a one-line addition.

## Skip-without-credentials, fail-loudly-when-reachable

`db-drift` is a migration drift check against a live database. Its contract: when the
connection string is absent it **skips** (so a contributor without credentials still gets
a green `gate`), and when the database is reachable it **fails loudly** on drift. The
check itself is project-specific, but the two-state contract is the portable part and
belongs anywhere a gate depends on an external service.

## `gate` as the enforcer of documentation

kiez extends `gate` with a rule that turns a doc into a test: every environment variable
the code or a workflow reads must appear in `docs/env.md` (name, reader, where it is set,
whether public), and `make gate` fails if one is read and undocumented. `.env.example`
lists names only. The table is kept current because the gate, not a reviewer, notices
when it is not.

## See Also
- [[Rollback Restores Code Only]] — related (promotion requires the gate green on the exact SHA)
- [[Claude Workflow System]] — extends (the local loop these targets belong to)
- [[UNGATED Metric Convention]] — related (the eval gate that runs inside `gate`/CI)
- [[Claude Code Hook Architecture]] — alternative-to (hooks enforce the same gates per tool call rather than per target)
- [[Kiez Project]] — instance-of (env-table enforcement)
