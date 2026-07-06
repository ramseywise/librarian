---
name: run-code-review
description: "Full galactus pre-PR quality gate — 6 phases: verify (run agent/eval/test), simplify + structural cleanup (file size, duplication, README accuracy, test coverage for new code), security scan, plan-fidelity review, DoD checklist, documentation. Ends with PR body draft. Run this before /quick-pr."
allowed-tools: Read Grep Glob Bash Write Edit
---

You are a senior engineer running the full quality gate before a PR is raised. Work through all phases in order. **STOP** if a blocking issue is found — do not proceed to the next phase.

`$ARGUMENTS` — review name (snake_case). If omitted, derive from branch name or active plan.

---

## Phase 1 — Verify

Confirm the change works end-to-end before spending time on review.

- **Agent changes**: run a representative query via the agent CLI or endpoint and observe output
- **Eval changes**: run the relevant dispatcher path, e.g. `uv run python -m evals.pipelines.run stats ...`, `run quality ... --limit 5`, or `run live ... --limit 5`
- **Script/pipeline changes**: invoke with representative input and inspect output
- **Library/grader changes**: `uv run pytest tests/ -q --tb=short -k "<relevant test>"`

Record: what was tested, what was observed, pass/fail.

**STOP if broken.** Do not continue until the feature works.

---

## Phase 2 — Simplify & Structural

Scan all changed files. Apply all fixes in this phase before moving on.

### 2a — Simplify

- Extract duplicated logic into existing utilities (search before adding new helpers)
- Flatten unnecessary nesting (early returns > nested ifs)
- Remove dead branches, unused imports, and commented-out code
- Preserve public interfaces and behavior — semantic changes are out of scope

Run `uv run pytest --tb=short -q` after each change. Revert and note if a test breaks.

### 2b — File size

```bash
git diff --name-only main...HEAD
wc -l $(git diff --name-only main...HEAD | grep '\.py$')
```

For each changed Python file over 300 lines, identify split points:
- **Independent concepts** bundled together → separate module
- **Output vs. computation** (logging, HTML rendering) → separate from data aggregation
- **Sub-functions** averaging 30–100 lines, each independently testable

Do NOT split a single-pass loop just to hit 300L — document why splitting would be harmful.

### 2c — Duplication grep

Grep changed files for:
- Identical helper functions defined in more than one module (e.g. `_pct_bar`, try/except boilerplate)
- Constants or dicts that should be centralised (metric names, tier mappings, color maps)
- Copy-paste error handling in subclasses that should be a base method

### 2d — README accuracy

For each top-level directory containing changed files, read its `README.md` if present:
- Verify every listed file path exists on disk
- Flag new files/dirs not documented, removed files still listed, stale descriptions
- Grep `docs/` for deleted class/function/module names — stale references in actionable TODOs block future work

Fix README and docs issues inline — do not defer.

### 2e — Test coverage for new code

For each new public function, class, or module in the diff:
1. Grep the test tree (`tests/`) for the symbol name
2. If zero test hits: check whether the logic is trivial (pure delegation, single expression) — if not, it needs a test
3. For non-trivial new code with no tests: write a minimal smoke test covering the happy path and the primary sentinel/edge case

New graders, pipeline factories, and profile/config logic always require tests — do not skip.

Run `uv run pytest tests/ -q --tb=short` after adding tests.

### 2f — Structural rules

- **Circular imports**: extract shared code to C that neither A nor B imports from
- **Re-exports**: when callers use `from old_module import X` and X moves, re-export or update every caller
- **Hooks**: leave hook files alone unless >50 lines or doing something suspicious

---

## Phase 3 — Security

Scan the diff for security issues. **Critical and High findings block the PR.**

