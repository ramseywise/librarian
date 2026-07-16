---
title: Claude Workflow System
tags: [context-management, llm, pattern]
summary: Personal Claude Code harness — global skills, PreCompact hook, phase checkpoints, and session notes — that automates context management across multi-phase engineering workflows.
updated: 2026-07-14
sources:
  - raw/sessions/claude-2026-04-11-i-want-to-refactor-this-insights-skill-f-394ba556.md
  - raw/sessions/claude-2026-04-14-key-insights-re-claude-docs-restructurin-a6a9bcf4.md
  - raw/sessions/claude-2026-04-22-the-user-just-ran-insights-to-generate-a-198e7d2c.md
  - raw/claude-docs/_user/CLAUDE.md
  - raw/sessions/claude-2026-07-13-btw-i-think-we-do-not-have-claude-settin-a3b6ecb6.md
  - raw/sessions/claude-2026-07-06-can-we-reconcile-this-with-the-other-set-012cfada.md
  - raw/sessions/claude-2026-07-13-please-analyze-this-codebase-and-create-dfcde495.md
  - raw/sessions/claude-2026-07-14-can-we-run-the-ingestion-from-github-lib-63940e32.md
  - raw/claude-skills/README.md
  - raw/claude-skills/java/microprofile-backend.md
  - raw/claude-skills/web-components/frontend.md
  - raw/claude-docs/_user/commands/clean_memory.md
  - raw/claude-docs/_user/commands/end_session.md
  - raw/claude-docs/_user/commands/start_session.md
  - raw/claude-docs/_user/commands/insights.md
  - raw/claude-docs/_user/commands/consolidate.md
  - raw/claude-docs/project-g/skills/knowledge-creation/claude-insights/SKILL.md
  - raw/claude-docs/project-g/skills/knowledge-creation/knowledge-share/SKILL.md
  - raw/claude-docs/project-g/skills/knowledge-creation/skill-creator/SKILL.md
  - raw/claude-docs/project-g/skills/knowledge-creation/sync-sessions/SKILL.md
  - raw/claude-docs/project-g/skills/planning/define-milestones/SKILL.md
  - raw/claude-docs/project-g/skills/planning/design-sprint/SKILL.md
  - raw/claude-docs/project-g/skills/planning/doc-to-linear-tickets/SKILL.md
  - raw/claude-docs/project-g/skills/planning/linear-spike/SKILL.md
  - raw/claude-docs/project-g/skills/planning/scope-initiative/SKILL.md
  - raw/claude-docs/project-g/skills/planning/execute-tasks/SKILL.md
  - raw/claude-docs/project-g/skills/planning/github-projects/SKILL.md
  - raw/claude-docs/project-g/skills/workflow/akira/SKILL.md
  - raw/claude-docs/project-g/skills/workflow/code-debug/SKILL.md
  - raw/claude-docs/project-g/skills/workflow/compact-session/SKILL.md
  - raw/claude-docs/project-g/skills/workflow/prototype/SKILL.md
  - raw/claude-docs/project-g/skills/workflow/quick-commit/SKILL.md
  - raw/claude-docs/project-g/skills/workflow/quick-pr/SKILL.md
  - raw/claude-docs/project-g/skills/workflow/review-pr/SKILL.md
  - raw/claude-docs/listen-wiseer/skills/code-refactor/SKILL.md
  - raw/claude-docs/listen-wiseer/skills/code-test/SKILL.md
  - raw/claude-docs/listen-wiseer/skills/code_debug.md
  - raw/claude-docs/listen-wiseer/skills/code_execute.md
  - raw/claude-docs/listen-wiseer/skills/code_pr.md
  - raw/claude-docs/listen-wiseer/skills/code_refactor.md
  - raw/claude-docs/listen-wiseer/skills/code_review.md
---

# Claude Workflow System

## What It Is

A personal Claude Code harness built around `~/.claude/` that manages context, skills, and session continuity across multi-phase engineering work. The system enforces a research → plan → execute → review pipeline using [[SKILL.md Pattern|skills]] and a [[Prefix Caching|PreCompact]] hook.

## Components

### Global Skills (`~/.claude/skills/`)

22 skills auto-discovered in every project. Split by role:

| Category | Skills |
|----------|--------|
| Pipeline | research-review, plan-review, execute-plan, code-review |
| Session | compact-session, quick-pr, quick-commit |
| Product | define-epic, plan-epic, execute-tasks, github-projects |
| Tech domain | langgraph, mcp-builder, prototype, adk-python |

