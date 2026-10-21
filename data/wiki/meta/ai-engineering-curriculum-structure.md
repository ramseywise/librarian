---
title: AI Engineering Curriculum Structure
tags: [meta, foundations, concept, conflict]
summary: "The two-wave model of the learn-ai-engineering corpus — generative-ai as the application wave (seven pillars) and ai-engineering as the discipline wave (six foundations) — plus the dependency ordering that makes the pillar sequence more than a filing scheme."
updated: 2026-10-17
sources:
  - data/raw/repos/learn-ai-engineering/generative-ai--README.md
  - data/raw/repos/learn-ai-engineering/generative-ai--01-llm-fundamentals--README.md
  - data/raw/repos/learn-ai-engineering/generative-ai--02-rag-retrieval--README.md
  - data/raw/repos/learn-ai-engineering/generative-ai--03-agentic-foundations--README.md
  - data/raw/repos/learn-ai-engineering/generative-ai--04-agentic-frameworks--README.md
  - data/raw/repos/learn-ai-engineering/generative-ai--06-observability--README.md
  - data/raw/repos/learn-ai-engineering/generative-ai--07-agentic-applications--README.md
  - data/raw/claude-docs/learn-ai-engineering/docs/research/2026-07-21_curriculum-architecture_meta.md
  - data/raw/claude-docs/learn-ai-engineering/docs/research/2026-07-21_readings-interviewing_crosscut.md
  - data/raw/claude-docs/learn-ai-engineering/docs/research/2026-07-22_docs_inventory.md
  - data/raw/claude-docs/learn-ai-engineering/docs/research/2026-07-21_generative-ai_inventory.md
  - data/raw/claude-docs/learn-ai-engineering/docs/plans/2026-07-17-curriculum-pillars.md
  - data/raw/repos/learn-ai-engineering/.claude--docs--plans--2026-07-17-curriculum-pillars.md
  - data/raw/claude-docs/learn-ai-engineering/docs/plans/2026-07-21-ai-engineering-foundations.md
  - data/raw/repos/learn-ai-engineering/.claude--docs--plans--2026-07-21-ai-engineering-foundations.md
  - data/raw/claude-docs/learn-ai-engineering/docs/plans/2026-07-21-curriculum-buildout.md
  - data/raw/repos/learn-ai-engineering/.claude--docs--plans--2026-07-21-curriculum-buildout.md
  - data/raw/claude-docs/learn-ai-engineering/docs/plans/LAE-28-research.md
  - data/raw/repos/learn-ai-engineering/.claude--docs--plans--LAE-28-research.md
  - data/raw/claude-docs/learn-ai-engineering/docs/plans/LAE-28-plan.md
  - data/raw/repos/learn-ai-engineering/.claude--docs--plans--LAE-28-plan.md
  - data/raw/repos/learn-ai-engineering/CURRICULUM.md
  - data/raw/repos/learn-ai-engineering/README.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--README.md
  - data/raw/repos/learn-ai-engineering/interviewing--README.md
  - data/raw/repos/learn-ai-engineering/interviewing--guides--00-start-here.md
  - data/raw/repos/learn-ai-engineering/interviewing--guides--0-programming--00-overview.md
  - data/raw/repos/learn-ai-engineering/interviewing--guides--1-foundations--00-overview.md
  - data/raw/repos/learn-ai-engineering/interviewing--guides--2-llm-fundamentals--00-overview.md
  - data/raw/repos/learn-ai-engineering/interviewing--guides--3-rag--00-overview.md
  - data/raw/repos/learn-ai-engineering/interviewing--guides--4-agents--00-overview.md
  - data/raw/repos/learn-ai-engineering/interviewing--guides--5-context-cost--00-overview.md
  - data/raw/repos/learn-ai-engineering/interviewing--guides--6-evals-observability--00-overview.md
  - data/raw/repos/learn-ai-engineering/interviewing--guides--7-security-safety--00-overview.md
  - data/raw/repos/learn-ai-engineering/interviewing--guides--8-data-eng-mlops--00-overview.md
  - data/raw/repos/learn-ai-engineering/interviewing--guides--9-system-design--00-overview.md
  - data/raw/repos/learn-ai-engineering/interviewing--guides--10-product-delivery--00-overview.md
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

