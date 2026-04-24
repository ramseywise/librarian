---
name: plan_risk
description: "Guides the Risks & Rollback section of PLAN.md. Step-specific failure modes, blast radius, and concrete rollback commands. Loaded by the plan agent."
---

Use this skill when writing the `## Risks & Rollback` section of PLAN.md. Generic risks ("deployment could fail") are useless. This section exists to answer: *if this specific step goes wrong, what breaks and how do we recover?*

## Per-step failure mode analysis

For each step in the plan, ask:

1. **What breaks if this step fails mid-way?** Is the codebase in a valid state, or is it left with partial changes? (e.g., a schema migration that ran but the code using it wasn't deployed)
2. **What breaks if this step succeeds but is wrong?** (e.g., a refactor that passes tests but silently changes behavior)
3. **Who or what is affected?** Is this a local failure (one module), a data failure (corrupted records), or a user-visible failure (broken feature)?

## Blast radius classification

| Class | Condition | Example |
|-------|-----------|---------|
| **Local** | Affects only dev environment; no data or users impacted | Test fails, import error |
| **Data** | Could corrupt, lose, or mis-transform persisted data | Schema change, ETL rewrite |
| **User-visible** | Breaks or degrades a user-facing feature | API change, model swap |
| **Systemic** | Affects multiple services or downstream consumers | Shared schema, package API change |

Flag any step with Data or higher blast radius explicitly in the risk entry.

## Rollback requirements

Every risk entry must have a rollback that is:

- **Specific** — an exact command or sequence, not "revert the change"
- **Testable** — after rollback, how do you confirm you're back to baseline?
- **Scoped** — does rollback affect only this step, or does it cascade?

Examples:
```
# Good
Rollback: `git revert HEAD~1 --no-edit && uv run pytest --tb=short -q`

# Good (data risk)
Rollback: restore from pre-migration snapshot; verify row count matches baseline

# Bad
Rollback: undo the changes
```

If a step has no clean rollback (e.g., a destructive migration with no snapshot), that is itself a risk — flag it.

## Output format for PLAN.md

```markdown
## Risks & Rollback

### Step N: [step name]
- **Risk**: [specific failure mode — what goes wrong and when]
- **Blast radius**: Local | Data | User-visible | Systemic
- **Rollback**: [exact command or steps]
- **Verify rollback**: [how to confirm baseline is restored]

### Step M: [step name]
...

### Global rollback
If multiple steps have been applied and need to be reversed together:
`git revert HEAD~N..HEAD --no-edit` (where N = steps applied)
Or: [specific sequence if git revert is insufficient]
```

## Rules

- Every step with Data or higher blast radius gets its own entry — no batching
- "git revert HEAD" is acceptable only if the step has no side effects outside the repo (no DB changes, no deployed artifacts)
- If a step is genuinely low risk with a clean `git revert`, a one-liner entry is fine — don't pad
- Flag steps with no clean rollback explicitly; do not pretend they are reversible
