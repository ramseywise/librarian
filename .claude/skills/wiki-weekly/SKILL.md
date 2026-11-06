---
name: wiki-weekly
description: "Weekly review of the wiki, under one page: what was added, what is unresolved, thin spots and three next actions, from the telemetry in data/telemetry/ and open conflicts. This is not the course repo's /weekly. Use when asked for the wiki's weekly review, what changed in the wiki this week, or how the wiki's health is trending. Do NOT use for the course health report on tests, reviewers, readings and decks (/weekly), a full page-by-page health check (/lint), or merging and retiring pages (/compact-wiki)."
allowed-tools:
  - Read
  - Grep
  - Bash(uv run librarian wiki stats --json)
  - Bash(uv run librarian wiki snapshot)
  - Bash(uv run librarian wiki check)
  - Bash(uv run librarian wiki graph --json)
  - Bash(uv run librarian wiki gaps)
  - Bash(uv run librarian wiki log weekly *)
---

You are writing the wiki's weekly review. This is not the course `/weekly` from `learn-ai-engineering`, which reports on course tests, reviewer findings, readings and decks: this one covers `data/wiki/` only.

## Core rule

Every number comes from the telemetry script or its files, and the report ends in exactly three next actions, each traceable to a line above it.

## Workflow

`$ARGUMENTS` is ignored. The window is the last seven days, ending today.

1. **Current numbers.**
   ```bash
   uv run librarian wiki stats --json
   ```
   Use `metrics.<name>.value` and `.status`, `pages`, `domains` and `open_conflicts`. Never compute or estimate a rate yourself. If this fails, print the failure and stop: there is no review without it.

2. **Trend.** Read `data/telemetry/metrics.jsonl`. Rows are oldest first, so the latest row is the last line. If there is no row, or the latest row is seven or more days old:
   ```bash
   uv run librarian wiki snapshot
   ```
   and remember that a snapshot was written. Compare the current numbers with the row that was latest before this step. With no earlier row, write `first row`. `metrics.jsonl` is tracked and holds no page titles beyond public hubs, so leave it for Ramsey to stage.

3. **What was added.** Read `data/telemetry/operations.jsonl` if it exists. Entries have `date`, `op` and `detail`; rows with a `month` key are older roll-ups, so ignore those. Take entries in the window, newest first. Missing file or no entries: `nothing logged this week`. Do not reconstruct the week from git.

4. **Unresolved.** Read `data/wiki/_conflicts.md`: an entry whose `**Status:**` does not start with `Resolved` is open. The count must match `open_conflicts`; if not, say so. Then run the leak check:
   ```bash
   uv run librarian wiki check
   ```
   Exit 1 is a blocker: report the public file and line it gives, never a private title. Warnings are counted, not listed.

5. **Thin spots.** Refresh and read the gaps:
   ```bash
   uv run librarian wiki gaps
   ```
   Take the top three lines it prints. Add any metric whose status is `watch` or `broken`, and any domain with fewer than five pages. Do not open `data/wiki/private/`.

6. **Shape.**
   ```bash
   uv run librarian wiki graph --json
   ```
   Report the number of entries in `clusters`, then `unsettled`, then the `page` of the first entry in `bridges`. If `stability` is below 0.9, append ` (clusters unsettled)` to the line. No trend and no verdict: these numbers have no bands. If this fails, print `Shape: unavailable (<reason>)` and carry on: the review does not depend on it.

7. **Three next actions**, in order of what they would change most. Each one names a command (`/ingest <source>`, `/lint`, `/compact-wiki`, `/gaps`, or `/ingest resolve`) and the line above that it answers. Exactly three, even in a quiet week: `make wiki-check` passing does not count as an action.

8. **Log, only if a snapshot was written in step 2.**
   ```bash
   uv run librarian wiki log weekly "snapshot <date>, <pages> pages, <open_conflicts> open conflicts"
   ```
   `operations.jsonl` is tracked in a public repo and gaps come from query history, so the detail is those counts and never a gap topic or page name. A re-run inside the week wrote no snapshot, so it is a no-op and logs nothing. If `log` exits 2 it refused the text: report that, and do not retry with other wording.

## Output format

```
Wiki week: <YYYY-MM-DD> to <YYYY-MM-DD>

Added:
- <YYYY-MM-DD> <op> <detail>

Health: <pages> pages, orphan <n>%, average degree <n>, main component <n>%, stale <n>%, typed links <n>%, stubs <n>%
Against <YYYY-MM-DD>: <what moved, with both numbers, or "no change", or "first row">

Unresolved: <n> open conflicts
- <conflict topic>
Private leak check: <clean | <n> blockers: <public file:line> | unavailable (<reason>)>

Shape: <n> clusters, <n> unsettled pages, top bridge <page>

Thin spots:
- <gap line, watch or broken metric, or small domain>

Next:
1. <action> (`/command`): <the line it answers>
2. <action> (`/command`): <the line it answers>
3. <action> (`/command`): <the line it answers>

Snapshot: <written | not needed, latest row <YYYY-MM-DD> | failed (<reason>)>
```

`Added:` is followed by `nothing logged this week` when empty, and `Thin spots:` by `none`. Rates print as percentages from the script's fractions.

## Calibration

Over one page is the first failure: this is read in a minute, and past about 40 lines it stops being read. List at most ten operations, and summarise the rest as a count.

Treating page count as progress is the second. A week of 30 new pages with a rising stub rate is a worse week than three pages with none, and page count is never a health number. Read trends against each metric's `status` from the script, and do not call a move of under one percentage point a trend.

Vague actions are the third: "improve coverage" gets nothing done. An action Ramsey cannot start from the line as written is not one of the three.
