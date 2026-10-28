---
title: Edit In Place by Diffing on the Natural Key
tags: [infra, pattern]
summary: "To edit a parent whose children carry other users' data through an ON DELETE CASCADE (poll options → votes), diff the submitted set against the current rows by natural key inside one transactional function: delete only the unmatched, insert only the new, keep every surviving child's id. Delete-all-and-reinsert silently orphans every vote through the same cascade. And the edit form must render the record's current members, not only whatever the discovery pool still contains."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-21-dis339-poll-inplace-edit.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-21-dis339-poll-inplace-edit.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-21-dis339-poll-inplace-edit.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-21-dis339-poll-inplace-edit.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-21-dis339-poll-inplace-edit.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-21-dis339-poll-inplace-edit.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-21-dis339-poll-inplace-edit.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-21-dis339-poll-inplace-edit.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-21-dis339-poll-inplace-edit.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-21-dis339-poll-inplace-edit.md
---

# Edit In Place by Diffing on the Natural Key

From a group-poll feature in akira (2026-09-21). The share screen's "Edit poll" button
linked to the create form, so every "edit" minted a second, unrelated poll. The fix was a
real in-place edit: rename, change the deadline, add or remove options (bounded 1–5),
host-only, and closed once voting has closed or a plan is confirmed.

## The load-bearing property: surviving children keep their ids

`poll_options` is unique on `(poll_id, event_id)`. `poll_votes.poll_option_id` references
it `ON DELETE CASCADE`. So:

- **Removing an option = deleting its option row.** The cascade deletes its votes for free,
  and every other participant's votes, which point at different, untouched option ids, are
  structurally unaffected.
- **Delete-all/reinsert-all is the trap.** It mints new option ids for the options that
  stayed too, and the same cascade silently wipes every existing vote. Nothing errors. The
  poll just reads as if nobody voted.

The edit function diffs the submitted `event_ids` array against current options **by
`event_id`**. It deletes unmatched current rows, inserts unmatched submitted ids, rewrites
`sort_order` to the submitted order, and updates name and deadline in the same statement.

## Do the diff inside the database function

The diff runs inside one transactional RPC, the same shape as the existing create and
ballot functions: `security invoker`, empty `search_path`, schema-qualified, executable
only by the service role, and raising typed errors that the store maps to a typed
`EditPollError`. The alternative was compare-then-delete-then-insert from the application,
several round trips, where a mid-sequence failure leaves a poll with a half-edited option
list. Host-token and still-open checks run first, inside the function, so a forged or stale
request never reaches the diff. Both the ballot function and the edit function take
`for update` on the same parent row, so Postgres serializes an edit racing a vote. That is
invisible from reading either function alone, so the header comment says it.

The product decision taken at triage: removing an option deletes its votes, and every other
ballot stays intact. This matches whole-ballot-replacement voting semantics and keeps an
already-shared link meaningful. The rejected alternatives were reopening voting on any
structural edit, and blocking edits after the first vote.

## Defect class found in review: the form renders from the pool, not the record

The edit page built its pickable events from a discovery window (14 days, capped at 50) and
derived the *selected* list by looking each current option up in that pool. An option whose
event had started, moved out of the window or sorted past the cap vanished from the list,
along with its remove control. It still counted toward the 5-option cap and was still
submitted. A full poll could then never swap an option. **An edit form must load the
record's current members separately and merge them into what it renders**, or show unknown
selected ids as a removable fallback row. The test that would have caught it is a selected
id absent from the pool.

The same review found the integration test exercising 2 options with 1 retained, while the
test plan specified 3 options with 2 retained across two participants. The weaker scenario
cannot show that votes on *several* surviving options survive.

## See Also
- [[One Use Case Behind Two Transports]] — instance-of (the edit use case behind both the route and the server action)
- [[Data Clusters by Writer and Trust]] — related (the cascade that makes the diff load-bearing)
- [[Capability Token in a Serialized Row]] — related (host and participant identity on the same poll tables)
- [[Natural Key Without a Discriminator Collapses Rows]] — related (natural-key identity going wrong the other way)
