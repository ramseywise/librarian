---
name: dod-check
description: "Definition of Done gate. Runs the full DoD checklist before a PR is raised or merged: AC, tests, Linear linking, self-review, documentation, deployment readiness."
disable-model-invocation: true
allowed-tools: Read Grep Glob Bash
---

You are a senior engineer running a pre-PR quality gate. Do not implement anything. Report pass/fail per section and block if any required item is unmet.

`$ARGUMENTS` — optional plan name. If omitted, derive from branch name.

---

## Before starting

1. Read the active plan (for AC) from `.claude/docs/plans/` matching `$ARGUMENTS` or branch ticket ID
2. Run `git branch --show-current` — verify branch name contains a ticket ID (e.g. `VIR-123`, `LIN-123`)
3. Run `uv run pytest --tb=short -q` — record pass/fail

---

## DoD Checklist

Work through each section. Mark each item `✅ pass`, `❌ fail`, or `⚠️ n/a (reason)`.

### ✅ AC Met
- [ ] Every acceptance criterion from the plan is fulfilled
- [ ] No `TODO`, `NotImplementedError`, `return None`, `pass` stubs on critical paths
- [ ] If any AC cannot be met: reason is documented and scope is adjusted in the plan

Check: grep changed files for `TODO\|NotImplementedError\|raise NotImplementedError`.

### 🧪 Self-reviewed
- [ ] Tests pass locally (`uv run pytest`)
- [ ] No syntax errors: `python3 -c "import ast, pathlib; [ast.parse(f.read_text()) for f in pathlib.Path('src').rglob('*.py')]"`
- [ ] Linting clean: `uv run ruff check src/` (if ruff is configured)
- [ ] No other parts of the app visibly broken (check diff for side-effect imports)

### 🔗 Linear linked
- [ ] Branch name contains the Linear ticket ID (e.g. `vir-212-...`)
- [ ] PR body will include `Related Issue(s): VIR-XXX` — confirm this is prepared

Check: `git branch --show-current | grep -iE '[A-Z]+-[0-9]+'`

### 📄 Documented
- [ ] PR body will summarize what was tested and what reviewers need to check
- [ ] Ticket comment or Notion page updated if this is a spike or discovery
- [ ] If agentic/architectural change: observability schema updated (`ExperimentRun`, tracing fields)

### 🚀 Deployment readiness
- [ ] No new env vars introduced without noting them for staging/prod
- [ ] No new migrations without noting they must run before deploy
- [ ] No disruptive change for end users without prior coordination
- [ ] If agentic change: Langfuse/tracing instrumentation is in place

---

## Output

Print a summary table:

```
| Section              | Status | Blockers |
|----------------------|--------|----------|
| AC Met               | ✅/❌  | ...      |
| Self-reviewed        | ✅/❌  | ...      |
| Linear linked        | ✅/❌  | ...      |
| Documented           | ✅/❌  | ...      |
| Deployment readiness | ✅/❌  | ...      |
```

**Verdict:**
- All ✅ → `DoD: PASSED — ready for /run-code-review and /quick-pr`
- Any ❌ → `DoD: BLOCKED — resolve items above before raising PR`

Do not proceed to `/quick-pr` if verdict is BLOCKED.

---

**Next step:** `/run-code-review` then `/quick-pr` once DoD is PASSED.
