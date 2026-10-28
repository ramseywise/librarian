---
title: Adoption Ban Needs an Escape Hatch
tags: [patterns, infra, pattern]
summary: "A lint rule that bans raw elements outside a primitives folder, with no exemption path and no primitive for every case it bans, forces callers to misuse the nearest primitive — a native radio was pushed through a text-input component and inherited its border — so ship a ban with its escape hatch, test every behaviour the new dependency was justified by, and treat a missing budget as an absent control rather than a pass."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-02-dis49-primitives.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-02-dis49-primitives.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-02-dis49-primitives.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-02-dis49-primitives.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-02-dis49-primitives.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-02-dis49-primitives.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-02-dis49-primitives.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-02-dis49-primitives.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-02-dis49-primitives.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-02-dis49-primitives.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-02-dis49-primitives.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-02-dis49-primitives.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-02-dis49-primitives.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-02-dis49-primitives.md
---

# Adoption Ban Needs an Escape Hatch

From building a UI primitives layer (Button, Input, Card, Dialog via `cva` +
`tailwind-merge` + Radix) in a Next.js app (repo akira), migrating 78 measured call sites
(54 buttons, 22 inputs, 2 dialogs), then adding a lint gate so the raw elements could
not creep back.

## The ban and what it forced

The gate was an ESLint `no-restricted-syntax` rule on `JSXOpeningElement` named `button`
or `input` — AST-based, so a string `"<button>"` in a comment or fixture does not match —
across `src/app/**/*.tsx`, ignoring only the primitives folder and tests.

Review found its cost one call site later. A poll form's deadline picker is a native
radio. Banned from writing `<input type="radio">`, the author routed it through `Input`,
whose base classes are for text fields. `tailwind-merge` resolved the conflicting
utilities the caller overrode (`w-full`→`w-4`, `rounded-xl`→`rounded-full`, padding to 0)
but the caller passed no border utility, so `border border-zinc-300` survived onto the
radio — a browser-dependent stray ring. Behaviour was correct; the shape was wrong.

The root cause was not the call site but the rule: **no escape hatch and no primitive for
the banned case.** Options named: add `Radio`/`Checkbox` primitives; narrow the selector
to text-like `type` values; or a documented per-site exemption. A ban is complete only
when every banned use has a sanctioned destination.

## Test what justified the dependency

Radix's dialog was adopted because the two hand-rolled dialogs lacked four things: focus
trap, Escape to close, focus restore, scroll lock. The tests covered three. The fourth —
the one most likely to regress silently in a library upgrade — had none. When a
dependency's justification is a list of behaviours, that list is the test plan.

## An absent control is not a clean pass

The contracts reviewer returned no findings because the change contract declared **no
dependency budget** — so five new runtime dependencies breached nothing. Review recorded
this as an absent control: a primitives layer pulling in a dialog library and a toast
library is the archetypal case a budget exists to govern. "Nothing violated" and "nothing
to violate" read identically in a findings list.

## Silent drops found along the way

- **Opacity modifiers on CSS-variable colour tokens.** The design tokens were
  `var(--color-x)` resolving to plain hex. Tailwind's opacity modifier (`bg-ink/40`) needs
  channel-format variables; with hex it compiles, passes type-check, lint and the
  token-lint gate, and renders the colour at **full opacity**. The dialog overlay kept
  the literal `bg-black/40`, with an inline comment and a recorded design decision so a
  later "tokenise everything" cleanup would not ship an opaque backdrop.
- **Deferred client chrome in a Server Component.** `next/dynamic(..., { ssr: false })`
  for the global toast mount fails the build when called in the root layout (a Server
  Component). Moved into a tiny `'use client'` wrapper imported normally — same deferred
  hydration, only the file boundary moved. The performance reviewer had credited the
  mitigation as written; it existed only in its moved form.

## Scope fences that held

The plan listed what the issue must **not** do: define tokens (another issue's), create
the Skeleton (another plan already specified it at the same import path — two creators
would collide), or convert existing inline error banners to toasts — that would silently
expand "primitives" into "notification UX", a design decision the issue did not own.

## See Also
- [[Scan-Floor Guard Against Silent No-Op Checks]] — related (a gate with nothing to check reports clean)
- [[Readiness Is Pinned to a Tree State]] — related (re-refined the same day a dependency merged)
- [[Layout Membership by Location]] — related (sibling frontend-quality issue)
- [[Silence Reads as Clean]] — related (the silently dropped opacity)
- [[Component Test in a Shape the App Never Uses]] — extends (the focus-restore justification, tested in the app's controlled shape, was broken)
- [[Green Lint Proves Absence, Not That the Rule Fires]] — related (the ban rule sat dead behind another config block)
