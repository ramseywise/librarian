---
title: Readiness Is Pinned to a Tree State
tags: [patterns, pattern]
summary: "A plan's READY is true only of the tree and decisions it was checked against. When a dependency lands it can add a gate the plan's own snippets now fail, move every target path, or quietly close the findings the plan was written to fix. So readiness is re-earned against the live tree after each landing, never carried forward from an earlier pass's summary."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-01-dis51-font-theme.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-01-dis51-font-theme.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-01-dis51-font-theme.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-01-dis51-font-theme.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-01-dis51-font-theme.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-01-dis51-font-theme.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-01-dis51-font-theme.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-01-dis52-route-boundaries.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-01-dis52-route-boundaries.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-01-dis52-route-boundaries.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-01-dis52-route-boundaries.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-01-dis52-route-boundaries.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-01-dis52-route-boundaries.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-01-dis52-route-boundaries.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-01-dis58-accessibility-sweep.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-01-dis58-accessibility-sweep.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-01-dis58-accessibility-sweep.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-01-dis58-accessibility-sweep.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-01-dis58-accessibility-sweep.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-01-dis58-accessibility-sweep.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-01-dis58-accessibility-sweep.md
  - data/raw/claude-docs/akira/docs/plans/2026-08-31-vitest-lockfile-pin.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-08-31-vitest-lockfile-pin.md
  - data/raw/repos/akira/.claude--docs--plans--2026-08-31-vitest-lockfile-pin.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-08-31-vitest-lockfile-pin.md
  - data/raw/claude-docs/playground/docs/plans/2026-08-31-vitest-lockfile-pin.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-08-31-vitest-lockfile-pin.md
  - data/raw/repos/playground/.claude--docs--plans--2026-08-31-vitest-lockfile-pin.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-01-dis55-mobile-fit.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-01-dis55-mobile-fit.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-01-dis55-mobile-fit.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-01-dis55-mobile-fit.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-01-dis55-mobile-fit.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-01-dis55-mobile-fit.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-01-dis55-mobile-fit.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-02-dis48-design-tokens.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-02-dis48-design-tokens.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-02-dis48-design-tokens.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-02-dis48-design-tokens.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-02-dis48-design-tokens.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-02-dis48-design-tokens.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-02-dis48-design-tokens.md
  - data/raw/claude-docs/akira/docs/plans/2026-08-31-g6-domain-dns.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-08-31-g6-domain-dns.md
  - data/raw/repos/akira/.claude--docs--plans--2026-08-31-g6-domain-dns.md
  - data/raw/claude-docs/playground/docs/plans/2026-08-31-g6-domain-dns.md
  - data/raw/repos/playground/.claude--docs--plans--2026-08-31-g6-domain-dns.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-08-31-g6-domain-dns.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-08-31-g6-domain-dns.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-15-dis274-enrichment-judges.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-15-dis274-enrichment-judges.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-15-dis274-enrichment-judges.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-15-dis274-enrichment-judges.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-15-dis274-enrichment-judges.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-15-dis274-enrichment-judges.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-15-dis274-enrichment-judges.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-16-dis237-qc-runner.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-16-dis237-qc-runner.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-16-dis237-qc-runner.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-16-dis237-qc-runner.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-16-dis237-qc-runner.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-05-dis145-record-canon-decisions.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-05-dis145-record-canon-decisions.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-05-dis145-record-canon-decisions.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-05-dis145-record-canon-decisions.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-05-dis145-record-canon-decisions.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-05-dis145-record-canon-decisions.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-05-dis145-record-canon-decisions.md
  - data/raw/repos/librarian/.claude--docs--plans--2026-07-31-LIB-57-factstore-failure-attribution.md
  - data/raw/repos/librarian/.claude--docs--plans--2026-07-31-LIB-58-experiment-verdicts-as-data.md
  - data/raw/repos/librarian/.claude--docs--plans--2026-07-31-LIB-59-ledger-chart-annotations.md
  - data/raw/repos/librarian/.claude--docs--plans--2026-07-31-LIB-60-session-note-derivation.md
  - data/raw/repos/librarian/.claude--docs--plans--2026-07-31-LIB-61-insights-section-contract.md
  - data/raw/repos/librarian/.claude--docs--plans--2026-07-31-LIB-75-region-renderers.md
  - data/raw/repos/librarian/.claude--docs--plans--2026-08-02-review-LIB-60-cron-fail-loud.md
  - data/raw/repos/librarian/.claude--docs--plans--2026-08-04-LIB-110-restructure-shared-extraction.md
