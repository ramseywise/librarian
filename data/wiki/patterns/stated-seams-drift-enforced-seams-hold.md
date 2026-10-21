---
title: Stated Seams Drift, Enforced Seams Hold
tags: [patterns, infra, pattern]
summary: Two repos built from the same architecture refs diverge exactly where one enforces a seam in lint/CI and the other only describes it in CLAUDE.md — a stated layer arrow is broken within weeks, a stated "one model seam" is bypassed by judges, a stated failure path fabricates success — so every architectural rule needs an enforcing check with an empty exception list.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/diskoe/docs/research/2026-10-06-claude-setup-parity-dssg.md
  - data/raw/claude-docs/akira/docs/research/2026-10-06-claude-setup-parity-dssg.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-10-06-claude-setup-parity-dssg.md
  - data/raw/repos/akira/CLAUDE.md
  - data/raw/claude-docs/akira/docs/plans/2026-08-29-b79-core-dependency-direction.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-08-29-b79-core-dependency-direction.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-08-29-b79-core-dependency-direction.md
  - data/raw/claude-docs/playground/docs/plans/2026-08-29-b79-core-dependency-direction.md
  - data/raw/repos/akira/.claude--docs--plans--2026-08-29-b79-core-dependency-direction.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-08-29-b79-core-dependency-direction.md
  - data/raw/repos/playground/.claude--docs--plans--2026-08-29-b79-core-dependency-direction.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-14-dis240-candidates-to-agents.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-14-dis240-candidates-to-agents.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-14-dis240-candidates-to-agents.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-14-dis240-candidates-to-agents.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-14-dis240-candidates-to-agents.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-14-dis240-candidates-to-agents.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-14-dis240-candidates-to-agents.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-14-dis240-candidates-to-agents.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-14-dis240-candidates-to-agents.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-14-dis240-candidates-to-agents.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-14-dis240-candidates-to-agents.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-14-dis240-candidates-to-agents.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-14-dis240-candidates-to-agents.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-14-dis240-candidates-to-agents.md
---

# Stated Seams Drift, Enforced Seams Hold

Found by comparing diskoe against the repo its `.claude/` was copied from, six weeks
after the fork. Both shared a design vocabulary — pure agents, one model gateway, an eval
registry, a layered `src/` — because both were designed from the same refs. Where they
diverged was not design but **enforcement**.

## The observation

| Seam | Stated only (in docs) | Enforced (lint/CI) |
|---|---|---|
| Layer arrows | Drawn in CLAUDE.md — and already broken by a `schemas/index.ts` back-arrow re-export from an agent folder | Import rules in ESLint with an **empty exception list** |
| One model seam | A thin gateway exists, but LLM judges import the provider SDK directly | Provider-leak lint: no module outside the gateway imports a provider package |
| Type boundary | `as any` on the model call and on DB results | `as unknown as` banned; rows parsed by schema |
| Logging | `catch { /* logged */ }` that logs nothing | `no-console` lint + structured logger |
| Run recording | Spec says "record failures"; code returns `crypto.randomUUID()` on failure — a fabricated run id that reads as success | Append-only verdict tables, failure is a row |
| DB tests | Test target passes with **zero assertions** | Test target fails on zero tests |

Every "stated" row is a rule someone wrote down and believed was true. Every one was false
within weeks, and none was detectable without reading the code.

## Why stating isn't enough

- A seam stated in prose is checked only when a human happens to read both the rule and
  the violating line together. Agents writing code read the rule rarely and the
  neighbouring code constantly; the neighbouring code wins
  ([[The Untested Copy Wins]]).
- An exception list that starts non-empty grows. "Empty exception list" is the
  enforceable version of the rule.
- Silent failure paths (fake UUIDs, zero-assertion test runs) are the same defect as
  [[Silence Reads as Clean]] and [[Scan-Floor Guard Against Silent No-Op Checks]] — a
  check that can pass without checking anything.

## Applying it

1. For each architectural rule in CLAUDE.md, name the check that enforces it. No check →
   the rule is a wish; either add the check or label the rule aspirational.
