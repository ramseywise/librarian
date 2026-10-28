---
title: Vendored Hooks Resolve to the Global Copy
tags: [patterns, infra, pattern]
summary: Hooks registered as $CLAUDE_PROJECT_DIR/.claude/hooks/<name> run whatever that path resolves to; when the session root's .claude is a symlink to ~/.claude, the repo's vendored hook copies never execute, so edits to them change nothing. Fix in global canon first, re-vendor byte-identical, and check parity every session.
updated: 2026-10-17
sources:
  - data/raw/repos/galactus/CLAUDE.md
  - data/raw/claude-docs/galactus/docs/plans/2026-08-15-gal-27-band-contract-hitl-gates.md
  - data/raw/repos/galactus/.claude--docs--plans--2026-08-15-gal-27-band-contract-hitl-gates.md
---

# Vendored Hooks Resolve to the Global Copy

galactus vendors copies of the operator's global `~/.claude/` skills, specs and hooks, so that a
fresh clone is a self-contained working setup. Duplicate names are normally a double-load
blocker; here they are intentional, and the global `~/.claude/` stays canonical.

## The trap

The skills are copies that do run. The **hooks are copies that do not run**:

- `settings.json` registers each hook as `$CLAUDE_PROJECT_DIR/.claude/hooks/<name>`.
- In this workspace, `~/workspace/.claude` is a **symlink to `~/.claude`**.
- In a session rooted at `~/workspace`, that path resolves to the global hooks, never to the
  files in the repo's `.claude/hooks/`.

So editing the repo-local hook changes nothing at runtime. In the incident behind this note, the global
copies had fallen behind while everyone edited the repo-local ones, which were never invoked.
The fixes looked applied and the behaviour did not change. A fresh clone *would* run the vendored copies, which is
exactly what makes the bug invisible from inside the repo.

## The rule

1. **Fix the hook in `~/.claude/hooks/` first**, then re-vendor into the repo.
2. **Keep the two byte-identical.** A vendored file is rendered payload, not a fork.
3. **Enforce parity mechanically.** A `hook_parity_check.sh` hook fires once per session on
   `UserPromptSubmit`. It iterates over the vendored set and warns on any `cmp` mismatch or
   missing global counterpart.

The general lesson: when a config path goes through an environment variable, a symlink can
quietly redirect it. Before debugging a hook, confirm *which file* the harness actually executes.


## Parity is a fact about now (galactus, 2026-08)

A dispatcher plan found the repo's vendored hook tree and the global copy had drifted:
the global copy lacked transition-ledger emission entirely. Parity was repaired the same
day, but nothing *enforced* it, and it had been false eight hours earlier. So the
dispatch-time assertion was upgraded from "a hook is registered here" to **"the hook that
will actually run emits transitions"** (grep the resolved hook for the ledger call), and
the dispatcher refuses to run from the wrong execution root. A repaired drift is latent,
not gone. See [[Dispatcher Carries the Skill Body]].

## See Also
- [[Claude Code Hook Architecture]] — extends (how hooks are registered and resolved)
- [[Sync as Render, Not Copy]] — extends (vendored copies are rendered payload with a parity check)
- [[The Untested Copy Wins]] — related (the edited copy is not the executed one)
- [[Claude Workflow System]] — related (config layering: ~/workspace/.claude is a symlink to ~/.claude)
- [[Dispatcher Carries the Skill Body]] — extends (dispatcher asserts the hook that will run)
