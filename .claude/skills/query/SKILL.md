---
name: query
description: "Ask a question against the compiled wiki. Gives grounded answers from synthesised knowledge, not raw chunks. Optionally files the answer back as a new wiki page."
allowed-tools: Read Glob Grep Write
---

You are querying a compiled personal knowledge base. Answer only from what is in the wiki — do not use general knowledge unless the wiki has no coverage and you explicitly flag it.

## Input

`$ARGUMENTS` is the question. Answer it from the wiki.

## Protocol

1. Read `wiki/_index.md` to identify relevant pages by title and tags.

2. Read the relevant pages in full using the Read tool.

3. Synthesise a grounded answer:
   - Lead with the direct answer.
   - Cite specific wiki pages: `(→ [[Page Title]])`.
   - Note confidence: if the wiki coverage is thin, say so.

4. If the answer reveals new, synthesisable insight not currently in the wiki, offer:
   > "This answer surfaces something worth adding to the wiki. Want me to file it as a new page?"

5. If the question exposes a coverage gap (no relevant wiki pages), flag it:
   > "The wiki doesn't cover this yet. Sources to ingest: [suggest raw sources or note the gap]."

## Output format

Direct answer first, then citations. Keep it tight — this is a knowledge tool, not a chatbot.
