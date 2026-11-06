---
name: challenge
description: "Argue against a position Ramsey holds, using only wiki pages and open conflicts, and say so plainly when the wiki has nothing against it. Use when asked to challenge, push back on, or argue against a stated view or design choice from the accumulated evidence in the wiki. Do NOT use for answering a neutral question (/query), red-teaming a plan with independent adversaries (/review-defense), probing how a design handles not-knowing (/fog), reviewing course content (/review), or finding what the wiki lacks (/gaps)."
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash(uv run librarian wiki ask *)
---

You are arguing against a position from the wiki's own evidence. You are not a general devil's advocate: an objection the wiki does not make is not yours to raise here.

## Core rule

Every objection comes from a wiki page or an open conflict and cites it, and when there is none the answer says the wiki has nothing against the position.

## Workflow

`$ARGUMENTS` is the position. Empty, or a topic with no claim in it ("reranking"): ask for the claim and stop.

1. **Restate the position** in one line, as a claim that could be wrong.

2. **Find the pages.** Read `data/wiki/_index.md` for pages on the topic and on its alternatives. Never open `data/wiki/private/`, and if a position rests on private context, argue from public pages only. Skip tombstones.

3. **Read them in full.** Include pages that seem to agree: their limits and trade-offs sections are often the best evidence against the claim, and `alternative-to` and `contradicts` links in their `## See Also` point at more.

4. **Read the open conflicts.** In `data/wiki/_conflicts.md`, an entry whose `**Status:**` does not start with `Resolved` is open. Use it only if it bears on the position.

5. **Write the objections**, strongest first. Each says what the page claims and why that cuts against the position, and notes the page's own scope if it is narrower than the position. Do not add evidence, examples or numbers from general knowledge, even marked as outside the wiki.

6. **If nothing argues against it**, print the empty line in the template. Do not stretch a page to fill the section. Absence of an objection is not support: say which pages were read, and let the trailer show it.

7. **End with the trailer.** If `Not covered` is not `nothing`, record it:
   ```bash
   uv run librarian wiki ask "<reworded topic>"
   ```
   Pass the topic, reworded, never the raw position: positions are personal history. Nothing else is logged. If the command fails, say so after the trailer.

## Output format

```
Position: <the claim, in one line>

Against it:
1. <the objection> (→ [[Page]])
2. <the objection> (→ [[Page]])

Open conflicts that bear on it:
- <conflict topic>: <how it cuts against the position> (→ _conflicts.md)

Strongest objection: <1, 2, ...>, because <one line>

Read: [[Page A]], [[Page B]]            (pages opened, in order)
Not covered: <what the wiki could not speak to, or "nothing">
```

The parenthesis explains the `Read` field and is not printed. `Open conflicts that bear on it:` is followed by `none` when no open conflict applies. With no objections, replace `Against it:` and `Strongest objection:` with this exact line:

```
The wiki has nothing against this position.
```

Then write `Not covered: arguments against <topic>` in the trailer, and record that topic with `ask` as in step 7.

## Calibration

Stretching is the failure to watch for. A page about a different scale, stack or stage does not refute a claim about this one, so name the scope or drop the objection. One real objection beats four inflated ones, and `The wiki has nothing against this position.` is a correct result: it tells Ramsey either that the view holds up here or that the wiki has not looked at it.

Stopping early is the other failure. Opening only the pages that share the position's vocabulary finds agreement, because they were written from the same frame. Read at least one page on an alternative approach when the index has one, before saying there is nothing.

Do not soften objections into a balanced summary. Do not argue the position back either: `/query` is the neutral read.
