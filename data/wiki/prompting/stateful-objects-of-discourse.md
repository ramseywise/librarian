---
title: Stateful Objects of Discourse
tags: [prompting, pattern]
summary: Collaboration talks about persistent objects, but plain chat duplicates them into the transcript and makes "it" ambiguous — separate the object (own pane, short name, updated in place) from the conversation, prefer diffs and edit tools over regeneration, support several objects, and feed user edits back as diffs.
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--11-applications.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--05-tools-and-function-calling.md
---

# Stateful Objects of Discourse

People collaborating talk *about* a persistent thing — a file — change it, and discuss the
change. Plain chat doesn't: ask for a function and then a change, and the transcript holds
two full copies, with "it" ambiguous between them. Artifact-style UIs (an object pane
updated in place, beside the conversation) separate the object from the talk about it.

Berryman & Ziegler's critique doubles as a design checklist:

- **Regeneration isn't editing.** Rewriting the whole object on each change doesn't scale
  to long documents — prefer diffs and edit tools ([[Tool Definitions as Prompts]]).
- **Support several objects**, each with a short name both the user and the prompt can
  use; otherwise a new topic overwrites the only slot.
- **Let the user edit directly** and feed that diff into the next prompt so the model
  knows what changed.

In the context of a tool-using agent the same idea appears as **artifacts**: attached data
(a flight list, a document) presented in an `<artifact>` tag or an attached-data section,
summarized rather than inlined when large, with the UI showing which artifacts the agent
is attending to ([[XML Prompt Structuring]]).

Conversational UI also keeps a human in the loop who can catch drift before it compounds
([[Prompt Chaining]]). Without a designed object layer, a chat wrapper is a gimmick.

## See Also
- [[Tool Definitions as Prompts]] — extends
- [[Prompt Chaining]] — extends
- [[Context Anatomy]] — extends
