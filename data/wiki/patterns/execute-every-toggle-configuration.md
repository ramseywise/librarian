---
title: Execute Every Toggle Configuration
tags: [infra, pattern]
summary: "A scaffold toggle is verified only when each of its configurations is rendered, installed, and *run* — and checked by asserting paths and markers, not exit codes — because across one template's build-out nearly every real bug lived in a non-default configuration that rendered cleanly and failed silently."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/ai-project-template/docs/plans/2026-07-12-puffin-integration.md
  - data/raw/repos/ai-project-template/.claude--docs--plans--2026-07-12-puffin-integration.md
  - data/raw/claude-docs/ai-project-template/docs/plans/2026-07-14-template-backlog.md
  - data/raw/repos/ai-project-template/.claude--docs--plans--2026-07-14-template-backlog.md
  - data/raw/claude-docs/ai-project-template/docs/plans/2026-07-16-production-hardening.md
  - data/raw/repos/ai-project-template/.claude--docs--plans--2026-07-16-production-hardening.md
  - data/raw/claude-docs/ai-project-template/docs/plans/2026-07-17-template-core-redesign.md
  - data/raw/repos/ai-project-template/.claude--docs--plans--2026-07-17-template-core-redesign.md
  - data/raw/claude-docs/ai-project-template/docs/plans/2026-07-18-template-full-mirror-redesign.md
  - data/raw/repos/ai-project-template/.claude--docs--plans--2026-07-18-template-full-mirror-redesign.md
  - data/raw/claude-docs/ai-project-template/docs/plans/2026-07-19-cicd-standardization.md
  - data/raw/repos/ai-project-template/.claude--docs--plans--2026-07-19-cicd-standardization.md
  - data/raw/repos/ai-project-template/.claude--docs--in-progress--production_hardening--plan.md
  - data/raw/repos/ai-project-template/.claude--docs--in-progress--puffin-integration--plan.md
  - data/raw/repos/ai-project-template/.claude--docs--in-progress--template-backlog--backlog.md
  - data/raw/claude-docs/ai-project-template/docs/plans/multi-agent-tooling-expansion.md
  - data/raw/repos/ai-project-template/.claude--docs--plans--multi-agent-tooling-expansion.md
  - data/raw/claude-docs/ai-project-template/docs/reviews/AIT-43-review.md
  - data/raw/repos/ai-project-template/.claude--docs--reviews--AIT-43-review.md
  - data/raw/claude-docs/ai-project-template/docs/plans/2026-07-19-two-root-scaffold.md
  - data/raw/repos/ai-project-template/.claude--docs--plans--2026-07-19-two-root-scaffold.md
  - data/raw/claude-docs/ai-project-template/docs/plans/AIT-33-plan.md
  - data/raw/repos/ai-project-template/.claude--docs--plans--AIT-33-plan.md
---

# Execute Every Toggle Configuration

A copier template with N boolean/choice toggles is N products that share a source tree.
The default render is the one everyone looks at; the off-configurations are the ones
nobody does. Over roughly a dozen build sessions on the ai-project-template, almost every
real defect was found only by rendering a *non-default* configuration **and then running
it** — `uv sync`, lint, `pytest`, the eval chain, `npm install && build` — rather than
stopping at "copier exited 0".

## Three levels of "verified", only one of which counts

| Level | Check | What it misses |
|---|---|---|
| Rendered | copier exit code | cleanup tasks that silently did nothing; unrendered `{{ }}` |
| Inspected | `test -d` / `test -f` on every gated path, grep for leftover Jinja | code that imports a module the config removed |
| Executed | install + lint + tests + the real pipeline per config | — |

Bugs caught only at the third level, across the plans:

- **Cleanup targeted the final path, content was still staged.** An `include_x=false`
  `rm -rf` pointed at `src/agents/x`, but that tree lived under `_scaffold/` until a
  *later* `mv` task — so the delete ran before the content existed and the "off" render
  shipped the tree anyway. Copier exited 0. Caught by `test -d`.
- **Root fixture imported an optional package.** `tests/conftest.py` imported the
  LangGraph agent's settings unconditionally; every render without that agent failed test
  collection. Fix: move config-specific fixtures into a nested `conftest.py` that is
  pruned together with its directory.
- **Settings drift between sibling agents.** New fields added to one agent's settings
  but not its sibling's crashed with `AttributeError` the first time the eval ran against
  the sibling in a config where it was the only backend.
- **Same bytes cannot lint clean in both configs.** Ruff's first-party detection depends
  on whether a directory exists, so an import block was correctly sorted in one render and
  I001 in another. Fix: pin by name (`known-first-party = [...]`), which is stable whether
  or not the directory exists; directory-based `src = [...]` resolution flips per config.
- **Short-circuit guards leak.** Task guards of the form `(not full) or include_x` shipped
  hooks into every layering render. Positive guards (`include_x`) do not.
