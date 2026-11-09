---
title: Long-Context Prompting
tags: [prompting, llm, concept]
summary: Ordering and grounding rules for long prompts — recency bias plus lost-in-the-middle create a Valley of Meh, so frame with an introduction, put longform data next, refocus the question at the end, transition into the answer, and ground in extracted quotes.
updated: 2026-11-08
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt--prompt-engineering.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--02-prompt-anatomy.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--01-how-models-read-prompts.md
  - data/raw/papers/2026-11-07-shi-2023-large-language-models-can-be.md
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

## Distraction by Irrelevant Context (GSM-IC)

GSM-IC, a 2023 dataset, inserts a single templated irrelevant sentence into each of 100 easy GSM8K problems (58,052 examples; 4,000 sampled), and tests four prompting techniques on code-davinci-002 and text-davinci-003 (self-reported, greedy unless stated):
- Chain-of-thought overall micro accuracy was 72.4 but macro accuracy, where a base problem counts only if solved under every distractor, was 6.0. Least-to-most was the most robust base technique (77.5 and 18.0); zero-shot chain-of-thought was the most distracted (29.0 against a base of 44.0).
- Twenty-sample self-consistency raised micro accuracy by over 11 points (chain-of-thought plus self-consistency reached 88.1 micro, 30.0 macro).
- The instruction "Feel free to ignore irrelevant information" lifted chain-of-thought micro 72.4 to 77.8 and macro 6.0 to 15.0; an exemplar containing an irrelevant sentence lifted micro to 76.8. Neither hurt clean GSM8K.
- In-topic distractors were harder than off-topic (63.1 against 80.7) and role-name overlap hurt (68.3 against 76.6).

Limits: two GPT-3-family models, now retired; an easy base subset chosen because some prompt solves it; one-sentence template distractors; no seeds or significance tests.

## See Also
- [[Prompt Engineering]] — related (part of)
- [[XML Prompt Structuring]] — prerequisite-for
- [[Context Engineering]] — extends
- [[Prompt Assembly as Snippet Packing]] — extends
- [[Prompts as Document Completion]] — prerequisite-for
- [[Output Length Confounds Reference Metrics]] — related (L-Eval: scoring long-context answers fairly)
- [[Cache-Augmented Generation]] — instance-of (preloading a small corpus into the window's cache instead of retrieving)
- [[RAG vs Long Context: Evaluation Evidence]] — related (head-to-head evaluations)
- [[LongRAG Long Retrieval Units]] — related (a long-context reader over long retrieval units)
- [[LongICLBench and Many-Shot ICL Scaling]] — instance-of
- [[LC-Boost Short-Context Processing of Long Inputs]] — related
- [[BABILong Benchmark]] — related
- [[System 2 Attention]] — instance-of (regenerating context before answering)
- [[Lost in the Middle]] — related (position effects)
