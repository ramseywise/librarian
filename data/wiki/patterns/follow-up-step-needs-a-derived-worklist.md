---
title: Follow-Up Step Needs a Derived Worklist
tags: [infra, pattern]
summary: "When a follow-up form appears only in the client render right after an action flips a row's status, the revalidated query that excludes the new status removes the row in the same transition, so the entry point is transient at best and gone after any reload; list the follow-up from a persistent anti-join ('accepted with no source yet'), which also makes duplicates structurally impossible to offer."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-17-dis191-content-sources-slice3-propose-from-venue.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-17-dis191-content-sources-slice3-propose-from-venue.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-17-dis191-content-sources-slice3-propose-from-venue.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-17-dis191-content-sources-slice3-propose-from-venue.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-17-dis191-content-sources-slice3-propose-from-venue.md
---

# Follow-Up Step Needs a Derived Worklist

From an akira admin-tab plan (2026-09-17). Its scope collapsed once it was checked
against the tree: the feature it was meant to design (propose a content source from a
just-accepted venue, pre-filled) had **already shipped** under another issue. Rebuilding
it would have stated one fact in two places. The real gap was smaller and had never been
tested.

## The defect

The propose form rendered only inside the candidate row, gated on the accept action's
local success state. But:

- The tab listed candidates with `status = 'proposed'`.
- The accept action flipped the status to `accepted` and revalidated the page.
- The router refetched the server tree **in the same transition** as the local state
  update, so the row, and the form it would have shown, was pruned from the list on the
  very re-render that should have revealed the form.

At best the form flickered. After a reload, navigating away, or a failed validation, the
venue could no longer be reached from the UI to propose a source, with no error and no
sign that it needed one. No e2e spec covered accept → propose, and a three-round review of
the original feature never asked what happens to the row across a reload. Code reading
alone settled it. A dev-server spike was optional.

## The fix

A **persistent section** listing every accepted venue with **no** `content_sources` row
(an anti-join), each with the existing propose form. One mechanism closes two gaps:

- **Durability.** The follow-up is derived from state that lasts, not from a render.
- **Duplicate prevention without a constraint.** Once a source exists for a venue, the
  venue drops off the list, so the UI stops offering it. No unique constraint was added
  (the FK was plain and nullable, and a second source per venue was not ruled out). The
  generic add-source form, which has no venue picker, stays available for that case. A
  two-operator race could still create two rows. That was accepted for a single-operator
  tool and flagged.
- **Always render the section** with an explicit empty-state line. Every other tab in the
  dashboard did this, and the draft's "render only when non-empty" had no reason to
  differ. Omitting the section looks the same as never having checked.

The in-render form became likely dead code, left for a fast follow so it stayed out of
this plan's file list.

## The general rule

Any action that moves a row out of the query that lists it has to say where the next step
for that row lives. If the answer is "in the same render", it lives nowhere. Derive the
worklist from the state that defines "still needs the next step", and the list empties
itself as the work gets done.

## See Also
- [[Map Every State to Its Writer]] — related (the mirror check: every state needs a reader that surfaces its next step)
- [[Silence Reads as Clean]] — instance-of (a venue needing a source, with no visible trace)
- [[Review Stamp Moves Only When the Verdict Does]] — related (the sibling slice of the same admin tab)
