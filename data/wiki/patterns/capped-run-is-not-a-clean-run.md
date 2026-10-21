---
title: A Capped Run Is Not a Clean Run
tags: [infra, llm, pattern]
summary: A per-item spend stop that works but lets the batch exit 0 makes a truncated run read green — surface exhaustion as a distinct exit code and a grep-able run-row signal, count skips like any other skip, and run a costed batch with a verified prerequisite, a true count, a sample that still spends, and a kill condition stated before the full run.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-08-29-g3-spend-cap.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-08-29-g3-spend-cap.md
  - data/raw/repos/akira/.claude--docs--plans--2026-08-29-g3-spend-cap.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-08-29-g3-spend-cap.md
  - data/raw/claude-docs/playground/docs/plans/2026-08-29-g3-spend-cap.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-08-29-g3-spend-cap.md
  - data/raw/repos/playground/.claude--docs--plans--2026-08-29-g3-spend-cap.md
  - data/raw/claude-docs/akira/docs/plans/2026-08-29-v4-catalogue-enrichment-run.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-08-29-v4-catalogue-enrichment-run.md
  - data/raw/repos/akira/.claude--docs--plans--2026-08-29-v4-catalogue-enrichment-run.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-08-29-v4-catalogue-enrichment-run.md
  - data/raw/claude-docs/playground/docs/plans/2026-08-29-v4-catalogue-enrichment-run.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-08-29-v4-catalogue-enrichment-run.md
  - data/raw/repos/playground/.claude--docs--plans--2026-08-29-v4-catalogue-enrichment-run.md
---

# A Capped Run Is Not a Clean Run

From a model-enrichment importer (repo akira, 2026-08). The spend guard already existed
and fired correctly: each item checked `ledger.exhausted` before its model call and
recorded a `spend_limit` outcome. The defect was one level up — **the run finished with
status `partial`, exit code 0, and nothing in the console or the run row said the cap was
the reason.** A run that stopped paying for work halfway looked identical to one that had
nothing left to do.

## The fix shape

- **A distinct exit code for "partial by design".** The CLI already mapped every thrown
  error to exit 1. A capped run throws a dedicated `SpendCapError` after the per-source
  loop, mapped to **exit 2** — "spend cap hit, partial run, not a crash". Scripts that
  only test non-zero still see failure; scripts that care can tell the two apart.
- **The per-item guard stays a counter the caller consults, not a throw.** The importer
  already has a per-item failure vocabulary, and a spend stop must be recorded as a
  normal, explicable outcome for the remaining items rather than an exception that
  unwinds a partly successful batch. The throw happens once, at run level, after every
  item has its outcome. (The same reasoning kept the guard out of the model gateway —
  [[Model Gateway Is Transport, Call Site Owns Meaning]].)
- **Count it like the other skips.** A `spendCapSkips` counter beside the existing
  `hashMatchSkips`, printed in the run summary line.
- **Encode the signal where it is already read, not in a new column.** The run row's
  existing `error_message` leads with `spend_cap_exhausted` when the status is partial
  and the cap fired — grep-able, no migration. A new column would need a reader first
  ([[Every Column Names Its Reader]]).

## Running a costed batch (the run that followed)

The first real full-catalogue enrichment run produced its own checklist, most of which
generalises to any batch that spends money per item:

1. **Verify the prerequisite fix is on the executing branch, not just merged.** The cap
   fix had merged elsewhere but `git merge-base --is-ancestor <fix> HEAD` said no. Check
   for the symbol (`grep SpendCapError`) before relying on it.
2. **Query the true count; do not inherit arithmetic.** The plan carried a guessed
   "~364" eligible items. Run the eligibility query first and compare it with the count
   the run itself prints.
3. **Eligible is not publishable.** The set that needs enrichment (anything unenriched,
   including past-dated items) differs from the set that is served. Sizing from the wrong
   one misprices the run.
4. **A dry run still spends.** The importer's dry-run mode skipped persistence but still
   made every model call. That is useful — it validates cost per item without writing
   bad rows — but it is not free. Run a small slice (one small source) first and read
   the printed spend line.
5. **State the kill condition before the full run.** A soft go/no-go threshold on the
   sample's cost per item, written down before the number is seen.
6. **Source-ordered batches as manual checkpoints**, not one unattended invocation; after
   each, check for cap warnings. The content-hash gate makes re-running a batch cheap
   ([[Spend Gate Before the Model Call]]).
7. **The ledger is per-process**, so a multi-batch total is summed by hand.
8. **"Paid, not persisted."** A crash between the model call and the row write produces
   spend with no enrichment; the ledger and the table can disagree after a failure.
9. **Check the execution vehicle exists.** The issue assumed a standalone batch CLI;
   none existed, and the run had to go through the importer instead.

## See Also
- [[Silence Reads as Clean]] — instance-of (exit 0 on a truncated run)
- [[Harness Events Are Not Task Failures]] — related (separating "stopped by the harness" from "failed")
- [[Spend Gate Before the Model Call]] — extends (what happens at run level when the per-call gate starts saying no)
- [[Model Gateway Is Transport, Call Site Owns Meaning]] — related (why the cap is not in the gateway)
- [[Budget Without a Meter Is a Preference]] — related (a cap is only real once something reports it fired)
- [[Dropped Filter Flips the Truncation Direction]] — related (a binding LIMIT whose dropped rows changed when a filter moved)
