---
title: AI Engineering Curriculum Structure
tags: [meta, foundations, concept]
summary: "The two-wave model of the learn-ai-engineering corpus — generative-ai as the application wave (seven pillars) and ai-engineering as the discipline wave (six foundations) — plus the dependency ordering that makes the pillar sequence more than a filing scheme."
updated: 2026-08-04
sources:
  - data/raw/repos/learn-ai-engineering/generative-ai--README.md
  - data/raw/repos/learn-ai-engineering/generative-ai--01-llm-fundamentals--README.md
  - data/raw/repos/learn-ai-engineering/generative-ai--02-rag-retrieval--README.md
  - data/raw/repos/learn-ai-engineering/generative-ai--03-agentic-foundations--README.md
  - data/raw/repos/learn-ai-engineering/generative-ai--04-agentic-frameworks--README.md
  - data/raw/repos/learn-ai-engineering/generative-ai--06-observability--README.md
  - data/raw/repos/learn-ai-engineering/generative-ai--07-agentic-applications--README.md
---

# AI Engineering Curriculum Structure

How the `learn-ai-engineering` corpus organises the field. Two top-level domains that are
**complementary, not redundant** — and the distinction between them is the useful part,
because it is a claim about how the discipline actually developed rather than a filing
convention.

## The two waves

| Domain | Wave | What it carries |
|---|---|---|
| `generative-ai/` | **Application wave** — building things with LLMs | Course material, foundational papers, practical patterns |
| `ai-engineering/` | **Discipline wave** — making those things reliable | Prompt → context → harness → loop → graph → eval |

The ordering claim: the discipline wave **emerged after the application wave and presumes
it**. You cannot write a harness spec for a loop you have never built, and context
engineering is only a discipline once you have hit a context window in anger. This is why
the corpus tells you to learn the gen-AI pillars first and layer engineering practice on
top — not because the discipline material is harder, but because its concepts are
*abstractions over experience* the application wave supplies.

The practical consequence for retrieval: a question of the form "how do I do X" usually
routes to the application wave; "why does X keep breaking" routes to the discipline wave.
The same technology appears in both, described at different altitudes.

## The seven pillars (application wave)

```
LLM fundamentals → RAG & retrieval → Agentic foundations → Agentic frameworks
                                                         → RL & alignment
                                                         → Observability
                                                         → Agentic applications
```

The sequence is not alphabetical or arbitrary — **the order encodes dependency and
temporal emergence** simultaneously, which is why the first three are a chain and the last
four fan out from the third.

| # | Pillar | What it covers | Depends on |
|---|---|---|---|
| 01 | **LLM fundamentals** | Architecture, training, prompting — the conceptual bedrock | — |
| 02 | **RAG & retrieval** | The first killer app: augment a model with external knowledge at inference time | 01 |
| 03 | **Agentic foundations** | Learning frameworks through courses — models that plan, use tools, run in loops | 02 |
| 04 | **Agentic frameworks** | Reference material: comparisons, feature parity, selection guides | 03 |
| 05 | **RL & alignment** | RL foundations, RLHF pipeline, preference optimisation (PPO/DPO/GRPO), reward modelling, constitutional AI/RLAIF, RL for agentic systems | 03 |
| 06 | **Observability** | Tracing, scoring, evaluation pipelines — LangFuse-centric | 03 |
| 07 | **Agentic applications** | End-to-end built projects, deliberately small — only genuinely built things, not course material | 03 |

The 03/04 split is the one worth internalising and the easiest to collapse by accident:
**03 is learning a framework, 04 is choosing one.** They hold different artefact types
(courses vs. comparison documents) and answer different questions, and merging them
produces a directory where selection guidance is buried inside tutorial material. The same
distinction appears in the wiki as the difference between a framework's mechanics page and
a comparison page — see [[ADK vs LangGraph Comparison]] against [[LangSmith Platform]].

Pillar 07's stated constraint — *only genuinely built things* — is a quality gate
masquerading as a scoping rule. A projects directory that admits course exercises stops
being evidence of anything.

## Cross-wave mapping

Each gen-AI pillar has a discipline-wave counterpart that generalises it:

| gen-AI pillar | ai-engineering depth |
|---|---|
| 01 LLM fundamentals | `01-prompt/` — prompt engineering |
| 02 RAG & retrieval | `02-context/` + `05-graph/` |
| 03–04 Agentic foundations + frameworks | `03-harness/` + `04-loop/` |
| 06 Observability | `06-eval/` — evaluation and measurement |

The 02 → context + graph mapping is the most informative row, and it is a two-step
generalisation. RAG is described in the corpus as **fundamentally a context assembly
pattern** — the retrieved documents *become* the context window, so the discipline-wave
treatment of RAG is not "better retrieval" but context engineering, of which retrieval is
one supplier. See [[Context Engineering]] and [[Context Retrieval Strategies]]. The graph
half covers the same content once relationships between documents matter rather than
similarity alone.

Note also the 06 pairing: **observability is the infrastructure, eval is the discipline.**
Tracing tells you what happened; eval tells you whether it was good. Conflating them
produces a dashboard nobody can act on — the same split the wiki keeps between
[[Observability and Runtime Patterns]] and [[RAG Eval Gate Contract]].

Pillar 05 has no discipline-wave counterpart, which is correct: alignment is done to the
model before you receive it, so it is background rather than practice for anyone consuming
models through an API.

## The summary/depth layering

A third axis crosses both waves. `interviewing/guides/` is a **pointer-only summary
layer** for exam prep; the pillar directories are the depth layer. Each pillar README
carries an explicit crosswalk link to its guide, and guides link back into both waves for
depth.

The corpus made a deliberate structural choice here: operational notes live **directly
inside each pillar directory** rather than in a separate `notes/` pointer layer, which was
absorbed during the curriculum buildout. Notes sit next to the material they annotate;
only the exam-prep summaries are kept separate. The reason a pointer layer survives at all
for guides and not for notes is that the two compress differently — a summary written for
recall under time pressure is a genuinely different artefact from the material it
summarises, whereas a note about a course is just more course material.

This is the same three-way split the wiki enforces between `patterns/` (discovered while
building), subject directories (synthesised from external sources), and `interview/`
(true only while interviewing) — three buckets that **decay at different rates**, which is
the actual justification for keeping them apart.

## See Also
- [[Skill-Knowledge Information Flow]] — part-of (the corpus as one of four parallel systems, and its ingest contract into this wiki)
- [[Karpathy LLM Wiki Pattern]] — complements (how this corpus is compiled into wiki pages)
- [[Context Engineering]] — extends (the discipline-wave generalisation of pillar 02)
- [[ADK vs LangGraph Comparison]] — instance-of (pillar 04 selection material)
- [[Observability and Runtime Patterns]] — instance-of (pillar 06 infrastructure)
- [[RAG Eval Gate Contract]] — complements (the discipline-wave counterpart to pillar 06)
- [[Data Engineering Foundations]] — part-of (the data pillar, upstream of both waves)
- [[Data Science Curriculum Layers]] — part-of (the analytics and ML pillars that precede the application wave)
