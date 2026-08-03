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

## Production Repos (2026-07-19)

Repos warranting full CI/CD and standardized templates: **librarian, guacamayo, atlas, ai-project-template, listen-wiseer**. Others are non-production or exploratory.

## See Also
- [[AI Project Template Scaffold]] — extends
- [[Librarian Project]] — instance-of (KB for DSSG)
- [[SANYI Change-Contract System]] — prerequisite-for
- [[AI Project Archetypes]] — extends (archetype selection for volunteer projects)
- [[Project Discovery Conversation]] — prerequisite-for (entry point for new project ideas)
- [[Scope-POC Design Interview]] — extends (DSSG platform context block; the five-tier framework)
