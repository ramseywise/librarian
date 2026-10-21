---
title: Layout Membership by Location
tags: [patterns, infra, pattern]
summary: "Decide which screens get which chrome by where the file lives (nested route groups), not by a pathname conditional or a hand-kept list — then guard the location itself, because a page moved one directory silently gains or loses its tab bar while every render test still passes."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-02-dis53-layouts.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-02-dis53-layouts.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-02-dis53-layouts.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-02-dis53-layouts.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-02-dis53-layouts.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-02-dis53-layouts.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-02-dis53-layouts.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-02-dis53-layouts.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-02-dis53-layouts.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-02-dis53-layouts.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-02-dis53-layouts.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-02-dis53-layouts.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-02-dis53-layouts.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-02-dis53-layouts.md
---

# Layout Membership by Location

From a Next.js App Router restructure (repo akira) that collapsed 11 copy-pasted page
headers and a duplicated tab bar into one layout per structural group.

## Structure, not a conditional

Four consumer routes show a bottom tab bar; their siblings (event detail, poll detail,
poll creation, a kiosk board) must not. The tempting implementation is one consumer
layout that branches on `usePathname()`. Instead, a **nested route group** —
`(consumer)/(tabbed)/` — holds exactly the four tabbed routes and its `layout.tsx` mounts
the tab bar; the bare routes sit as direct children of `(consumer)`, which has no layout
of its own. Route groups are stripped from URLs, so no `href` anywhere changes.

Whether a route gets the tab bar is then answered by `find` on the tree, not by reading a
conditional — the same lesson the project had already learned from a hand-maintained
route→tab map that drifted. Trade-off accepted: more directories, and one URL prefix
(`/poll`) split across two physical subtrees (list page tabbed, detail pages bare) —
documented for the next reader because it surprises.

A fourth group named in the issue was *not* created: reading its four pages showed no
shared chrome to hoist, so its layout would have been an empty pass-through. Recorded as
a deliberate deviation from the issue title rather than silently dropped.

## Guard the location, because location is now the invariant

Round-one review found the positive case tested (the tabbed layout renders the bar) and
nothing guarding the complement. Moving `results/page.tsx` out of `(tabbed)/`, or
`events/[slug]` into it, renders fine, passes every test, and silently changes which
screens show navigation. The fix is a structural assertion: the set of directories under
`(tabbed)/` holding a `page.tsx` equals exactly `{'', 'poll', 'results', 'saved'}`, and
none of those names also resolves to a page outside `(tabbed)/` (exact-path match — a
suffix check false-positives on every nested `poll/[id]/page.tsx`). It was then proven by
mutation: move a bare route in → 1 failure; move a tabbed route out → 2 failures;
restore → green.

The same review caught the companion guard being calibrated to pass: a grep for
`<TabBar` asserted a count of **3** — the one real layout, a component test, and the guard's
own source containing the pattern. Scoped to production code (`--exclude-dir=__tests__`)
it asserts the actual criterion, **1**. See [[Red-Then-Green Proof for Fix-Stage Tests]].

## Derived targets over history

The shared settings header computes its back target from the pathname (`/profile` →
home; everything else → `/profile`) rather than taking per-page props, which layouts
cannot receive anyway. `router.back()` was rejected for a concrete reason: several
settings screens are reached by tapping a link in an email, which opens a **fresh tab
with no history** — `back()` silently does nothing or leaves the app. A fixed target has
no such failure mode. Cost accepted: one flow's conditional back target (to login after
a password reset) collapsed into the hub, safe because the whole group is auth-gated.

## Sequencing and safety checks

- **Order against the issue body when the evidence says so.** The issue declared a
  dependency on the error-boundary work landing first; analysis showed that order was
  worse, because two of that work's `loading.tsx` files rendered their own tab bar and
  would break the one-tab-bar invariant. The plan executed the restructure first and
  flagged the override for the other issue's owner.
- **Check what keys on paths before moving files.** The auth proxy matched on URL
  pathnames, never filesystem paths, so relocating every admin and settings page into
  parenthesised directories left auth intact — the one candidate blocker, verified.
- **`git mv` leaves empty directories behind**, and a doc-path checker that tests the
  filesystem passed locally for that reason while it would fail on a clean CI checkout —
  see [[Always-Red Check Carries No Signal]].

## See Also
- [[Derive the Gate, Don't Copy It]] — instance-of (membership derived from structure, not a maintained list)
- [[Red-Then-Green Proof for Fix-Stage Tests]] — related (mutation-proving the structural guard)
- [[Always-Red Check Carries No Signal]] — related (green for the wrong reason after `git mv`)
- [[Template Migrations for Structural Moves]] — related
- [[Readiness Is Pinned to a Tree State]] — related (the boundaries plan whose paths this move invalidated)
