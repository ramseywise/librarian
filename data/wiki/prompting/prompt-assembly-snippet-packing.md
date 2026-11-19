---
title: Prompt Assembly as Snippet Packing
tags: [prompting, context-management, pattern]
summary: The feedforward pass of an LLM app (retrieve → snippetize → score → assemble) ends in a packing problem — pick snippets by priority under a token budget, honouring elastic versions and mutual exclusion, then emit the winners in document order.
updated: 2026-11-19
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--02-prompt-anatomy.md
  - data/raw/papers/2026-11-08-prompt-engineering-for-generative-ai-ch02-intro-to-llms-for-text-generation.md
---

# Prompt Assembly as Snippet Packing

An LLM application translates between the user's domain and the model's (a document to
complete). Each request is a round trip (Berryman & Ziegler, Ch 4–6):

1. **Feedforward**: context retrieval → **snippetizing** (prompt-sized pieces) →
   **scoring and prioritizing** → **prompt assembly** within a budget.
2. Model → completion.
3. **Transform back**: parse the completion into an answer, edit, tool call or UI update.

The loop gets harder along four axes: interaction state, external context, reasoning depth
and tool use.

## Static vs dynamic content

The engineering split is by *origin*, not by what the text says: **static** content (task
definition and rules, identical for every user) vs **dynamic** content (per-request
context). A programmatic call gets no conversational repair, so clarifying the static part
is a bigger reliability lever than expected. Dynamic sources are judged on **latency**
(can the user wait?), **preparability** (can it be built offline — embeddings, summaries?)
and **comparability** (can it be scored against other candidates?). Sort candidate sources
by **proximity** to what the user is doing and **stability**; close-and-volatile sources
are the most relevant and the most expensive to keep fresh.

**Summarization** for oversized context: hierarchical (chunks → sections → summary of
summaries) suffers the **rumor problem** — each level can drop or distort a detail. A
*general* summary can be prepared ahead; a *specific* one ("…with respect to termination
clauses") is more useful but per-request.

## The packing step

Each snippet has a priority and a token cost. Two relations constrain the choice:

- **Elastic** — a snippet has several versions (full → trimmed → minimal); take the
  largest that fits.
- **Mutually exclusive** — two snippets cover the same thing (a document and its summary);
  include at most one.

Greedy: sort by priority, for each snippet skip it if its group is covered, otherwise take
the largest version that fits. **Score by priority, emit in document order.**

## Snippet checklist

- **Modular** — insert or drop like list items.
- **Natural** — reads as part of the document's genre ([[Four Prompt Criteria]]).
- **Brief.**
- **Inert** — its token count doesn't change with its neighbours. Tokenization isn't
  additive (`"Hello"` + `" world"` may not tokenize like `"Hello world"`), so start
  snippets with a single leading space or end them with a newline, consistently — and
  don't start them with a newline.

Where to place the packed material is governed by the Valley of Meh
([[Long-Context Prompting]]). Window-level composition, budgets and cache-stable ordering
are [[Context Anatomy]].

## Budgeting in tokens

The Prompt Engineering for Generative AI chapter on text generation models advises measuring a model's processing limits in token counts rather than word counts. It gives a rule of thumb that 100 tokens is roughly 75 words, with no tokenizer or language named.

## Limits

- The token rule of thumb is a general statement from an introductory chapter whose authors are not named in the extraction; it names no tokenizer or language.

## See Also
- [[Four Prompt Criteria]] — extends
- [[Context Anatomy]] — extends (the context-engineering view of the same assembly)
- [[Long-Context Prompting]] — prerequisite-for
- [[Prompt Engineering]] — instance-of
- [[Prompts as Document Completion]] — prerequisite-for
