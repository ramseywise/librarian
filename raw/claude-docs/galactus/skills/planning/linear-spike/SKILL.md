---
name: linear-spike
description: "Create a time-boxed spike or exploration ticket in Linear. Use when the next step is research, prototyping, or investigation before committing to an implementation. Triggers on: 'create a spike', 'open a Linear spike', 'let's spike on X', 'I need to investigate Y before building it'."
---

# Create a Linear Spike Ticket

A spike is a time-boxed investigation. It produces a decision or a short doc — not production code. Use it when the right implementation path isn't clear yet.

---

## Before you start

Ask the user for:
1. **Topic** — what are we investigating?
2. **Why now** — what decision does this unblock?
3. **Timebox** — how many hours/days? (default: 1 day)
4. **Success criteria** — what will we have at the end? (doc, prototype, ADR, benchmark)
5. **Branch** — which vir-NNN ticket will this live under? (or create a new one)

If the user gave partial context in the conversation, infer what you can and confirm before creating.

---

## Ticket format

```
Title: [Spike] <short topic> (<timebox>)

e.g.: [Spike] Evaluate Google ADK vs LangGraph for agent layer (1 day)
      [Spike] Benchmark Gemini 2.5 Flash grading accuracy on BKH sample (4h)
```

**Description template:**

```markdown
## Goal
<One sentence: what question are we answering?>

## Why now
<What decision does this unblock? What happens if we skip it?>

## Timebox
<N hours / N days — hard stop>

## Approach
- [ ] <Step 1>
- [ ] <Step 2>
- [ ] <Step 3>

## Success criteria
<What deliverable do we produce? — ADR / benchmark table / working prototype / short doc>

## Out of scope
<What are we explicitly NOT building?>
```

---

## Linear fields to set

| Field | Value |
|---|---|
| **Title** | `[Spike] <topic> (<timebox>)` |
| **Type / Label** | `Spike` or `Research` (use whichever label exists in the team) |
| **Priority** | Match the decision it unblocks — usually `Medium` |
| **Estimate** | 1 point per half-day (so a 1-day spike = 2 points) |
| **Project** | Same project as the feature it unblocks |
| **Assignee** | Current user unless specified |
| **Branch** | `vir-{id}-spike-{short-slug}` |

---

## After creating the ticket

1. Create branch: `git checkout -b vir-{id}-spike-{slug}`
2. Write findings in `.claude/docs/research/{slug}.md` as you go
3. Close the spike with a comment linking to the doc or decision
4. If the spike produces actionable next steps: create follow-up implementation tickets referencing `vir-{id}`

---

## Step-by-step (what to do when invoked)

1. Gather the 5 inputs above — ask only for what's missing
2. Draft the title and description using the templates above
3. Show the draft to the user for confirmation
4. Use the Linear MCP tool (`mcp__claude_ai_Linear__save_issue`) to create the ticket
5. Report the issue ID and URL back to the user
6. Optionally: suggest the git branch name

```python
# MCP call shape
mcp__claude_ai_Linear__save_issue(
    title="[Spike] <topic> (<timebox>)",
    description="<rendered markdown body>",
    labelNames=["Spike"],   # or ["Research"] — check what exists
    priority=2,             # 1=urgent, 2=high, 3=medium, 4=low
)
```
