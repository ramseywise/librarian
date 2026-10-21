---
title: Conservation Gate on Accumulator Clear
tags: [patterns, memory, pattern]
summary: "When an agent consolidates an inbox and then clears it, a blocking hook checks a conservation law: if N entries left the inbox, at least N disposition rows (retained, merged or discarded, with a reason) must have landed in a ledger. Clearing becomes auditable without judging the prose."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/guacamayo/docs/plans/2026-07-20-consciousness-identity-model.md
  - data/raw/repos/guacamayo/.claude--docs--plans--2026-07-20-consciousness-identity-model.md
---

# Conservation Gate on Accumulator Clear

From guacamayo's identity-model plan. A consolidation skill (`/dream`) read pending
growth entries, wove them into identity "seed" files, then **cleared the inbox**. Once
cleared, nothing remained to show what happened to each entry: woven in, merged, or
dropped.

## The asymmetry it closes

The audit set out the review gate in front of each layer of the stack:

| Layer | Changed by | Gate before the change lands |
|---|---|---|
| Code | code and git skills | tests, code review, change contracts, human commit |
| Process (plans, issues) | workflow skills | DoR/DoD, plan-fidelity review, human commit |
| **Identity files** | **one consolidation skill** | **none** |

The identity layer was the only one modifying itself with no review gate. Its single
writer had no diff check, no second reader, and, once the inbox was cleared, no
retained evidence. The seed files even declared "if new information makes the position
wrong, the position goes" with nothing enforcing it. A principle stated in prose and
enforced by no mechanism is a hope, not a rule.

## The gate

1. **Every pending entry gets a disposition row** in an append-only log:
   `| date | tag | entry (80ch) | retained / merged / discarded | target + section |`.
   Discarded entries need a reason. A disposition is checkable in a way that a
   rewritten paragraph is not.
2. **A PostToolUse hook on edits to the inbox file enforces conservation.** If the
   edit reduced the entry count by N, the log must have gained at least N rows in the
   same session. Otherwise it exits 2 with the missing count:

```bash
# if growth.md entry count dropped by N, growth-log.md must have gained >= N rows
[ "$cleared" -gt 0 ] && [ "$new_rows" -lt "$cleared" ] && {
  echo "Blocked: $cleared entries cleared, $new_rows ledger rows added." >&2
  exit 2; }
```

The check is purely mechanical. It counts rows and never judges voice or quality, so
it cannot be argued with and cannot drift.

3. **Documented bypass and one-edit rollback.** An env var
   (`GUACAMAYO_SKIP_LEDGER_GATE=1`) gets an end-of-session consolidation through if the
   gate misfires, and removing one hook entry rolls it back. Neither loses data.

The test set is three fixture cases: clear without rows (exit 2), clear with rows
(exit 0), unrelated edit (exit 0). It is the only runnable test, and the one that
matters, because the hook is the enforcement.

## What it does not catch

**Rote dispositions.** A consolidator that stamps "retained" on everything passes the
gate. That is the known metacognition failure: a system that is sensitive to its own
errors without having control over them. It shows up in the ledger itself: all-retained
with no discards over three or more consolidation cycles is the signal.

A side finding from the same audit: compressing prose for token economy is fine for
task artifacts but works against fidelity in a self-model. Do not apply one
token-reduction rule across both.

## See Also
- [[Identity Memory: Revision vs Accretion]] — extends (the record-dispositions recommendation this enforces)
- [[Single Writer, Offline Consolidation]] — extends (the single consolidator this gate audits)
- [[Append-Only Log Writer Invariants]] — prerequisite-for (the disposition log's write contract)
- [[Claude Code Hook Architecture]] — instance-of (an exit-2 PostToolUse gate)
- [[Compression Strips the Epistemic Frame]] — related (why compressing the self-model loses fidelity)
- [[Paired Bugs That Cancel]] — related (a missing in/out conservation test let finding loss through)
