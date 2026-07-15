---
title: SANYI Change-Contract System
tags: [meta, pattern, concept, conflict]
summary: Three-layer change-contract system (变易/简易/不易) for agent architectures — classifies every component into ever-changing, simple, or invariant, then enforces cross-layer discipline via init/review/audit modes. Violation-code table has an unresolved conflict — see [[Conflicts]].
updated: 2026-07-14
sources:
  - raw/claude-docs/galactus/skills/SANYI/SKILL.md
  - raw/claude-docs/galactus/skills/SANYI/README.md
  - raw/claude-docs/galactus/skills/SANYI/references/contract-spec.md
  - raw/claude-docs/galactus/skills/SANYI/references/interview-guide.md
  - raw/claude-docs/galactus/skills/SANYI/references/violations.md
---

# SANYI Change-Contract System

三易 SANYI — a change-contract discipline for agent architectures, grounded in I Ching philosophy. The core premise: **agent systems fail because teams confuse which components should be changeable, which should be simple, and which should be invariant.**

## The Three Layers

| Layer | Chinese | Meaning | Examples |
|---|---|---|---|
| **变易 Bianyi** | 变易 | Ever-changing | Prompts, feature flags, eval thresholds, A/B configs |
| **简易 Jianyi** | 简易 | Simple/structured | Schemas, graph topology, tool signatures, API contracts |
| **不易 Buyi** | 不易 | Invariant | Safety constraints, PII rules, compliance requirements, escalation path |

### Why Agent Systems Need This

- Same constraint can be implemented in prompt (soft) OR code (hard) OR config (dynamic)
- LLM-based safety is Bianyi (probabilistic) — MUST be code-enforced at Buyi level
- Schemas that grow entropy (new optional fields added weekly) are Jianyi drifting toward Bianyi
- **First Law:** LLM constraints in prompts are soft. Buyi invariants need deterministic code enforcement.

## Violation Codes

> **⚠️ Unresolved conflict:** the table below is sourced from the original `SKILL.md`/`README.md` ingest (2026-07-05). A fuller reference doc (`references/violations.md`) ingested later declares itself authoritative and assigns **different meanings** to several of the same codes (e.g. its BY-1 is "direct modification of Buyi-guarded code," not "hardcoded tunable" — that concept is its BN-1 instead). See [[Conflicts]] for the full side-by-side and do not treat either table as settled until reviewed. The "Report Template and Severity Semantics" section below reflects `violations.md`'s version instead.

### Bianyi violations
| Code | Description | Severity |
|---|---|---|
| BY-1 | Tunable hardcoded in source (threshold in `.py` not env/config) | Medium |
| BY-2 | Prompt embedded in code (not in `prompts/` or Langfuse) | Medium |
| BY-3 | Feature flag not exposed as env var | Low |
| BY-4 | Dead config entry (declared but never read) | Low |

### Jianyi violations
| Code | Description | Severity |
|---|---|---|
| JY-1 | Schema entropy growth (more than 2 new optional fields without review) | Medium |
| JY-2 | Graph topology change without contract update | High |
| JY-3 | Tool signature drift (added/removed params without schema bump) | High |

### Buyi violations
| Code | Description | Severity |
|---|---|---|
| BN-1 | Invariant moved to prompt/config (hardcoded safety → env var or prompt) | Critical |

### Migration/hygiene violations
| Code | Description | Severity |
|---|---|---|
| MG-1 | Layer migration not recorded in SANYI.md | Medium |
| UN-1 | Component not classified in contract | Low |
| UN-2 | Dangling contract entry (component deleted, contract not updated) | Low |

## Modes

### `/sanyi init` — Create contract

1. Auto-draft from `CLAUDE.md` + codebase scan
2. Interview per layer: name each component, assign layer, justify
3. Buyi interview: is this enforced in code or prompt? Can it be bypassed?
4. Push back on over-declaration (too many Buyi = brittle, too few = unsafe)
5. Closing audit: run audit on initial draft, fix any immediate violations

### `/sanyi review` — Enforce on diff

Runs on every PR diff:
1. Glob-match changed files against SANYI.md component registry
2. Per-layer checks (11 check types)
3. Bookkeeping: update SANYI.md Pending → Resolved for addressed violations
4. Optional `--fix` flag: auto-fixes BN-1 only (moves hardcoded value to env var)
5. Reports only NEW violations in this diff

### `/sanyi audit` — Full repo re-measure

- BY-4 sweep: find all declared config entries, check each is read
- BN-1 inventory: scan all Buyi components, verify code-enforcement in place
- Jianyi entropy measurement: count schema fields added since last audit
- Migration drift: check all layer migrations are recorded
- Hygiene: flag dangling entries and unclassified components

## Design Principles

- **Report-only by default** — SANYI is an observer, not an enforcer. Humans decide on violations.
- **Buyi never auto-fixed** — The only safe fix for a critical violation is a human decision.
- **Anti-staleness built in** — Audit mode detects if the contract has drifted from the codebase.
- **Buyi stays scarce** — Over-classification as invariant creates rigidity. Challenge every Buyi entry.

## SANYI.md Format (Contract File)

Lives at repo root, **sibling to `CLAUDE.md`** — never buried in `docs/`. Both humans and agents read it, and review/audit runs write back to it (stamps, debt records) — it is a contract, not documentation.