| Category | What to look for |
|---|---|
| Injection | String formatting into SQL, shell commands, file paths, LLM prompts |
| Secrets | Hardcoded keys/tokens/credentials (complement to secrets-scan hook) |
| Auth boundaries | New endpoints or tools without access control |
| Deserialization | `pickle.loads`, `yaml.load` without `Loader=yaml.SafeLoader` |
| Agent-specific | Prompt injection vectors, tool call input validation, guardrail bypass paths |
| SSRF / path traversal | User-controlled URLs or file paths passed to fetch/open |

Severity: **Critical** (stop now), **High** (stop now), **Medium** (warn), **Low** (note).

---

## Phase 4 — Plan fidelity

1. Read active plan from `.claude/docs/plans/` matching `$ARGUMENTS` or branch name
2. `git diff main...HEAD` — read every changed file in full
3. Check each plan step: implemented? covered by tests?

| Plan step | Implemented | Tests | Status |
|---|---|---|---|
| Step N: ... | actual code | PASS/FAIL | Match / Deviation / Missing |

**Findings:**
- **[Blocking]** `file:line` — issue and fix
- **[Non-blocking]** `file:line` — issue and fix
- **[Nit]** — style or preference

Grep changed files for `TODO`, `FIXME`, `NotImplementedError`, bare `pass` on critical paths.

---

## Phase 5 — DoD checklist

Mark each `✅ pass`, `❌ fail`, or `⚠️ n/a (reason)`.

**AC met**
- [ ] Every acceptance criterion from the plan is fulfilled
- [ ] No `TODO`, `NotImplementedError`, or stub on a critical path
- [ ] Any unmet AC is documented and scope adjusted in the plan

**Self-reviewed**
- [ ] Tests pass: `uv run pytest --tb=short -q`
- [ ] No syntax errors:
  ```bash
  python3 -c "
  import ast, pathlib
  errors = []
  for f in pathlib.Path('src').rglob('*.py'):
      try: ast.parse(f.read_text())
      except SyntaxError as e: errors.append(f'{f}: {e}')
  print('\n'.join(errors) if errors else 'All OK')
  "
  ```
- [ ] Lint clean: `make lint`

**Linear linked**
- [ ] Branch name contains the ticket ID: `git branch --show-current | grep -iE 'vir-[0-9]+'`
- [ ] PR body will include `Closes VIR-XXX`

**Deployment readiness**
- [ ] No new env vars without updating CLAUDE.md feature flags table
- [ ] No new migrations without noting they must run before deploy
- [ ] If agent change: Langfuse/tracing instrumentation in place (`ExperimentRun`, trace fields)
- [ ] If agentic/architectural change: observability schema updated

---

## Phase 6 — Documentation

Update stale docs only:

- **README.md** — new features, changed CLI flags, updated setup steps
- **`docs/`** — new patterns, updated tool wiring, changed eval architecture
- **CLAUDE.md** — new agents, new env vars (feature flags table), updated safeguards layer table
- **`.claude/docs/plans/`** — if work is complete, add a `## Done` note at the top of the plan linking to the Linear ticket, then leave it in place (no archive folder)

---

## Output

Return results directly in chat — do not write a file.

**Phase 1 — Verify:** [what was tested, output observed, pass/fail]

**Phase 2 — Simplify & Structural:** [changes applied, findings fixed, or "no changes needed"]

**Phase 3 — Security:** [findings by severity, or "no issues found"]

**Phase 4 — Plan Fidelity**
Fidelity table + findings list (`[Blocking]` / `[Non-blocking]` / `[Nit]`)

**Phase 5 — DoD**
| Section | Status | Notes |
|---|---|---|
| AC met | ✅/❌ | |
| Self-reviewed | ✅/❌ | |
| Linear linked | ✅/❌ | |
| Deployment readiness | ✅/❌ | |

**Phase 6 — Documentation:** [docs updated, or "no changes needed"]

**Verdict:** Needs changes | Approved with minor fixes | Approved

**If approved:** draft the PR body using `.github/pull_request_template.md`, then run `/quick-pr`.
**If blocked:** list what must be resolved before `/quick-pr`.
