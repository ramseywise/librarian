---
name: query
description: "Ask a question against the compiled wiki. Gives grounded answers from synthesised knowledge, not raw chunks. Optionally files the answer back as a new wiki page. Use when the question should be answered from the wiki: what it knows about a topic, what a pattern or convention is, or a lookup whose answer may be worth filing as a page. Do NOT use for compiling new sources (/ingest), health checks (/lint), merging or retiring pages (/compact-wiki), or questions the wiki has nothing to do with."
allowed-tools:
  - Read
  - Glob
  - Grep
  - Write
  - Bash(uv run librarian wiki ask *)
---

You are querying a compiled personal knowledge base. Answer only from what is in the wiki — do not use general knowledge unless the wiki has no coverage and you explicitly flag it.

## Core rule

Every claim in the answer comes from a wiki page and cites it, and anything that does not sits on a line starting "Outside the wiki:".

## Workflow

`$ARGUMENTS` is the question. Answer it from the wiki.

1. Read `data/wiki/_index.md` to identify relevant pages by title and tags.

2. Read the relevant pages in full using the Read tool.

3. Synthesise a grounded answer:
   - Lead with the direct answer.
   - Cite specific wiki pages: `(→ [[Page Title]])`.
   - Note confidence: if the wiki coverage is thin, say so.
   - Never fill a gap from general knowledge without saying so on a line that starts "Outside the wiki:".

4. If the answer reveals new, synthesisable insight not currently in the wiki, offer:
   > "This answer surfaces something worth adding to the wiki. Want me to file it as a new page?"

5. If the question exposes a coverage gap (no relevant wiki pages), flag it:
   > "The wiki doesn't cover this yet. Sources to ingest: [suggest raw sources or note the gap]."

6. End with the trailer (see Output format). If `Not covered` is not `nothing`, record it:
   ```bash
   uv run librarian wiki ask "<reworded topic>"
   ```
   Queries are personal history: pass the topic, reworded, never the raw question. If the command fails, say so after the trailer.

## Output format

Direct answer first, then citations. Keep it tight — this is a knowledge tool, not a chatbot.

```
<direct answer, citing pages inline: (→ [[Page Title]])>

Outside the wiki: <only if used, one line per claim>

Read: [[Page A]], [[Page B]]            (pages opened, in order)
Not covered: <what the wiki could not answer, or "nothing">
```

The trailer goes on every answer, including an answer that finds nothing, and it comes after any offer from steps 4 and 5. The parenthesis explains the `Read` field and is not printed. `_index.md` is not a page: if no page was opened, write `Read: none`.

## Calibration

Reading too little is the common failure: answering from the first page that matches when the index lists others on the topic, then writing `Not covered: nothing` about pages never opened. Reading too much is the opposite failure: opening a whole domain to answer a narrow question spends the context on pages that add nothing, so stop when another page stops changing the answer.

If the wiki has nothing on the topic, say so and stop. Padding an empty result with general knowledge is worse than the gap, because the answer can no longer be checked against a page. A partial answer names the part it could not answer: two parts out of three covered is a non-empty `Not covered` line, not `nothing`.
