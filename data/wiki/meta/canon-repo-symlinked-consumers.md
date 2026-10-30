---
title: Canon Repo, Symlinked Consumers
tags: [meta, pattern]
summary: Every shared skill, spec and hook lives in exactly one repo, the one whose job it serves; ~/.claude and rendered templates reach it through symlinks pointing into that repo, never copies — copier follows symlinks so generated projects get real files, and the only permitted fork is a .jinja twin kept line-for-line with its root apart from a rendered path.
updated: 2026-10-30
sources:
  - data/raw/repos/galactus/CLAUDE.md
  - data/raw/repos/guacamayo/CLAUDE.md
---

# Canon Repo, Symlinked Consumers

How the personal workspace keeps one copy of each Claude Code skill, spec and hook while
using them from every repo.

## Ownership rule (2026-10-29)

**Every skill lives in exactly one repo, the one whose job it serves.** The memory,
maintenance and review skills live in the identity/review repo; the prototyping skills
live in the prototyping repo; knowledge and drill skills live in this wiki's repo.
`~/.claude/skills/` holds symlinks to the shared ones, never copies. Capabilities used
everywhere, such as `/fog` and its advisor agent, are reached through those symlinks, so
paths inside them are absolute to the owning repo.

## Direction of the links

In the prototyping repo, `.claude/skills/`, `.claude/specs/` and `.claude/hooks/` are the
canonical copies. `~/.claude/` holds none of them and is **not upstream of anything**:

- `~/.claude/skills/new` is a symlink into the repo, so `/new` works from any directory.
- The convention refs in `~/.claude/refs/` are symlinks into the repo's `.claude/specs/`,
  so a bare `Refs: python.md` line in any repo's CLAUDE.md reads the canonical copy.
- Edits happen in the repo, never through the global path.

## Templates ship from the same files

The repo also renders new projects from a copier template. Every shared skill or hook
under `template/.claude/` is a symlink into the root `.claude/`. Copier follows symlinks,
so a rendered project gets real files while the template itself holds no second copy.
Two rules keep this from drifting:

- **Never replace a symlink with a file.** Doing so forks the canon silently, and the fork
  ships to every future project.
- **A `.jinja` twin exists only where the generated project needs a rendered path**, and
  it must stay line-for-line with its root twin apart from that path.

## The trap this sets

Hooks registered as `$CLAUDE_PROJECT_DIR/.claude/hooks/<name>` fire only when the session
is rooted in the owning repo. In this workspace `~/workspace/.claude` is itself a symlink
to `~/.claude`, so a session rooted one level up resolves the hooks path to a directory
that does not exist, and no guard fires. That failure is written up in
[[Vendored Hooks Resolve to the Global Copy]].

A related shadow: the identity repo keeps a mobile mirror of `~/.claude/refs/` for cloud
clones. It is labelled "shadows, not canon"; the global originals win on the Mac and the
mirror is refreshed at session end.

## See Also
- [[Vendored Hooks Resolve to the Global Copy]] — extends (what breaks when the session root is wrong)
- [[Archived Skills Convention]] (where retired skills go in the same repos)
- [[Capability vs Phase Skills]]
- [[Puffin Consciousness Development Skills]]
