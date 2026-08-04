---
title: Few-Shot Prompting
tags: [llm, concept]
summary: Providing 3–5 worked examples before the task — the most reliable lever for steering output format, tone, and structure without fine-tuning.
updated: 2026-08-04
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt--prompt-engineering.md
---

# Few-Shot Prompting

## Zero-Shot vs Few-Shot

- **Zero-shot** — instruct with no examples, relying on the model's general knowledge.
  Sufficient for well-known tasks with unambiguous output shape.
- **Few-shot (multishot)** — provide 3–5 worked examples before the actual task.

Examples are one of the most reliable ways to steer output format, tone, and structure.
Where a paragraph of instructions describing the desired format often underspecifies,
three examples of it pin it down exactly.

## Three Properties of Good Examples

| Property | Requirement | Failure if violated |
|---|---|---|
| **Relevant** | Mirror the actual use case | Model generalises from the wrong domain |
| **Diverse** | Cover edge cases; vary enough | Model latches onto an unintended pattern shared by all examples |
| **Structured** | Wrap in `<example>` tags | Model confuses examples with instructions |

The diversity requirement is the one most often missed. If every example happens to have a
short answer, the model will infer "short answers" as a rule you never stated.

## Structuring

Wrap examples in tags so the model distinguishes demonstration from instruction — see
[[XML Prompt Structuring]]:

```xml
<examples>
<example>
  <input>...</input>
  <output>...</output>
</example>
</examples>
```

## Combining with Reasoning

Few-shot composes with [[Chain of Thought]]: examples that show the *reasoning chain*, not
just the input/output pair, teach both the format and the method. This is few-shot CoT, and
it outperforms either technique alone on multi-step tasks.

## See Also
- [[Prompt Engineering]] — part-of
- [[XML Prompt Structuring]] — depends-on
- [[Chain of Thought]] — composes-with
