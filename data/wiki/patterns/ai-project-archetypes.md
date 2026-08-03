---
title: AI Project Archetypes
tags: [llm, reference]
summary: Four archetypes — Information Retrieval, Document Generation, Workflow Automation, Conversational Interface — that cover most nonprofit AI projects, each with a complexity floor, disambiguating questions, and a mapping to concrete scaffold parameters.
updated: 2026-08-03
sources:
  - data/raw/claude-docs/ai-project-template/skills/project-discovery/reference/archetype-selection.md
  - data/raw/claude-docs/ai-project-template/skills/project-discovery/SKILL.md
---

# AI Project Archetypes

Four patterns covering the majority of nonprofit AI projects. The selection rule:
**pick the one where the hard problem lives, not where the most code goes.**

| Archetype | The AI's job | Complexity floor |
|---|---|---|
| Information Retrieval | Find and surface existing knowledge | Multi-sprint |
| Document Generation | Draft artifacts from templates + context | Weekend sprint |
| Workflow Automation | Orchestrate multi-step processes | Multi-sprint |
| Conversational Interface | Natural-language access to complex systems | Semester |

## Information Retrieval

Search a corpus (PDFs, policies, regulations, case notes) and return answers with source
citations. Core value: *"stop digging through files manually."*

**Use when** lookup time is significant, the answers already exist, accuracy and
source-tracing matter (legal/compliance/policy), and the corpus is stable.
**Avoid when** the information doesn't exist yet, the corpus is tiny (<20 documents — a
FAQ page suffices), or real-time data is needed.

Maps to `project_type=rag`, `primary_chat_agent=lg_agent`, `vector_backend=duckdb`
(<10k docs) or `postgres` at scale, `agent_memory=conversation`, `agent_tools=[mcp]`.

**Key risk:** retrieval quality — below 0.7 hit_rate on the golden QA set, the system
isn't useful yet. See [[Golden Set Mechanics]].

## Document Generation

Draft documents, reports, or communications from templates, context, and prior examples.
Core value: *"stop writing the same thing from scratch every time."*

**Use when** documents are repetitive, 50–80% of content is reusable boilerplate, human
review before sending is acceptable, and output format matters.
**Avoid when** every document is genuinely unique, there's zero error tolerance (contracts,
legal filings) without mandatory human review, or the real bottleneck is data gathering
rather than writing — that needs retrieval first.

The only archetype with a **weekend-sprint floor**: a prompt-only version works in a day;
structured templates and context injection take 2–4 weeks.

Maps to `project_type=agent`, `agent_memory=none|conversation`,
`optional_features=[promptfoo]`.

**Key risk:** template drift when the org's format changes. Quality is also subjective —
hard to evaluate automatically.

## Workflow Automation

Orchestrate multi-step processes: extract, route, act, notify. Core value: *"five manual
steps now happen automatically when an event occurs."*

**Use when** the process has clear sequential steps, multiple systems need coordination,
the bottleneck is handoff friction between steps, and rules are expressible.
**Avoid when** each case needs unique human judgment, the process isn't stable yet, only
one system is involved, or volume is under ~5 cases/week.

Maps to `project_type=workflow`, `primary_chat_agent=lg_agent` (graph control flow fits
multi-step), `external_systems=[slack, calendar, email]`, `agent_tools=[mcp, custom]`,
`human_approval=sometimes` (approve irreversible actions).

**Key risk:** reliability — *"a workflow that fails silently is worse than manual. Build
notifications for failures from day one."*

## Conversational Interface

Natural-language access to a complex system. Core value: *"ask in plain language — no
training needed."*

**Use when** users are non-technical, the underlying system has a steep learning curve,
users need different slices of the same data, or repetitive support load is high.
**Avoid when** users are already comfortable with the existing system, the interaction is
purely transactional (needs a better form, not AI), or privacy/security makes open chat
risky.

The **semester-floor** archetype — it alone requires auth/identity, per-user data scoping,
conversation history, tool-calling, external deployment, and evaluation.

Maps to `project_type=chat_app`, `primary_users=customers|public_api`,
`frontend_backend_topology=split_service`, `agent_memory=long_term`,
`deployment_target=cloud|serverless`.

**Key risk:** scope — *"a 'chatbot for everything' fails."* Constrain to 3–5 specific
tasks with clear handoff to humans.

## Disambiguating questions

When the choice is unclear, four questions resolve it:

1. **Does the answer already exist, or need to be created?** Exists → Retrieval;
   needs creating → Generation.
2. **Is the main value finding information, or taking action?** Finding → Retrieval;
   acting → Workflow.
3. **Internal team, or the nonprofit's clients/community?** External → Conversational
   (needs auth + scoping).
4. **One step or many?** One → Retrieval/Generation; many → Workflow.

A pain point spanning archetypes gets a **primary** (where the hard problem lives) and the
secondary noted as a phase-2 add-on. Hedging with "a mix of retrieval and generation" is
explicitly disallowed.

## Complexity budget

| Tier | Time | Team | Achievable |
|---|---|---|---|
| Weekend sprint | 1–2 focused days | 1–2 | Working prototype, one happy path. No auth, deploy, or eval suite. |
| Multi-sprint | 2–6 weeks | 2–4 | Production-ready core feature, basic eval, deployed. |
| Semester | 8–12 weeks | 3–6 | Auth, multi-tenancy, integrations, eval gates, monitoring, handoff docs. |

The governing rule when capacity doesn't match ambition: **reduce scope, not quality.**
*"A weekend sprint that delivers one working feature well is more valuable than a semester
plan that ships nothing because the team ran out of hours."*

Because each archetype has a **complexity floor**, the budget is a selection constraint,
not just a schedule — a team with weekend capacity cannot choose Conversational Interface,
they must reframe toward Document Generation.

## See Also
- [[Project Discovery Conversation]] — prerequisite-for
- [[AI Project Template Scaffold]] — extends (archetype → copier parameters)
- [[NYC-DSSG Project]] — instance-of
- [[Golden Set Mechanics]] — extends (retrieval hit_rate gate)
- [[Integration Pattern Selection]] — extends (archetype constrains the plausible integrations)
