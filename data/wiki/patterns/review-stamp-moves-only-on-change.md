---
title: Review Stamp Moves Only When the Verdict Does
tags: [infra, pattern]
summary: "In a human review UI that records a verdict plus evidence and a reviewed-at timestamp, stamp the time on the server and only when that axis actually changed (read before write), keep the evidence when a verdict reverts to 'needs review', and give the privileged columns their own separately named write action, because anything that later triggers re-review off the timestamp is lying once every re-save moves it."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-17-dis191-content-sources-slice2-posture-review.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-17-dis191-content-sources-slice2-posture-review.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-17-dis191-content-sources-slice2-posture-review.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-17-dis191-content-sources-slice2-posture-review.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-17-dis191-content-sources-slice2-posture-review.md
---

# Review Stamp Moves Only When the Verdict Does

From an akira admin-tab plan (2026-09-17). The tab let an operator record per-source
rights verdicts on four axes (legal, image, text, redistribution). Each axis had a
posture value, evidence columns (notes, credit text, terms URL, `reviewed_by`) and
`<axis>_reviewed_at`. The spec was a rubric for *what justifies* a value, not a form
spec, so four gaps between "what a reviewer must do" and "what a schema enforces" had to
be decided.

## The rules

1. **The server stamps the time.** `reviewed_at = now()` inside the action, never read
   from form data or a client clock. The automated accelerator that seeds mechanical
   verdicts already injected `now()` the same way.
2. **Stamp only on a real change.** Before writing, compare the submitted axis (posture
   plus its evidence fields) with what is stored, and move `reviewed_at` only if
   something on that axis changed. The first draft called this "accuracy the loop does
   not need". It was reversed, because the spec's annual re-review trigger for the
   strongest permissions reads that timestamp. If every unchanged re-save moved it, the
   trigger would run on a schedule nobody actually kept. One extra single-row
   `select` per submit is cheaper than a timestamp nobody can trust.
3. **Reverting to "needs review" keeps the paper trail.** An axis set back to
   `review_needed` round-trips its existing evidence and timestamp unchanged. To really
   erase a mistaken entry, the operator blanks each field explicitly. "Refuse the revert
   without a reason" was rejected, because it needed new schema state to tell a revert
   with an explanation from one without.
4. **Verdict and evidence in one sitting.** `reviewed_by` is required whenever an axis
   leaves `review_needed`. Notes are required where the rubric needs them: one
   permissive value, and `prohibited`, where the notes are the only place to record
   *which* of three prohibition bases applied. A terms URL is never required, because the
   accelerator legitimately writes `prohibited` with no URL.
5. **A second, separately named action for the privileged columns.** The existing
   registry-edit action guaranteed it wrote *exactly* eight fields, and a test pinned
   that, so a hidden posture field posted to it had nowhere to go. Widening that action
   would quietly void the guarantee. A separate `updatePostureReviewAction` leaves the
   first test proving what it always proved. Only the axes actually submitted are
   patched, and the other three round-trip unchanged.

## Name process controls as process controls

The admin area had one shared Basic-auth credential and no per-person identity, so "only
the named reviewer may set `licensed`" could not be enforced in code. The plan wrote it
down as a **documented process control**: `reviewed_by` is free text the operator types
on each edit. It did not pretend this was access control, and it did not grow a user
system inside a UI slice.

## Accepted residuals

- Read-before-write leaves a small race between two concurrent edits. It was accepted
  for a single-operator tool.
- The tab became a second caller of an exported queue-ordering function, with no
  ownership marker on that module, so a future edit there could break the tab without
  touching it.
- The badge shows *exposure ordering*, not *staleness*. Re-review triggers (terms URL
  404, origin change, annual review) were flagged and not built.

## See Also
- [[Hotlink-Not-Copy Image Posture]] — extends (the rights axes this UI records verdicts for)
- [[Every Column Names Its Reader]] — instance-of (reviewed-at's reader is the re-review trigger, so its write semantics follow from it)
- [[Principal Write-Surface Matrix]] — related (a privileged column set gets its own write surface)
- [[Follow-Up Step Needs a Derived Worklist]] — related (the sibling slice of the same admin tab)
- [[Snapshot the Judged Value on the Verdict Row]] — extends
