---
title: Guard the Source, Not the Destination
tags: [patterns, infra, pattern]
summary: "An empty-input guard that checks the pipeline's destination goes permanently dead after the first successful run, so a source that later breaks still exits 0. Check the source for emptiness instead, keep the cold-start guard for its own case, and pin both the stall case and the legitimate idle week in tests."
updated: 2026-10-17
sources:
  - data/raw/repos/librarian/.claude--docs--plans--2026-08-03-LIB-94-cron-output-and-stall-detection.md
  - data/raw/repos/librarian/.claude--docs--plans--2026-08-02-review-LIB-60-cron-fail-loud.md
  - data/raw/repos/librarian/.claude--docs--plans--2026-07-31-LIB-60-session-note-derivation.md
---

# Guard the Source, Not the Destination

From librarian's session-ingestion cron (cartographer), 2026-08. Two passes at one
fail-loud requirement. The first pass closed one failure mode and left a harder one open.

## The sequence

1. **Cold start.** On empty input, the cron wrote a 67-byte placeholder report ("No
   session data available") and exited 0. From outside, that was byte-for-byte a healthy
   run. The fix raised an error and exited non-zero. Its tests asserted both directions:
   empty input fails, populated input succeeds.
2. **The guard checked the destination.** It asked "does `raw/sessions/` contain any
   notes?" A later change derived 343 notes into that directory. From then on the guard
   **could never fire again**.
3. **Stall.** The live summary then read `sessions_synced: 0, problems: [], exit 0` while
   the source directory held only 5 stale files. The source could have been broken for
   good and every run would still pass. The suite was green because it covered only the
   cold case. No test had "destination populated, source stalled".

Stall is the harder case because it only shows up after the tool has worked once, and
that is also when people stop watching it.

## The rule

- **The discriminator is the source.** "0 synced" with a non-empty destination is
  ambiguous. It could be a quiet week (legitimate, exit 0) or a source that moved,
  emptied, or lost permissions (a fault, exit 1). Only the source's state tells the two
  apart. If the source itself is empty, it is broken, whatever the destination holds.
- **Keep both guards.** The destination check is still right for cold start. The source
  check catches stall. Neither covers the other.
- **Record the discriminating field.** Write `source_note_count` next to
  `sessions_synced`, so a reader of the run summary can tell "nothing to do" from "ran
  clean".
- **Pin the idle week too.** Add one test where the source is populated and already
  synced, and assert exit 0. Without it, the fix can over-correct into a guard that fires
  every quiet week, and people learn to ignore it. That is the failure the guard was built
  to fix.
- **Prove the guard can fail.** Plant a defect (`if False and ...`) and confirm the new
  tests go red. Then point the source at a populated tmpdir and confirm the idle-week test
  stays green, which shows the guard is not always on.

## Deliberately not built

The team declined a staleness threshold, which would flag a source that is non-empty but
has had no new file for N weeks. It is a separate decision, and every threshold fires on
some legitimate quiet stretch. The residual gap was accepted and written down: a source
that stops growing but stays non-empty still reads as healthy. The follow-up gets filed if
that case is ever observed, not before.

## Adjacent lessons from the same work

- **A verification run of a writer is a mutation.** The cron writes to three places, so
  "just check it against the real repo" changes the live tree. Run it from a scratch
  worktree, or with every path pointed at a tmpdir.
- **The output nobody reads.** The run summary had zero readers (checked by grep) and was
  being written into a config directory that was meant not to exist. It was moved into
  the repo that writes it rather than deleted. A failed run needs somewhere durable to
  record why it was judged stalled.
- **Faults are collected, not raised.** Each stage appends to a `problems` list, and the
  summary is written *before* the non-zero exit. A starved stage never throws away work a
  later stage finished.

## See Also
- [[Silence Reads as Clean]] — instance-of (a destination-emptiness guard that can no longer fire)
- [[Scan-Floor Guard Against Silent No-Op Checks]] — extends (a guard must be able to fail in the production state)
- [[Known-Gap Alarms Ship as Warn]] — alternative-to (when an accepted residual gap needs a visible alarm rather than silence)
- [[Paired Allow Test for Deny Rules]] — extends (the idle-week test is the paired allow case for the stall guard)
- [[Readiness Is Pinned to a Tree State]] — extends (the plan that closed cold start was outrun by its own derivation step)
