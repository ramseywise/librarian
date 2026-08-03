---
title: AI Project Template Scaffold
tags: [infra, pattern]
summary: A generic, framework-agnostic starter repo pattern for standing up new AI agent projects — modeled on a mature reference project's skills/docs/infra layout plus a conventional data-science project skeleton (`.github`, `project_init.sh`, `.vscode`, `data/`, `docs/`, `infrastructure/`), kept as its own repo rather than nested under the reference project.
updated: 2026-07-19
sources:
  - raw/sessions/claude-2026-07-06-we-have-a-template-for-github-ai-project-268f0009.md
  - raw/sessions/claude-2026-07-14-what-is-the-git-origin-for-ai-project-te-c90bb5d6.md
  - raw/sessions/claude-2026-07-12-can-we-do-a-thorough-code-review-of-puff-a5c50915.md
  - raw/sessions/puffin-chat-2026-07-15-19-11.md
  - raw/sessions/claude-2026-07-16-so-i-m-thinking-about-comparing-our-ai-p-73f6b61f.md
  - raw/sessions/claude-2026-07-19-none-of-my-cicd-pipelines-run-we-need-to-d7cdbb90.md
---

# AI Project Template Scaffold

A reusable starter-repo pattern for bootstrapping a new AI agent project, distilled from an existing mature reference project (docs, Claude commands/skills, data pipeline, evals, and infra) plus a conventional data-science project skeleton borrowed from a separate template repo.

## What It Should Carry Over From a Mature Reference Project

- `.claude/` — skills and commands, already refined through real use
- `docs/` — the research→plan→archive lifecycle (see [[Claude Workflow System]])
- Data pipeline and eval scaffolding (see [[Synthetic Dataset Generation for RAG Eval]], [[RAG Eval Metrics Suite]] for the shape of what belongs here)
- Infra: AWS deployment config, LangFuse/LangSmith integration wiring, FastAPI service skeleton, CI/CD pipeline, Terraform

## What It Should Carry Over From a Conventional DS Project Skeleton

Comparing against a separate, more classically-structured data-science project template surfaced a gap list: `.github/` (CI workflows), `project_init.sh` (bootstrap script), `.vscode/` (editor config), and consistently-named top-level dirs — `configs/`, `data/`, `docs/`, `infrastructure/`.

**Gap identified against "the image of an AI app":** the reference project template was missing explicit frontend scaffolding and some other app-shell pieces beyond the backend/eval/infra stack — worth auditing for any new template before treating it as complete.

## Repo Placement Decision

**Decision: the template lives in its own dedicated repo**, not nested inside the reference project (e.g. not `playground/ai-project-template/`). Rationale: a template needs an independent git origin so it can be instantiated cleanly for new projects (`git clone` + rename) without dragging along the reference project's own history or unrelated files. This is the same boundary logic as [[Multi-Repo Claude Organization]] — shared tooling that should be reusable across repos belongs in its own repo, not embedded in one consumer.

**Local testability requirement:** before relying on the template, it should be possible to test it locally as a generator — i.e. actually instantiate a new project from it and confirm the result runs — not just review the file layout by eye.

## Copier-Based Templating (2026-07-15+)

The template uses [Copier](https://copier.readthedocs.io/) as its generator (`copier.yaml` at root). Key additions from July 2026 sessions:

- **`DESIGN.md.jinja`** — always generated (not gated on a toggle). Pre-fills `data_sensitivity` from copier answer. Ships with clear placeholders if `/scope-poc` wasn't run.
- **`/scope-poc` skill** — five-tier interview framework (problem/actors → system boundaries → AI design → constraints → MVP scope) for scoping a new project before implementation. DSSG-aware: auto-detects nonprofit-success-ai vs. project-mgmt-ai from repo names and loads shared platform context (Supabase, actor roles, Engagement lifecycle).
- **`/project-genesis`** (updated) — Step 0 reads existing `DESIGN.md` first; recommended sequence is `/scope-poc` → `/project-genesis`.
- **`scripts/sync-global-skills.sh`** — one-way sync from `~/.claude/skills/` → `template/.claude/skills/`. The template vendors global skills because scaffolded projects have no access to `~/.claude`. Hard-fails on unknown skill names (since 2026-07-19).

## CI/CD Standardization (2026-07-19)

**Problem:** CI/CD pipelines were broken across repos. Root cause: no shared template for workflows.

**Decision:** standardize via the template's `.github/workflows/` — reusable across production repos. Non-production repos may not warrant CI/CD.

**Production repos** (those warranting full CI/CD): librarian, guacamayo, atlas, ai-project-template, listen-wiseer.

## Skill Porting

Porting skills into the new template (`new-agent` skill work) raised the question of where supporting specs/docs should live — collected under a `root/docs`-style location rather than scattered — mirroring the docs lifecycle pattern in [[Claude Workflow System]].

## SANYI Integration (2026-07-16)

The template seeds a per-repo `SANYI.md` change contract on generation. When added to a repo, SANYI sets up the contracts for that repo's layers — which components are invariant (不易), which are tunable (简易), which change freely (变易). See [[SANYI Change-Contract System]].

## See Also
- [[Agent Scaffolding Skill Layers]] <!-- auto-linked -->
- [[Multi-Repo Claude Organization]]
- [[Claude Workflow System]]
- [[ADK Scaffold Patterns]]
- [[Puffin Consciousness Development Skills]]
- [[NYC-DSSG Project]] — instance-of (primary consumer of templates)
- [[Skill-Knowledge Information Flow]] — extends (template sync contract)
- [[Eval-Driven Development (EDD)]] — extends (golden set as discovery-exit artifact)
- [[Golden Set Mechanics]]
