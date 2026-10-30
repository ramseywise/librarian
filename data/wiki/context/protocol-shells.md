---
title: Protocol Shells
tags: [context, llm, reference]
summary: "Pseudo-code prompt structure (name, intent, input, process, output) from a no-code context-engineering track — the explicit four parts measurably improve consistency, but the syntax itself has no special power; a markdown prompt with the same sections performs about the same."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--02-context-engineering--notes--09-protocols.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--02-context-engineering--notes--99-speculative-field-track.md
---

# Protocol Shells

A protocol shell is a structured prompt written in pseudo-code. The model does not execute
it; the structure is useful because it is **explicit, reusable and easy to share** with
people who don't write code. It is the no-code counterpart of the prompt programs in
[[Cognitive Tools]].

```
/research.literature{
    intent="Develop a structured understanding of existing work on a topic",
    input={ research_topic="…", key_questions=[…], scope_boundaries={include:…, exclude:…} },
    process=[ /map{…}, /explore{…}, /synthesize{…}, /evaluate{…} ],
    output={ map="…", findings="…", gaps="…", confidence="High/medium/low per finding" }
}
```

| Part | Job | Common mistake |
|---|---|---|
| Name (`/category.variant`) | Findable, reusable | Generic names like `/do.task` |
| Intent | One sentence on what success looks like | A list of activities instead of a goal |
| Input | Everything the task depends on, named | Constraints hidden inside process steps |
| Process | Ordered steps, one action each | Steps that each do three things |
| Output | Shape of the deliverable | "A good summary", unstructured |

This is the input schema of [[Structured Context and Schemas]] with the process made
explicit.

## The Operation Vocabulary

Process steps use `/operation.modifier{parameters}` (the course calls it "Pareto-lang").
Operations group by context lever: information management (`/extract`, `/filter`,
`/prioritize`) ≈ Select; transformation (`/compress`, `/restructure`) ≈ Compress;
analysis (`/compare`, `/synthesize`). The model has no parser — it reads
`/filter.relevance{threshold=0.7}` as a compact, unambiguous instruction. Brevity is the
point.

The course ships ~50 ready-made shells in families (conversation, document, research,
knowledge, creative, meta-recursive self-critique, interpretability, human-in-the-loop
collaboration, cross-modal).

## Design Tests

- **One action per step** — if a step needs "and", split it.
- **Inputs, not assumptions** — anything the task depends on is a named field.
- **Declared output** — name every field.
- **Modular** — a reusable step becomes its own protocol.
- **Proportionate** — a three-line request doesn't need a shell; structure must pay for
  its tokens ([[Context Window Budgeting]]).

## Honest Assessment

**Real:** explicit intent, inputs, steps and output improve consistency. That is ordinary
[[Prompt Engineering]]; the shell is a discipline for making sure you do it. Good for
repeatable workflows, prompt libraries, and handing a procedure to a non-engineer.

**Oversold:** the syntax has no special power — a well-structured markdown prompt with the
same four sections performs about the same. The "field operations" (`/attractor.*`,
`/resonance.*`) belong to [[Context Field Theory (Speculative)]].

**Use it when** the people using the procedure don't write code. If they do, the same
structure belongs in a prompt template with variables ([[Prompt Templates and Variables]]).

## See Also
- [[Cognitive Tools]] — alternative-to (prompt programs, in code)
- [[Structured Context and Schemas]] — extends
- [[Prompt Templates and Variables]] — alternative-to
- [[Context Field Theory (Speculative)]] — prerequisite-for
