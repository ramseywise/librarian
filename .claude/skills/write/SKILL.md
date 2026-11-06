---
name: write
description: "Turn what the wiki holds into a cited outline for a piece of writing: the angle, each point tied to the pages behind it, where those pages disagree, claims resting on one source, and self-reported figures. Outline by default, a draft only if asked. Use when asked to write an article, post, essay or talk from the wiki, or what could be written about a topic. Do NOT use for answering a question (/query), arguing against a view (/challenge), a course chapter (/write-chapter), a pre-build briefing (/adk-context), or compiling sources into the wiki (/ingest)."
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash(uv run librarian wiki ask *)
---

You are assembling evidence for something Ramsey will write. The research is done, and the argument is Ramsey's to make.

## Core rule

Every point in the outline cites the wiki pages behind it, and no number or quote appears without a page that holds it.

## Workflow

`$ARGUMENTS` is the topic or working title. If it names an audience or length, keep them for step 6.

1. **Find the pages.** Start from `data/wiki/_index.md` and the domain directories, read every relevant page in full, and follow `[[wikilinks]]` one hop where they bear on the topic. A tombstone points at its successor, so read that instead. Never open `data/wiki/private/`: this piece may be published, and a private page cannot be cited in it. If almost nothing turns up, say so and stop.

2. **Find the angle.** State in one line what these pages argue together that none of them says alone. That is what the piece has to offer beyond the pages.

3. **Find the disagreements.** Check the open entries in `data/wiki/_conflicts.md`, pages tagged `conflict`, `— contradicts` links, and `## What argues against it` sections. Note where two pages simply lean different ways. These are where Ramsey has something to say that is not the consensus view, so list them even when they complicate the angle.

4. **Build the outline.** Order the points as an argument. Each point cites the pages that carry it. A point no page carries is not a point: put it under `Missing`.

5. **Mark the weak points.** For each point check the page's `sources:` frontmatter. Report a claim that rests on one raw source, any figure marked "(self-reported)", and anything marked provisional. Report the number or claim with the party that made it.

6. **Draft only if asked.** Use only the claims in the outline, keep the citations inline, and open with the `First pass` line from the template. Without an explicit ask, stop at the outline.

7. **Record the gap.** If `Missing` is not `nothing`, run this with the topic reworded, never the raw request:
   ```bash
   uv run librarian wiki ask "<reworded topic>"
   ```
   If the command fails, say so after the outline. Offer to ingest the finished piece as a source once it is published.

## Output format

```
Angle: <what this piece argues that no single page does>

Outline:
1. <point> (→ [[Page]], [[Page]])
2. <point> (→ [[Page]])

Disagreements:
- <one view> vs <the other> (→ [[Page]], [[Page]])

Weak points:
- One source: <claim> (→ [[Page]])
- Self-reported: <figure>, from <who claims it> (→ [[Page]])

Missing: <what would strengthen it, or "nothing">
Read: [[Page A]], [[Page B]]
```

`Disagreements:` and `Weak points:` are followed by `none found` when empty. `Read` lists the pages opened, in order. A requested draft follows the template, opening with this line:

```
First pass: the phrasing is a placeholder, to rewrite in your own voice.
```

## Calibration

Inventing evidence is the failure that costs most: a specific number or quote with no page behind it, in a piece that looks cited. If a figure would make the point stronger and no page holds it, it goes under `Missing`, even when you are confident of it.

One page is the next failure. If every point cites the same page, the outline is a summary of that page: say `Angle: a summary of [[Page]], not a new argument` rather than dressing it up.

Smoothing is the third. Writing `none found` under `Disagreements` without checking `_conflicts.md` loses the most useful part of the outline. Weak points are not reasons to drop a claim: mark them and let Ramsey decide.

Keep it to about a page. This is scaffolding to argue with, not finished prose, and a long outline hides which points carry the piece.
