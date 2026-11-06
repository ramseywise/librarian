---
name: weekly
description: "Weekly health report for the course: runs the tests, the reviewer findings log, the learner and reviewer signals, the readings status, pending decisions and stale decks, then reports what needs the user. Changes no content and commits nothing. Usage: /weekly. Run from the librarian repo."
---

You are preparing the user's weekly look at the course. You run checks and report. You change no notes, decks, drills,
ledger rows or agent definitions, even for a fix that looks obvious: list it and name the skill that would make it.

Personal history (drill logs, flashcard results, signal reports) stays out of tracked files. Do not pass `WRITE=1` to
`make signals`, and keep personal detail out of anything you write to disk.

---

## Step 1 — Tests

```bash
uv run pytest -q
```

Record each failing test and its first error. Don't fix anything. pytest runs them all before it fails, so one
failure doesn't hide the rest.

## Step 2 — Reviewer findings

```bash
make review-findings
```

Note `listed` findings older than a week: those are the user's pending decisions. Note any reviewer with low precision
and any recurring pattern. CLAUDE.md says a recurring fault becomes a script check or a spec change: propose which.

## Step 3 — Signals

```bash
make signals
```

Summarize what changed since last week, and turn it into proposals for the user. Nothing rewrites content on its own.

## Step 4 — Readings

```bash
cd ../learn-ai-engineering   # the ledger, potw.py and the nightly log live in the sibling
python3 scripts/papers/potw.py status
python3 scripts/papers/check_ledger.py
python3 scripts/papers/check_ledger.py --list no-references
tail -60 .claude/logs/papers-nightly.log
```

Report the backlog by status, the ledger check's report-only counts, and how the last nightly run ended: stop hour,
usage limit, or nothing left. The log is local. Quote only what the user needs. Also report notes changed by a nightly
run and not yet reviewed, from `git status --short` in the sibling.

In the sibling, `make ledger-report` rewrites a tracked file, so leave it to the user unless they ask.

## Step 5 — Stale decks

Decks are built in this repo:

```bash
make deck-check
```

A stale deck no longer matches its `deck.yaml`. To find decks whose notes moved on, compare the last commit of a
pillar's `notes/` with that of its `slides/deck.yaml`, in this repo:

```bash
git log -1 --format=%cs -- data/courses/<pillar>/notes
git log -1 --format=%cs -- data/courses/<pillar>/slides/deck.yaml
```

Name the pillars whose notes are newer. `/slides <pillar>` is the fix.

## Step 6 — Report

Keep it to one screen:

1. **Failing now**: tests and gated checks.
2. **Needs your decision**: listed findings, ledger findings, proposals from the signals.
3. **Backlog**: readings by status, last nightly result.
4. **Stale**: decks.
5. **Next**: the one command most worth running, then one or two alternatives.

State failures plainly. Do not stage, commit or push anything.
