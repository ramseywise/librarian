---
title: XML Prompt Structuring
tags: [llm, concept]
summary: Wrapping distinct prompt sections in descriptive XML tags so the model cannot confuse instructions with data, examples, or constraints.
updated: 2026-08-04
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt--prompt-engineering.md
---

# XML Prompt Structuring

## The Problem It Solves

A complex prompt concatenates several kinds of content — instructions, the document to
operate on, examples, constraints. Without delimiters the model must infer which is which
from prose alone, and misattribution is a common failure: instructions get read as data,
or injected document text gets read as instruction (the mechanism behind
[[Prompt Injection]]).

## The Technique

Wrap each distinct section in a descriptive tag:

```xml
<instructions>Summarize the document below.</instructions>
<context>{{DOCUMENT}}</context>
<constraints>Max 3 sentences. Plain text only.</constraints>
```

## Best Practices

- **Consistent, descriptive tag names** — reuse the same tag for the same role across
  prompts. Arbitrary names work, but consistency lets you reason about a prompt library.
- **Nest for hierarchical content** — `<documents>` > `<document index="n">` >
  `<document_content>` is the canonical shape for multi-document inputs.
- **Use tags as format indicators too** — `"Write your analysis in <analysis> tags"`
  makes the response parseable without asking for full JSON.

## Relation to Structured Output

XML structuring governs the *input* side; [[Structured Output]] governs the *output* side.
They are frequently used together: XML-tagged input sections, JSON-schema'd response.

## See Also
- [[Prompt Engineering]] — part-of
- [[Structured Output]] — alternative-to
- [[Few-Shot Prompting]] — used-by
- [[Long-Context Prompting]] — used-by
