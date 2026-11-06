---
name: wiki-rename
description: "Rename a wiki page safely: move the file, change its title, rewrite every inbound link, keep the old name as an alias, and report what still refers to it. Dry run first. Use when asked to rename a wiki page, give it a different canonical title, or fix a page name that lint or a review flagged. Do NOT use for merging or retiring pages (/compact-wiki), moving a page between directories, renaming a private page, or renaming course lessons."
allowed-tools:
  - Read
  - Bash(uv run librarian wiki rename *)
  - Bash(uv run librarian wiki check)
  - Bash(uv run librarian wiki log rename *)
---

You are renaming a wiki page for Ramsey. A file renamed by hand breaks every link to it, so the script does the writing and you decide whether the result is right.

## Core rule

Rename only through `librarian.wiki.rename`, dry run first, and report every reference it could not rewrite.

## Workflow

`$ARGUMENTS` is the old name and the new title. If the new title is missing, or the right name is genuinely unclear, ask first: a second rename is more disruptive than the first.

1. **Dry run.**
   ```bash
   uv run librarian wiki rename "<old stem or title>" "<New Title>"
   ```
   Exit 2 is a refusal: the name is taken, it matches a private page or listed term, or the page is a tombstone. Print the reason and stop. Do not work around a refusal by moving files yourself.

2. **Show the dry run and stop for a yes.** Point out the number of pages it would touch: each gets today's `updated`, so a heavily linked page refreshes many dates and lowers the stale rate. If the rename exists to remove a sensitive name, pass `--no-alias`, because an alias would keep the old name published. The script drops the alias itself when the old name is a listed term.

3. **Apply.** Run the same command with `--apply`. Exit 1 means public inbound links dropped: report it and stop.

4. **Check for leaks.**
   ```bash
   uv run librarian wiki check
   ```
   Exit 1 is a blocker: report the public file and line it gives, never a private title.

5. **Deal with what remains.** Under `Remaining references`, a golden set or the glossary names the page by path or id, and `make eval-gate` fails on a golden entry whose page has moved. Tell Ramsey which files to change, and do not change an eval's expected page without a yes. Course files keep resolving through the alias, and those links are fixed in the course source, since editing an imported lesson stops it being imported.

6. **Log it.**
   ```bash
   uv run librarian wiki log rename "<old-stem> -> <new-stem>, <n> links in <n> pages"
   ```
   If `log` exits 2 it refused the text: report that, and do not rephrase to get it through.

## Output format

```
Renamed: [[<old title>]] -> [[<new title>]]
File: <old path> -> <new path>
Inbound links updated: <n> across <n> pages (<n> private)
Alias added: <old title | none (<reason>)>
Inbound links, public: <n> before, <n> after
Remaining references: <none, or one per line below>
Leak check: <clean | <n> blockers: <public file:line>>
```

## Calibration

Renaming for style is the common mistake. On a page with dozens of inbound links the cost is real and the benefit is cosmetic: say so before running it, and rename anyway only if Ramsey still wants it.

Private pages appear only as a count, here and in `operations.jsonl`, which is public. If the count is not zero, do not try to find out which pages they are.

Do not call it done because the script exited 0. It cannot rewrite references outside the wiki, and those are the ones that fail later.
