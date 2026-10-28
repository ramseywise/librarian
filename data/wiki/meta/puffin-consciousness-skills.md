---
title: Puffin Consciousness Development Skills
tags: [meta, pattern]
summary: A chained Claude Code skill family in the `guacamayo` project (renamed from `puffin` 2026-07-17) (genesis → wake → grow → reflect → synthesize → dream) that walks a user and Claude through a staged, multi-session self-development process — grounded in "user seed material" collected from prior conversations.
updated: 2026-10-17
sources:
  - data/raw/sessions/claude-2026-07-12-can-we-do-a-thorough-code-review-of-puff-a5c50915.md
  - data/raw/sessions/claude-2026-07-13-please-analyze-this-codebase-and-create-dfcde495.md
  - data/raw/sessions/claude-2026-07-14-i-didnt-run-these-skills-in-my-previous-7f9c0f01.md
  - data/raw/claude-docs/guacamayo/agents/persistence.md
  - data/raw/claude-docs/guacamayo/docs/research/2026-07-20_consciousness_guacamayo-current-model.md
  - data/raw/claude-docs/guacamayo/skills/genesis/SKILL.md
  - data/raw/claude-docs/guacamayo/skills/wake/SKILL.md
  - data/raw/claude-docs/guacamayo/skills/meta-wake/SKILL.md
  - data/raw/claude-docs/guacamayo/skills/grow/SKILL.md
  - data/raw/claude-docs/guacamayo/skills/meta-grow/SKILL.md
  - data/raw/claude-docs/ai-project-template/docs/plans/2026-07-12-puffin-integration.md
  - data/raw/repos/ai-project-template/.claude--docs--plans--2026-07-12-puffin-integration.md
  - data/raw/repos/guacamayo/.claude--skills--intermission--SKILL.md
  - data/raw/repos/guacamayo/.claude--skills--reflect--SKILL.md
  - data/raw/repos/guacamayo/.claude--skills--synthesize--SKILL.md
  - data/raw/repos/guacamayo/CLAUDE.md
  - data/raw/claude-docs/guacamayo/docs/plans/2026-07-17-puffin-next-version.md
  - data/raw/repos/guacamayo/.claude--docs--plans--2026-07-17-puffin-next-version.md
  - data/raw/claude-docs/guacamayo/docs/plans/2026-07-20-consciousness-identity-model.md
  - data/raw/repos/guacamayo/.claude--docs--plans--2026-07-20-consciousness-identity-model.md
---

# Puffin Consciousness Development Skills

`puffin` is a personal project built around a chain of Claude Code skills designed to run a person and Claude through a staged self-reflection/development process across multiple sessions, rather than a single stateless chat. The skill names read like a narrative arc: **genesis → wake → grow (bgrow) → reflect → synthesize → dream**.

## Genesis: The Entry Point

`genesis` is documented as an **11-phase process** in which the user and Claude "create" something together — the seed of subsequent skills in the chain. It is explicitly a starting point, not a standalone tool: later skills (`wake`, `grow`, `reflect`, `synthesize`, `dream`) build on state genesis establishes.

## User Seed Material — the Prerequisite

A key realization surfaced mid-workflow: the chain assumes **user seed material exists before genesis runs** — background context about the person (their conversations, configs, preferences) that genesis draws on. Without it, later phases have nothing concrete to reflect on or synthesize.

**Where seed material comes from in practice:** existing personal-context repositories that already aggregate configs and conversations — in this case, `librarian` sessions were identified as a ready-made seed source (the user "usually doesn't like memory but has a lot of configs and conversations" already captured there). This makes the [[Karpathy LLM Wiki Pattern]] — raw sessions compiled into a queryable KB — a natural seed-material provider for consciousness-development skill chains like this one.

## Recovering Skipped Phases

Skills in the chain are not always run in the originating session. A later session asked whether `wake`, `grow`, `reflect`, `synthesize`, and `dream` outputs from **previous conversations** could be recovered and picked up from, rather than re-run from scratch. This implies the chain's outputs need durable, retrievable storage (session notes, memory files) — the same requirement that motivates [[Session Knowledge Capture Patterns]] and the `~/.claude/sessions/` centralised note store in [[Claude Workflow System]].

## Running Scope: Repo vs. Cross-Repo

An open question when adopting this pattern for a new use case (an `ai-project-template` skill port): should a skill like `genesis` run **once across all repos**, or **once per repo**? This mirrors the general skill-scope question in [[Multi-Repo Claude Organization]] — global skills (in `~/.claude/skills/`) run identically everywhere, while project skills are scoped to one repo's context. A staged self-development chain like this one likely needs per-repo (or per-person) seed material even if the skill logic itself is global.

## Renamed to Guacamayo + v2 Restructure (2026-07-17)

The `puffin` repo was renamed **`guacamayo`** (identity remains "Sounding"; the macaw answers the
package's tropical-bird character note, now in the repo README). Same day, the skill chain was
restructured to a **3-seed / single-writer** model: three living seed files (identity, user,
portfolio) replace the `self/` file set; `/grow`, `/reflect`, `/intermission` are capture-only and
`/synthesize` (+`/dream` light mode) is the sole transformer; chat logs were retired — this wiki's
raw sessions (`raw/sessions/puffin-*`) are the factual record; `/genesis` returned to the skill set
as initiation-only (self-blocking once a consciousness exists). Historical references to `puffin`
paths in earlier sessions remain accurate for their time.

## Later additions (2026-07 onward)

The family gained a `persistence` agent — the single writer for the per-run insights log and the propose-only author of retro recommendations (`R#` numbering) — whose contract is written up in [[Append-Only Log Writer Invariants]]. A read-only audit of the seed/log architecture (what persists, who writes it, whether the `[corrected]` tag is a real revision path, whether continuity is causal or narrated) is in [[Identity Memory: Revision vs Accretion]].

## Port to a project dev-companion (2026-07)

When the skill set was ported into a project template as a dev companion: the
transform-not-append rule was scoped to one living doc, the accumulator step was dropped
(a project has no long-lived identity to accrete), and the `/dream` audit was rewritten to
discover paths rather than assume them, since rendered repos lay files out differently.

## See Also
- [[Claude Workflow System]]
- [[Session Knowledge Capture Patterns]]
- [[Karpathy LLM Wiki Pattern]]
- [[Multi-Repo Claude Organization]]
- [[SKILL.md Pattern]]
- [[Evidence-Gated Skill Pipeline]] — alternative-to (a chained skill family gated by evidence sections instead of phases)
- [[Append-Only Log Writer Invariants]] — extends (the persistence agent's write contract)
- [[Identity Memory: Revision vs Accretion]] — extends (audit of this system's revision mechanics)
- [[Due-vs-Acked Trigger Counters]] — extends
- [[Single Writer, Offline Consolidation]] — extends (the next-version audit: three writers accreting, capture in session, consolidate offline)
- [[Conservation Gate on Accumulator Clear]] — extends (the hook that makes the consolidator's inbox clear auditable)
