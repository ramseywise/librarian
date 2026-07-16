---
title: ADK Scaffold Patterns
tags: [adk, infra, pattern]
summary: Agent Starter Pack CLI patterns for scaffolding ADK agent projects — templates, deployment options, prototype-first workflow, DESIGN_SPEC.md contract, and development phase guidelines.
updated: 2026-07-14
sources:
  - raw/claude-docs/project-g/.agents/skills/adk-scaffold/SKILL.md
  - raw/claude-docs/project-g/.agents/skills/adk-dev-guide/SKILL.md
  - raw/agent-skills/adk-scaffold/SKILL.md
  - raw/agent-skills/adk-dev-guide/SKILL.md
---

# ADK Scaffold Patterns

The `agent-starter-pack` CLI (`uvx`) scaffolds production-ready ADK agent projects with deployment infrastructure, CI/CD, observability, and testing. This page covers the scaffolding workflow, available templates, deployment options, and the development lifecycle.

For deployment details (CI/CD, service accounts, Terraform), see [[ADK Deployment Patterns]]. For evaluation patterns, see [[ADK Eval Guide]].

---

## Requirements Gathering (Before the Spec)

Before drafting `DESIGN_SPEC.md`, gather requirements with a fixed set of always-ask questions, plus conditional follow-ups:

**Always ask:** (1) what problem the agent solves, (2) what external APIs/data sources and auth are needed, (3) safety constraints — what the agent must NOT do, (4) deployment preference (prototype-first recommended, or full deployment — and if so, Agent Engine or Cloud Run).

**Ask based on context:** if retrieval/search is mentioned → datastore choice (`vertex_ai_search` vs `vertex_ai_vector_search`) via `--agent agentic_rag --datastore <choice>`; if the agent should be callable by other agents → `--agent adk_a2a`; if full deployment chosen → CI/CD runner (GitHub Actions vs Cloud Build); if Cloud Run chosen → session storage type; if CI/CD chosen → whether a git repo already exists or needs creating (and visibility).

## DESIGN_SPEC.md — The Primary Contract

**Before writing any code**, write a `DESIGN_SPEC.md`. This is the source of truth for all implementation decisions.

Required sections:
```markdown
## Overview
2-3 paragraphs describing the agent's purpose and how it works.

## Example Use Cases
3-5 concrete examples with expected inputs and outputs.

## Tools Required
Each tool with purpose, API details, and authentication needs.

## Constraints & Safety Rules
Specific rules — not just generic statements.

## Success Criteria
Measurable outcomes for evaluation.

## Edge Cases to Handle
At least 3-5 scenarios the agent must handle gracefully.
```

**The spec is your contract.** All implementation decisions align with it.

---

## Prototype-First Pattern (Recommended)

Start with `--prototype` to skip CI/CD and Terraform. Focus on getting the agent working first, then add deployment later:

```bash
# Step 1: Create a prototype
uvx agent-starter-pack create my-agent --agent adk --prototype -y

# Step 2: Iterate on agent code (make playground, make eval)

# Step 3: Add deployment when ready
uvx agent-starter-pack enhance . --deployment-target agent_engine -y
```

**Why prototype-first:** Scaffolding with CI/CD and Terraform before the agent behavior is validated creates unnecessary overhead. The `enhance` command adds infrastructure incrementally.

---

## Creating a New Project

```bash
uvx agent-starter-pack create <project-name> \
  --agent <template> \
  --deployment-target <target> \
  --region <region> \
  --prototype \
  -y
```

**Project name constraints:** 26 characters or less, lowercase letters, numbers, hyphens only.

**Critical:** Do NOT `mkdir` the project directory before running `create` — the CLI creates it. Pre-creating causes `enhance` mode instead of `create` mode.

### Template Options

| Template | Description |
|---|---|
| `adk` | Standard ADK agent (default) |
| `adk_a2a` | Agent-to-agent coordination (A2A protocol) |
| `agentic_rag` | RAG with data ingestion pipeline |

### Deployment Targets

| Target | Description |
|---|---|
| `agent_engine` | Managed by Google (Vertex AI). Sessions handled automatically. |
| `cloud_run` | Container-based. More control, requires Dockerfile. |
| `none` | No deployment scaffolding. Code only. |

### Key Create Flags

| Flag | Default | Description |
|---|---|---|
| `--agent` / `-a` | `adk` | Agent template |
| `--deployment-target` / `-d` | `agent_engine` | Deployment target |
| `--region` | `us-central1` | GCP region |
| `--prototype` / `-p` | off | Skip CI/CD and Terraform |
| `--cicd-runner` | `skip` | `github_actions` or `google_cloud_build` |
| `--datastore` / `-ds` | — | `vertex_ai_search` or `vertex_ai_vector_search` |
| `--session-type` | `in_memory` | `in_memory`, `cloud_sql`, `agent_engine` |
| `--auto-approve` / `-y` | off | Skip confirmation prompts |
| `--agent-directory` / `-dir` | `app` | Agent code directory name |
| `--agent-guidance-filename` | `GEMINI.md` | Use `CLAUDE.md` or `AGENTS.md` for other IDEs |
| `--skip-checks` / `-s` | off | Skip GCP/Vertex AI verification checks |
| `--google-api-key` / `-k` | — | Use Google AI Studio instead of Vertex AI |
| `--debug` | off | Enable debug logging for troubleshooting |

**RAG/search:** if retrieval or data search is required, use `--agent agentic_rag --datastore <choice>`:
- `vertex_ai_vector_search` — embeddings, similarity search
- `vertex_ai_search` — document search, search engine