Tech-domain skills are grounded in this wiki (see [[SKILL.md Pattern]]). Pipeline skills live directly in `~/.claude/skills/`.

### PreCompact Hook (`~/.claude/hooks/pre-compact.sh`)

Fires on every context compaction (manual or auto-triggered). Reads the JSONL transcript to count tokens, detects the current phase from recent skill invocations, and writes a checkpoint note to `~/.claude/sessions/`.

This ensures no session context is lost on compact, even without explicit `/compact-session` calls.

### Phase Checkpoint Pattern

Each phase skill calls `/compact "phase: X → Y"` at handoff. The `custom_instructions` field is picked up by the PreCompact hook to label the snapshot.

```
research-review  →  /compact "phase: research → plan"
plan-review      →  /compact "phase: plan → execute"
execute-plan     →  /compact "step N: <title>"        (per step)
execute-plan     →  /compact "phase: execute → review"
code-review      →  /compact "phase: review → done"
```

### Session Notes (`~/.claude/sessions/`)

All session notes are centralised here — not project-relative. Sources:
- PreCompact hook (every compact)
- `/compact-session` (explicit end-of-session)
- `uv run python -m tools.cartographer --migrate` (batch migrate JSONL → skeleton notes)

**`/compact-session` — operational detail.** Detects mid-session (steps 1–4, then `/compact` with a seed prompt) vs. end-of-session (steps 1–5, then stop) from context. Step 0 classifies the session into three front-matter fields before writing the note: `work_type` (one of `debug`/`feature`/`refactor`/`review`/`planning`/`research`/`config`/`chat`), `output_type` (`pr`/`plan_doc`/`code_change`/`decision`/`wiki_page`/`analysis`/`config_change`/`none`), and `key_output` (one short phrase — a file path, PR title, or decision made). The note itself is a YAML-fronted markdown file with Position/Metadata/Gotchas/Friction signals/Attribution notes/Open questions/Skill candidates/Session insights/Next session prompt sections — the "Next session prompt" is deliberately 3–5 sentences so a cold session can resume without re-reading `PLAN.md`. **Memory-write gate** (end of session only): save a memory entry only if the fact is non-obvious and would change future behavior — the test is "would a cold session make a worse decision without this?" — split into `user` (role/preferences), `project` (non-obvious decisions/constraints not in code or git), and `reference` (pointers to external system locations) types; code patterns, git history, debugging solutions, and anything already in `CLAUDE.md` are explicitly excluded. **Branch/commit rule:** commit to the current branch if already on a feature/fix branch; if on `main`/`master`/`cord`, create `session/{YYYY-MM-DD}-{slug}` first. A PR is opened only at end-of-session, and is skipped outright if tests are failing, if `skill_candidates > 2` (skill generation still pending), if the user declines, or for any mid-session checkpoint (checkpoints never open a PR).

### Project-Local Session State (`.claude/docs/SESSION.md`)

A second, complementary artifact — distinct from the centralised `~/.claude/sessions/` checkpoint notes above. `SESSION.md` lives **inside the current project directory** and tracks the "current position" of an in-progress multi-session task (step number, test count, gotchas, open questions, next-session prompt) — it is the project-relative counterpart to `PLAN.md`/`RESEARCH.md` in the same `.claude/docs/` gitignored-artifact family, not a replacement for the global session-note pipeline.

Three commands operate on it:

| Command | When | What it does |
|---|---|---|
| `/start_session` | Session kickoff | Reads `SESSION.md` + `CLAUDE.md`; outputs current position, active gotchas, next action, and a token-usage reminder (`/compact` at 40%). Explicitly does **not** read `PLAN.md`/`RESEARCH.md` unless `SESSION.md` flags something blocked — keeps kickoff terse |
| `/end_session` | Session close | Updates position/token log/gotchas/open-questions in `SESSION.md`; rewrites the "next session prompt" (3–5 lines of must-know context so a cold session can resume without reading `PLAN.md`); marks completed `PLAN.md` steps ✓ DONE; flags anything worth promoting to memory |
| `/clean_memory` | Periodic hygiene | Audits `~/.claude/projects/<slug>/memory/` for stale project state, redundant/duplicate feedback, and decisions that now contradict `CLAUDE.md`; applies approved deletions/merges and rewrites the `MEMORY.md` index. Also sweeps project `.claude/docs/` for completed `RESEARCH.md`/`PLAN.md`/`CHANGELOG.md`/`EVAL.md` (gitignored throwaway artifacts, deleted once merged) |

