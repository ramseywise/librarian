---
title: Few-Shot Prompting
tags: [prompting, llm, concept, conflict]
summary: Providing worked examples before the task — the most reliable lever for steering output format, tone and structure without fine-tuning, but examples teach more than intended (distribution, order, range), so use them only for what is genuinely non-obvious.
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt--prompt-engineering.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--03-core-techniques.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--09-evaluating-prompts.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--10-adversarial-prompting.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--08-prompt-optimization.md
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

## What Examples Actually Teach

In-context learning emerges with scale — small models barely benefit. Examples teach far
more than the rule you had in mind: a handful of `(title): (rating)` pairs implicitly
teach that ratings are integers 1–5, the exact line format, and the *distribution* of
ratings. That makes few-shot good for "I know it when I see it" categories and a cheap way
to pin down format.

What matters in the examples (Min et al., 2022):

- **Label space and input distribution** matter more than per-example label correctness —
  random labels still beat no examples.
- **Format** matters a lot; a consistent format with random labels still helps.
- Sampling labels from the true distribution beats a uniform spread.

## Three Drawbacks (Berryman & Ziegler)

Use few-shot only when something is genuinely non-obvious:

| Drawback | What happens | Mitigation |
|---|---|---|
| Scales badly with context | Each example must carry the real question's context; the prompt balloons and similar blocks confuse attention | Scope examples to teaching format only |
| Anchoring | The examples' range becomes the model's expectation | Match the true outcome distribution; include edge cases without overweighting them |
| Spurious patterns | Example *order* is learned instead of content | Shuffle; evaluate subsets and orders; let [[DSPy]] select and order against a metric |

Three examples land in accidentally ascending order one time in six. "Happy path first,
edge cases last" is the classic trap: the model learns the sequence, so a real question
that breaks it is predicted from position, not content. Shortening examples to dodge the
context cost can also nudge the model away from deeper reasoning.

**Bias from the prompt itself:** skewed label distributions (8 negative, 2 positive) tip
ambiguous inputs toward the majority label; strong models resist on clear inputs. Grouping
labels by position teaches a positional pattern. Synthetic examples inherit whatever skew
their seeds had ([[Diversity Seeding for Synthetic Data]]).

**Placement in agent prompts:** 2–3 boundary-covering examples in the system prompt or as
synthetic first-turn messages, kept **byte-stable** — per-request "most relevant" examples
break the prefix cache ([[SOP-Style Agent System Prompts]]).

Structure-oriented meta-prompting — an abstract solution template instead of worked
examples — avoids anchoring at lower token cost ([[Prompt Optimization]]).

## Combining with Reasoning

Few-shot composes with [[Chain of Thought]]: examples that show the *reasoning chain*, not
just the input/output pair, teach both the format and the method. This is few-shot CoT, and
it outperforms either technique alone on multi-step tasks.

> ⚠️ **Conflict.** In Clavié et al. (2023), zero-shot CoT (F1 81.4) beat few-shot CoT
> (F1 78.4) on a classification task needing no expert knowledge — the examples anchored
> the model ([[Evaluating Prompts]]). The claim above may hold only for genuinely
> multi-step reasoning tasks. Unresolved; see `_conflicts.md`.

## See Also
- [[Prompt Engineering]] — part-of
- [[XML Prompt Structuring]] — depends-on
- [[Chain of Thought]] — composes-with
- [[DSPy]] — extends (automated example selection and ordering)
- [[Prompting Technique Selection]] — extends
- [[Evaluating Prompts]] — contradicts (zero-shot CoT beat few-shot CoT)
