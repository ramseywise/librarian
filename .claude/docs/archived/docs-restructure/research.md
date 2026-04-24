# Research: `.claude/docs/` Structure Refactor
 
**Date:** 2026-04-14
**Status:** Decisions locked — ready to plan
**Confidence:** High (based on full inventory + cross-reference analysis of 32 docs)
**Branch:** `cord/refactor-docs-structure-4182e9`
 
## Problem
 
The current `.claude/docs/` structure organizes artifacts by type (`research/`, `plans/`, `reviews/`) rather than by topic. This causes three concrete failures:
 
1. **Reviews don't feed back into plans.** Two reviews flagged issues ("Needs changes") that were never incorporated into their corresponding plans. The `/code-review` skill is terminal — no iteration mode, no mechanism to route findings back.
2. **Research gets disconnected from the plans it scopes.** Six research docs are orphaned — no plan was ever written against them. One plan-type doc is misclassified under `research/`.
3. **The INDEX.md can't keep up.** Six broken paths, references to nonexistent `archived/` directories, stale status markers. The flat index tries to manually track relationships that directory structure should enforce.
 
## Current State Inventory
 
### Relationship map (what's connected)
 
```
research/infrastructure/terraform-restructure.md
    → plans/terraform-restructure.md
    → plans/backlog/github-cicd-pipeline.md (§ 4)
 
research/infrastructure/ts-copilot-service.md
    → plans/backlog/ts-copilot-upgrades.md
 
research/librarian/librarian-vs-bedrock-kb.md
    → plans/orchestration-rollout.md
    → plans/librarian/librarian-prod-hardening.md
 
research/librarian/librarian-vs-google-adk-orchestration.md
    → plans/orchestration-rollout.md
 
plans/orchestration-rollout.md
    → reviews/orchestration-rollout.md (VERDICT: needs changes — 3 BLOCKING)
 
plans/librarian/librarian-hardening.md
    → reviews/librarian_hardening.md (VERDICT: needs changes — 2 non-blocking)
 
plans/langgraph-adk-compatibility.md
    → plans/librarian-rag-upgrade.md (depends on; supersedes ADK section)
 
research/agents/research-agent-refactor.md → plans/agents/research-agent-refactor.md
research/agents/visualizer-improvements.md → plans/agents/visualizer_improvements.md
plans/librarian/retrieval_pipeline_productionize.md ↔ plans/infrastructure/triage_infra_security_fixes.md
plans/backlog/ts-copilot-upgrades.md ↔ plans/backlog/py-copilot-service.md
```
 
### Disconnected artifacts
 
| File | Issue |
|------|-------|
| `research/agents/infra_support.md` | No plan written — listen-wiseer recommender scoping |
| `research/librarian/rag-agent-template.md` | Fed a plan that was merged into `librarian-rag-upgrade.md`; research link lost |
| `research/librarian/rag-tradeoffs.md` | Evergreen decision log — no single plan consumer |
| `research/librarian/librarian-stack-audit.md` | Architectural reference — no plan consumer |
| `research/tooling/codebase-deduplication.md` | D3+ findings open, no plan queued |
| `research/tooling/skills-workflow-audit.md` | Findings actionable, no plan written |
| `reviews/rag_core_infra_improvements.md` | Orphaned — no matching plan exists |
| `research/librarian/librarian-architecture-tradeoffs.md` | Misclassified — header says "Plan:", lives in research/ |
| `plans/librarian/librarian-restructure.md` | Self-declared superseded, still in active directory |
 
### The workflow gap
 
The CLAUDE.md workflow defines iterate phases for research (1a) and planning (2a), but review (Phase 4) is terminal:
 
| Phase | Has iteration? | Skill subcommands |
|-------|---------------|-------------------|
| 1. Research | Yes (1a) | `review`, `refine`, `argue` |
| 2. Plan | Yes (2a) | `review`, `refine` |
| 3. Execute | N/A | — |
| 4. Review | **No** | None — write and stop |
 
The one review that closed the loop (`rag_core_infra_improvements`) did so ad-hoc by embedding a "Post-review fixes applied" section in the review itself. The workflow didn't support this — the reviewer improvised.
 
## Proposed Structure: Scope / Build / Archive
 
Group by **lifecycle phase and topic**, not by artifact type:
 
```
.claude/docs/
  scope/<topic>/              # Discovery + scoping (stays live through review)
    research.md               # Primary analysis / decision support
    research-<aspect>.md      # Additional research if topic is broad
  build/<topic>/              # Active implementation + verification
    plan.md                   # Implementation spec (cites scope/ research)
    review.md                 # Fidelity review (cites plan)
  build/backlog/<topic>/      # Blocked or deferred work
    plan.md
  reference/                  # Evergreen docs without a specific build target
    <name>.md                 # Stack audits, decision logs, architecture refs
  archive/<topic>/            # Cascade-archived when review resolves
    scope/                    # (scope files moved here)
    build/                    # (build files moved here)
  sessions/                   # Unchanged — session handoff notes
  INDEX.md                    # Updated to reflect new layout
```
 
