---
title: Four-Stage Design Pipeline with Backflow
tags: [meta, llm, pattern]
summary: A design-of-record pipeline in four stages (initiative → product → system → roadmap) that re-enters at the earliest stale stage, detects staleness from a backflow digest of decisions added downstream, starts with a tree-first build-state audit, and treats phases as hypotheses with failure branches.
updated: 2026-10-30
sources:
  - data/raw/claude-docs/playground/skills/design-system/SKILL.md
  - data/raw/claude-docs/playground/skills/design-product/SKILL.md
  - data/raw/claude-docs/playground/skills/design-roadmap/SKILL.md
  - data/raw/claude-docs/playground/skills/design-initiative/SKILL.md
  - data/raw/claude-docs/akira/skills/design-initiative/SKILL.md
  - data/raw/claude-docs/diskoe/skills/design-initiative/SKILL.md
  - data/raw/claude-docs/kiez-archive/skills/design-initiative/SKILL.md
  - data/raw/claude-docs/akira/skills/design-product/SKILL.md
  - data/raw/claude-docs/kiez-archive/skills/design-product/SKILL.md
  - data/raw/claude-docs/diskoe/skills/design-product/SKILL.md
  - data/raw/claude-docs/akira/skills/design-system/SKILL.md
  - data/raw/claude-docs/kiez-archive/skills/design-system/SKILL.md
  - data/raw/claude-docs/diskoe/skills/design-system/SKILL.md
  - data/raw/claude-docs/akira/skills/design-roadmap/SKILL.md
  - data/raw/claude-docs/diskoe/skills/design-roadmap/SKILL.md
  - data/raw/claude-docs/kiez-archive/skills/design-roadmap/SKILL.md
  - data/raw/claude-docs/guacamayo/skills/design-initiative/SKILL.md
  - data/raw/repos/nonprofit-success-ai/.claude--skills--design-initiative--SKILL.md
  - data/raw/repos/nonprofit-success-ai/.claude--skills--design-product--SKILL.md
  - data/raw/repos/nonprofit-success-ai/.claude--skills--design-roadmap--SKILL.md
  - data/raw/repos/nonprofit-success-ai/.claude--skills--design-system--SKILL.md
---

# Four-Stage Design Pipeline with Backflow

akira's design skills split design-of-record into four stages, each a separate skill with
its own human gate:

1. **Initiative** — the bet, its thesis, phases, and failure branches.
2. **Product** — workstreams, requirements, delivery coverage, quality ladder.
3. **System** — semantics, schema, trust boundaries, provenance.
4. **Roadmap** — issues, commitment classes, ordering.

## Resume at the earliest stale stage

On any change, the pipeline does not restart at the top or patch the bottom; it routes to
the **earliest stage whose inputs moved**. A routing table maps change kinds to stages.

## Backflow digest — detecting staleness from below

Downstream work keeps minting decisions the design never made. Before a design run, build a
digest since the last run's base commit:

- decision / assumption / constraint / risk IDs (`D`, `DA`, `DC`, `RK`) added since BASE
  (`git` + `comm` against the BASE registry), with the commits that added them;
- plan questions tagged `origin: upstream-silent` or `upstream-wrong`;
- review findings anchored on `.md`/`.html` design files.

**A dimension with ≥3 backflow rows is stale at product level or above.**

## Phase 0 — read the tree before the docs

The first deliverable is a build-state audit against the working tree, not the docs. In
one run, **6 of 8 green "built" markers were wrong.** Rules:

- A capability with no file path is ABSENT.
- BUILT ≠ accepted — keep separate columns.
- A wrong build-state marker is costlier than a missing one.
- The system stage uses a four-state vocabulary — BUILT / BUILT, NOT WIRED / SPECIFIED /
  GAP — and no prose states. With no working tree, nothing is BUILT.

## Delivery envelope

The initiative is checked against a fixed envelope so no dimension is silently skipped:
user value, product states, data lifecycle, trust/rights, operations, delivery,
verification (named corpus + row count), economics, retirement. The product stage
re-walks it as a coverage table where each row has a disposition: IN DELIVERABLE / SHARED /
RESEARCH FIRST / DEFERRED — <trigger> / N/A — <reason>.

## Phases are hypotheses

A phase is not a calendar bucket. Each carries evidence, entry assumptions, an exit
condition, the decisions it unlocks, and a **failure branch**. An untested thesis is a
risk, not a foundation; an initiative without a failure branch has assumed its thesis.

## Roadmap rules worth keeping

- **Issue filing is the first irreversible step**, so it has its own invocation, a dry-run,
  and an idempotent reconcile against existing issues.
- Commitment classes: PHASE / DECISION BEFORE PHASE / LATER IDEA / NOT PLANNED.
- **Enforcement lands after the thing it enforces** — a metrics file declared 13 metrics
  gated at 1.0 that nothing computed.
- An AI issue whose eval corpus has zero rows is blocked by the issue that produces the rows.
- The delta registry owns IDs: two docs that minted their own D1–D18 agreed on none.

## See Also
- [[Validated Concept vs Unmeasured System]] — extends (the tree-first audit generalised into a pipeline stage)
- [[Three-Doc Spec Split]] — related (where the stages' outputs land)
- [[Decision-ID Reservation Across Concurrent Plans]] — related (the registry-owns-IDs rule)
- [[Named-Trigger Deferral]] — related (DEFERRED — <trigger> disposition)
- [[Q0–Q5 Quality Ladder]] — related (part of; the product stage's quality plan)
- [[Principal Write-Surface Matrix]] — related (part of; system stage trust plate)
- [[Four-Source Provenance Contract]] — related (part of; system stage provenance plate)
- [[Budget Without a Meter Is a Preference]] — related (part of; product stage budget rule)
- [[Design Decisions Migrate Into Plans]] — extends (why one-shot design output goes inert; the evidence for backflow)
- [[Confirm vs Decide Decision Packet]] — related (the exec-facing format for open questions)
- [[Fix the Generator, Not the Generated Record]] — extends (review findings on a generated design record are sorted by where the fix belongs)
