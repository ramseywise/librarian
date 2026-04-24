---
name: define-epic
description: Define a new Epic for ROADMAP.md with user story, scope, ADRs, and API/UX design. Use when the user wants to create a new epic, define a feature, or says things like "neues Epic", "definiere E12", or "ich brauche ein Feature für...".
model: opus
---

Define a new Epic for ROADMAP.md. Act as the **Product Owner / Architect** — focus on *what* and *why*, not *how*.

**GitHub Projects sync:** Use the github-projects SKILL for all GraphQL templates and configuration variables.

## Input
- If $ARGUMENTS contains an epic number or feature description, use it as starting point
- If $ARGUMENTS is empty, ask the user what capability they want to add

**Before proceeding, evaluate and present alternatives:**
- **Simpler approach**: config flag, extra field, or small extension instead of a new concept?
- **Extend existing**: existing endpoint, entity, or flow that could be enhanced?
- **Established pattern**: well-known pattern (standard pagination, soft-delete, webhook) that achieves the same with less complexity?
- **Defer or reject**: if effort-to-value ratio is low, say so with reasoning

Present alternatives clearly. Only proceed with the confirmed approach.

## Step 1: Context Gathering
- Read `ROADMAP.md` fully — understand existing epics/milestones, ADRs, and numbering
- Next epic number: scan for `E{n}:` entries; fall back to counting `M{n}:` entries if no epics exist
- Next ADR number: scan for `ADR-XX` entries
- Check open milestones: `gh api repos/{REPO}/milestones --jq '.[] | select(.state == "open") | .title'`
- Flag dependency on incomplete predecessors to the user

## Step 2: User Story & Goal
Formulate: **Goal** (one sentence), **Motivation** (one paragraph), **User Story**.
Present to the user for confirmation before proceeding.

## Step 3: Scope Definition
- **In scope** / **Out of scope** (with brief reason)
- Keep focused — an epic should be achievable in a reasonable sprint

## Step 4: API / UX Design
- Which endpoints are added or changed? (method, path, request/response shape)
- HTTP status codes and error cases?
- If frontend tasks included: what views/interactions?

Present API design to the user before finalizing ADRs.

## Step 5: Architecture Decisions (ADRs)
- One ADR per non-trivial design choice — explain decision and rationale
- Only for decisions not obvious from the code
- Note "supersedes ADR-XX" if applicable; do **not** mark old ADR obsolete yet (that happens in `execute-tasks`)
- Present options to user when multiple valid approaches exist

## Step 6: Task Outline
Plain scope bullets grouped by component (Backend, Frontend, AI Service, etc.) — **no `[ ]` markers**. Keep coarse — `plan-epic` will break them down.

## Step 7: Create Epic Issue + Milestone

### 7a — Create Epic issue
```bash
gh issue create -R {REPO} \
  --title "E{n}: {Short Goal}" \
  --label "epic,{backend|frontend|ai-service|devops}" \
  --body "$(cat <<'EOF'
## Goal
{One-line goal}

## Motivation
{Motivation paragraph}

## Scope
See `docs/epics/E{n}-TASKS.md` for full task breakdown (created by `plan-epic`).
EOF
)"
```

### 7b — Add to project, set Status = Backlog
Use github-projects SKILL: add issue to project (note item ID), then set status to `{STATUS_BACKLOG}`.

### 7c — Create Milestone
```bash
gh api repos/{REPO}/milestones \
  --method POST \
  -f title="E{n}: {Short Goal}" \
  -f description="{One-line goal}"
```

Report Epic issue URL and Milestone URL to the user.

## Output
- Append new epic to `ROADMAP.md` under `## Epics` (create section if needed, after `## Milestones`)
- Structure: Goal, Motivation, Architecture Decisions, Scope by component (plain bullets)
- Preserve all existing content
- TASKS file `docs/epics/E{n}-TASKS.md` is created by `plan-epic`

## Rules
- Every ADR must explain *why*, not just *what*
- No duplicate tasks from existing epics unless dependency is explicit
- Keep epic focused on a single coherent goal
- Ask when trade-offs exist — no silent product decisions
- All content in ROADMAP.md must be in English
