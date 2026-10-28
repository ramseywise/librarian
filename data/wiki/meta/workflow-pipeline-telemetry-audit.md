---
title: Workflow Pipeline Telemetry Audit
tags: [llm, meta, pattern]
summary: What a week of telemetry on a triage → build → review agent pipeline actually showed — ledgers that do not join, a retry counter at 0.017 while plans failed one stage downstream, 3 of 3 unscoped issues routed straight to plan later invalidated versus 0 of 44 scoped ones, logging that dies with the loop, and a BUILT row that outran its evidence.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/playground/skills/workflow-review/SKILL.md
  - data/raw/claude-docs/playground/skills/workflow-build/SKILL.md
  - data/raw/claude-docs/playground/skills/workflow-triage/SKILL.md
  - data/raw/claude-docs/playground/docs/research/2026-08-28-data-stack-map.md
  - data/raw/claude-docs/akira/docs/research/2026-09-02-agent-pipeline-audit.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-02-agent-pipeline-audit.md
  - data/raw/claude-docs/akira/docs/research/2026-08-28-data-stack-map.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-08-28-data-stack-map.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-02-agent-pipeline-audit.md
  - data/raw/claude-docs/playground/docs/research/2026-09-02-agent-pipeline-audit.md
  - data/raw/claude-docs/diskoe/docs/research/2026-08-28-data-stack-map.md
  - data/raw/claude-docs/akira/skills/workflow-triage/SKILL.md
  - data/raw/claude-docs/diskoe/skills/workflow-triage/SKILL.md
  - data/raw/claude-docs/kiez-archive/skills/workflow-triage/SKILL.md
  - data/raw/claude-docs/akira/docs/retro/2026-09-03-retro.md
  - data/raw/claude-docs/kiez-archive/docs/retro/2026-09-03-retro.md
  - data/raw/claude-docs/diskoe/docs/retro/2026-09-03-retro.md
  - data/raw/claude-docs/playground/docs/retro/2026-09-03-retro.md
---

# Workflow Pipeline Telemetry Audit

The akira repo logged every stage of its three-skill pipeline to JSONL ledgers for a
week (203 rows, 40 CI runs) and then audited the ledgers. The findings are about
instrumenting an agent workflow, not about the product, and most of them generalise.

## The ledgers did not join

`issue` mixed four ID formats; `repo` had three spellings of one repository; findings
had no `round` field. The only consistently keyed field was the plan path, so the whole
analysis had to be keyed on `(plan, id)`. Findings were logged twice — `open` at review,
`fixed` after — with no key linking the pair; 19 of 64 rows were duplicates and a naive
count reported 32 open findings where the true figure was 13. **Normalise identifiers
and emit a terminal row with a join key before collecting anything.**

## Logging that lives in the loop dies with the loop

10 of 23 build runs ended at `started` with no terminal row because the log line was a
mid-loop `echo`. Six issues carried review rows at two identical timestamps and no
execute rows — backfilled after the fact, not observed. One issue's review rows preceded
its execute row. A reconstructed ledger is a narrative, not telemetry.

## The retry counter measured nothing

