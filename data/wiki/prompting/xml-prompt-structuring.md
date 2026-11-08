---
title: XML Prompt Structuring
tags: [prompting, llm, concept]
summary: Wrapping distinct prompt sections in descriptive XML tags so the model cannot confuse instructions with data, examples, or constraints.
updated: 2026-11-08
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt--prompt-engineering.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--02-prompt-anatomy.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--11-applications.md
  - data/raw/papers/2026-11-06-he-2024-does-prompt-formatting-have-any.md
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

## XML vs YAML vs JSON

| Format | Strength | Weakness |
|---|---|---|
| XML | Tolerates free text inside tags; the closing tag is a natural stop | More tokens |
| YAML | Light on tokens | Whitespace-sensitive |
| JSON | Easiest to parse | Expensive to escape long text; one missing brace breaks it |

Plain delimiters (`###`, `"""`) suffice for simple prompts. Structured output also lets
the app **route parts of a completion** — hide a `<thinking>` block, render an
`<artifact>` block in a side panel. A widely used artifact feature works exactly this way:
a structured system prompt explains in prose when to create an artifact, wraps each worked
example in XML, and the app parses the emitted artifact tags out of the completion
([[Stateful Objects of Discourse]]).

## Relation to Structured Output

XML structuring governs the *input* side; [[Structured Output]] governs the *output* side.
They are frequently used together: XML-tagged input sections, JSON-schema'd response.

## Measured format effects (He et al.)

He et al. (Microsoft and MIT, arXiv 2411.10541, preprint, 2024) compare plain text, Markdown, YAML and JSON versions of the same five-part prompt (persona, task instructions, examples, output format, user ask) on six benchmarks. Models are 2023 OpenAI snapshots through Azure; content is identical across formats, and the authors do not separate the section-splitting effect from the syntax effect. HTML and XML were not tried, so the study says nothing directly about XML tags.

- gpt-35-turbo-0613 on MMLU (14,079 questions): 59.7 with JSON against 50.0 with Markdown (self-reported). On HumanEval (164 problems, pass@1): 59.8 with JSON against 40.2 with plain text (self-reported). Both gaps p<0.001 on a one-sided matched-pair t-test (self-reported).
- GPT-4 moved much less: the paper's dispersion measure across the four formats stayed below 0.036 for gpt-4-1106-preview on every benchmark, against 0.035 to 0.176 for the GPT-3.5 series (read from a figure; self-reported).
- Best format differs by model and task: the GPT-3.5 series favoured JSON on several tasks while GPT-4 favoured Markdown. Overlap between top-format sets was often below 0.2 across model series and above 0.7 within one sub-series.
- Worst case: gpt-4-32k-0613 on HumanEval scored 21.95 with JSON against 76.22 with plain text (self-reported); the authors read outputs and report the model wrote its reasoning but not the code, and call the cause a hypothesis.
- On MMLU at temperature 0, GPT-3.5 gave identical answers under Markdown and JSON for only 16% of items (self-reported).

## Limits

The extraction notes Table 1 disagrees with Tables 7 and 8 in several cells (GPT-4-1106 code-translation entries), and the abstract's "up to 40%" and the text's 200% and "over 300%" swings do not match the tables exactly (76.22 over 21.95 is about 3.5x). No seeds or prompt-wording variants are reported, the models are superseded snapshots, and the authors give no mechanism. See [[Benchmark Prompt Format Sensitivity]] for the same effect as an evaluation hazard.

## See Also
- [[Prompt Engineering]] — related (part of)
- [[Structured Output]] — alternative-to
- [[Few-Shot Prompting]] — related (used by)
- [[Long-Context Prompting]] — related (used by)
- [[Stateful Objects of Discourse]] — extends
- [[Benchmark Prompt Format Sensitivity]] — related (format changes move benchmark scores)
- [[Principled Instructions (26 Prompt Principles)]] — related
