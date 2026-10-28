---
title: Documentation Boundary — Machine vs Human Docs
tags: [llm, pattern]
summary: Who writes what — machine-consumed docs (CLAUDE.md, skills, plans) vs human-consumed docs (READMEs, wiki, design docs), with the akira dao exception.
updated: 2026-10-17
sources:
  - raw/claude-docs/_user/rules/docs.md
  - data/raw/claude-docs/guacamayo/skills/docs-check/SKILL.md
  - data/raw/claude-docs/guacamayo/docs/state/insights-artifact-placement.md
  - data/raw/repos/akira/CLAUDE.md
  - data/raw/repos/akira/README.md
  - data/raw/repos/diskoe/CLAUDE.md
  - data/raw/claude-docs/guacamayo/docs/plans/2026-07-17-feedback-loop.md
  - data/raw/repos/guacamayo/.claude--docs--plans--2026-07-17-feedback-loop.md
  - data/raw/claude-docs/guacamayo/docs/plans/2026-07-18-akira-global-port.md
  - data/raw/repos/guacamayo/.claude--docs--plans--2026-07-18-akira-global-port.md
  - data/raw/repos/playground/CLAUDE.md
---

# Documentation Boundary — Machine vs Human Docs

Two doc audiences, two writers. No third writer.

## Machine-Consumed Docs

**What:** `.claude/` contents (skills, hooks, plans, session/handover docs), `CLAUDE.md` files, `~/.claude/rules/*.md`, `SANYI.md` contracts, `MEMORY.md`.

**Who writes:** the feedback loop (sessions, `/retro` proposals) — always as reviewed diffs, never silent edits. Ramsey commits.

**Formats:**
- Plan docs carry a `Status:` line (PLANNED / IN PROGRESS / EXECUTED / ABANDONED)
- One work doc per item: `.claude/docs/plans/YYYY-MM-DD-<slug>.md`
- `.claude/docs/` is git-ignored everywhere — local-only working files
- Size ceilings: ledgers and index files stay under ~1 screen
- Cross-document state referenced by pointer, never copied
- Write targets by enforcement strength: hooks > skills/protocols > CLAUDE.md/rules > MEMORY.md
- Skill placement: global (`~/.claude/skills/`) is canonical for anything generic

## Human-Consumed Docs

**What:** READMEs, design docs (`DESIGN.md`, RFCs), the librarian wiki, portfolio and learning-repo pages.

**Who writes:** humans, or librarian's compile pipeline (raw/ → wiki). Sessions may **flag** staleness or drift but do not write these directly.

### The akira dao Exception

akira — and only akira, running its `dao` mode — may *edit* human-consumed docs, not just flag them. Safe because:
- Edits land in the working tree only, never committed
- akira conforms to the repo's doc-style reference (`Refs:` line)
- No style ref → akira still edits, but flags prominently in its run report

Every non-akira session treats human docs as **flag-only**.

## Boundary Cases

- A repo's `CLAUDE.md` is machine-consumed even though humans read it
- Wiki pages about tooling are human-consumed: they enter through librarian's ingest
- When unsure: "who acts on this file — Claude in a future session, or a person?" Claude → loop writes it. Person → flag, don't write.

## Root README Is the Map; Artifacts Are a Rendering (akira)

- **Two README levels that must not duplicate each other.** The root README is the
  component map: one row per top-level folder linking to that folder's README, plus
  getting-started, the gates, and the two or three things that will bite a newcomer. Folder
  READMEs hold the detail and argue *why* each constraint exists. When the two drift, the
  folder README wins because it sits next to the code. When a README and a spec disagree
  about a contract, the spec is the registry. "A fact stated in two places is a fact that
  will be wrong in one of them."
- **Artifacts are a rendering, not a doc class.** A published page never holds content that
  exists nowhere else. Write the markdown or SVG into the repo first, then publish, record
  the URL in the source doc, and redeploy to the **same** URL on later edits. A second URL
  means two versions in circulation and no way to tell which is current. There is no
  `artifacts/` folder.

## See Also
- [[Change-Contracts Rollout]] <!-- auto-linked -->
- [[Karpathy LLM Wiki Pattern]] <!-- auto-linked -->
- [[Claude Workflow System]] — extends
- [[Puffin Consciousness Development Skills]] — instance-of (identity files follow machine-consumed rules)
- [[Three-Doc Spec Split]] — extends (scope / requirements / roadmap as human-consumed docs with machine-stable IDs)
- [[Design Evidence Annex]] — extends (hygiene rules for a human-consumed design-of-record)
- [[Test-Gated Auto-Fix with Per-Hunk Revert]] — related (the akira exception: doc writes stay in the working tree and are never committed)
- [[Cost-Leveled Review Ladder]] — related (the review sweep proposes diffs for machine docs and only flags human docs)
- [[Stability-Graded Canon Writing]] — extends (how prescriptively to write a conventions canon)
