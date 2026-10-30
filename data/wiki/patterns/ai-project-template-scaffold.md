---
title: AI Project Template Scaffold
tags: [infra, pattern]
summary: A generic, framework-agnostic starter repo pattern for standing up new AI agent projects — modeled on a mature reference project's skills/docs/infra layout plus a conventional data-science project skeleton (`.github`, `project_init.sh`, `.vscode`, `data/`, `docs/`, `infrastructure/`), kept as its own repo rather than nested under the reference project.
updated: 2026-10-30
sources:
  - data/raw/sessions/claude-2026-07-06-we-have-a-template-for-github-ai-project-268f0009.md
  - data/raw/sessions/claude-2026-07-14-what-is-the-git-origin-for-ai-project-te-c90bb5d6.md
  - data/raw/sessions/claude-2026-07-12-can-we-do-a-thorough-code-review-of-puff-a5c50915.md
  - data/raw/sessions/puffin-chat-2026-07-15-19-11.md
  - data/raw/sessions/claude-2026-07-16-so-i-m-thinking-about-comparing-our-ai-p-73f6b61f.md
  - data/raw/sessions/claude-2026-07-19-none-of-my-cicd-pipelines-run-we-need-to-d7cdbb90.md
  - data/raw/claude-docs/ai-project-template/docs/research/multi-agent-tooling-parity.md
  - data/raw/claude-docs/ai-project-template/docs/research/template-pillar-gaps.md
  - data/raw/claude-docs/ai-project-template/docs/plans/2026-07-19-two-root-scaffold-decision-tree.md
  - data/raw/claude-docs/ai-project-template/docs/prompts/2026-08-05-HOLD-workflow-and-graph-capabilities.md
  - data/raw/claude-docs/ai-project-template/docs/research/2026-08-29_diskoe-parity_template-conventions.md
  - data/raw/repos/ai-project-template/README.md
  - data/raw/repos/ai-project-template/.claude--docs--in-progress--genesis-dryrun--friction-log.md
  - data/raw/repos/ai-project-template/.claude--docs--in-progress--genesis-dryrun--render-review.md
  - data/raw/repos/ai-project-template/.claude--docs--in-progress--production_hardening--plan.md
  - data/raw/repos/ai-project-template/.claude--docs--in-progress--puffin-integration--plan.md
  - data/raw/repos/ai-project-template/.claude--docs--in-progress--template-backlog--backlog.md

  - data/raw/claude-docs/ai-project-template/docs/plans/2026-07-12-puffin-integration.md
  - data/raw/repos/ai-project-template/.claude--docs--plans--2026-07-12-puffin-integration.md
  - data/raw/claude-docs/ai-project-template/docs/plans/2026-07-14-template-backlog.md
  - data/raw/repos/ai-project-template/.claude--docs--plans--2026-07-14-template-backlog.md
  - data/raw/claude-docs/ai-project-template/docs/plans/2026-07-16-genesis-dryrun.md
  - data/raw/repos/ai-project-template/.claude--docs--plans--2026-07-16-genesis-dryrun.md
  - data/raw/claude-docs/ai-project-template/docs/plans/2026-07-16-production-hardening.md
  - data/raw/repos/ai-project-template/.claude--docs--plans--2026-07-16-production-hardening.md
  - data/raw/claude-docs/ai-project-template/docs/plans/2026-07-17-evals-suite-port.md
  - data/raw/repos/ai-project-template/.claude--docs--plans--2026-07-17-evals-suite-port.md
  - data/raw/claude-docs/ai-project-template/docs/plans/2026-07-17-template-core-redesign.md
  - data/raw/repos/ai-project-template/.claude--docs--plans--2026-07-17-template-core-redesign.md
  - data/raw/claude-docs/ai-project-template/docs/plans/2026-07-18-template-full-mirror-redesign.md
  - data/raw/repos/ai-project-template/.claude--docs--plans--2026-07-18-template-full-mirror-redesign.md
  - data/raw/claude-docs/ai-project-template/docs/plans/2026-07-19-cicd-standardization.md
  - data/raw/repos/ai-project-template/.claude--docs--plans--2026-07-19-cicd-standardization.md
  - data/raw/claude-docs/ai-project-template/docs/plans/2026-07-19-genesis-lifecycle-architecture.md
  - data/raw/repos/ai-project-template/.claude--docs--plans--2026-07-19-genesis-lifecycle-architecture.md
  - data/raw/claude-docs/ai-project-template/docs/plans/2026-07-19-template-toplevel-structure.md
  - data/raw/repos/ai-project-template/.claude--docs--plans--2026-07-19-template-toplevel-structure.md
  - data/raw/claude-docs/ai-project-template/docs/plans/2026-07-19-two-root-scaffold.md
  - data/raw/repos/ai-project-template/.claude--docs--plans--2026-07-19-two-root-scaffold.md
  - data/raw/claude-docs/ai-project-template/docs/plans/2026-08-05-workflow-and-graph-capabilities.md
  - data/raw/repos/ai-project-template/.claude--docs--plans--2026-08-05-workflow-and-graph-capabilities.md
  - data/raw/claude-docs/ai-project-template/docs/plans/AIT-22-research.md
  - data/raw/repos/ai-project-template/.claude--docs--plans--AIT-22-research.md
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
- **`/scope-poc` skill** — see [[Scope-POC Design Interview]]. Five-tier interview framework (problem/actors → system boundaries → AI design → constraints → MVP scope) for scoping a new project before implementation. Platform-aware: auto-detects nonprofit-success-ai vs. project-mgmt-ai from repo names and loads shared platform context (Supabase, actor roles, Engagement lifecycle).
- **`/project-genesis`** (updated) — see [[Asked vs Derived Scaffold Variables]]. Step 0 reads existing `DESIGN.md` first; recommended sequence is `/scope-poc` → `/project-genesis`.
- **`scripts/sync-global-skills.sh`** — one-way sync from `~/.claude/skills/` → `template/.claude/skills/`. The template vendors global skills because scaffolded projects have no access to `~/.claude`. Hard-fails on unknown skill names (since 2026-07-19). The sync is a transform, not a mirror — the two trees address the same file differently, so link targets and copier variables are rewritten in transit; see [[Sync as Render, Not Copy]]. Extending it to the capability payload required first fixing six defects in the canonical copies, since a mirror stamps every canon bug into every scaffolded project — see [[Payload Security Defects at Canon]].