---

# Readiness Is Pinned to a Tree State

In one sprint of frontend issues in akira, five issues ran in parallel: design tokens,
UI primitives, route groups, the deletion of a legacy UI cluster, and an accessibility
sweep. Every plan written before the others landed went stale. In most cases nothing
about the stale plan looked wrong. The file paths still resolved and the status still
said `READY`.

## How a landed dependency breaks a READY plan

| What landed | What it did to a plan written earlier | Symptom if executed as written |
|---|---|---|
| A new lint gate (raw hex colours banned in `.tsx`) | Plan snippets wrote `bg-[#F5F3F0]` | Red `make gate` on the next PR |
| A primitives issue banned raw `<button>` | An error-boundary snippet used one | Lint error |
| Route groups moved four directories | Every `loading.tsx` target path was gone | Files created in dead locations |
| Route groups made one layout the only `<TabBar />` site | Two skeletons rendered their own TabBar | An existing test asserting exactly 1 TabBar fails, and the UI shows two bars |
| Route groups moved the admin dark shell into a layout | A step's gate said "grep must return 4 hits" in a directory that no longer existed | A gate that can never pass |
| Legacy-cluster deletion and Radix dialogs | Three of 12 audit findings described deleted files. A fourth was now provided free by the library | No-ops, or a hand-built focus trap duplicating Radix |

The accessibility plan's own retro has the worst case: *"the file paths still resolved,
so executing the old plan verbatim would have either no-op'd or re-implemented something
the library now provides."* An audit is a snapshot. A plan built on it decays as quietly
as the audit does.

The same thing happens outside code:

- **The target field disappeared.** An eval plan was written to add three LLM judges, one
  per enrichment attribute. Two days later another issue deprecated one of the attributes,
  so the model no longer emitted it. The executor re-checked the plan's vocabulary claims
  against the tree, found the drift, and stopped instead of writing fixtures for a value
  that no longer existed. The judge was dropped. The same plan's "19 registered metrics"
  had meanwhile become 28, so every snippet line number had to be re-derived.
- **A stale "blocked on" note.** A QC-runner issue carried a triage comment saying it was
  blocked on a model-migration issue. Reading the blocker's actual `READY` plan showed that
  it explicitly excluded QC. The runner also embedded no prompt text, so a later prompt
  rewrite would cost it nothing. The plan answered the sequencing question with evidence,
  proceeded, and asked for the stale note to be updated at PR time so a reviewer would not
  re-block on it.

- **Premise already fixed.** A lockfile-skew plan's Step 0 expected the lockfile to read
  the wrong version. By pickup, another PR had fixed it, so Step 0 would have reported
  "failure" on a correct repo. The urgency had disappeared too: a live hazard (every green
  gate had run on a version nobody declared) had become ordinary end-of-life debt.
- **A decision made after the plan was written.** A domain-purchase plan labelled `ready`
  told an operator to buy one apex. Three days later, a recorded decision chose a
  different apex, and that one turned out to be unobtainable. Nobody had reconciled the
  two, so the plan would have run as written.

## The rules

1. **Name what READY was earned against.** One plan re-earned `READY` against the tokens
   issue only. Route groups then landed and invalidated it. The status line could not show
   that, because it never listed which dependencies it had checked.
2. **Re-verify against the tree, not against the previous pass.** Each re-plan pass
   re-ran `find`, `grep`, and `cat -n` on every path and line it cited. It did not trust
   the earlier "why this is not READY" summary. A later refine pass did the same check
   against the re-plan's own claims before promoting.
3. **Write contingencies in advance, then honour them.** The font plan had said: *"when
   route groups land, the class moves to the layout and is removed from these pages."*
   That contingency fired. A recorded contingency only helps if re-triage actually runs
   when the dependency lands.
4. **Give a shared block one owner.** Two issues both needed to edit the same `:root` CSS
   block. The tokens plan claimed it outright. The other plan's "delete the dead block"
   step became a two-grep verification with a "stop and rebase if this fails" instruction.
   A block edited twice by two issues ends with one edit overwriting the other.
5. **Re-measure counts at execute time.** "203 arbitrary values" in the issue measured
   210 at plan time. Step 0 re-runs the grep, so drift between plan and execution is
   absorbed instead of surprising the executor.
6. **Keep superseded passes, clearly marked.** Earlier passes stay as an audit trail. Each
   opens with a supersession notice before any instruction, so an executor cannot follow
   stale steps by accident.

