---
title: Observed Transitions, Not Declared
tags: [meta, infra, pattern]
summary: "A PostToolUse hook can only see the file after a write, so a declared prior state (From:) is a self-report it cannot verify; a PreToolUse hook reads the doc before the write and checks the declaration against the observed state — scoped to fragments that carry a real move, with a restatement branch and two-sided negative controls so it never false-rejects settled docs."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/galactus/docs/plans/2026-08-14-gal-14-observed-transitions.md
  - data/raw/repos/galactus/.claude--docs--plans--2026-08-14-gal-14-observed-transitions.md
  - data/raw/claude-docs/galactus/docs/plans/2026-08-14-pipeline-orchestration.md
  - data/raw/repos/galactus/.claude--docs--plans--2026-08-14-pipeline-orchestration.md
  - data/raw/claude-docs/galactus/docs/plans/2026-08-14-orchestrator-design.md
  - data/raw/repos/galactus/.claude--docs--plans--2026-08-14-orchestrator-design.md
---

# Observed Transitions, Not Declared

The galactus plan-doc state machine (`Status:` plus a `From:` companion naming the state
advanced from) was validated by a PostToolUse hook. Research found that hook validated
**vocabulary, not transitions**: it checked the token was one of nine and never read the
prior value, so `RESEARCH → COMPLETE` in one edit passed — "a state machine enforced as a
spellchecker." Adding a legal-edge table helped, but a PostToolUse hook still cannot see
what was there before, so a writer that lies about `From:` passes whenever the claimed
edge is legal. It catches accidental skips, not deliberate ones.

## Split the hooks by what each can observe

| Hook | Sees | Owns |
|---|---|---|
| **PreToolUse** | the file *as it stands before the write* plus the incoming fragment | "was that prior state actually there" |
| **PostToolUse** | the resulting file | field presence, legal-edge table |

Two files, not one dual-registered script branching on the event name — that would put two
exit-code contracts in one script. The edge table is duplicated in both, with a drift test
asserting byte equality of the two literals (and a perturbation check so it cannot pass
vacuously) — cheaper than a shared sourced file in a directory the agent cannot edit.

## The fragment rule and the restatement branch

PreToolUse sees an edit *fragment* (`new_string` or `content`), not the resulting file.
Simulating the edit to derive the result was rejected — it means reimplementing Edit
semantics. So the hook validates **only fragments carrying both `From:` and `Status:`**,
and passes everything else.

That was not enough. Because `From:` persists after a write, the pair is the *resting
state* of every settled doc; the first version false-rejected 3 of 14 corpus docs. The fix
is a **restatement branch**: if the fragment's `Status:` equals the on-disk `Status:`,
it is restating settled front matter, not declaring a move, and passes. Origin writes (no
file, or no `Status:` on disk) pass without `From:` and are *rejected* if they declare one
— claiming a prior state that never existed is exactly the lie being caught.

**Accepted cost, written into the hook:** a writer that splits the pair across two edits
evades the check. Before building, this was *measured* rather than asserted — 7 of 7 real
passing writes produced exactly one ledger edge, timestamps aligned — so the gap is latent
and the build is not inert.

## What "verified" certifies

`observed: verified` means the `From:` named in the write matched the `Status:` on disk at
that moment. It does **not** certify the phase ran: a writer told "you declared READY but
the doc is at PLANNED" can retry with `From: PLANNED` and pass, correctly labelled, having
skipped whatever the operator thought happened. The edge table catches illegal edges; this
field is about file state.

## Test discipline for a blocking hook

A false reject on PreToolUse `Write|Edit` blocks every plan-doc write in every session, so:

- **Two negative controls.** Stub the hook to exit 0 — the "lying `From:`" cases must fail
  (proves it fires). Remove the restatement branch — the corpus cases must fail (proves it
  does not over-fire). The original suite could pass while failing the second.
- **Corpus sweep.** Run the finished hook against every existing doc using its own front
  matter as the fragment; any block is a false reject on a file already in the repo.
- **Register last.** Registration lands only after the tests are green; a hook live before
  its tests pass blocks the pipeline for everyone.
- **A crashed hook looks like a pass** (every guard exits 0 on absence) — so verification
  is recorded positively, never inferred from silence. See
  [[Read-Side Retraction by Observer Vintage]] for the ledger side.

## See Also
- [[Plan-Doc Status Enum]] — extends (the enum and edge rules being enforced)
- [[Claude Code Hook Architecture]] — instance-of (PreToolUse vs PostToolUse capabilities)
- [[Read-Side Retraction by Observer Vintage]] — prerequisite-for
- [[Map Every State to Its Writer]] — extends (the companion "honest state machine" fix)
- [[Paired Allow Test for Deny Rules]] — extends (testing that a guard does not over-fire)