This is consistent with the "no project-relative memory" decision below — `SESSION.md` is project-relative by design (it tracks *this project's* current position), while durable `MEMORY.md` facts stay centralised at `~/.claude/projects/<slug>/memory/` so they aren't git-committed and survive across projects.

### `/claude-insights` — Operational Detail

Expands on the "Session" skill row above. `/insights` runs `python3 ~/.claude/scripts/insights.py` (requires `ANTHROPIC_API_KEY`; the command aborts with a one-line instruction if unset), then opens `~/.claude/usage-data/report.html`. Options: `--dry-run` (stats only, prints JSON, no API call), `--model` (default `claude-opus-4-5`, can downshift to a cheaper/faster model), `--output` (custom report path). Before running, the command loads `.claude/skills/insights_analysis.md` as the interpretation framework for reviewing the generated report with the user — i.e. the analysis lens is itself a versioned skill, not ad hoc.

**Cartographer source-routing (which data backs which report section):** session notes (`.claude/sessions/*.md`, written by `/compact-session`) are the canonical, portable source — they work on any machine and capture qualitative context JSONL never can; per-machine JSONL transcripts are supplementary quantitative enrichment only. Four source-availability modes: notes+JSONL → notes primary + JSONL enrichment; notes-only → works standalone (e.g. on a machine with no local JSONL history); JSONL-only → run `--migrate` first to backfill notes; neither → error. **Implication: always end sessions with `/compact-session`** — the report is only as good as the notes written. Three other cartographer flags close the loop: `--migrate` (JSONL → skeleton session notes, quantitative fields filled automatically, qualitative fields left as placeholders to hand-fill), `--cron` (reads notes + a `PostToolUse`-hook-written `.claude/friction-log.jsonl`; outputs a dated markdown report plus a GENERATE/SKIP/MERGE verdict on skill candidates, auto-writing approved ones to `.claude/skills/`), `--compare` (diffs JSONL vs. notes per date to catch note-taking gaps — did the note capture gotchas/attribution/skill candidates that the raw transcript shows happened?).

**Signal taxonomy** behind the report's "Friction"/"New Patterns" sections, split into two axes: **context engineering (CE)** — is the right augmentation tool being used (Bash-antipattern count, empty skill-invocation lists, low read/edit ratio, zero hook blocks across sessions, long sessions with no `TodoWrite`, near-zero cache-read tokens, 3+ compacts per session, 3+ unprocessed skill candidates in notes); **prompt engineering (PE)** — are outputs well-scoped (output-tokens/message p75 >800, >3 user interruptions/session, >2 `edit_failed`/`file_not_found` errors, >1 `user_rejected` error, >20% week-over-week input-token growth). Each pattern reported as **signal → interpretation → recommendation (category: Hook/Skill/Condense/Session preference/CLAUDE.md/Settings) → attribution (root cause)**, capped at 3–5 patterns per report.

**`sync-sessions` operationalizes this pipeline end-to-end** from any project: run `cartographer --migrate` → `--enrich` (backfills cost + Haiku-based `work_type`/`output_type`/`key_output` classification, degrading gracefully to cost-only if `ANTHROPIC_API_KEY` isn't set in `librarian/.env`) → `--cron` (sync to `raw/sessions/` + insights analysis), all from the librarian repo regardless of which project triggered it.

### `/skill-creator` — Skill Authoring Loop

The meta-skill for writing and iterating on `SKILL.md` files themselves. Core loop: (1) extract trigger/output intent from conversation history, asking only about gaps; (2) draft `SKILL.md` under ~300 lines, moving long reference content to `references/<topic>.md`; (3) test with 2–3 realistic prompts via background agents, run with-skill vs. without-skill (or old-vs-new) side by side — see [[Skill Eval Pipeline (Blind Comparison + Grading)]] for the three-agent blind-comparison + grading mechanism this step delegates to; (4) iterate from specific feedback ("the table section is missing," not "not quite right"), repeating from step 3.

Two rules worth generalizing beyond this one skill: **frontmatter `description` should be "slightly pushy"** — Claude tends to under-trigger skills, so prefer "use whenever the user mentions X, even if they don't say the word Y" over a bare feature description; and **bundle repeated work into `scripts/`** — if independent test runs each reinvent the same helper, that's the signal to make it a deterministic script instead of regenerated inline code. Resource layout: `SKILL.md` (instructions) / `references/` (on-demand docs) / `scripts/` (executable helpers) / `assets/` (templates). This is the authoring-time counterpart to the [[SKILL.md Pattern]] page's runtime-loading-strategy content — that page covers how a written skill gets loaded into context; this section covers how the skill gets written and tested in the first place.

### `/consolidate` — Code & Architecture Cleanup

A `category: refactor`, `trigger: manual` skill (`name: consolidate`) for code and architecture cleanup passes. The global raw definition is still a title-only stub (`## Usage` with no body), but [[Listen-Wiseer Project]]'s project-local `code_refactor` skill (identical content under both `code-refactor/SKILL.md` and `code_refactor.md` — old vs new naming convention, not two concepts) is a fully-specified instance of the same idea and is the best available reference until `/consolidate` itself is filled in: **quality-driven, not plan-driven** — unlike `/execute-plan`, there is no PLAN.md; the skill reads and understands the code first (map files, trace flow, find patterns — read every file in scope fully before identifying anything), then identifies smells in three impact tiers (**high**: duplicated logic across 3+ blocks, functions >40 lines mixing concerns, nesting >3 levels; **medium**: unclear names, magic numbers, dead code, inconsistent patterns for the same operation; **low**: missing type hints/docstrings, redundant comments), then **proposes every change as `file:line — what and why` and waits for confirmation before touching anything**, then applies one logical change at a time, running the test suite after each and reverting-and-investigating on any failure. Hard rules: no behavior changes (a refactor that reveals a bug gets noted, not fixed, as a separate task), all previously-passing tests must still pass, and touching more than 10 files is itself a signal to stop and escalate to the full research→plan→execute pipeline instead of a `/consolidate`-style pass.

### Skill Pipeline (tech-domain skills)

```
librarian/raw/claude-skills/<name>/<name>.md  ← workshop (grounded in wiki)
         ↓  promote-skill.sh <name>
~/.claude/skills/<name>/SKILL.md              ← active everywhere
```

Skill states tracked in `raw/claude-skills/README.md`: `langgraph/` is promoted (backed by [[LangGraph CRAG Pipeline]], [[LangGraph Advanced Patterns]], [[Production Hardening Patterns]]); `google-adk/` is workshop (promote when building ADK agents); `fastapi/` is a stub not yet written.

### Archived Reference Skills (Different Stack, Out of Scope)

Two `claude-skills/` entries are explicitly archived reference material for a different tech stack, not part of the active agent/RAG design knowledge this wiki tracks — noted here for coverage completeness rather than concept extraction:
- `raw/claude-skills/java/microprofile-backend.md` — Java 25 / MicroProfile / Jakarta EE backend conventions (BCE layering, JAX-RS, CDI, gradle testing strategy).
- `raw/claude-skills/web-components/frontend.md` — vanilla web components frontend conventions (lit-html, Redux Toolkit, Vaadin Router, BCE layering, no-build-step philosophy), based on the `bce.design` quickstarter.

Both apply the same Boundary-Control-Entity (BCE) architectural pattern to their respective stack, mirroring each other across backend/frontend — the only cross-cutting fact worth noting since neither stack otherwise intersects with the LangGraph/ADK/RAG agent-design focus of this wiki.

**The same BCE/Gradle reference stack has its own dev-workflow skill trio**, found (identical byte-for-byte) in the project-g, playground, and playground-global skill directories — confirming they are copied template files, not project-g-authored: `execute-tasks` (works a `docs/epics/{ID}-TASKS.md` file top to bottom, trunk-based direct-commit by default or one git worktree per independent task group for parallel execution, `./gradlew compileJava compileTestJava` as the verification gate, closes the GitHub milestone and flips `ROADMAP.md` "Scope" sections to "Delivered" when all tasks land), `github-projects` (GraphQL template library for GitHub Projects V2 — item-ID lookup, status/iteration field mutation, sub-issue linking — read from a `GitHub Project Integration` section in `CLAUDE.md`; every mutation is best-effort, appending `|| true` so a sync failure never blocks the actual work), and `review-pr` (PR review gated on the same BCE layering + task acceptance criteria + `./gradlew test`, capped at 3 review rounds before escalating to the user). Noted here for skill-inventory completeness alongside the microprofile-backend/frontend pair above — out of scope for this wiki's agent/RAG focus, and superseded within project-g itself by the Python/`uv`/Linear-VIR-ticket pipeline documented in [[project-g Dev Hooks & Git Workflow]].

## Evolution

The system was iteratively developed April 2026:
- **2026-04-10 to 04-14**: `.claude/docs` restructuring — research→plan chain pattern identified; lifecycle model (in-progress / archive / backlog) established
- **2026-04-14**: `a6a9bcf4` — key insight: reviews were disconnected; `/code-review` had no iteration mode; feedback loop from review → plan formalized
- **2026-04-22**: `198e7d2c` — `/claude-insights` skill created; doc-to-linear-tickets skill added
- **2026-04-26**: PreCompact hook wired; phase checkpoints added to all four phase skills; session notes centralised

## Key Design Decisions

- **No project-relative memory**: memory lives at `~/.claude/projects/<slug>/memory/`, not `<repo>/.claude/memory/`, to avoid git-committing private notes
- **PreCompact not Stop hook**: compaction checkpoints fire on compact (context boundary), not on every response — avoids noise
- **500k token gate**: stubbed in hook, not yet enforced — can be activated by uncommenting the threshold constant

## Current Global Skills (as of 2026-07-06)

Full skill inventory from `~/.claude/CLAUDE.md`:

| Category | Skill | What it does |
|---|---|---|
| Session/git | `/compact-session` | Checkpoint: save artifacts, note, memory, commit + push + PR |
| Session/git | `/quick-pr` | Stage → commit → push → draft PR |
| Session/git | `/quick-commit` | Stage → commit (no push) |
| Session/git | `/claude-insights` | HTML report from session notes + JSONL |
| Discovery | `/research-review` | Research phase: write `.claude/docs/research/{name}.md` |
| Discovery | `/plan-review` | Planning phase: write `.claude/docs/plans/{name}.md` |
| Discovery | `/plan-refactor` | Plan a refactor before executing |
| Dev execution | `/execute-plan` | Step through active plan, append to `CHANGELOG.md` |
| Dev execution | `/code-review` | Write `.claude/docs/reviews/{name}.md` + PR |
| Dev execution | `/review-pr` | Review an open PR |
| Dev execution | `/code-debug` | Diagnose and fix a bug |
| Product/Linear | `/define-milestones` | Define milestones: goal, success metrics, initiative list |
| Product/Linear | `/design-sprint` | Ideate: HMW → workstreams → named initiatives |
| Product/Linear | `/scope-initiative` | Initiative → backward mapping, task backlog, Linear hierarchy |
| Product/Linear | `/doc-to-linear-tickets` | Push planning doc into Linear issues |
| Product/Linear | `/linear-spike` | Create a time-boxed spike/investigation ticket |
| Product/Linear | `/execute-tasks` | Step through task list, mark done |
| Product/Linear | `/github-projects` | Manage GitHub Projects V2 |
| Tech domain | `/langgraph` | State design, node/edge patterns, HITL, checkpointing |
| Tech domain | `/prototype` | Rapid prototype: skip tests, skip polish, just build |
| Tech domain | `/mcp-builder` | Build MCP servers (Python FastMCP or Node SDK) |

**`/prototype` — scope and exit.** Relaxes TDD and layering rules deliberately (tests optional, hardcoded values and skipped validation allowed) so the sole goal is answering one stated question ("does this work?", "how does this API behave?") as fast as possible — no refactoring of existing production code as a side effect, and prototype code stays clearly separated (its own directory or explicit "experimental" marking). Exits into one of three outcomes decided with the user: **adopt** (rewrite properly under the full backend/frontend skill rules), **adapt** (refactor the prototype into production), or **discard** — prototype code is never merged directly into a production path.

**Session/git safety rails (`/quick-commit`, `/quick-pr`):** both skills share the same guardrails — never force-push or amend a published commit, never skip hooks (`--no-verify`), never commit `.env`, `*.pem`, `models/*.pkl`, or files over 10 MB, and always show the staged file list before committing. `/quick-commit` derives the branch name from the current branch's ticket ID if present (`feature/lin-{id}-<slug>`) or falls back to a bare `feature/<slug>` when no per-repo type taxonomy applies — the generic counterpart to the type-prefixed convention in [[Branch Naming Convention Pattern]]. `/quick-pr` extends this with push-with-rebase-retry on a rejected push, a PR body templated from `.github/pull_request_template.md` with fields auto-filled from the diff, and an optional immediate squash/merge.

**Product/Linear pipeline detail:** `/design-sprint` runs an IDEO/Stanford d.school HMW sprint in six phases (deconstruct pain points → HMW reframes → named technical solutions per HMW → workstream clustering by role → 5–7 named initiatives with dependencies → an HTML dependency-map artifact) and hands off to `/scope-initiative` per initiative. `/define-milestones` sits one level up — one goal sentence, 2–3 *verifiable* (not activity-based) success metrics, and 2–5 candidate initiatives per milestone; if the candidate initiatives aren't clear yet, it defers to `/design-sprint` first. Both write to `.claude/docs/` and create the corresponding Linear milestone/initiative directly. `/knowledge-share` (project-g-specific instance, not yet in the global skill set) is the adjacent "turn repo state into a stakeholder artifact" skill — Notion page / Google Drive doc / Google Slides deck via MCP, always drafted and confirmed before creation.

**`/scope-initiative` — six-section output:** takes a named, agreed initiative (from `/design-sprint`) and produces a Linear-ready backlog: (1) failure modes & HMWs table, every later task traces to at least one failure mode; (2) research — reusable assets, per-layer libraries, technical unknowns and what each blocks; (3) task backlog — goal, concrete deliverable (never "implement X"), risks, T-shirt size (S <1wk / M 1–2wk / L 2–4wk / XL >sprint); (4) summary table + critical path — week-1 decisions, highest-risk dependency; (5) numbered open questions, each with a named owner; (6) Linear hierarchy — Initiative → Projects → Issues with Given/When/Then acceptance criteria and blocking relationships. Hands off to `/doc-to-linear-tickets` once reviewed.

**`/doc-to-linear-tickets` — sizing, priority, and backlog-ordering discipline:** maps doc size tags to story points (XS=1, S=2–3, M=5, L=8 — flag for breakdown, XL=13 — flag for breakdown) and doc priority tags to Linear priority, capped at **Medium** for "High" doc-priority and **never Urgent** (max is High, reserved for true blockers). Every issue gets a workstream label (created first if missing) and is filed in **Backlog** state, not "To Do". Issues are created in **reverse dependency order** — most-blocked first, least-blocked last — so the resulting backlog naturally sorts with the next actionable issue at the top. Dependencies are referenced by issue name, never by number (numbers change, names don't).

**`/linear-spike` — time-boxed investigation ticket:** distinct from a regular issue — produces a decision or short doc, not production code. Title format `[Spike] <topic> (<timebox>)`; estimate is 1 point per half-day; branch `vir-{id}-spike-{slug}`; findings written to `.claude/docs/research/{slug}.md` as the spike proceeds. Used when the implementation path isn't clear yet — `/research-review` and `/plan-review` both suggest creating one first for exploratory (no-ticket) work.

## Docs Lifecycle Pattern

From `.claude/docs/` conventions:

| Directory | Git-tracked | Purpose |
|---|---|---|
| `research/` | Yes | Permanent knowledge base — architecture decisions, evaluated patterns |
| `tooling/` | Yes | Curated reference for dev tooling |
| `plans/` | No (gitignored) | Local-only implementation specs — delete after execution |
| `reviews/` | No (gitignored) | Local-only code review artifacts — ephemeral |

**Promotion flow:** When a plan is executed, promote key decisions into a `research/` doc and delete the plan file.

## Issue Tracking (Linear ↔ GitHub)

Branch, commit, and PR naming must include `LIN-{id}` for auto-linking:
- Branch: `feature/LIN-123-short-description`
- Commit: `feat(LIN-123): short imperative title`
- PR title: must contain `LIN-123`

Stack: Code → GitHub | Tasks → Linear | Knowledge → Notion

## Commit Style

- Conventional commits: `feat:`, `fix:`, `refactor:`, `docs:`, `chore:`, `session:`, `checkpoint:`
- Title under 60 chars, imperative mood
- Body: why, not what

See [[Claude Code Hook Architecture]] for how hooks enforce commit and code quality automatically.

## Settings Hierarchy Across a Multi-Repo Drive

When working across many repos under one root (e.g. an external drive with `github/<repo>` for each project), permission prompts multiply if every repo has its own disconnected settings. The fix pattern:

- Set the **drive/org root** (e.g. `github/`) as a project-level settings scope with broad, low-risk read/bash permissions — so opening any repo underneath it inherits sane defaults.
- Layer **per-repo `.claude/settings.json`** underneath for repo-specific permissions (build tools, test runners specific to that stack) — same layering as the three-tier settings model in [[project-g Dev Hooks & Git Workflow]] (`~/.claude/settings.json` → `.claude/settings.json` → `.claude/settings.local.json`).
- **Always open Claude Code sessions inside a repo directory** (`github/<repo>`), not at the drive root — permissions and project context are scoped per-directory, and opening at the root loses per-repo specificity.

This generalizes the settings-layering rule already documented for `project-g`: instead of just global vs. one-repo, insert an intermediate "root of all my repos" layer when working across many sibling projects on the same machine/drive.

## Documentation-Gap Friction: Commands Not in the README

A recurring small friction: operational commands (e.g. "how do I run ingest again, and does it also update the wiki index?") get re-asked across sessions because they live only in skill definitions or in the operator's memory, not in the repo's `README.md`. **Mitigation:** whenever a skill's usage pattern gets re-explained in a session, that's the signal to add it to the README, not just answer inline — otherwise the same question resurfaces next session.

## Related Tooling: Akira, SANYI, and Claude Insights Are Different Layers

A clarifying distinction surfaced from a cross-project discussion: these three tools sound similar (all "review the work") but operate at different altitudes:
- **Akira** — a code-quality review agent (`CodeQualityAgent`) — reviews code changes.
- **[[SANYI Change-Contract System]]** — also a code/architecture review discipline, but at the level of *change contracts* (which layers of a system are allowed to change) rather than line-level code quality.
- **`/claude-insights`** — operates one level up from both: it reviews *sessions* (the process of working), not the code produced by them.

The "ralph" concept (a habit of repeatedly asking "why") is cited as the origin of Akira's review posture — asking why a change was made, not just whether it's syntactically fine.

**Akira's three modes** (delegates to `src/akira/`, a LangGraph agent with three subgraphs): **kiyoko** (陰 yin wanderer) reads the current diff mid-session and answers questions in chat — the lightweight, no-artifact mode; **kaneda** (陽 yang scanner) fans out 5 parallel domain subagents over a path and writes a dated findings doc (`src/akira/findings/findings-{date}.md`) — the same parallel-subagent-per-concern discipline as [[Agent Scaffolding Skill Layers]]' L1 factory, applied to review instead of generation; **dao** (道, "the path") triages that findings doc per-item — auto-fixes low-blast-radius findings, reverts any fix that breaks tests, surfaces complex findings for human review, and discards false positives, writing a run summary at the top of the findings file. The kaneda → dao sequence is Akira's version of the generate-then-triage pattern also seen in SANYI's report-then-`--fix` flow, but scoped to code quality rather than change-contract violations.

### `/code-debug` — Debugging Loop

The `/code-debug` skill runs a six-step scientific-debugging loop, tightest at step 3: (1) build a reproducible feedback loop — prefer an existing failing test, then a new regression test at the public interface, then a CLI/HTTP call, then a minimal throwaway harness, then a repeated loop for flaky bugs; the loop must assert the user's actual symptom, not just "doesn't crash"; (2) reproduce and confirm the failure matches the report; (3) form **3+ independent, falsifiable hypotheses** before investigating any — specific claims only ("the loader returns an empty frame when the env var is unset", not "something is wrong with state") — then test the best-ranked one; (4) diagnose by reading failing code in full context and tracing data flow backwards, changing one variable at a time; (5) fix with the minimal behavior-preserving change, explaining root cause before applying it — no adjacent refactoring; (6) verify the original loop plus regression and adjacent tests pass, and remove temporary `[DEBUG-...]`-tagged probes. **Key constraint:** one change at a time — if three things change and it works, the actual cause is unknown. Escalates to `/research-review` → `/plan-review` → `/execute-plan` if the fix needs more than 3 files, or restarts with fresh hypotheses after 3 failed fix attempts.

A project-local instantiation of this skill (`code_debug` in [[Listen-Wiseer Project]], stack-specific commands: `uv run ruff check . --fix`, `git log --oneline -10`) adds one detail worth generalizing: an explicit **cognitive-bias-to-antidote table** for the hypothesis step — confirmation bias (only seeking evidence for the first guess → actively seek disconfirming evidence), anchoring (first explanation becomes the anchor → generate 3+ hypotheses before investigating any), availability (assuming this bug matches a recent one → treat each bug as novel until evidence says otherwise), and sunk cost (30 minutes down one path → ask "if I started fresh, is this still the right path?" every 30 minutes). Also names a debugging-your-own-code trap: your mental model of the code is a guess, not truth — read your own code as if someone else wrote it, since you remember intent, not what actually shipped.

### Listen-Wiseer Generic Dev-Workflow Skill Family

[[Listen-Wiseer Project]] defines its own project-local six-skill family (`code_debug`, `code_execute`, `code_pr`, `code_refactor`, `code_review`, `code_test`) that mirrors this global pipeline one level down — a useful reference instantiation since three of the six add detail this wiki didn't yet have:

- **`code_execute`** (≈ this system's `/execute-plan`): treats a plan step as a strict contract — before touching any file, extract **Files** (the only files that may be touched), **What**, **Snippet** (implement the pattern shown, don't "improve" it), **Test**, and **Done when**; if any are missing, stop and surface a blocker rather than guessing. Ambiguity (a decision the plan didn't make) is a hard stop with a templated `## Blocker: Step [N]` report listing options and consequences — never guessed past. Any departure from the plan, however small, is recorded in `CHANGES.md` under "Deviations from PLAN.md" (what the plan said, what was done, why) — a clean execution has zero deviations, and hiding them (not having them) is the failure mode, not the deviations themselves.
- **`code_review`**: three-tier severity labelling — **[Blocking]** (correctness bug, data-loss risk, security issue, test failure, hard-rule violation — must fix before merge), **[Non-blocking]** (quality issue, missing edge-case test — should fix but doesn't block), **[Nit]** (style/naming preference beyond what the linter enforces). Review dimensions: correctness, code quality (function length, nesting depth, mutable defaults, magic numbers), API/interface stability, plan fidelity (a per-step "Plan said / Code shows / Tests / Status" table when an active plan exists), test coverage, and production readiness (hardcoded secrets, `print()` vs structured logging, TODO tracking). Two reusable test-quality traps called out explicitly: the **fixture-dedup trap** (when code groups/deduplicates by a field, fixtures must use distinct values for that field or they silently collapse to one result) and **graph path coverage** (nodes reachable via multiple routing paths need a test per path, not just isolated node I/O — directly applicable to LangGraph agent graphs). Review discipline: apply equal scrutiny to improvements and regressions, and never bury a real Blocking finding inside a list of Nits to make the review "look balanced."
- **`code_pr`**: generates PR title (imperative, <60 chars, specific) and description from `git diff main...HEAD --stat` + `git log --oneline` + `CHANGELOG.md` + the active plan file — reads every non-obvious changed file rather than inferring from the diff alone. Templated sections (What/Why/How/Testing/Test quality checks/Checklist) are **omitted, not left empty**, when they have nothing non-obvious to say (e.g. no `## How` section if there are no non-obvious implementation decisions) — the same anti-padding discipline as `/execute-plan`'s "implement exactly what's specified."
- **`code_test`**: synthetic-fixtures-only rule (no real files, network calls, or model weights in tests), test-behavior-not-implementation, and a what-to-test/what-not-to-test table (test happy path/empty input/nulls/boundaries/error paths/type contracts; don't test private helpers, framework behavior, or third-party libraries).
- **`code_refactor`** (identical byte-for-byte between the `code-refactor/SKILL.md` and `code_refactor.md` naming variants — old vs new skill-naming convention, not two concepts) — see the `/consolidate` section below, which this content now fills in.

## See Also

- [[SKILL.md Pattern]]
- [[Prefix Caching]]
- [[Karpathy LLM Wiki Pattern]]
- [[Session Log]]
- [[Claude Code Hook Architecture]]
- [[project-g Dev Hooks & Git Workflow]]
- [[SANYI Change-Contract System]]
- [[Puffin Consciousness Development Skills]]
- [[Agent Scaffolding Skill Layers]]
- [[Skill Eval Pipeline (Blind Comparison + Grading)]]
- [[Branch Naming Convention Pattern]]
