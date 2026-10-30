---
title: Four Prompt Criteria
tags: [prompting, llm, concept]
summary: Every prompt must at once resemble training data (the Little Red Riding Hood principle), carry all and only the relevant information (Chekhov's gun), lead to a solution, and have a natural stopping point — chat tuning gives you three for free, never the second.
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--02-prompt-anatomy.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--11-applications.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--04-controlling-output.md
---

# Four Prompt Criteria

From Berryman & Ziegler (Ch 4), derived directly from [[Prompts as Document Completion]].

1. **Resemble training data — the Little Red Riding Hood principle.** Stay on the path
   the model was trained on. Familiar document shapes (markdown reports, transcripts,
   homework problems, code) give predictable completions; clean grammar in, clean grammar
   out. The principle extends to images (standard chart types beat invented ones) and to
   fine-tuned models (make the prompt look like the start of your fine-tuning documents —
   [[Fine-Tuning as Prompt Compression]]).
2. **Carry all relevant information — and only that — Chekhov's gun.** Models assume
   anything included must matter: retrieve two reviews when one is relevant and the answer
   will use both. Missing context fails; padding distracts.
3. **Lead to a solution** — point at an answer, not at further elaboration of the problem.
4. **Have a natural stopping point** — end of the assistant turn, a closing tag, or a stop
   sequence ([[Stop Sequences and Completion Anatomy]]).

Chat models get 1, 3 and 4 nearly free through fine-tuning. **Criterion 2 is never
automatic** — gathering and shaping context is where most of the work goes, which is why
[[Context Engineering]] is its own layer.

## Worked example: the homework document

A raw maths question invites any continuation. Rewritten as a document the model has seen
thousands of times — `# Homework assignment: Algebra I` / `## Problem 1` / the question /
`## Solution` — it answers in shape. Without the stop sequence `\n#` it solves Problem 1
and then invents Problem 2, because that is what homework documents do. The transform-back
step extracts the text under `## Solution`.

## Choosing the document type

| Archetype | Good for | Notes |
|---|---|---|
| Advice conversation | Chat, multi-turn, tool use | Default for chat models; synthetic prior turns count as the model's own |
| Analytic report (markdown) | Analysis then decision | Safest default; a `Scope` section bounds better than conversational exclusions; `# Analysis` before `# Conclusion` gives a scratchpad; a trailing `# Appendix` heading is a clean stop |
| Structured document (XML/YAML/JSON) | Parseable output | Lets the app route output parts (hide a thinking block, render an artifact) — see [[XML Prompt Structuring]] |

Injected data should match the archetype: an assistant line in a conversation, a heading
plus prose in a report, a tagged element in a structured document. Material that doesn't
fit the flow goes in an **aside** the genre already allows (blockquote, `Note:`, code
comment).

## See Also
- [[Prompts as Document Completion]] — extends
- [[Prompt Engineering]] — prerequisite-for
- [[Prompt Assembly as Snippet Packing]] — prerequisite-for
- [[Context Engineering]] — prerequisite-for (criterion 2 is its whole job)
- [[Prompting Technique Selection]] — related