## Why six peer foundations, not four plus a frontier tier

The discipline wave's six numbered foundations were a decision, and the research behind it
recommended a different shape. Every source that listed the *foundational* stack gave the
same four layers in the same order: **prompt → context → harness → loop**. They nest:
the harness implements loops, each loop step assembles context, and context contains
prompts. Graph engineering was described everywhere as a tier *above* loops ("graphs
contain loops"), applying loop design to multi-agent organisations. Evaluation was the
strongest fifth candidate. One source named it as a fifth discipline, while another folded
verification into harness "sensors", so the research rated it medium confidence. Memory
and tool design were rejected as pillars because every taxonomy treats them as
sub-components of harness or context.

The research therefore recommended four foundations, eval as a fifth, and graph in a
labelled `frontier/` tier. The owner overrode it and made **graph a peer fifth and eval a
peer sixth**, with no frontier tier. Graph keeps its "builds on loops" position (it sits at
05, after loop) but became a first-class pillar instead of an advanced add-on. The plan records
this as the owner's direction and gives no reason that comes from the sources. What it
added was a parity rule: each of the six pillars had to point to a real cleaned note, and the two missing notes (prompt, graph) were
written from web sources so that no pillar shipped as a stub. When reading the numbering,
keep the research view in mind: 01–04 are a strict dependency chain, while 05 and 06 are
peers by curation decision.

## The summary/depth layering

A third axis crosses both waves. `interviewing/guides/` is a **pointer-only summary
layer** for exam prep; the pillar directories are the depth layer; and a **reference layer**
of papers and book chapters (no notes) sits colocated with the pillar that uses it. The
stated reading order is depth first, the summary layer as a self-test after each pillar
(not as the primary learning surface), and readings only when a code exercise leaves a "why
does this work?" gap. The curriculum coordinator also routes by goal: an AI-engineering path
(Python → LLM fundamentals → the six discipline pillars → the application pillars 02–07), a
data-engineering path, and a broad full-stack path. Its one notable sequencing claim is
that the application pillars are easier to absorb *after* the discipline wave, because the
code patterns then make structural sense. Each pillar README
carries an explicit crosswalk link to its guide, and guides link back into both waves for
depth.

The corpus ended up with operational notes living **directly
inside each pillar directory** rather than in a separate `notes/` pointer layer, which was
absorbed during the curriculum buildout. Notes sit next to the material they annotate;
only the exam-prep summaries are kept separate. This layout was not planned. The plans resolved on a pointer-only layer, and execution absorbed the notes into the pillars instead. The README sentence that described the pointer model outlived the change (see [[Execution-Made Decisions Leave Stale Invariants]]). The reason a pointer layer survives at all
for guides and not for notes is that the two compress differently — a summary written for
recall under time pressure is a genuinely different artefact from the material it
summarises, whereas a note about a course is just more course material.

This is the same three-way split the wiki enforces between `patterns/` (discovered while
building), subject directories (synthesised from external sources), and `interview/`
(true only while interviewing) — three buckets that **decay at different rates**, which is
the actual justification for keeping them apart.

## When a numbered foundation sequence generalizes

The discipline wave's numbered chain (`01-prompt` → `06-eval`) works because each layer
**inherits the weaknesses of** the one beneath it. A curriculum audit tested whether the
same shape should be imposed on every domain. It concluded that it should not. The shape
has to match how the domain's knowledge actually depends on itself:

| Shape | Fits when | Domains |
|---|---|---|
| **Linear chain** | Each stage consumes the previous stage's output | ai-engineering, data engineering, data analytics |
| **Tree** | Shared foundations, then branches that do not depend on each other | data science, generative AI |
| **Topic library + difficulty ladder** | Topics are independent; only difficulty orders them | programming |

Forcing a chain onto a tree invents dependencies that do not exist. The "inherits the
weaknesses of" sentence in each pillar README is the load-bearing test. If you cannot
write that sentence truthfully for a pair of adjacent stages, the domain is not a chain.

Two maintenance rules carry over to every shape:

- **Crosswalks are one-way pointers.** A guide links to the depth material and never copies
  it. A copied summary drifts from its source the first time either is edited.
- **Guides and depth docs are complementary on purpose.** The guide is compressed for
  recall and the depth doc is detailed for understanding. Merging them loses one of the two
  jobs.

## The interview-prep taxonomy

The exam-prep layer uses its own ten-pillar taxonomy. It does not reuse the two-wave
structure, because interviews probe across both waves at once:

| # | Pillar | # | Pillar |
|---|---|---|---|
| 1 | Foundations | 6 | Evals & Observability |
| 2 | LLM Fundamentals | 7 | Security & Safety |
| 3 | RAG | 8 | DE & MLOps |
| 4 | Agents | 9 | System Design |
| 5 | Context & Cost | 10 | Product & Delivery |

Each pillar folder has three layers — a `00-overview.md` (why it matters, a learning path,
and a resource map over readings, runnable course code, wiki pages, and notes), detailed notes,
and an `interview-guide.md` read *last* as a self-test. The compiled guides are
[[Programming Interview Study Guide]] (a pillar 0 for coding screens), [[ML Foundations Interview Study Guide]],
[[LLM Fundamentals Interview Study Guide]], [[RAG Interview Study Guide]],
[[Agents Interview Study Guide]], [[Context Engineering and Cost Interview Study Guide]],
[[Evals and Observability Interview Study Guide]], [[Security and Safety Interview Study Guide]],
[[Data Engineering and MLOps Interview Study Guide]], [[System Design Interview Study Guide]], and
[[Product and Delivery Interview Study Guide]]. The overviews' recurring sequencing claims:
build before reading (read a paper or textbook chapter *after* the code has made its diagrams
familiar), and fluency before patterns for coding.

The weighting of these pillars by role, and the round types a loop actually runs, are in [[AI Role Interview Loop Map]]. Pillars 1 and 8 can be studied in parallel. Pillars 9 and 10 are *integrative*: they assume
the others and test whether you can combine them under constraints, so they come last.

The taxonomy is implemented as a **hybrid topic index**. A topic-organized index file
points into files that stay owned by their pillar directories. Each piece of content
therefore has one canonical location, and topic-based discovery still works. This is the
same one-way-pointer rule applied at the index level.

## See Also
- [[Skill-Knowledge Information Flow]] — part-of (the corpus as one of four parallel systems, and its ingest contract into this wiki)
- [[Karpathy LLM Wiki Pattern]] — complements (how this corpus is compiled into wiki pages)
- [[Context Engineering]] — extends (the discipline-wave generalisation of pillar 02)
- [[ADK vs LangGraph Comparison]] — instance-of (pillar 04 selection material)
- [[Observability and Runtime Patterns]] — instance-of (pillar 06 infrastructure)
- [[RAG Eval Gate Contract]] — complements (the discipline-wave counterpart to pillar 06)
- [[Data Engineering Foundations]] — part-of (the data pillar, upstream of both waves)
- [[Data Science Curriculum Layers]] — part-of (the analytics and ML pillars that precede the application wave)
- [[Execution-Made Decisions Leave Stale Invariants]] — extends (how the absorbed-into-pillars layout replaced the planned pointer layer)
- [[AI Role Interview Loop Map]] — extends (role weighting over the ten-pillar interview taxonomy)
