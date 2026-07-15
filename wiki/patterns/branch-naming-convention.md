---
title: Branch Naming Convention Pattern
tags: [infra, pattern]
summary: Ticket-linked, type-prefixed branch naming (`type-TICKET-slug`) with per-repo type taxonomies and a `hotfix` escape hatch for production-blocking bugs.
updated: 2026-07-14
sources:
  - raw/notion/2026-06-03-branch-naming-convention-va-team.md
  - raw/claude-docs/galactus/skills/workflow/quick-commit/SKILL.md
---

# Branch Naming Convention Pattern

A lightweight convention for naming git branches so that every branch is traceable to a ticket, and the branch name itself signals the nature of the change before a PR is even opened.

## Format

```
<type>-<TICKET-ID>-<short-description>
```

- **`type`** — the nature of the change (see "Per-Repo Type Taxonomy" below)
- **`TICKET-ID`** — the issue tracker ID, copied directly from the ticket (many trackers, e.g. Linear, expose a "copy git branch name" action that pre-fills this)
- **`short-description`** — kebab-case slug, max 4–5 words

## Why This Pattern

- **Traceability** — every branch links back to a ticket automatically (enables PR ↔ ticket automation, e.g. auto-closing issues on merge)
- **Clarity at a glance** — the type prefix tells reviewers the scope of review before opening the diff (`feat` vs `fix` vs `infra` warrant different review depth)
- **Consistency across repos** — critical once a team spans multiple repos with different concerns (e.g. a product backend vs. a data/eval pipeline) — onboarding is faster when the *shape* of the convention is shared even if the type vocabulary differs per repo

## Per-Repo Type Taxonomy Is Not One-Size-Fits-All

The key generalizable insight: **don't force a single flat type vocabulary across repos with different concerns.** A product/backend repo and a data-science/eval repo have different branch archetypes:

- A backend repo needs types like `feat`, `fix`, `refactor`, `chore`, `infra`, `test` — plus domain-specific types where a category of change has a distinct review/deploy lifecycle (e.g. a `prompt` type for LLM system-prompt changes, since prompt changes often ship on a different cadence than code).
- A data-science/eval repo needs types like `eval` (new grader/pipeline), `data` (ingestion, PII scrubbing, dataset prep), `exp` (experiment/prototype that may never merge), `nb` (analysis notebook) — categories that don't exist in a typical backend taxonomy. `exp` in particular matters: distinguishing "this may be abandoned" work from `feat` avoids polluting PR history with unfinished exploration.

Define the taxonomy per repo, but keep the `type-TICKET-slug` shape constant across repos.

## The `hotfix` Exception

One type breaks the rule deliberately: `hotfix-<short-description>` (no ticket ID required) branches directly off the main/trunk branch, bypassing the normal ticket-first flow.

**When to use it:** a bug is actively blocking users in production (payment failure, crash, data loss), no existing feature branch can absorb the fix, and the fix must ship without waiting for the normal cycle. It must be merged back into the trunk branch promptly to avoid being silently overwritten by the next regular release.

This is the pattern's pressure-release valve — a convention that has no exception for genuine emergencies will get bypassed entirely under pressure, which is worse than having a narrow, well-defined escape hatch.

## Generic Fallback When No Per-Repo Taxonomy Exists

The `/quick-commit` skill's branch-naming logic is the fallback instance of this pattern for repos (or moments) without a defined per-repo type taxonomy: if the current branch already carries a ticket ID (e.g. `feature/lin-{id}-*`), it carries that ID forward into the new branch name (`feature/lin-{id}-<slug>`); otherwise it falls back to a bare `feature/<slug>` with no type prefix and no ticket ID at all. This is intentionally looser than the `type-TICKET-slug` shape above — it is a "just get something committed" fallback, not a replacement for adopting a real per-repo taxonomy once one exists.

## Enforcement

Pair this convention with a pre-commit or pre-push hook that blocks commits on a branch missing the expected `type-TICKET-` prefix — see the `branch-guard` hook pattern in git workflow tooling. Convention without enforcement drifts quickly once a team grows past a handful of contributors.

## See Also
- [[Multi-Repo Claude Organization]]
- [[Galactus Dev Hooks & Git Workflow]]