## The payoff

The route-boundaries plan was dropped from `READY` to `REFINED` after three merges broke
it in five places. It was then repaired and DoR-gated against the live tree the day
before execution. Its execution record says that all 10 steps were implemented exactly as
written, with no deviations, *"the DoR gate's tree-verification the day before meant every
path and token name in the plan matched the tree at execute time."* The one deviation left
was a snippet with an unused import, which would have failed lint. Code in a plan is
untested code too.

## The Issue Body Is the Oldest Snapshot (librarian cartographer, 2026-07/08)

A batch of six dashboard and telemetry issues was filed, three PRs merged, and then the
plans were written. Every plan opened with a correction section before its first step,
because the issue body described a tree that no longer existed:

- **Functions gone or moved.** A ledger parser the issue cited at `__main__.py:148-178`
  had been removed and replaced by a function in another module. Other cited line numbers
  had drifted by 50 to 170 lines.
- **Counts wrong.** "31 ledger rows" measured 32. "`absence:` = 17" measured 15.
  "FRICTION = 11" measured 5. A cited p90 metric did not exist. Only p50 did.
- **Premise inverted.** "No renderer exists" was false: all four card renderers existed
  and were already called on another code path. Only a one-line alias layer and the
  wiring were missing. "Reinstating means writing new code" was false too: a
  JSONL-to-note renderer was already in the repo behind a CLI flag, and it already
  satisfied the parser contract. "Do this after #105, whose tests will pin the behaviour"
  was false as well. Once #105 landed, no test asserted the behaviour in question.
- **The research doc the plan was based on did not exist.** `.claude/docs/` was
  gitignored, so the research behind one issue was never committed. The plan re-derived
  every finding from source and said so in its `Based on:` line.

The habit that worked: each plan was **based on direct codebase inspection**, every
citation was rewritten to the current tree with the commit it was verified at, and a
later refine pass rechecked everything after the next merge ("treat all plan line
numbers as ±2").

### A shipped guard inside the function a plan deletes

The sharpest version is a collision. A plan written on 07-31 said to delete an LLM
report stage outright, noting "verified: no callers outside the cron". Two days later an
interim fix landed a fail-loud empty-input guard **inside that function**, with tests
calling it directly in both directions. A review of the fix called it correct but flagged
that it contradicted Step 4 of its own plan: Step 4 now had more to delete, not less.
A reconciliation section was added to the plan before execution, and the decision was
**relocate, not drop**. The stage was still retired, the guard moved to the new entry
point, and its tests were rewritten to target the new site, keeping both directions. The
guard was not allowed to disappear; only its address changed. The same reconciliation
found the input count had tripled (309 to 1,004 files), and noted that 5 notes newly in a
source directory came from a one-off run, not a live producer. The plan's premise held,
but only because someone checked.

## A Registry Row Is a Claim Too (akira decision-canon review, 2026-09-05)

A prose-only diff recording decisions in a canon registry marked one decision **BUILT**
while its implementation sat on an unmerged branch. The review called that "premature,
not false". The same diff cited regression tests that did not exist ("do not keep the
claim without the test") and cited the wrong decision row. Rule: a status in a registry
is pinned to a tree state exactly like plan readiness. It says BUILT only once the code
is on the base branch, and every cited test must resolve. The review deliberately skipped
code reporters on the prose-only diff, so they would not invent findings to fill a lane.

## See Also
- [[Plan-Insufficient Is Not Blocked]] — extends (the loop outcome that a stale premise should raise)
- [[Plan Epistemic State Axis]] — extends (a status field that says what was actually checked)
- [[Execution-Made Decisions Leave Stale Invariants]] — alternative-to (the same staleness in the other direction: docs left behind by execution)
- [[Decision-ID Reservation Across Concurrent Plans]] — alternative-to (another collision between concurrent plans, solved by reservation)
- [[One-Off Codemod, Permanent Gate]] — prerequisite-for (the tokens issue whose new gate invalidated its siblings)
- [[The Free Decision Is the Long-Lead Item]] — extends (the domain plan that predated its own decision)
- [[Layout Membership by Location]] — related (the route-group move that relocated the boundaries plan's targets)
- [[Adoption Ban Needs an Escape Hatch]] — related (the primitives plan re-refined the day its token dependency merged)
- [[Guard the Source, Not the Destination]] — extends (a fail-loud guard outrun by the plan's own derivation step)
- [[Defined but Never Wired]] — extends (an issue that blamed the model for a contract the code never sent)