**A2A:** if agent should be available to other agents, use `--agent adk_a2a`.

---

## Enhancing an Existing Project

```bash
uvx agent-starter-pack enhance . \
  --deployment-target <target> \
  -y
```

Run from inside the project directory. Enhance creates new files (`.github/`, `deployment/`, `tests/load_test/`, etc.) that need to be committed.

### Enhance Flags (additional)

| Flag | Description |
|---|---|
| `--name` / `-n` | Project name for templating (default: directory name) |
| `--base-template` / `-bt` | Override base template (e.g. `agentic_rag` to add RAG) |
| `--dry-run` | Preview changes without applying |
| `--force` | Force overwrite all files (skip smart-merge) |

**Agent directory gotcha:** if agent code lives outside `app/`, pass `--agent-directory <dir>`. Getting this wrong causes enhance to miss or misplace files.

### Common Enhance Workflows

```bash
# Add deployment to prototype
uvx agent-starter-pack enhance . --deployment-target agent_engine -y

# Add CI/CD pipeline (ask user: GitHub Actions or Cloud Build?)
uvx agent-starter-pack enhance . --cicd-runner github_actions -y

# Add RAG with data ingestion
uvx agent-starter-pack enhance . --base-template agentic_rag --datastore vertex_ai_search -y

# Preview what would change
uvx agent-starter-pack enhance . --deployment-target cloud_run --dry-run -y
```

---

## Development Lifecycle (Four Phases)

### Phase 1: Understand the Spec
Read `DESIGN_SPEC.md` thoroughly. Identify core capabilities, constraints, success criteria.

### Phase 2: Build and Implement
```bash
make playground  # or: adk web .
```
Iterate on implementation. Use the interactive web UI for testing. Consult [[ADK Python API Reference]] for API patterns.

### Phase 3: Evaluate (Most Important)
```bash
make eval  # or: adk eval <agent_dir> <evalset>
```
Start with 1-2 eval cases. Iterate until quality thresholds are met. Expect 5–10+ iterations. See [[ADK Eval Guide]] for criteria selection.

**Tests (`pytest`) are NOT evaluation** — they test code correctness, not agent behavior.

### Phase 4: Deploy
```bash
make deploy  # requires explicit human approval
```
**Never deploy without explicit human approval.**

---

## Scaffold as Reference

When you need specific infrastructure files but don't want to scaffold the current project, create a temporary reference project:

```bash
uvx agent-starter-pack create /tmp/ref-project \
  --agent adk \
  --deployment-target cloud_run \
  --cicd-runner github_actions \
  -y
```

Inspect generated files, adapt what you need, copy into actual project. Delete the reference project when done. Useful for non-standard project structures or cherry-picking specific files (Terraform, CI/CD workflows, Dockerfile).

---

## Make Commands Reference

| Make command | ADK CLI equivalent | Purpose |
|---|---|---|
| `make playground` | `adk web .` | Interactive local testing |
| `make test` | `pytest` | Unit and integration tests |
| `make eval` | `adk eval <agent_dir> <evalset>` | Run evaluation against evalsets |
| `make lint` | `ruff check .` | Code quality check |
| `make setup-dev-env` | — | Set up dev infrastructure (Terraform) |
| `make deploy` | — | Deploy to dev (requires human approval) |

---

## Operational Guidelines for Coding Agents

**Session continuity:** on long sessions, re-read the relevant skill before each phase (cheatsheet before coding, eval guide before evals, deploy guide before deploying, this scaffold guide before scaffolding) — context compaction may have dropped earlier skill content.

**Code preservation & isolation (Principle 1):** alter only the code segments directly targeted by the request; strictly preserve all surrounding and unrelated code (config values like `model`/`version`/`api_key`, comments, formatting). Before finalizing a code replacement, verify the exact target lines against the user's explicit instructions and confirm nothing outside that target changed.

**Breaking infinite loops:** stop immediately after seeing the same error 3+ times in a row; don't retry failed operations blindly — fix the root cause. Red flags: incrementing lock IDs, names appending v5→v6→v7, repeating "I'll try one more time." For state conflicts (409 already-exists), use `terraform import` instead of retrying creation. For tool bugs, fix the source rather than working around it; when stuck, fall back to running underlying CLIs (e.g. `terraform`) directly instead of a wrapping tool.

**Stale-skills check:** if repeated errors or unexplained gaps appear in skill instructions, run `npx skills check -g` (only when stale skills are suspected, not every session) and tell the user to `npx skills update -g` if it reports outdated skills.

## Critical Rules

- **NEVER change the model** in existing code unless explicitly asked
- **NEVER `mkdir` before `create`** — pre-creating the directory causes wrong CLI behavior
- **NEVER create a Git repo or push to remote** without asking — confirm repo name, visibility, whether user wants it
- **Always ask before choosing CI/CD runner** — don't default silently between GitHub Actions and Cloud Build
- **Agent Engine clears session_type** — if deploying to `agent_engine`, remove any `session_type` setting
- **Project names** must be ≤26 characters, lowercase, letters/numbers/hyphens only

---

## Troubleshooting

**`uvx` not found:** Install `uv`:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Fallback (pip):**
```bash
python -m venv .venv && source .venv/bin/activate
pip install agent-starter-pack
agent-starter-pack create <project-name> ...
```

---

## See Also

- [[ADK Deployment Patterns]]
- [[ADK Eval Guide]]
- [[ADK Python API Reference]]
- [[ADK Context Engineering]]
- [[Production Hardening Patterns]]
