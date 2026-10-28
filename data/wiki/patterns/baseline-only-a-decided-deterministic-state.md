---
title: Baseline Only a Decided, Deterministic State
tags: [patterns, eval, pattern]
summary: Visual-regression baselines are only worth committing for UI whose design is decided and whose pixels are deterministic — generated on CI Linux, masked for time-dependent content, and captured after layout fixes land, never before.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-04-dis61-visual-regression.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-04-dis61-visual-regression.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-04-dis61-visual-regression.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-04-dis61-visual-regression.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-04-dis61-visual-regression.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-04-dis61-visual-regression.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-04-dis61-visual-regression.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-04-dis161-tabbar-width.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-04-dis161-tabbar-width.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-04-dis161-tabbar-width.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-04-dis161-tabbar-width.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-04-dis161-tabbar-width.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-04-dis161-tabbar-width.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-04-dis161-tabbar-width.md
---

# Baseline Only a Decided, Deterministic State

A screenshot baseline asserts "this is correct". Capturing one for a state that is undecided,
nondeterministic, or about to be fixed produces a baseline that will be thrown away — or worse,
one that pins a bug. From the akira visual-regression and tab-bar layout plans.

## Determinism rules

- **Generate baselines in CI, on Linux only.** Font rendering differs per OS. Use
  `toHaveScreenshot` (which suffixes baseline names by platform) rather than
  `toMatchSnapshot`; baselines come from a `workflow_dispatch` job running
  `--update-snapshots`, uploaded as an artifact that a human reviews and commits. A
  `-darwin.png` file in a diff is the tell that a local baseline slipped in.
- **Mask what depends on run time:** dates rendered relative to "now", fixture names built from
  `Date.now()`. Disable animations. Set `snapshotPathTemplate` explicitly so paths do not
  depend on defaults.
- **Watch conditional navigation.** An unconditional screenshot placed after a conditional
  `goto` captures whatever page the test happened to be on.
- Diff tolerance (`maxDiffPixelRatio: 0.02`) was a guess; treat it as a starting knob, not a
  derived threshold (same spirit as [[UNGATED Metric Convention]]).

## Decision rules

- **Never baseline an undecided state.** The desktop viewport was deliberately left out because
  its layout depended on an open design decision; a baseline captured now would be discarded
  under either outcome. Partial delivery (one viewport of two) was recorded on the issue and in
  the roadmap rather than silently closing the ticket — see [[Landed Is Not Complete]].
- **Land layout fixes before capturing.** A bottom tab bar stretched full-width on wide screens;
  the fix constrained the `<nav>` box itself (`fixed left-0 right-0 mx-auto max-w-xl`), not
  just its contents. Baselining before the fix would have pinned the broken chrome.

## Layout needs a real browser

jsdom performs no layout, so unit tests cannot assert widths or heights. The tab-bar fix was
verified by a real-browser e2e that pins the element's box (height 64px, bounded width). A
component test that "passes" on layout properties is asserting nothing — the same family as
[[Hydration Gap Silent Input Loss]], where the failure lives in a layer the test harness lacks.

## See Also
- [[Landed Is Not Complete]] — extends (partial delivery recorded, not closed)
- [[UNGATED Metric Convention]] — extends (tolerances start as guesses)
- [[Hydration Gap Silent Input Loss]] — extends (failures only a real browser sees)