Header: `project`, `version` (bump on structural change), `last-audit`. Six sections, names matched verbatim (they're the parser's anchors):
- `## 不易 Buyi` — invariants. **The admission test is the gate, not an entry count:** something is Buyi only if violating it causes a security, legal, financial, or trust failure. Every Buyi entry needs a deterministic code-layer implementation (a prompt-only invariant is BY-4) and must never be bypassable via config/env/flag (making it conditional is BY-2, a *semantic downgrade* — "every individual line looks innocent," only diffing against the contract reveals the demotion). No sub-tiers — a felt "lesser Buyi" is almost always a mis-split (the threshold value is Bianyi, "a fallback must fire" is the real Buyi).
- `## 简易 Jianyi` — complexity-budgeted components, with three complexity carriers: **shape** (schema/tool-schema field count), **escape hatches** (untyped `dict`/`Any`/`**kwargs` catch-alls that hide unbounded growth behind one field — JY-3), and **control flow** (the execution graph itself — usually the *dominant* complexity source for agent systems; a perfect schema can wrap a hellish graph). Deterministic graph-metric counting (fan-out, depth, cycles) is deferred — judged qualitatively until scripted analysis exists.
- `## 变易 Bianyi` — must stay easy to change without a deploy; a hardcoded literal outside its declared layer is BN-1.
- `## Migrations` — the evolution log (`- YYYY-MM-DD: <from> → <to> / <entry> — <rationale>. (author: <who>)`). Layer assignment isn't permanent — a prompt that survives hundreds of experiments can be promoted Bianyi → Buyi; an unrecorded shift is MG-1.
- `## Pending` — disputed assignments, enforced as Buyi (strictest) by default until resolved.
- `## Debt` — baseline of known, accepted violations (linter-baseline pattern) — review reports only *new* violations, so history doesn't flood every report.

Entry fields: `paths` (glob, symbol-scoped via `file.py#PREFIX_*`), `contract` (testable, not aspirational), `evidence` (test file guarding a Buyi contract — deleting/weakening it is BY-3), `budget`/`current` (Jianyi only — `current` is re-stamped by every review/audit run).

## `init` — Interview Heuristics

Two of the three layers are largely inferable from code — draft them before asking the human anything:

| Signal | Suggests |
|---|---|
| Repo's `CLAUDE.md` conventions (prompts-in-`prompts.py`, tunables-in-`config.py`) | Bianyi/Jianyi entries directly — promote declared conventions rather than re-deriving them |
| `config.py` / settings modules / `prompts.py` contents | Bianyi candidates |
| `TypedDict`/dataclass/pydantic models, tool schemas | Jianyi candidates (shape) — measure `current` on the spot |
| LangGraph `StateGraph`, conditional edges, retry/reflect loops | Jianyi candidates (control flow) — usually the dominant complexity source |
| Security/auth/PII/compliance/escalation-fallback code | Buyi **candidates only** — confirm in interview, never auto-assign |
| Hardcoded prompt strings / literal thresholds in business logic | Pre-draft BN-1 debt |

**Integration boundaries are a cross-layer violation hotspot** — an `integrations/` module typically holds all three layers in one file; split into separate entries (retry/backoff → Bianyi, wrapper interface → Jianyi, credentials → Buyi).

Buyi is the one layer machines can't infer (business/safety intent isn't in any AST) — the question bank: what must the agent never do/say/promise; which compliance constraints apply; which escalation fallbacks must always fire; which data must never leave the system boundary; which actions are irreversible and what guards them; what would a misbehaving agent concretely cost. **The first-law probe** for every Buyi candidate: "where is this enforced in deterministic code?" — a prompt-only answer still gets recorded as Buyi (the declared intent is real) but immediately logs a BY-4 debt entry. **Over-declaration pushback**: if Buyi count exceeds ~7, re-challenge each entry against the consequence test rather than inventing softer Buyi sub-tiers (rejected as an inflation vector).

## Report Template and Severity Semantics (per `violations.md`)

| Severity | Meaning | Tool behavior |
|---|---|---|
| blocker | change-contract structure altered | report + revert/redesign/amend-contract options — never auto-fixed |
| warning | entropy contract under pressure | report + bookkeeping (`current` stamp update) |
| info | changeable made rigid | report; auto-fixable with `--fix` |
| notice | contract hygiene signal | report only |

`--fix` auto-fixes **BN-1 only** (move the literal/prompt to its declared layer file, name it consistently, replace the usage site with an import, confirm behavior-preserving) — BY-\* and JY-\* are never auto-fixed because a Buyi "fix" is a human decision (revert/redesign/amend) and a Jianyi fix needs redesign or justification, never silent field deletion. The tool applies SANYI to its own output: reports are Bianyi (regenerate freely), contract bookkeeping is Jianyi (minimal necessary writes, always on), code modification is opt-in and restricted to BN-1 (the closest it gets to touching Buyi territory).

**Anti-staleness rules:** every review/audit run updates `current` stamps (audit also refreshes `last-audit`); a dangling `paths` match (UN-2) is always reported, never silently skipped; Pending defaults to strictest enforcement so parking is safe but not free; Debt excludes known violations from future reports so reviews stay quiet about history and loud about news; layer migrations must leave a `## Migrations` record — an unrecorded move is MG-1, except the one direction that's always the more specific BY-2 blocker: silently making an invariant bypassable.

> **Note:** the original `SKILL.md`/`README.md` ingest described `SANYI.md`'s sections differently (`## Components`, `## Buyi Enforcement`, `## Migrations`, `## Pending Violations`, with no per-entry field spec). The "SANYI.md Format" section above reflects the fuller `contract-spec.md` reference doc instead. See [[Conflicts]] for both versions side by side — unresolved.

## See Also
- [[ADK Context Engineering]]
- [[Input Guardrails Pipeline]]
- [[Production Hardening Patterns]]
- [[Claude Workflow System]]