## Capability Roadmap Method (2026-07-14)

When two downstream projects (project-mgmt-ai, grant-fundraising-ai) each arrived with tool
stacks the template didn't cover, the roadmap was set by a [[Capability Parity Audit]] —
every requested capability classified have/partial/gap against the *grepped* scaffold, then
prioritized by how many projects shared the gap. Three shared gaps emerged
(Supabase/pgvector, n8n reachability, CrewAI); the n8n item resolved to a
[[Callable-By Integration Contract]] rather than new infrastructure.

A later audit of the same payload found the parity question itself was malformed for
part of the list: six of the fourteen capabilities never touch the runtime, so asking
what their LangGraph version looks like has no answer. See
[[Capability Runtime-Coupling Tiers]].

## Pillar Gap Analysis (2026-07-29)

A second roadmap pass scored the template against the
[[Six-Pillar Agent Engineering Assessment]] and intersected the result with a portfolio-wide
scan of the five existing repos — [[Template Floor Raising]]. Outcome: **25/25 Must-tier
requirements met, 5/17 Should, 2/11 Nice (65% overall)**, with Loop the weakest pillar at
50% and Evaluation the strongest at 76%. The top three additions (verification-loop wrapper,
token-budget utility, OTel spans) were each chosen because 4–5 of the 5 existing repos
lacked them, not because any one project asked.

## CI/CD Standardization (2026-07-19)

**Problem:** CI/CD pipelines were broken across repos. Root cause: no shared template for workflows.

**Decision:** standardize via the template's `.github/workflows/` — reusable across production repos. Non-production repos may not warrant CI/CD.

**Production repos** (those warranting full CI/CD): librarian, guacamayo, atlas, ai-project-template, listen-wiseer.

**What the audit actually found** (premise corrected — application CI had never been written, not broken):

