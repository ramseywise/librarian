---
title: Prompt Engineering
tags: [llm, concept]
summary: The innermost layer of the agent stack — governs the instructions and examples themselves, ending where decisions about what to include in the window begin.
updated: 2026-08-04
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt--prompt-engineering.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt--README.md
---

# Prompt Engineering

## Position in the Stack

Prompt engineering is the **innermost layer**: context contains prompts. Every assembled
context window ultimately delivers one or more prompts to the model, and the quality of
those prompts determines what the model does with the surrounding context.

The nesting rule from the six-pillar model: *prompt engineering ⊂ context engineering ⊂
harness engineering.* See [[Context Engineering]] for the next layer out.

## The Prompt / Context Boundary

The boundary is crisp and worth memorising, because it decides which discipline owns a
given problem:

| Prompt engineering | Context engineering |
|---|---|
| The instructions and examples themselves | What to *include* alongside the instructions |
| How you phrase the task, format requests, structure XML | Which documents, memory chunks, tool outputs, history to inject |
| Role setting, CoT, few-shot, output format | Window composition, token budget, retrieval strategy |

Once you are deciding *what* is in the window rather than *how* to phrase what is already
there, you have crossed into [[Context Engineering]].

## Core Principle

**Be clear and direct.** Treat the model as a capable but context-free new employee: the
more precisely you state the task, constraints, and desired output, the better the result.

**The golden rule:** show your prompt to a colleague with minimal context. If they would
be confused, the model will be too.

A corollary that generalises better than most rules here — **tell the model what to do
rather than what not to do**. "Respond in flowing prose paragraphs" outperforms "Do not
use markdown", because the negative form leaves the target underspecified.

## Techniques

- **System prompts and role setting** — the highest-authority instruction layer, set
  before any user message. One focused sentence often beats extensive inline instruction.
  Authority hierarchy: developer role > user role > instructions parameter.
- **[[Few-Shot Prompting]]** — 3–5 worked examples; the most reliable way to steer format.
- **[[Chain of Thought]]** — reason step-by-step before answering. Note that reasoning
  models do this internally, making explicit CoT prompts redundant though still valid.
- **[[XML Prompt Structuring]]** — wrap distinct prompt sections in tags to prevent
  misinterpretation.
- **[[Structured Output]]** — request JSON or a schema, paired with harness-side validation.
- **[[Prompt Templates and Variables]]** — separate the fixed skeleton from variable content.
- **[[Long-Context Prompting]]** — ordering and grounding rules past ~20k tokens.
- **[[Prompt Chaining]]** — decompose multi-step tasks into a sequence of simpler prompts.

## Add Context and Motivation

Explaining *why* a constraint exists helps the model generalise it correctly rather than
applying it narrowly:

```
Never use ellipses — this response will be read aloud by a text-to-speech engine that
cannot pronounce them.
```

This outperforms a bare `NEVER use ellipses`, which the model may interpret as applying
only to the literal case it can imagine.

## Security Facet

Prompt injection — manipulating behaviour via adversarial input embedded in user data —
is the primary security concern for any system with external inputs. See
[[Prompt Injection]].

## See Also
- [[Scope-POC Design Interview]] <!-- auto-linked -->
- [[Context Engineering]] — extends
- [[Few-Shot Prompting]] — instance-of
- [[Prompt Injection]] — alternative-to
- [[Chain of Thought]] — instance-of
