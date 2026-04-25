---
name: write-tickets
description: "Turn rough requirements, notes, or a feature description into one or more Linear-ready tickets using the standard template (Goal, Context, Size, Expected outcome, Acceptance Criteria, Risks). Use when asked to write tickets, flesh out requirements, or create Linear issues."
disable-model-invocation: true
allowed-tools: Read Bash Grep Glob Write mcp__claude_ai_Linear__list_teams mcp__claude_ai_Linear__list_projects mcp__claude_ai_Linear__create_issue mcp__claude_ai_Linear__search_issues
---

Turn the following into Linear-ready tickets: `$ARGUMENTS`

## What to produce

One ticket per logical unit of work. A ticket maps to something shippable and testable by one person in one sprint. If the input spans multiple concerns, split them — output multiple tickets, each complete.

## Before writing

If any of the following are missing or ambiguous, ask before writing:

1. **Goal** — what problem is being solved or what capability is being added?
2. **Context** — relevant technical background, links, prior decisions, related tickets
3. **Size** — S / M / L / XL (see sizing guide below)
4. **Expected outcome** — what concretely exists or works when done?
5. **Acceptance criteria** — specific, testable conditions (not just "it works")
6. **Risks and uncertainties** — open decisions, BE/FE contracts not yet agreed, product decisions needed

If the input is detailed enough to infer reasonable answers, write the tickets and flag your assumptions at the end — don't stall for clarification on things you can reasonably derive.

## Sizing guide

| Size | Effort | Unknowns |
|------|--------|----------|
| S    | < 1 day | None — known path, no open questions |
| M    | 1–3 days | Some — one or two unknowns, resolvable in-ticket |
| L    | 3–5 days | Significant — depends on external decisions or BE contracts |
| XL   | > 1 sprint | Major — needs scoping or a spike first; consider splitting |

## Output format

For each ticket, output exactly this structure (no extra sections):

---
**[Ticket title — imperative, concrete, <60 chars]**

**Goal**
[One sentence: what are we trying to achieve?]

**Context**
[Technical background, relevant links, prior decisions, related ticket IDs. Use bullet points if multiple items. Omit if truly none.]

**Size:** [S / M / L / XL]

**Expected outcome**
[What concretely exists or works when this is done? Describe the deliverable, not the work.]

**Acceptance criteria**
- [Testable condition 1 — specific enough that a reviewer can verify it without asking the author]
- [Testable condition 2]
- [...]

**Risks and uncertainties**
- [Open question or dependency that could block or scope-creep this ticket]
- [...]
---

## Acceptance criteria style guide

Good criteria are **specific and verifiable**:
- Alias names, timeout values, error behavior, edge cases
- "X is aliased to Y per codebase conventions"
- "stale time is set to 0"
- "fails gracefully for unknown values — no crash if a new value arrives"
- "returns 422 with field-level errors on validation failure"

Avoid vague criteria:
- ~~"works correctly"~~
- ~~"handles errors"~~
- ~~"follows conventions"~~

## After writing

1. List any **assumptions** you made (things you inferred from the input rather than were told).
2. Flag any criteria that need a **product or BE decision** before they can be implemented.
3. If the input should be split into more tickets than you wrote, say so and why.

## Pushing to Linear

After presenting the tickets, ask: **"Push these to Linear? (yes / no / edit first)"**

- If **no** — stop here.
- If **edit first** — apply the user's changes, re-present, then ask again.
- If **yes** — follow the steps below.

### Push steps

1. **Resolve team and project** — call `mcp__claude_ai_Linear__list_teams` to get available teams. If the user didn't specify a team, ask. If they didn't specify a project, call `mcp__claude_ai_Linear__list_projects` and ask or confirm.

2. **Map size to Linear estimate** — use this mapping for the `estimate` field (story points):
   | Size | Points |
   |------|--------|
   | S    | 1      |
   | M    | 2      |
   | L    | 3      |
   | XL   | 5      |

3. **Build the description** — format each issue's `description` in Linear's markdown as:
   ```
   **Goal**
   <goal text>

   **Context**
   <context text>

   **Expected outcome**
   <outcome text>

   **Acceptance criteria**
   - <criterion 1>
   - <criterion 2>

   **Risks and uncertainties**
   - <risk 1>
   ```

4. **Create issues** — call `mcp__claude_ai_Linear__create_issue` for each ticket with:
   - `title` — the ticket title
   - `teamId` — from step 1
   - `projectId` — from step 1 (if specified)
   - `estimate` — mapped points from step 2
   - `description` — formatted markdown from step 3

   Create them one at a time. Do not batch — if one fails, report the error and continue with the rest.

5. **Report results** — after all issues are created, output a summary table:
   | Title | Linear ID | URL |
   |-------|-----------|-----|
   | ...   | LIN-xxx   | ... |

   If any failed, list them separately with the error message.