2. Turn on strictness that already costs nothing — the client repo's `tsc --strict`
   reported 0 errors; it was simply never switched on.
3. Hand-copied skill files and gates evolving in two repos are a third seam that drifts;
   extract a portable core into a template before a third repo copies it
   ([[AI Project Template Scaffold]]).

## Two enforcement details from the akira CLAUDE.md

- **No inline disables: the config names the exception.** Lint bans (`no-console`, a
  double-cast ban on DB results) allow zero inline `eslint-disable` comments. Every allowed
  file is listed in a named-exception block in the lint config, each with a reason. An
  inline disable is invisible to anyone reading the rule, and that is how a seam erodes back
  into the habit it replaced. Adding a file to the list is a diff a reviewer sees.
- **Find the mechanism that produced the violations before banning them.** The repo
  carried 71 `as unknown as` casts on database results because *no command regenerated the
  generated DB types*. The types drifted, callers hit type errors that were wrong about
  reality, and a cast was the cheapest correct-looking fix. The ban only held once
  `make db-types` (regenerate, stamped with date and command) and a post-merge
  `db-types-drift` check existed. Banning the symptom without fixing the drift would have
  just moved the casts.
- **Split a boundary violation by shape before choosing a fix (B-79).** A `core/` CLI
  imported three things from `products/`. The pure, policy-free `chunk` helper moved to
  `lib/` — strictly correct, three import edits. The two eligibility functions could not
  move: every neutral layer failed its own placement test, and duplicating ~140 lines of
  policy would recreate the drift the rule exists to prevent. So the rule was amended with
  **one named exception** — that one file, that one import, with the reason ("must score
  against the same eligibility logic as the request path it fixtures") — enforced by a
  file-scoped `no-restricted-imports` override, not left to prose. Same plan: no
  re-export shim when moving a test util (update all 14 call sites — a shim is a second
  path that outlives the migration), and a deterministic lint guard over an LLM review
  dimension for a rule a parser can check. "Empty exception list" stays the default; an
  exception that exists is named in config, scoped to a file, and argued.
- **Retire the named exception once a home passes the placement test (2026-09-14).** Two
  weeks later the eligibility file moved to `agents/scoring/eligibility.ts`. It passed the
  two-part test: no I/O, and it was the substrate for three trees. A districts helper it
  imported moved with it, so the move did not create an agents-to-products back-arrow.
  The row types moved to `schemas/` and were re-exported from their old module, so
  importers kept their names. The ESLint override was deleted and the deletion verified
  with a scratch file holding a violating import. That proved the rule still fired and had
  not been silently disabled. Code and doc edits were staged as separate commits, so a code
  regression could not hide inside a doc diff. A related review class from the same week:
  code comments that cite a gitignored plan doc as their authority point at nothing a
  later reader can open.

## See Also
- [[The Untested Copy Wins]] — extends
- [[Silence Reads as Clean]] — extends
- [[Scan-Floor Guard Against Silent No-Op Checks]] — extends
- [[Derive the Gate, Don't Copy It]] — extends
- [[Capability Parity Audit]] — prerequisite-for
- [[Execution-Made Decisions Leave Stale Invariants]] — instance-of (a stated pointer-only invariant falsified by execution, caught by re-running the plan's grep)
- [[Every Registration Site Needs a Guard]] — extends (a schema doc claimed a test guarded it; none did)
- [[A Check Must Say Why It Could Not Check]] — related
- [[Model Gateway Is Transport, Call Site Owns Meaning]] — instance-of (the enforced one-model-seam, and what it must not absorb)
- [[Default-Deny Guard With a Named Allowlist]] — extends (how to word an enforced seam's exceptions)
- [[Triage Casts by Mechanical Probe]] — prerequisite-for (the cleanup of casts that accumulated from type drift)
- [[Type Home Decided by Importers]] — instance-of (type layer arrows lint-enforced)
- [[Server-Derived Autonomy Tier]] — instance-of (tier boundary enforced by schema and one switch)
