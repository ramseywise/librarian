---
title: Long-Context Prompting
tags: [llm, concept]
summary: Ordering and grounding rules for 20k+ token prompts — longform data at the top, query at the end, responses grounded in extracted quotes.
updated: 2026-08-04
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt--prompt-engineering.md
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

## Where This Stops Being a Prompt Problem

These rules govern arrangement of content already in the window. Deciding *which*
documents belong there at all — retrieval, ranking, token budgeting — is
[[Context Engineering]], not prompt engineering.

## See Also
- [[Prompt Engineering]] — part-of
- [[XML Prompt Structuring]] — depends-on
- [[Context Engineering]] — extends
