---
name: doc-to-linear
description: >
  Use this skill whenever the user wants to convert a high-level planning document
  such as a workstream overview, initiative breakdown, or product spec into structured
  Linear issues. Triggers include requests like create Linear tickets from this doc,
  turn this into Linear issues, convert this to tickets, push this to Linear, create
  issues for this initiative, or any request to translate written planning content into
  actionable Linear issues. Also use when the user shares a doc with initiatives and
  issues listed and asks to create, populate, or update Linear tickets from it. The
  skill handles parsing the document structure, mapping content to the correct Linear
  fields, inferring dependencies and priority, and creating tickets in the right project
  and team.
---

# Doc to Linear Tickets

## Overview

This skill converts high-level planning documents into structured Linear issues. It handles the full flow: parsing the document, mapping content to Linear fields, creating parent initiatives and child issues, and setting dependencies, priority, and size labels correctly.

## Input formats

The user may provide content in several ways:
- Pasted text directly in the conversation
- A Google Doc (via Google Drive MCP or shared file ID)
- A previously drafted doc from this conversation

Always confirm which section or initiative to convert before creating tickets — documents often contain multiple initiatives and the user may only want one.

## Document parsing

Before creating any tickets, parse the document structure:

1. Identify the **workstream** (top-level grouping, e.g. "HC Data Ingestion")
2. Identify **initiatives** (mid-level groupings, e.g. "Ingest Billy Raw Articles")
3. Identify **issues** (individual tickets within each initiative)
4. For each issue, extract:
   - Title
   - Goal
   - Context
   - Expected Outcome
   - Acceptance Criteria
   - Risks & Uncertainties
   - Dependencies (by issue name, not number)
   - Size tag (XS / S / M / L / XL)
   - Priority tag (Blocker / High / Secondary / V2)

If any field is missing, infer it from context or flag it to the user before creating the ticket.

## Size and priority mapping

Map document size tags to story points as follows. All estimates are for one person.

| Doc tag | Story points | Rationale |
|---------|-------------|-----------|
| XS | 1 SP | Very simple, minimal effort — minor updates, confirmations, access checks |
| S | 2–3 SP | Low complexity — 2 SP if normally less than a day, 3 SP if 1–2 days |
| M | 5 SP | 3–4 working days |
| L | 8 SP | Complex, likely more than a week — flag to user, prefer breaking down |
| XL | 13 SP | Very large or highly uncertain — flag to user, should be broken down if possible |

Note: avoid creating 8 SP and 13 SP issues where possible. If a doc item is sized L or XL, flag it to the user and suggest breaking it into smaller issues before creating it.

Map priority tags to Linear priority as follows. **Never use Urgent** — High is the maximum priority used.

| Doc tag | Linear priority | When to use |
|---------|----------------|-------------|
| Blocker | High | Blocks other issues from starting |
| High | Medium | Required for MVP but not blocking others |
| Secondary / Spike | Low | Exploratory, not blocking anything |
| V2 | Low + add [V2] prefix to title | Post-MVP scope |

## Labels

Always apply a workstream label to every issue. Labels group issues by track so the backlog stays filterable. Create labels before pushing if they don't exist.

Current label taxonomy for the HC/VA Eval & Improvement workstream:

| Label | Color | Use for |
|-------|-------|---------|
| HC Data Ingestion | #5e6ad2 | All Billy, Intercom, SKAT, GDPR masking, and data validation work |
| HC Feedback Loop | #f2994a | CS onboarding, annotation guidelines, HITL sampling queues |
| HC Evaluation | #4cb782 | Eval dataset curation, LLM-as-judge, benchmarking, clustering |

If a new workstream is introduced (e.g. VA Feedback Loop), create a new label before pushing — don't reuse an existing one. Check with the user if unsure which label applies to a borderline ticket.

## Backlog state and ordering

All newly created issues must be set to **Backlog** state (not "To Do").