- The template's own CI used `setup-uv` with a cache keyed on `uv.lock`, which cannot exist at a template root — the cache step failed before any test ran.
- Dependabot auto-merge was *believed* ungated: it merged without waiting on required checks. A 2026-07-28 live check (`gh api`) found branch protection already requires the CI check on all four production repos, and `gh pr merge --auto` honors it, so auto-merge was in fact gated. See [[Gate Dependabot Auto-Merge on Branch Protection]].
- Fix shape: one reusable `workflow_call` workflow with `lint-paths`, `test-command` and `tests-blocking` inputs, so repos whose suites are not yet green can run tests non-blocking without skipping lint. Callers *should* pin `@v1`, not `@main`; as of 2026-07-28 the downstream callers still referenced `python-ci.yml@main`, so `@v1` is the convention to migrate to, not current practice.
- A relative copier `dst` inside CI rendered into `out/out/`; use absolute paths. See [[Verify CI Steps by Extraction, Not Retyping]] and [[Execute Every Toggle Configuration]].

## Skill Porting

Porting skills into the new template (`new-agent` skill work) raised the question of where supporting specs/docs should live — collected under a `root/docs`-style location rather than scattered — mirroring the docs lifecycle pattern in [[Claude Workflow System]].

## SANYI Integration (2026-07-16)

The template seeds a per-repo `SANYI.md` change contract on generation. When added to a repo, SANYI sets up the contracts for that repo's layers — which components are invariant (不易), which are tunable (简易), which change freely (变易). See [[SANYI Change-Contract System]].

## Genesis Dry-Run and Production Hardening (2026-07)

A full genesis dry-run (interview → render → review) and the production-hardening plan
surfaced template-level gaps that a fresh render never shows:

- **No pipeline shape.** The template shipped only a chat-agent shape, so a batch/pipeline
  project rendered a chat service around itself. The resolution, as of the README:
  architecture is **no longer asked at genesis**. It is derived from `project_type`, with
  one shape example per project type. More shapes are added later through
  `copier update -d …` / `/add-capability` (see [[Copier Re-Entry as Capability Path]]),
  which keeps the interview at 11–14 questions.
- **An example agent shipped unconditionally.** A RAG agent rendered into every project,
  justified by a toggle that was off in that render. See
  [[Derived-and-Hidden Design Decisions]].
- **Rules the template could not comply with.** The rendered rules banned `print`, but no
  logging utility was shipped. A `deployment_target` answer was asked for and consumed by
  no file.
- **An optional-import guard hid the headline feature.** A `try/except ImportError` around
  an integration router's mount meant a missing router left the app healthy and the feature
  unreachable (logged in [[Silent Failure Catalogue]]).
- **CI matrix: two tiers.** Render + lint on every row, test execution on one config per
  feature axis, on the evidence that bugs cluster per axis (detail in
  [[Execute Every Toggle Configuration]]).
- **Experiment tracking: one optional hook, not an abstraction.** The backlog declined to
  revive a four-backend tracker interface in favour of a single W&B hook gated on the key's
  presence, so it degrades to a no-op without it.
- **Ports become rewrites.** A planned "minimal port" of an entangled agent from another repo
  became a rewrite inspired by its architecture. Real runs caught the bugs the port scripts
  missed: a packaging bug, a Settings env collision
  ([[Settings Field Names Are a Shared Env Namespace]]), and a test regression from running
  ad-hoc scripts instead of the project suite.

## Two-Root Staging Layout (2026-07-19)

The scaffold stages everything under `_scaffold/` and promotes it in `_tasks`. Two shapes
of content need two different promotion rules:

- **The universal shell merges** (`.github/`, `.claude/`, `.agents/`, `Makefile`, docs) —
  it lands on top of whatever the destination already has.
- **Per-language project roots promote atomically** (`{{ py_project_root }}`,
  `{{ ts_project_root }}`) — a whole tree moved in one step, so a half-promoted backend
  cannot exist.

Decisions taken while settling the layout:

- **Remove an asymmetry rather than document it.** Where the Python and TypeScript roots
  were staged differently, the fix was to make them identical, not to explain the
  difference in a README.
- **Retire a variable, don't alias it.** A superseded root variable was deleted outright;
  keeping it as an alias would have left two names for one path in every consumer's
  answers file.
- **`.agents/` vs `.claude/` is split by audience, not vendor.** Cross-tool agent material
  lives in `.agents/`; Claude Code-specific runtime config in `.claude/`.
- **The TypeScript eval story is promptfoo plus a `run.ts`**, deliberately not a port of the
  Python harness.
- **`eval_root` stays a sibling of the serving root.** Nesting evals under the serving
  package would make the serving layer own its own judge — a layer violation.
