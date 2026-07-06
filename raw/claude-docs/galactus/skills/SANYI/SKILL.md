---
name: sanyi
description: "三易 SANYI change-contract system for agent architectures. Use when the user invokes /sanyi (init|review|audit), asks to create or enforce a SANYI.md change contract, classify components into 变易/简易/不易 layers, or check a diff/repo for cross-layer violations (invariants made configurable, prompts or tunables hardcoded, schema entropy growth)."
---

# SANYI (三易) — change contracts for agent architectures

## Core model (operational summary)

SANYI is a **change-contract** system: it sorts every component into one of
three change layers, records the assignment in `SANYI.md` at the repo root, and
reports **cross-layer violations** on each diff — the decay dimension single-PR
review cannot see. The three layers:

- **变易 Bianyi (the ever-changing)** — must be cheap to change: prompts,
  thresholds, routing rules, flags. Their values live only in the config/prompt
  layer; hardcoding one elsewhere is BN-1.
- **简易 Jianyi (the simple)** — must stay simple: state schemas, interfaces,
  tool schemas, and the execution graph. Unjustified, unbounded complexity is
  debt against a `budget` (JY-1/2/3).
- **不易 Buyi (the invariant)** — must never change without the highest review:
  safety, compliance, escalation fallbacks. Never bypassable via config / env /
  flag (BY-1/2/3). Admission test: violating it causes a security, legal,
  financial, or trust failure.

Layers may also **evolve on purpose**, recorded in `## Migrations`; only silent
moves are violations (MG-1).

> **First Law of agent SANYI:** LLMs are probabilistic, so a constraint
> implemented only in a prompt is soft. A Buyi invariant MUST have a
> deterministic code-layer implementation; a declared invariant that is
> prompt-only is violation **BY-4**.

The full rationale, I Ching grounding, and worked examples live in
`README.md` (human-facing) — this file is the operational spec the skill
executes.

## Mode dispatch

| Invocation            | Mode                                           |
| --------------------- | ---------------------------------------------- |
| `/sanyi init`         | Create the contract (interview)                |
| `/sanyi review`       | Enforce the contract against the current diff  |
| `/sanyi review --fix` | Same, plus auto-fix BN-1 findings              |
| `/sanyi audit`        | Re-measure the whole repo against the contract |
| no argument           | Ask which mode                                 |

If `review` or `audit` is requested and the target repo has no `SANYI.md`,
offer to run `init` first.

## References — load on demand

| File                            | Read when                                                                                                                | Used by                             |
| ------------------------------- | ------------------------------------------------------------------------------------------------------------------------ | ----------------------------------- |
| `references/contract-spec.md`   | before writing or parsing any `SANYI.md`                                                                                 | all modes                           |
| `references/violations.md`      | before emitting any finding or report — violation codes, severities, and the report template live here; use them exactly | review, audit, init's closing audit |
| `references/interview-guide.md` | drafting and classifying components during an interview                                                                  | init only                           |

## Shared rules (all modes)

1. **Debt baseline**: report only NEW violations. Anything recorded in
   `## Debt` is known and is not re-reported.
2. **Dangling detection**: an entry whose `paths` match no existing file is
   reported as UN-2 — never silently skipped.
3. `## Pending` entries are enforced at the strictest level (as Buyi).

## Mode: init

Read `references/interview-guide.md` first — it carries the heuristics and the
question bank. Then:

1. **Auto-draft**: read the target repo's `CLAUDE.md`, directory structure,
   config/prompt/state files, and integration boundaries. Draft Bianyi and
   Jianyi entries directly from conventions and schemas (measure `current` on
   the spot); collect Buyi _candidates_ only.
2. **Confirm per component** — one question at a time, multiple-choice
   (accept / re-layer / park). Disputes go to `## Pending`.