### How the lifecycle flows
 
```
                    ┌──────────────────────────────┐
                    │        scope/<topic>/         │◄── stays live until review
                    │  research.md(s)               │    resolves (not at plan)
                    │  /research-review iterate     │
                    └───────────┬──────────────────┘
                                │ research complete (scope remains)
                                ▼
                    ┌──────────────────────────────┐
                    │        build/<topic>/         │
                    │  plan.md (cites scope)        │
                    │  /plan-review iterate         │
                    │  /execute-plan                │
                    │  /code-review → review.md     │
                    │  review findings → plan.md    │◄── NEW feedback loop
                    └───────────┬──────────────────┘
                                │ review Approved (or findings resolved)
                                ▼
                    ┌──────────────────────────────┐
                    │       archive/<topic>/        │◄── CASCADE: scope + build
                    │  scope/ + build/ moved here   │    archive together
                    └──────────────────────────────┘
```
 
### Key design decisions
 
**D1: Topic as the grouping unit.** A topic like `orchestration-rollout` keeps its research, plan, and review together. No more cross-referencing across `research/librarian/`, `plans/`, and `reviews/` by filename convention.
 
**D2: Scope vs. Build separates intent.** Scope answers "what should we build and why?" Build answers "how do we build it and did we build it right?" This matches the user's mental model of scoping plans vs. implementation plans.
 
**D3: Reference folder for evergreen docs.** Some docs don't scope a specific build topic — they're standing references (stack audits, tradeoff logs, decision registers). These don't fit the scope→build lifecycle. Examples: `rag-tradeoffs.md`, `librarian-stack-audit.md`.
 
**D4: Archive = all three artifacts present.** A topic reaches `archived/` only when all three exist: `scope/<topic>/research.md` + `build/<topic>/plan.md` + `build/<topic>/review.md` AND the review verdict is Approved (or all blocking findings resolved). Archive is a single cascade: `scope/<topic>/` and `build/<topic>/` move together into `archived/<topic>/`. No information loss. Legacy items in `archived/` that predate this workflow are marked "legacy" in INDEX.md.
 
**D5: One-to-many scope→build is the expected pattern.** Scope topics are intentionally broader than build topics — a single scope (e.g., `librarian-architecture`) feeds multiple build topics. Build plans cite specific sections of scope research. Topic names naturally diverge as scope splits into implementation work. Confirmed: do not force 1:1.
 
**D6: Backlog is a top-level folder.** Blocked or deferred plans live in `backlog/<topic>/plan.md`. Top-level keeps backlog clearly separate from active build work and scope research. Active build work is in `build/<topic>/` — no status marker needed.
 
**D7: Scope stays live until all three artifacts exist.** Scope is reference material during execution. It only archives when the full cycle is complete (D4 trigger). Scope never archives ahead of its build.
 
### What changes about the workflow
 
