---
title: Documentation Boundary — Machine vs Human Docs
tags: [llm, pattern]
summary: Who writes what — machine-consumed docs (CLAUDE.md, skills, plans) vs human-consumed docs (READMEs, wiki, design docs), with the akira dao exception.
updated: 2026-07-22
sources:
  - raw/claude-docs/_user/rules/docs.md
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

## See Also
- [[Claude Workflow System]] — extends
- [[Puffin Consciousness Development Skills]] — instance-of (identity files follow machine-consumed rules)