3. **Buyi interview** — the layer machines cannot infer. Use the question
   bank; run the first-law probe ("where is this enforced in deterministic
   code?") on every entry.
4. **Over-declaration pushback** — more than ~7 Buyi entries: challenge each;
   Buyi must stay scarce, like root access.
5. **Closing audit** — run the audit mode below; write findings into
   `## Debt`.
6. **Deliver** — `SANYI.md` at the repo root + a short debt summary.

## Mode: review [--fix]

Input: the current diff — staged changes if any; else uncommitted
working-tree changes if any; else current branch vs the default branch (if
the branch has diverged too far for a meaningful unit, say so and ask which
range to review) — plus `SANYI.md`.

1. Glob-match changed files to contract entries; note unmatched files (UN-1)
   and dangling entries (UN-2).
2. Enforce per layer:

| Check                                                         | Code | Severity | Default action                                                                         | With `--fix`                                   |
| ------------------------------------------------------------- | ---- | -------- | -------------------------------------------------------------------------------------- | ---------------------------------------------- |
| Buyi path edited directly                                     | BY-1 | blocker  | report + decision options (revert / redesign / amend contract via architecture review) | unchanged                                      |
| Buyi made bypassable (new flag/config/env around it)          | BY-2 | blocker  | same as BY-1                                                                           | unchanged                                      |
| Buyi evidence test deleted/weakened                           | BY-3 | blocker  | same as BY-1                                                                           | unchanged                                      |
| Declared invariant left prompt-only by this diff              | BY-4 | blocker  | report                                                                                 | unchanged                                      |
| Jianyi budget exceeded (shape / graph / complexity)           | JY-1 | warning  | report + update `current`                                                              | unchanged                                      |
| Anomalous single-PR growth within budget (≥3 fields/edges)    | JY-2 | warning  | report + update `current`                                                              | unchanged                                      |
| Unbounded escape hatch (`dict`/`Any`/`**kwargs` hides growth) | JY-3 | warning  | report                                                                                 | unchanged                                      |
| Bianyi value hardcoded outside its layer                      | BN-1 | info     | report                                                                                 | **auto-fix: relocate to config/prompts layer** |
| Unrecorded layer migration (no `## Migrations` record)        | MG-1 | notice   | report + offer to record the migration                                                 | unchanged                                      |
| Changed file matches no entry                                 | UN-1 | notice   | report                                                                                 | unchanged                                      |
| Entry paths match no file                                     | UN-2 | notice   | report                                                                                 | unchanged                                      |

Disambiguation rules:

- **Review is diff-scoped.** Pre-existing violations not caused by this diff
  (e.g. an invariant that was already prompt-only) are NOT Findings — surface
  them under "Debt candidates" with a recommendation to run an audit. JY-2 is
  subsumed by JY-1 when the same growth breaches the budget — report only
  JY-1.
- **BY-1 is subsumed** when BY-2 or BY-3 fires on the same entry — report only
  the more specific code.
- **Files referenced in an entry's `evidence` count as contract-matched** for
  UN-1 purposes (changes to them are BY-3 territory, not "unassigned").

3. **Bookkeeping (always, not gated on `--fix`)**: update Jianyi `current`
   stamps for touched entries.
   For MG-1, offer to add a `## Migrations` record (date, from → to,
   rationale) rather than treating the move as an error.
4. **`--fix`**: apply the BN-1 relocation procedure from
   `references/violations.md` §4. Never touch BY-\*, JY-\*, MG-\*, UN-\*
   findings.
5. Emit the report using the `references/violations.md` template, ending with
   the one-line verdict: _does this diff change the system's change-contract
   structure?_
6. Offer to record accepted findings into `## Debt` so they stop
   re-reporting.

## Mode: audit

Input: the whole repo (not a diff) plus `SANYI.md`. Invoked standalone or as
init step 5. Priority order:

1. **BY-4 sweep** — for every Buyi entry, find its deterministic code-layer
   implementation; prompt-only invariants are the #1 target.
2. **BN-1 inventory** — all Bianyi values hardcoded outside their declared
   layer.
3. **Jianyi entropy** — measure every budgeted component (shape, graph, and
   escape hatches: flag untyped `dict`/`Any` catch-alls as JY-3), refresh
   `current` stamps and `last-audit`.
4. **Migration drift** — components whose natural layer has shifted from their
   contract assignment with no `## Migrations` record (MG-1); propose the
   record.
5. **Hygiene** — UN-2 dangling entries; major components with no entry (UN-1).

Output: report (audit variant of the `references/violations.md` template);
offer to write/update `## Debt`.