1. **`/code-review` gets a feedback loop.** After writing `review.md`, if verdict is "Needs changes," the skill appends a `## Review Findings` section to `plan.md` with each finding and its status (open/addressed/deferred/won't-fix). This could be:
   - **Option A: Convention in CLAUDE.md** — cheapest, relies on discipline
   - **Option B: Skill enhancement** — `/code-review` automatically appends findings to plan.md when verdict != approved
   - **Option C: Hook** — PostToolUse hook on review file creation triggers plan update
 
   **Recommendation: Option B.** The skill already reads the plan during review — it can write back. A hook is too broad (fires on every write). A convention is too easy to skip (see: 2 reviews that didn't).
 
2. **`/research-review` creates under `scope/<topic>/`.** Instead of `research/<subdomain>/<name>.md`, the output goes to `scope/<topic>/research.md`.
 
3. **`/plan-review` creates under `build/<topic>/`.** Instead of `plans/<subdomain>/<name>.md`, the output goes to `build/<topic>/plan.md`.
 
4. **Archive is a deliberate action.** Either manual or a new `/archive-topic <topic>` command that moves scope + build folders into archive.
 
### Migration mapping
 
Current path → Proposed path for every file:
 
**Well-connected pairs (scope + build):**
 
| Current | Proposed |
|---------|----------|
| `research/infrastructure/terraform-restructure.md` | `scope/terraform-restructure/research.md` |
| `plans/terraform-restructure.md` | `build/terraform-restructure/plan.md` |
| `plans/backlog/github-cicd-pipeline.md` | `build/backlog/github-cicd-pipeline/plan.md` |
| `research/infrastructure/ts-copilot-service.md` | `scope/ts-copilot/research.md` |
| `plans/backlog/ts-copilot-upgrades.md` | `build/backlog/ts-copilot/plan.md` |
| `plans/backlog/py-copilot-service.md` | `build/backlog/py-copilot/plan.md` |
| `research/librarian/librarian-vs-bedrock-kb.md` | `scope/librarian-architecture/research-bedrock-kb.md` |
| `research/librarian/librarian-vs-google-adk-orchestration.md` | `scope/librarian-architecture/research-adk-orchestration.md` |
| `plans/orchestration-rollout.md` | `build/orchestration-rollout/plan.md` |
| `reviews/orchestration-rollout.md` | `build/orchestration-rollout/review.md` |
| `plans/librarian/librarian-prod-hardening.md` | `build/librarian-prod-hardening/plan.md` |
| `plans/librarian/librarian-hardening.md` | `build/librarian-hardening/plan.md` |
| `reviews/librarian_hardening.md` | `build/librarian-hardening/review.md` |
| `research/agents/research-agent-refactor.md` | `scope/research-agent-refactor/research.md` |
| `plans/agents/research-agent-refactor.md` | `build/research-agent-refactor/plan.md` |
| `research/agents/visualizer-improvements.md` | `scope/visualizer-improvements/research.md` |
| `plans/agents/visualizer_improvements.md` | `build/visualizer-improvements/plan.md` |
 
**Build-only (no research, based on codebase inspection):**
 
| Current | Proposed |
|---------|----------|
| `plans/infrastructure/triage_infra_security_fixes.md` | `build/infra-security-triage/plan.md` |
| `plans/librarian/retrieval_pipeline_productionize.md` | `build/retrieval-pipeline-prod/plan.md` |
| `plans/langgraph-adk-compatibility.md` | `build/langgraph-adk-compat/plan.md` |
| `plans/librarian-rag-upgrade.md` | `build/librarian-rag-upgrade/plan.md` |
| `plans/agents/mvp-feedback-evaluation.md` | `build/mvp-feedback-eval/plan.md` |
 
**Research-only (no plan yet → stays in scope, or move to reference):**
 
| Current | Proposed | Rationale |
|---------|----------|-----------|
| `research/agents/infra_support.md` | `scope/listen-wiseer-agents/research.md` | Active scoping, no plan yet |
| `research/librarian/rag-agent-template.md` | `scope/rag-agent-template/research.md` | Fed merged plan; re-link needed |
| `research/tooling/codebase-deduplication.md` | `scope/codebase-dedup/research.md` | Open items, plan expected |
| `research/tooling/skills-workflow-audit.md` | `scope/skills-audit/research.md` | Actionable findings, plan expected |
 
**Evergreen references:**
 
| Current | Proposed |
|---------|----------|
| `research/librarian/rag-tradeoffs.md` | `reference/rag-tradeoffs.md` |
| `research/librarian/librarian-stack-audit.md` | `reference/librarian-stack-audit.md` |
 
**Needs reclassification or archival:**
 
| Current | Action |
|---------|--------|
| `research/librarian/librarian-architecture-tradeoffs.md` | Move to `build/librarian-architecture/plan.md` (it's a plan) |
| `plans/librarian/librarian-restructure.md` | Move to `archive/librarian-restructure/plan.md` (superseded) |
| `reviews/rag_core_infra_improvements.md` | Move to `archive/rag-core-infra/review.md` (orphaned) |
 
## Decisions (formerly Open Questions)
 
**Q1 → RESOLVED: 1:m scope→build.** Scope topics are intentionally broader. Terraform research feeding both terraform-restructure and github-cicd-pipeline is the expected pattern, not an edge case. Build plans cite the relevant scope by path. See D5.
 
**Q2 → RESOLVED: Scope stays live; cascades to archive with build.** Scope is reference during execution. Archive is a single cascade action triggered when the topic's review reaches `Approved` or all blocking findings are incorporated. See D7.
 
**Q3: Naming convention for topics.** Kebab-case matching current file naming: `scope/terraform-restructure/`, `build/orchestration-rollout/`. No change needed — current convention holds.
 
**Q4 → RESOLVED: Skill enhancement (Option B).** `/code-review` appends a `## Review Findings` section to `plan.md` when verdict != approved. Hook rejected (too noisy). Convention rejected (proven unreliable by 2 existing reviews). See D1 in "What changes about the workflow."
 
**Q5: `sessions/` stays put.** Sessions are per-date, not per-topic. No change.
 
## Verdict
 
The scope/build/archive model is a clear improvement over the current artifact-type grouping. It solves the three concrete failures identified: review feedback loop, research-plan coupling, and index maintainability. The migration is mechanical — every file has a clear destination.
 
The biggest value-add beyond restructuring is closing the review feedback loop (D1 in "What changes about the workflow"). Without this, the new structure would just be a prettier version of the same disconnection problem.
 
Search files...
