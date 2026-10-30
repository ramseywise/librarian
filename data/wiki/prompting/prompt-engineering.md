---
title: Prompt Engineering
tags: [prompting, llm, concept]
summary: The innermost layer of the agent stack — the instructions and examples themselves, grounded in the document-completion mental model; ends where decisions about what to include in the window begin.
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt--prompt-engineering.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt--README.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--README.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--01-how-models-read-prompts.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--02-prompt-anatomy.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--03-core-techniques.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--04-controlling-output.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--06-chaining-and-workflows.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--11-applications.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--prompt-library.md
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

## The Mental Model

An LLM is a document completer: it predicts the next token of a document left to right,
read once, and is biased toward plausible rather than true continuations. Chat is a
transcript the model completes. Almost every prompting rule follows from this — see
[[Prompts as Document Completion]] and the [[Four Prompt Criteria]] (resemble training
data; include all and only relevant information; make the task obvious; end at a natural
stopping point).

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
- **[[Prompting Technique Selection]]** — which technique when: [[Self-Consistency]],
  [[Tree of Thoughts]], [[Program-Aided Language Models (PAL)]], [[Reflexion]], ReAct.
- **[[Prompt Assembly as Snippet Packing]]** — building prompts programmatically under a
  token budget; [[SOP-Style Agent System Prompts]] for agent system prompts.

## Controlling Output

[[Sampling Parameters]], [[Stop Sequences and Completion Anatomy]] and
[[Logprobs as Confidence Signal]] shape and score what comes back; tools are prompts too
([[Tool Definitions as Prompts]]). When the static prompt is long and still not followed,
[[Fine-Tuning as Prompt Compression]] moves it into weights. Reasoning models change the
advice from *how to think* to *what to achieve* ([[Prompting Reasoning Models]]).

## Measuring and Improving

Build the eval first ([[Evaluating Prompts]], judges via a [[SOMA Judge Rubric]]), then
search against it ([[Prompt Optimization]], [[DSPy]]).

## Applications

[[Diversity Seeding for Synthetic Data]], [[Code Generation Prompting]], and interface design
around [[Stateful Objects of Discourse]]. Images are just more context tokens: include only
relevant ones, introduce each in text, use familiar visual conventions, and keep content
first and question last in long documents.

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
- [[Prompts as Document Completion]] — prerequisite-for
- [[Four Prompt Criteria]] — instance-of
- [[Prompting Technique Selection]] — instance-of
- [[Evaluating Prompts]] — prerequisite-for
- [[Prompt Optimization]] — extends
- [[Prompt Leaking]] — instance-of