The skill named retry rate as its quality signal ("high retries = bad routing or weak
subagents"). It read 0.017 — `retries: 0` in 59 of 60 runs. Plans *were* failing, as
`PLAN_INVALID` / `FINDINGS_INVALID` a day later at build time, where the cost is a full
re-plan rather than a retry. The refine gate passed everything; build was doing refine's
job one stage downstream. The fix was to log the refine verdict and count invalidations,
i.e. **measure the failure where it is paid for, not where you hoped it would appear.**

## Skipping research is the only clean signal

Triage's own rule said `UNSCOPED → research`. Three unscoped issues were routed straight
to plan; all three were invalidated the next day and one then ran exactly the research
it had skipped. 0 of 44 `CLEAR`-routed items were invalidated. Small n, but the mechanism
is not mysterious: a plan written without research is a plan against an unverified
problem statement. The routing table was made non-discretionary.

## Doc drift was 28% of findings — and fixable at source

13 of 45 unique findings were stale README / spec / design-of-record content. The
documentation DoD table existed in `CLAUDE.md` and nothing in the plan or build stage
referenced it. See [[Scoped Phase Dispatch with Pre-Resolved Files]] for the fix.

The general lesson the audit drew: the knowledge existed and was correct; it was simply
not wired to the stage that could act on it. For every written rule, name the stage that
applies it and verify by grep — not memory — that the stage's skill or agent references
it. A rule only the reviewer knows is a tax paid on every branch; a rule the builder knows
is paid once.

## A `BUILT` row outran its evidence

The roadmap marked an item BUILT because its module landed and was tested, while two of
four review findings deferred to that item were still live — a billed-but-failed model
call still lost its call count, the exact defect the item existed to prevent. None of the
deferred findings was ever re-logged as fixed. The repo's own preamble names the trap:
*"BUILT means 'the module exists and is tested', not 'the deliverable is accepted'."* The
companion rule from the data-stack map: **a document whose stamp is newer than its
content is misleading in the dangerous direction** — a fresh date on stale claims is
worse than an old date.

## Review quality by surface

Frontend branches ran ~3× the finding density of backend ones, and both findings ever
rejected were reporters asserting a runtime fact they never observed, both on frontend
code. The newest surface is where reporters are most likely to narrate instead of
observe.

## First retro: the findings log decays into a lie

A hand-run first retro (2026-09-03, 132 review findings over 17 plans, 75 build rows,
123 triage rows) seeded the repo's `/retro` skill. The findings:

- **Outcomes written once, never reconciled.** 48.5% of findings were still `open`,
  including two blockers, and some cited paths that no longer existed because the fix had
  shipped. A reconcile step should flag open findings whose file doesn't resolve.
- **Line anchors drift.** A finding pointing at `doc.md:33` later pointed at unrelated
  text. Anchor on a quoted snippet plus a commit sha instead (cf.
  [[Cross-Sweep Finding Fingerprint]]).
- **An unenumerated `reporter` field split one dimension in two** (`silent-failure` 13 vs
  `silent_failure` 6), and 12% of rows weren't dimensions at all. Every per-dimension
  count was wrong until the writer rejected unknown values.
- **A missing global ref resolves to nothing and doesn't error.** A fresh tool install
  wiped `~/.claude/refs/`, and every session cited three empty refs for two days.
- **Staged-but-uncommitted work gets swept into a parallel session's commit** on the same
  branch.

How the retro handled its own output:

- **Withdrawn findings are recorded, not deleted.** One headline finding was false twice
  over: most of its rows were placeholder bookkeeping (the enum bug biting the analysis),
  and the rest were in an unmerged worktree. A retro that hides its own false positives
  can't be trusted about its true ones (cf. [[Void, Don't Close, an Invalid Measurement]]).
- **Questions aren't issues.** "Why do 55% of build rows stay pending?" has no acceptance
  criterion, so it goes into an open-hypotheses table, each row naming the command that
  re-checks it next pass. Minutes-sized skill edits that make every other number
  trustworthy are applied in the loop, not parked as low-priority issues.
- **Measure yield per dispatch, not per finding.** A conditional review dimension that
  rarely fires is working as designed; one that fires and finds nothing is not.
- **A decision registry only records answers to questions someone asked.** A
  URL-shape decision (paths vs subdomains per city) was missing from the multi-market
  research entirely because nobody had asked it. That blind spot is structural, so a
  retro should look for decisions that were never posed, not only ones left open.

## Writer-side vocabulary drift

The findings ledger's `reporter` field had 24 distinct values for 11 dimensions
(`architecture` and `review-architecture`, `silent-failure` and `silent_failure`), so every
GROUP BY on it was wrong by about 30%. Close rows had invented a reporter (`"round2"`) and an
impact (`"closed"`) because the schema had no `event` field. 26 rows did this even though
the skill had banned that row by name. The cure was a closed vocabulary, an `event`
discriminator (`finding` / `close`) and a schema lint in the gate. See
[[Contract-Anchored Findings Get Fixed]] for what the cleaned ledger showed.

## See Also
- [[Claude Workflow System]] — extends (what the pipeline's own numbers said about it)
- [[Always-Red Check Carries No Signal]] — part-of (findings 1 and 7 of the audit)
- [[Derive the Gate, Don't Copy It]] — part-of (finding 6)
- [[Scoped Phase Dispatch with Pre-Resolved Files]] — part-of (finding 4)
- [[Plan-Doc Status Enum]] — related (BUILT vs accepted is a status-vocabulary problem)
- [[Trajectory Over Outcome]] — related (the terminal row is the outcome; the stage rows are the trajectory)
- [[Retro Open-Hypotheses Loop]] — related (the recurring pass that consumes these findings)
- [[Cross-Sweep Finding Fingerprint]] — complements (stable anchors instead of line numbers)
- [[Void, Don't Close, an Invalid Measurement]] — related (record withdrawn findings rather than deleting them)
- [[Path-Verified Build State Markers]] — extends (the scoping rule this finding produced)
- [[Gate Pass Rate Measures Effort, Not Readiness]] — prerequisite-for (the triage→build join)
- [[Plan-Insufficient Is Not Blocked]] — related (the outcome that feeds reopened_from)
- [[Contract-Anchored Findings Get Fixed]] — related (what the cleaned findings ledger showed)
- [[Rate Metrics Measure the Logger]] — related (sampling-frame and field-semantics traps in session telemetry)
- [[Four-Stage Design Pipeline with Backflow]] — extends
