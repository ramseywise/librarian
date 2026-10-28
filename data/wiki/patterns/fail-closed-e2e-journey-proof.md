---
title: Fail-Closed E2E Journey Proof
tags: [patterns, eval, pattern]
summary: "An e2e test with a try/catch, success flag or conditional skip around its key step can report green without ever saving anything. Make the journey assert its key step unconditionally, wait on a named readiness attribute that mirrors the real interactivity gate, and record dated repeat counts (20/20 per engine). Report the claim as unverified until those counts exist."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-16-dis307-save-saved-e2e-deterministic.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-16-dis307-save-saved-e2e-deterministic.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-16-dis307-save-saved-e2e-deterministic.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-16-dis307-save-saved-e2e-deterministic.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-16-dis307-save-saved-e2e-deterministic.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-16-dis315-flow-c-seed-date.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-16-dis315-flow-c-seed-date.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-16-dis315-flow-c-seed-date.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-16-dis315-flow-c-seed-date.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-16-dis315-flow-c-seed-date.md
---

# Fail-Closed E2E Journey Proof

From an akira plan to make the "log in → save a result → see it on /saved" Playwright flow
a real proof. Research showed that the client-side race the issue was named after no longer
existed: saved ids were resolved on the server and the save button was gated on hydration.
The remaining defect was in the test.

## The defect: a test that could pass without the journey

The save step was wrapped in `try/catch` with a `saveSucceeded` flag and a skip annotation.
A missing save POST, a non-200 response, or a missing `/saved` title all ended in a green
run. The test could not tell a working journey from a broken one.

## The fix

1. **Assert unconditionally.** A missing POST, a non-200 status, or a missing `/saved` title
   is now a failure. No skip, flag or annotation remains.
2. **Wait on a named readiness contract, not on timing.** The button already had a native
   `disabled={!hydrated}` gate. A `data-save-ready="true|false"` attribute exposes the same
   gate, and component tests assert it agrees with the disabled state in both directions.
   The e2e test waits for `data-save-ready="true"` and `toBeEnabled()` before it clicks. See
   [[Hydration Gap Silent Input Loss]] for why the gate exists.
3. **Repeat counts as the evidence.** Metric: 20/20 on Chromium and 20/20 on WebKit with
   `--repeat-each=20`, each run including the `/saved` assertion. Final result: 40 passed.
4. **No claim without the counts.** The first session finished the code but could not
   collect the repeats. It wrote "NOT COLLECTED" and left the project's status doc
   unchanged. Writing the claim without the counts would repeat the unverified-assertion
   failures the workflow exists to prevent.

## What blocked the repeats (all environment, none in the plan's files)

- **Stale fallback keys.** The Playwright config and global setup hard-coded demo-shaped
  JWT fallbacks that no longer matched the local stack's live keys. Both read env vars
  first, so exporting the live values fixed it without editing files.
- **Build-time env.** Next.js inlines `NEXT_PUBLIC_*` values at `next build`. A
  `webServer.env` override has no effect on a build made before the variables were
  exported, so the build had to be redone.
- **Seed date vs default answer.** The seed wrote the event 7 days ahead, and the default
  intake answer was "today". The pool came back empty and the page fell back to demo items.
  This was confirmed by a data-only patch that was reverted right away. The fix landed in a
  separate issue.
- **A dropped foreign key broke an embed.** An unrelated migration dropped the saves →
  events FK, and the saved-items read failed with PostgREST `PGRST200`. PostgREST needs the
  FK to resolve the embed.

## The seed-date fix and what the repeats exposed (2026-09-17)

The separate seed-date issue kept the shared event at seven days out. It did not move
fixtures to "today" or change the production default. The journey now picks "Other date"
by accessible name and fills in the seeded date. Getting 20 repeat runs to pass exposed
more harness defects:

- **Read the seed back from the row, not from memory.** Global setup and the test worker
  are separate Node processes, so only the database row is visible to both. The helper
  reads `start_at` back and converts it to a local *calendar date* in the seed contract,
  not in the browser, so a run near midnight cannot shift the day. The spec never
  recomputes `now + 7 days` on its own.
- **`--repeat-each` turns leftover state into a different request.** Saved ids are
  resolved on the server, so a save from iteration 1 made the button render as
  already-saved in iteration 2. The click then fired `DELETE` instead of the `POST` the
  test waited for, and every iteration after the first failed. A per-test reset deletes
  the seeded save so each run starts from the same unsaved state as the seed.
- **The dropped-FK embed was fixed by not embedding.** The saved-items read now queries
  the saves table, then the events table by id. That removed the `as unknown as` casts,
  so the select is typed end to end. Eight new unit cases fail against the old code. A
  "FIXED" claim in the status docs for that read was now stale: the read had broken
  again, by a different mechanism, after an earlier fix.
- **The first repeat run wrote a missing baseline.** That screenshot step had never been
  reached before, so iteration 1 on one engine "failed" by creating the baseline, and
  iterations 2 to 10 matched it. Someone inspected and staged the new baseline. It was
  not accepted blindly.
- **Shared fixtures race at two workers.** Two browser projects sharing one test user and
  one seeded event produced an occasional 500 that did not reproduce at one worker. The
  evidence run used `--workers=1`, and the race was left open as a named follow-up.

## See Also
- [[Hydration Gap Silent Input Loss]] — extends (the readiness attribute exposes that page's hydration gate as a testable contract)
- [[Component Test in a Shape the App Never Uses]] — related (the sibling journey hit the same seed-date defect)
- [[Validator That Proves by Cast]] — related (the same saved-items read path broke earlier on view-model column names)
- [[Scan-Floor Guard Against Silent No-Op Checks]] — instance-of (a test that can pass without exercising its subject)
- [[Landed Is Not Complete]] — related (code done, evidence not collected)
