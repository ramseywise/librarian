---
title: NYC-DSSG Project
tags: [project]
summary: NYC Data Science for Social Good — platform engineering for a nonprofit serving 600+ nonprofits via 300 volunteers; building knowledge base, project templates, and PM agent.
updated: 2026-07-19
sources:
  - raw/gdrive/2026-07-15-dssg-ramsey-jian-chat.md
  - raw/sessions/puffin-chat-2026-07-15-19-11.md
  - raw/sessions/claude-2026-07-16-dssg-root-we-have-our-exec-summary-port-fc67b3f0.md
  - raw/sessions/claude-2026-07-19-none-of-my-cicd-pipelines-run-we-need-to-d7cdbb90.md
---

# NYC-DSSG Project

Data Science for Social Good (NYC-DSSG) supports approximately 600 nonprofits that lost funding due to cancelled grants. The organization leverages ~300 volunteers to provide pro bono AI, software, and IT services.

## Operational Model

Functions like a pro bono law firm:
1. **Intake** — nonprofit applies for help
2. **Feasibility assessment** — can the work be completed within an 8-hour hackathon limit?
3. **Ongoing support** — workshops, grant management tools, volunteer matching

## Current Tech Stack

| Layer | Technology |
|---|---|
| Code | GitHub |
| Deployment | Vercel |
| Backend data | Google Sheets (fragile, being replaced) |

## Ramsey's Role (joined 2026-07-15)

Platform engineering — building operational and technical support tools:

1. **Knowledge base repository** — centralize operational skills and workflows (this librarian instance)
2. **Project templates** — standardized scaffolding for volunteer projects (ai-project-template)
3. **PM agent** — project management AI agent for volunteer coordination (planned)

## Key Decisions (2026-07-15)

- Knowledge base repo creation authorized
- Commitment to test new templates once developed
- Centralize data management through unified KB and standardized project templates

## Strategic Priority

Replace fragmented Google Sheets backend and outdated repos with:
- Unified knowledge base
- Standardized project templates
- AI agent for project management and volunteer coordination

## Design Sprint & Milestones (2026-07-16)

Ran `/define-milestones` and `/design-sprint` against the DSSG roadmap. The roadmap itself already followed a C4 model with MVP vs. Phase 2 table and cross-cutting decisions.

Three planned initiatives:
1. **Knowledge Base** — centralize operational skills (this librarian instance)
2. **PM Agent (project-mgmt-ai)** — lifecycle backend guiding cohort operations (volunteer/staff-facing)
3. **Customer Success Agent (nonprofit-success-ai)** — customer portal (NPO client-facing)

Both DSSG agent projects are platform-level. The key gate question for nonprofit-success-ai: Firebase → Supabase migration must be resolved before any AI feature work.

## System Design Framework (2026-07-15)

A five-tier interview framework was synthesized for `/scope-poc` (see
[[Scope-POC Design Interview]]):
1. Problem / actors
2. System boundaries
3. AI design decisions
4. Constraints (cost, latency, compliance)
5. MVP scope

Each tier maps to copier variables in the [[AI Project Template Scaffold]].

## Platform Shape — The Shared Engagement Lifecycle (2026-07-15)

Both platform projects are built around **one** lifecycle object, not two:

`initial_meeting → budgeting → engagement_tracking → hackathon → membership_close`

Stage ownership is split rather than duplicated:

| Project | Actor | Stages owned |
|---|---|---|
| **nonprofit-success-ai** (customer portal) | NPO Client (external) | `initial_meeting → budgeting → engagement_tracking → membership_close` |
| **project-mgmt-ai** (lifecycle backend) | DSSG core volunteers, Data Diplomats (internal) | `hackathon` |

The handoff is a single field: project-mgmt-ai *"receives `Engagement.hackathon_project`
from nonprofit-success-ai's stage transition"* when `Engagement.stage === 'hackathon'`.

Three actor roles span the platform: **NPO Client** (external), **Data Diplomat** (cohort
volunteer), **DSSG core volunteer** (staff/leads). The external/internal split is what
forces a [[Split Service Deployment]] for the portal while the backend can stay internal.

### Shared infrastructure — owned by neither project alone

- Shared Supabase DB with `Business` / `Engagement` / `User` tables + RLS
- Platform API (auth check + engagement read/write + KB query stub)
- Comms sender triggered by `Engagement.stage` writes — *"plain transactional email — not n8n"*

The comms note is a deliberate scope decision: the trigger is simple enough that workflow
glue would be added complexity, not saved effort.

### Per-project constraints

- **nonprofit-success-ai** — stack is React 19 + Firebase Auth + Firestore with no backend
  server; the Firebase-vs-Supabase migration is the *"highest-leverage decision per
  roadmap §1."* AI scope is *"not yet defined"* (candidate: engagement summaries,
  stage-transition suggestions, client chat). **Multi-tenancy is non-negotiable** — one
  nonprofit must never see another's data.
- **project-mgmt-ai** — README only, nothing built. Named scope risk: *"8-sprint proposal
  covers too much; needs explicit MVP narrowing before sprint 1."* Auth *"must reuse
  whatever nonprofit-success-ai lands on (single identity system)"* — the identity decision
  is upstream of both projects.

## Production Repos (2026-07-19)

Repos warranting full CI/CD and standardized templates: **librarian, guacamayo, atlas, ai-project-template, listen-wiseer**. Others are non-production or exploratory.

## See Also
- [[AI Project Template Scaffold]] — extends
- [[Librarian Project]] — instance-of (KB for DSSG)
- [[SANYI Change-Contract System]] — prerequisite-for
- [[AI Project Archetypes]] — extends (archetype selection for volunteer projects)
- [[Project Discovery Conversation]] — prerequisite-for (entry point for new project ideas)
- [[Scope-POC Design Interview]] — extends (DSSG platform context block; the five-tier framework)
- [[Integration Pattern Selection]] — extends (n8n glue as insurance against volunteer turnover)
- [[DESIGN.md Artifact]] — extends (the design record both platform projects produce)
- [[Design-Before-Infrastructure Sequencing]] — extends (DSSG platform work was the specific driver)
- [[Split Service Deployment]] — instance-of (external NPO clients force the split topology)
