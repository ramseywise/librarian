---
title: Long-Context Prompting
tags: [prompting, llm, concept]
summary: Ordering and grounding rules for long prompts — recency bias plus lost-in-the-middle create a Valley of Meh, so frame with an introduction, put longform data next, refocus the question at the end, transition into the answer, and ground in extracted quotes.
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt--prompt-engineering.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--02-prompt-anatomy.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--01-how-models-read-prompts.md
---

# Long-Context Prompting

Past roughly 20k tokens of input, *where* content sits in the prompt starts to matter as
much as what it says.

## Three Rules

1. **Put longform data at the top**, above the query and examples. Anthropic's testing
   shows up to a **30% quality improvement** when the query appears at the end rather than
   before the documents.
2. **Structure multi-document inputs with XML tags** — `<document index="1">`, `<source>`,
   `<document_content>`. See [[XML Prompt Structuring]]. Without delimiters the model
   cannot reliably attribute a claim to a source.
3. **Ground responses in quotes** — ask the model to extract the relevant passages before
   answering. This narrows attention to the pertinent slice and gives you an audit trail
   for the answer.

## The Valley of Meh

Two attention effects pull against each other: **recency bias** (content near the end has
the most influence) and **lost in the middle** (beginning and end are recalled well, the
middle is underweighted). Together they make early-to-mid content the least effectively
used, and the valley widens as the prompt grows. There is no full fix — put the best
material at the start or end, and keep the prompt short.

## The Sandwich Skeleton

```
1. Introduction — what kind of document this is and what the task is
2. Context      — the long parade of reference material
3. Refocus      — restate the question
4. Transition   — the nudge from reading to answering
```

- The **introduction** frames the document so the context is read with the task in mind.
  When the instruction changes *how* content must be read (counting, extracting a field),
  state it up front — the model reads once, left to right and cannot go back
  ([[Prompts as Document Completion]]).
- The **refocus** brings the question back to the high-attention end; introduction plus
  refocus is the **sandwich technique**, consistent with rule 1 above.
- The **transition** ends the prompt where the answer begins — the end of the user turn,
  or a cue like `Answer:`. The **inception** trick writes the first words of the answer
  so the model is committed to the shape ([[Stop Sequences and Completion Anatomy]]).

Which content makes it into the parade under a token budget is a packing problem
([[Prompt Assembly as Snippet Packing]]).

## Where This Stops Being a Prompt Problem

These rules govern arrangement of content already in the window. Deciding *which*
documents belong there at all — retrieval, ranking, token budgeting — is
[[Context Engineering]], not prompt engineering.

## See Also
- [[Prompt Engineering]] — part-of
- [[XML Prompt Structuring]] — depends-on
- [[Context Engineering]] — extends
- [[Prompt Assembly as Snippet Packing]] — extends
- [[Prompts as Document Completion]] — prerequisite-for
