---
name: define-milestones
description: >
  Define Linear milestones — the goal posts that group initiatives by product goal or release.
  Use when starting a planning cycle, kicking off a new quarter, or answering "what are we
  shipping by when?" Triggers on: "define milestones", "plan Q3", "next milestone", "kick off
  planning", "what goes into V2", "release planning", "sprint goal", "what are we building next".
---

# define-milestones

Define the goal posts before you plan the work. A milestone answers *what by when* — it groups
2–5 initiatives into a coherent release or product goal. Detailed task breakdown happens in
`/scope-initiative`.

## Before you start

Ask if not provided:

1. **Driving event** — what's forcing this milestone? (release date, customer commitment, product launch)
2. **Success definition** — what capability or outcome does this deliver, and for whom?
3. **Candidate initiatives** — what 2–5 workstreams would constitute this milestone?
4. **Hard constraints** — team capacity, external dependencies, non-negotiable deadlines
5. **Out of scope** — what explicitly does NOT go into this milestone?

If the candidate initiatives aren't clear yet, run `/design-sprint` first.

## Process

1. **Goal statement** — one sentence: what does this milestone deliver and for whom?
2. **Success metrics** — 2–3 concrete, measurable conditions for "done" (not activity metrics)
3. **Initiative list** — named initiatives with one-line goals; flag cross-initiative dependencies
4. **Timeline + constraints** — target date, known blockers, capacity
5. **Scope boundary** — explicit in/out list; borderline items get deferred with a reason
6. **Create in Linear** — milestone with goal + metrics in description; link each initiative as a child project

## Output

Write to `.claude/docs/milestones/<slug>.md`:

```markdown
# Milestone: <name>
Date: <today>
Target: <date or quarter>

## Goal
<one sentence>

## Success metrics
- <metric 1 — measurable>
- <metric 2 — measurable>

## Initiatives
| Initiative | Goal | Owner |
|---|---|---|
| <name> | <one-line goal> | |

## Out of scope
- <item with reason>

## Constraints
<capacity, external deps, hard deadlines>
```

Then create the milestone in Linear with goal + success metrics in the description.

## Rules

- One goal sentence only — if you need two, the milestone is two milestones
- Success metrics must be verifiable, not activity-based ("users can create invoices" not "invoice feature built")
- Every initiative in scope gets a one-line goal — if you can't write it, the scope isn't clear enough
- Defer rather than stretch — a focused milestone ships; an overloaded one slips

---

**Upstream**: `/design-sprint` if you're still ideating what initiatives belong here.
**Next**: `/scope-initiative <initiative-name>` for each initiative in the milestone.
