---
title: SANYI Change-Contract System
tags: [meta, pattern, concept]
summary: Three-layer change-contract system (变易/简易/不易) for agent architectures — classifies every component into ever-changing, simple, or invariant, then enforces cross-layer discipline via init/review/audit modes.
updated: 2026-07-05
sources:
  - raw/claude-docs/galactus/skills/SANYI/SKILL.md
  - raw/claude-docs/galactus/skills/SANYI/README.md
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

Lives at repo root. Sections:
- `## Components` — registry of all components with layer classification and rationale
- `## Buyi Enforcement` — for each Buyi component: where is it enforced in code?
- `## Migrations` — log of layer changes (Bianyi → Jianyi, etc.) with dates and reasons
- `## Pending Violations` — open violations awaiting resolution

## See Also
- [[ADK Context Engineering]]
- [[Input Guardrails Pipeline]]
- [[Production Hardening Patterns]]
- [[Claude Workflow System]]
