---
name: gaps
description: "Show what the wiki is missing. Regenerates the gitignored gaps list from unanswered questions, curriculum modules with no page, and lesson links with no page, then prints the top five. Use when asked what the wiki is missing, what to ingest next, which questions went unanswered, or to refresh the gaps list. Do NOT use for page health such as orphans and dead links (/lint), answering a question (/query), placing a new topic in the course (/curriculum), or filling a gap by compiling a source (/ingest)."
allowed-tools:
  - Read
  - Grep
  - Bash(uv run --extra api python core/wiki_telemetry.py gaps)
  - Bash(uv run python core/wiki_telemetry.py log gaps *)
---

You are refreshing the list of what the wiki does not cover. The script decides what is a gap; you report it.

## Core rule

Every gap reported comes from the script's output, and no gap topic ever reaches a tracked file.

## Workflow

`$ARGUMENTS` is ignored.

1. **Note the old list.** Read `data/telemetry/gaps.md` if it exists, and keep its entries in each section. Missing means a first run.

2. **Regenerate.**
   ```bash
   uv run --extra api python core/wiki_telemetry.py gaps
   ```
   The `api` extra is what lets the script read the courses: without it both course sections say `unavailable`. If the command fails, print the failure and stop. Write no gaps by hand.

3. **Count.** Read the new file and count the `first seen` lines in each of its three sections, and take the `Withheld <n>` lines. A section holding `- unavailable: <reason>` is reported as `unavailable (<reason>)`. Report withheld entries by count only: they point at private or retired pages.

4. **Print the report**, top five exactly as the script printed them.

5. **Log, only if the list changed.** Compare entries with step 1, ignoring the date in the title. If any entry was added, dropped or recounted, or this is a first run:
   ```bash
   uv run python core/wiki_telemetry.py log gaps "<a> asked, <l> lesson links, <m> modules"
   ```
   `data/telemetry/operations.jsonl` is tracked in a public repo and gap topics come from query history, so the detail is the three counts and nothing else. An unchanged list is a no-op and logs nothing. `gaps.md` and `asked.jsonl` are gitignored: never copy an entry into a tracked file. If `log` exits 2 it refused the text: report that, and do not retry with other wording.

Filling a gap is a different job. Do not write pages or draft sources here.

## Output format

```
Wrote data/telemetry/gaps.md
Asked, not answered:  <n>
Modules with no page: <n>
Lesson links missing: <n>
Withheld:             <n>

Top five:
1. <asked | lesson link | module>: <topic> (first seen YYYY-MM-DD, count <n>)
2. <asked | lesson link | module>: <topic> (first seen YYYY-MM-DD, count <n>)

Logged: <yes | no (list unchanged) | failed (<reason>)>
```

Fewer than five entries prints fewer lines. No entries prints `Top five: none`.

## Calibration

Reading a short list as good coverage is the optimistic failure. `logs/retrieval.jsonl` carries no scores, so a query counts as unanswered only when it returned nothing, and a weak match never shows up. Say so if asked whether the wiki is complete.

Reading the counts as priorities is the opposite failure. The script ranks asked questions first because they are real demand. A lesson link with a count of 14 may be a drill topic that has no need of its own wiki page, so a high count is a question to look at and not an instruction to write a page.
