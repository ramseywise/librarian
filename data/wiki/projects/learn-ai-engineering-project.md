---
title: learn-ai-engineering Project
tags: [foundations, project]
summary: "The self-paced AI and data engineering curriculum repo — six subjects (programming, data analytics, data engineering, data science, generative AI, AI engineering), three learning paths, a depth/summary/reference layering with exam-prep guides kept in a separate repo, a five-criterion definition of done, and a structural freeze as of 2026-10-28."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/README.md
  - data/raw/repos/learn-ai-engineering/CURRICULUM.md
  - data/raw/repos/learn-ai-engineering/generative-ai--README.md
  - data/raw/repos/learn-ai-engineering/generative-ai--resources.md
  - data/raw/repos/learn-ai-engineering/generative-ai--01-llm-fundamentals--README.md
  - data/raw/repos/learn-ai-engineering/generative-ai--02-rag-retrieval--README.md
  - data/raw/repos/learn-ai-engineering/generative-ai--03-agentic-foundations--README.md
  - data/raw/repos/learn-ai-engineering/generative-ai--04-agentic-frameworks--README.md
  - data/raw/repos/learn-ai-engineering/generative-ai--05-RL--README.md
  - data/raw/repos/learn-ai-engineering/generative-ai--06-observability--README.md
  - data/raw/repos/learn-ai-engineering/generative-ai--07-agentic-applications--README.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--README.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--SOURCES.md
  - data/raw/repos/learn-ai-engineering/data-analytics--README.md
  - data/raw/repos/learn-ai-engineering/data-analytics--CURRICULUM.md
  - data/raw/repos/learn-ai-engineering/data-engineering--CURRICULUM.md
  - data/raw/repos/learn-ai-engineering/data-science--README.md
  - data/raw/repos/learn-ai-engineering/data-science--CURRICULUM.md
---

# learn-ai-engineering Project

A self-paced curriculum repo for AI and data engineering: notes, notebooks, exercises and
course material. Its courses are imported into this wiki's Courses tab by
`make import-courses`. The structural model of the two AI waves is covered in
[[AI Engineering Curriculum Structure]]; this page is the repo-level map.

## Six subjects

| Subject | Covers | Structure | Wiki map |
|---|---|---|---|
| Programming (added 2026-10-29) | Python, SQL, TypeScript tracks | Three partly parallel tracks | — |
| Data analytics | Statistics, A/B testing, Bayesian inference on the Python data stack | Linear, ends in a branching decision | [[Data Science Curriculum Layers]] |
| Data engineering | Pipelines and MLOps | Linear pipeline stages | [[Data Engineering Foundations]] |
| Data science | Classical ML, deep learning, NLP | Tree, not a sequence | [[Data Science Curriculum Layers]] |
| Generative AI | Seven pillars: LLM fundamentals → RAG → agentic foundations → frameworks → RL → observability → applications | Sequential, with branches after foundations | [[AI Engineering Curriculum Structure]] |
| AI engineering | Six foundations: prompt → context → harness → loop → graph → eval | Sequential nesting | [[AI Engineering Curriculum Structure]] |

"Generative AI builds things with LLMs; AI engineering is the discipline that makes them
reliable." Prerequisites are recommendations, not gates.

**Programming became a subject** because language fluency is a prerequisite for every
other subject but belonged to none of them; the repo had only a handful of pandas notebooks
and no SQL or TypeScript. The analytics Python notebooks moved into the programming track.
The split is: the curriculum repo holds the course, a separate interview-prep repo holds the
practice drills, and this wiki shows both.

## Three learning paths

- **A — AI engineering**: Python fluency → LLM fundamentals (build a tiny GPT, read the
  attention paper, RLHF, prompting) → the six AI-engineering foundations → the generative-AI
  application pillars. Discipline is placed *before* the application pillars so the code
  patterns make sense structurally.
- **B — Data engineering**: Python and SQL → the pipeline sequence → optional ML or
  LLM-native depth.
- **C — Full-stack data**: every subject, broad first and deep second (6–12 months at
  10–15 h/week).

## Three layers

| Layer | What | Where |
|---|---|---|
| Depth | Code, notebooks, notes — the actual learning | Subject directories |
| Summary | Compressed exam-prep guides and question banks | A separate private interview-prep repo (moved out 2026-10-28) |
| Reference | Papers, PDFs, book chapters | `readings/` and `sources/` beside each pillar |

Go deep first; use the summary guides as self-tests after each pillar. Operational notes
live inside each pillar directory rather than in a separate pointer layer — the planned
pointer layer was superseded during execution (see
[[Execution-Made Decisions Leave Stale Invariants]]). The AI-engineering README also keeps
a crosswalk from each pillar to the agent convention references it maps to, and a register
of recurring sources split into primary (cite directly) and aggregator (gap-detectors),
described in [[Automated Paper Discovery Pipeline]].

## Definition of done and the freeze

The curriculum is **structurally frozen as of 2026-10-28**: new material goes into an
existing pillar, and a new top-level folder needs a written reason first. A pillar is done
when it has (1) a README with order and prerequisites, (2) **no vendored snapshot left** —
upstream courses synthesised into cited notes, then deleted, (3) every notebook runnable
offline or labelled with what it needs, (4) a clean import into this wiki with no broken
links, and (5) cross-links to its summary guide and drills.

The open work is mostly criterion 2: condensing the remaining downloaded course snapshots
(RAG, agentic foundations and frameworks, observability, one application, a knowledge-graph
notebook set), one snapshot per session, on the precedent of the context-engineering
pillar (notes plus references, then delete). Vendored material records its upstream and
licence; snapshots were matched to upstream by content, not name.

## Book synthesis

A vendored agent-engineering book (*AI Agents in Depth*, Apache-2.0) was synthesised into
the pillar notes and removed on 2026-10-28. In the generative-AI subject it became three
notes, compiled here as [[Agent Fundamentals]], [[Post-Training for Agents]] and
[[Real-Time Multimodal Agents]]. Labs that run offline were copied in; the rest are linked
upstream because they need an API key, a GPU or hardware.

## Known gaps

- **TypeScript.** Only the LLM-fundamentals pillar has TypeScript examples (API call,
  structured output via forced tool use, a tool loop, multi-turn). Priority additions: a
  minimal TS RAG example, a TS agent loop, and TS tracing.
- **Statistics.** Causal inference, Bayesian A/B integration, non-parametric and time-series
  tests (see [[Data Science Curriculum Layers]]).
- **External resources** are a curated, de-duplicated link list per pillar, not compiled
  here.

## See Also
- [[AI Engineering Curriculum Structure]] — extends (the two-wave model of the AI subjects)
- [[Data Science Curriculum Layers]] — extends (the analytics and data-science subjects)
- [[Data Engineering Foundations]] — extends (the data-engineering subject)
- [[Agent Fundamentals]] — extends (generative-AI pillar 03 synthesis)
- [[Post-Training for Agents]] — extends (generative-AI pillar 05 synthesis)
- [[Real-Time Multimodal Agents]] — extends (generative-AI pillar 07 synthesis)