Issues must be created in **reverse dependency order** so that the backlog list is ordered correctly:
- Create the most-blocked issues first (they sink to the bottom of the backlog)
- Create the least-blocked issues last (they rise to the top, ready to be picked up)

The result should be a backlog where the top issue is the one the team can start next, and the bottom issues are the ones waiting on the most dependencies.

## Issue format

Each Linear issue must follow this structure:

**Title**: Clear, action-oriented. Prefix with [V2] if marked as V2.

**Description**:
```
**Goal**
[What are we trying to achieve?]

**Context**
[Background and why this matters]

**Expected Outcome**
[What exists when this is done]

**Acceptance Criteria**
- [ ] [criterion 1]
- [ ] [criterion 2]

**Risks & Uncertainties**
- [risk 1]
- [risk 2]

**Dependencies**
- [issue name or external dependency]
```

Never reference dependencies by issue number — always use the issue name. Numbers change; names don't.

## Linear MCP workflow

Use the Linear MCP tools in this order:

### Step 1 — Find the right team and project
```
Linear:list_teams → identify correct team
Linear:list_projects → find or confirm the target project
```

Always confirm with the user before creating anything:
> "I'll create these issues in [Project Name] under [Team Name]. Does that look right?"

### Step 2 — Check for existing issues
```
Linear:list_issues (filter by project) → check what already exists
```
Avoid duplicating issues that are already in Linear. If similar issues exist, flag them to the user and ask whether to skip, update, or create alongside.

### Step 3 — Create issues
```
Linear:save_issue → create each issue with full description
```

Create issues in **reverse dependency order** (most blocked first, least blocked last) so the backlog is ordered correctly — next actionable issue at the top, most dependent at the bottom.

### Step 4 — Confirm and summarise
After creating all issues, provide a summary table:
- Issue title, Linear ID, story points, priority
- Any issues skipped (duplicates or V2)
- Any fields that were inferred and should be reviewed

## Handling V2 items

V2 items should still be created as issues but:
- Prefix the title with [V2]
- Set priority to Low
- Set state to Backlog
- Add a note in the description: "This issue is scoped for V2 and should not be pulled into MVP sprints."

Do not skip V2 items unless the user explicitly asks to exclude them.

## Handling ambiguity

If the document is ambiguous on any of the following, ask before creating tickets:

- Which project or team the issues belong to
- Whether an initiative should be a Linear project or just a label/grouping
- Whether V2 items should be included
- Whether to create a parent issue for the initiative itself, or just the child issues

## Example trigger phrases

- "Create Linear tickets for the HC Data Ingestion initiative"
- "Push these issues to Linear"
- "Turn this doc into Linear tickets"
- "Can you create issues for the Eval & Improvement workstream?"
- "Convert the onboarding section into Linear issues"
- "Add these to the backlog in Linear"

## Quality checks before finishing

Before wrapping up, verify:
- [ ] All issues have a title, goal, and at least one acceptance criterion
- [ ] Dependencies reference issue names, not numbers
- [ ] State is set to Backlog (not To Do) on all issues
- [ ] Priority never set to Urgent — High is the maximum
- [ ] Issues created in reverse dependency order (most blocked first)
- [ ] V2 items labelled correctly and not mixed into MVP work
- [ ] Label applied to every issue — correct workstream label from taxonomy
- [ ] No duplicate issues were created
- [ ] User has confirmed the correct project and team

## Notes on this specific workstream

This skill was built in the context of the HC/VA Eval & Improvement workstream at Shine. The document conventions used there are:

- Issues listed as bullets under initiative headings
- Size in square brackets: `[S · High]`, `[M · Blocker]`, `[XS · Secondary]`
- V2 items marked inline: `[S · High] -> v2 for eng imp`
- Dependencies listed by initiative or issue name, not number
- Open questions captured as bullets under initiative descriptions

When parsing documents following this convention, extract size and priority from the bracket tag and treat "-> v2" annotations as V2 flags.