- **`{{ }}` in a path means substitution, not optionality.** Optional files come from
  `_tasks` `rm` and `_exclude`, never from a variable that may render empty. An earlier
  top-level-structure plan (superseded by this one) had read the braces as "optional".
- **A "guarded" profile narrows permissions, never hooks.** A profile labelled guarded that
  ships fewer safety hooks than the default is backwards; guard profiles may only remove
  permissions.
- **`.claude/` and `.agents/` at the template root are residue of the old layering mode**,
  not part of the rendered contract.

Path-level verification for this layout (a static sweep for missing task paths, orphan
dirs, and unrendered braces) is in [[Execute Every Toggle Configuration]]. Changing one of
these derived roots' defaults later is a migration — see
[[Changing a Derived Default Is a Migration]].

## Maintainer-Path Onboarding Findings (2026-08)

A cold walk through the template as a new maintainer (not via the `/project-genesis`
skill) found the skill path sound but the raw path rough:

- Raw `copier copy` rendered with project name `""` — the skill supplied it; nothing else did.
- The rendered `Makefile` included `~/.claude/Makefile.common`, which is not in the repo.
- The README promised 11–14 interview questions; the render asked 8.
- `data_sensitivity` was silently defaulted rather than asked.
- The vanilla profile ran `rm -rf .claude .agents` with no warning.

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
- [[AI Project Archetypes]] — prerequisite-for (archetype determines copier parameters)
- [[Scope-POC Design Interview]] — prerequisite-for (DESIGN.md precedes genesis)
- [[DESIGN.md Artifact]] — extends (every scaffolded project ships the stub)
- [[Design-Before-Infrastructure Sequencing]] — prerequisite-for (the HOW conversation runs second)
- [[Deferred Decision Status]] — extends (Key Decisions table semantics)
- [[Asked vs Derived Scaffold Variables]] — extends (the genesis interview over copier.yaml)
- [[Copier Re-Entry as Capability Path]] — extends (post-render capability additions)
- [[Project Discovery Conversation]] — prerequisite-for (upstream of scaffold)
- [[Integration Pattern Selection]] — extends (external_systems / optional_features toggles)
- [[Copier Upstream Update Workflow]] — extends (how template changes reach generated repos)
- [[Template Migrations for Structural Moves]] — extends (shipping structural moves downstream)
- [[Capability Parity Audit]] — extends (how the capability roadmap is chosen)
- [[Six-Pillar Agent Engineering Assessment]] — extends (the rubric the template is scored against)
- [[Template Floor Raising]] — extends (how pillar gaps are prioritized into a backlog)
- [[Capability Runtime-Coupling Tiers]] — extends (T1/T2/T3 sorting of the payload)
- [[Sync as Render, Not Copy]] — extends (how canon reaches the template)
- [[Payload Security Defects at Canon]] — prerequisite-for (fix before the mirror lands)
- [[Test Derived Defaults Without Overrides]] — extends (two-root scaffold research finding)
- [[Read-Every-Consumer Migration]] — extends (two-root scaffold research finding)
- [[Role-Scoped Parity]] — extends (diskoe parity audit)
- [[Template Only Decided Patterns]] — extends (the HOLD on workflow/graph capabilities)
- [[Three-Doc Spec Split]] — related (spec convention considered for adoption from diskoe)
- [[Settings Field Names Are a Shared Env Namespace]] — instance-of
- [[Execute Every Toggle Configuration]] — extends
- [[Verify CI Steps by Extraction, Not Retyping]] — extends
- [[Gate Coupled Features on the Producer, Not the Label]] — extends
- [[Circular Core Justification]] — extends (why the RAG/MCP chain left the core)
- [[Capability Catalog with Preconditions]] — extends
- [[REST-First, MCP as Adapter]] — extends (the service-boundary decision)
- [[Three-Surface Guardrail Asymmetry]] — extends (the scaffolded guard layers)
- [[ML Stage Layering with Typed Contracts]] — extends (the `ml_model` payload's stage architecture)
- [[Toggle Gates the Capability, Not the Runtime Default]] — extends
- [[Changing a Derived Default Is a Migration]] — extends (flipping a `when: false` root default under existing consumers)
- [[Name-Only Sync Guards Miss Content Drift]] — related (the vendored-skill sync guard)
- [[Gate Dependabot Auto-Merge on Branch Protection]] — extends (the CI auto-merge decision)