- **An unconditional merge leaked a language.** The Python source merge sat in the
  always-run block while the TypeScript merge was gated, so a TS-only project got a full
  Python `agents/` tree. Invisible until a re-parent put both under one directory name.
- **A blanket prune deleted sibling toggles' modules.** Four independent integration
  toggles shared one `integrations/` package. Tying `rm -rf integrations/` to any one
  toggle would delete modules the *other* toggles enabled. Prune per module, then a final
  catch-all removes the package only when none of the four is on. The render that catches
  it is the "one on, the rest off" mix, not all-on or all-off.
- **A prune took one test and left its siblings.** Turning the TS agent off pruned
  `tests/agent.test.ts` but left three other test files importing the removed
  `src/agent` — an unconditional suite failure in a config with no matrix row.
- **A toggle flipped an eagerly-read default.** See
  [[Toggle Gates the Capability, Not the Runtime Default]]: a checkpointer default read at
  graph-compile time broke every test that imported the app.

## Why the bugs cluster per-axis

The production-hardening plan scoped CI test execution to **one config per feature
axis**, not the cross-product, on the evidence that defects clustered per axis (staging
paths, dependency gating) rather than in axis interactions. The CI matrix therefore has
two tiers: render + lint on every row, real test execution on one row per axis. The one
interaction bug that did surface (a guard reachable only with *two* flags set) is the
argument for keeping a combined-render row too.

## The verification harness lies too

Several rounds were invalidated because the harness silently tested the default:

- **zsh does not word-split unquoted `$args`**, so a loop rendered seven configs as
  seven copies of the defaults. Unquoted `-d eval_metrics=[a,b]` is glob-mangled and
  renders the default set — which reads exactly like "the override was correctly refused."
- **`--vcs-ref HEAD` renders the committed tree**, so uncommitted edits show zero
  behavior change.
- **copier runs `_tasks` with cwd inside the destination**, so a relative destination
  (`out/`) made every task path `out/out/` — a silent no-op for `rm`, a hard failure only
  at the staging `mv`.
- **`cmd | tail` reports `tail`'s exit status**; use `${pipestatus[1]}`.

Rule: audit the rendered *toggle markers* (the gated paths, the dependency set) after
every sweep, never just "the sweep was green."

## Fresh-render-only CI hides re-entry bugs

Staging moves written as `mv _scaffold/X ./` worked on every fresh render and failed
"Directory not empty" on every re-render — so `copier update` flipped the answer and landed
zero files. The CI matrix had only ever rendered into empty directories. See
[[Copier Re-Entry as Capability Path]] for the fix; the verification lesson is to add a
render → commit → re-render-with-a-flipped-flag row.

## A static path sweep before the render matrix

The two-root restructure added `scripts/validate_paths.py`, a cheap static check that runs
before any render is installed:

- **`MISSING_TASK_PATH`** — a `_tasks` `rm`/`mv` names a path that no longer exists in the
  template, so the task is silently a no-op.
- **`ORPHAN_DIR`** — a staged directory that no task promotes or removes.
- **A rendered test matrix** scanned for leftover unrendered `{{ }}` and empty directories.

What building it found:

- A "ghost prune" task had been exempted from the missing-path check from day one — so it
  had always been a no-op, and the exemption hid that forever. Exemptions in a checker
  need their own expiry.
- The render step needs `copier --trust` (tasks are unsafe by Copier's definition); without
  it the sweep validates a render that skipped every task.
- CSS inside a Python f-string produced a false-positive "unrendered braces" hit — a reason
  to report the match location, not just a count.
- **Guard empty root variables before `rm -rf`.** A task like `rm -rf {{ ts_project_root }}`
  with `ts_project_root == ''` wipes the staging root; both language roots need an explicit
  non-empty guard.

The sweep's limit: it hardcodes the variables' default values, so it cannot catch a
regression in a *derived* default (see [[Changing a Derived Default Is a Migration]]).

## See Also
- [[Test Derived Defaults Without Overrides]] — extends (the derived-variable case of the same false green)
- [[Silence Reads as Clean]] — instance-of (a no-op cleanup is indistinguishable from a successful one)
- [[Copier Re-Entry as Capability Path]] — extends (re-render as a configuration to test)
- [[Verify CI Steps by Extraction, Not Retyping]] — extends (the CI layer of the same discipline)
- [[AI Project Template Scaffold]] — instance-of
- [[Read-Every-Consumer Migration]] — related
- [[Settings Field Names Are a Shared Env Namespace]] — extends (a collision that shows only when two gated components load together)
- [[Toggle Gates the Capability, Not the Runtime Default]] — extends (eager vs lazy consumption of a toggled default)
- [[CI Tests the Merge Ref, Not the Branch Tip]] — extends (a default changed on main is a config change under every open branch)
- [[Changing a Derived Default Is a Migration]] — related (what the static sweep cannot see)
