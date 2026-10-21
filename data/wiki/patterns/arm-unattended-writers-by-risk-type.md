---
title: Arm Unattended Writers by Risk Type
tags: [infra, pattern]
summary: "A scheduled job that writes production or spends money ships disarmed, and the disarm mechanism is chosen by what goes wrong if it fires: a commented-out cron for spend risk, cron-on with a dry-run default and a typed confirm string for destructive risk, and a single repository-variable `if:` guard for steps inside a workflow that must keep running — one switch for every vertical that should arm together."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-16-dis270-publish-automation.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-16-dis270-publish-automation.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-16-dis270-publish-automation.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-16-dis270-publish-automation.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-16-dis270-publish-automation.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-16-dis270-publish-automation.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-16-dis270-publish-automation.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-16-dis270-publish-automation.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-16-dis270-publish-automation.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-16-dis270-publish-automation.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-16-dis271-scheduled-sweep.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-16-dis271-scheduled-sweep.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-16-dis271-scheduled-sweep.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-16-dis271-scheduled-sweep.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-16-dis271-scheduled-sweep.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-16-dis271-scheduled-sweep.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-16-dis271-scheduled-sweep.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-16-dis271-scheduled-sweep.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-16-dis271-scheduled-sweep.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-16-dis271-scheduled-sweep.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-25-publishing-workflow.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-25-publishing-workflow.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-25-publishing-workflow.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-25-publishing-workflow.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-25-publishing-workflow.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-29-dis431-s1-aws-scheduler.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-29-dis431-s1-aws-scheduler.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-29-dis431-s1-aws-scheduler.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-29-dis431-s1-aws-scheduler.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-29-dis431-s1-aws-scheduler.md
---

# Arm Unattended Writers by Risk Type

An event-discovery catalogue (repo akira, 2026-09) had three GitHub Actions workflows that
write to production on their own: a daily crawl/import with archive sweeps, a batch-enrichment
sweep that spends model money, and a log-retention job that deletes permanently. All three were
built and merged before anyone wanted them running unattended. The repo ended up with three
different "off" mechanisms, and the reason for each was what goes wrong if it fires.

## The three conventions

| Risk if it fires | Mechanism | Why this one |
|---|---|---|
| **Spend** (batch-API money, production enrichment writes) | `schedule:` block commented out; `workflow_dispatch` the only live trigger | Nothing fires until an operator uncomments the cron *and* confirms the per-run `--limit` values. Cadence and spend are product decisions, so the code ships without them. |
| **Destruction** (permanent delete) | Cron **on**, but a manual dispatch runs dry unless a `confirm` input equals a fixed string | A scheduled run fires only from merged, reviewed code; the human typing the string is the rail on the ad-hoc path. See [[Atomic Archive-Then-Delete for Irreversible Retention]]. |
| **Premature publish** (steps inside a workflow that must keep running) | One repository variable guarding each step: `if: ${{ vars.PUBLISH_ENABLED == 'true' && !cancelled() }}` | The import and archive steps in the same workflow still have to run. Commenting out the cron would disable *when the workflow runs*; the variable disables *whether three steps inside it run*. |

The batch sweep chose the spend convention over the destructive one explicitly: "this job's
risk is spend, not data loss," so a typed confirm string guards the wrong thing.

## One switch for things that should arm together

The publish plan's default was to ship three per-vertical publish steps live, following the
precedent of the archive steps already in the file. Mid-build, the operator overrode it. Events
were frozen on a QC runner that had no production caller, and the operator did not want
activities and bars publishing on their own gates while events stayed frozen. So all three steps
got the **same** variable rather than one flag each. Arming is then a one-line
`gh variable set PUBLISH_ENABLED --body true`, not a code change. A future reader finds a guard
the plan does not explain, so the review recorded the override in writing.

## Switches nest: audit each one's real state, the outermost binds

Nine days later (2026-09-25) a plan asked why only 3 of 487 events were published. The publish
path turned out to be built and wired. What was missing was a picture of the switches. Three
independent switches governed it, and they were in three different states:

1. the workflow's `schedule:` block was **commented out**, so the workflow never fired on its own;
2. `vars.QC_ENABLED` had been **armed** (`true`) for nine days;
3. `vars.PUBLISH_ENABLED` was **unset**.

The armed QC variable had done nothing since it was set, because the cron around it never fired.
The outermost switch binds, so arming an inner one achieves nothing until the outer one is armed
too. Reading the switches from the workflow file wasn't enough. The plan's first draft treated
both variables as unset, and only `gh variable list` showed the real state. Two more findings
came out of the same audit:

- **Coupling hides a missing cadence.** `workflow_dispatch` was the only trigger, and it ran
  the whole job, including the paid, unarmed import step. There was no way to run QC + publish
  on a schedule without also running import. The plan recorded this as an open decision (a
  separate publish-only workflow, or coupling to import's cron once that is armed), not as
  something to fix in passing.
- **An issue's premise about scheduling went stale.** The issue said a retention sweep
  "exists; nothing schedules it". But a daily cron had been running it, armed, since before the
  issue was filed. The real gap was narrower: past-dated and undated `draft` / `needs_review`
  rows, which no sweep touches. The plan made those rows *countable* with a read-only gap
  report (per-reason blocker tallies across the whole draft pile) rather than inventing a new
  lifecycle value for them.

The plan also kept its `Done target` honest. It produced code, tests and a spec but no
production observation, so the header said `built`, not `measured`. The production publish (a
real visibility change, though it costs no tokens) and the QC backlog run (which does spend
tokens) were operator follow-ups, each listed with its exact command and its cost.

## Moving the runner without dropping the chain (akira #431, 2026-09-29)

The scheduled pipeline moved from GitHub Actions (free-tier minutes exhausted) to
EventBridge Scheduler and ECS Fargate. A coordinator review of the first draft found a
blocking defect. The container ran only the importer, but cutover disarmed the Actions
trigger that gated the **whole** job: import, QC backlog, three publish steps, two archive
steps and the health check. Disarming one switch would have silently stopped publish, the
step that makes rows servable.

- **Disarming a trigger disarms everything it gates.** Before you flip it, list every step
  under that condition, not just the one you are porting. The fix ran the full chain in one
  container entrypoint, in the same order and with the same flags and exit-code handling.
- **One container over a second offset schedule.** The tail steps depend on import
  *finishing*, which can take anywhere from seconds to the 30-minute timeout. A fixed-offset
  second schedule can't express that without Step Functions or polling glue, and on a slow
  day it publishes against a partial import. The single task is no wider than the Actions
  job it replaces, so it adds no new timeout risk.
- **On a platform with no free always-firing cron, the schedule's own state is the
  switch.** An EventBridge rule that doesn't exist can't fire, and a disabled one doesn't
  fire. So the Actions pattern of an armed trigger and a gated job has no equivalent there.
- **A runner migration reproduces the current arm state and arms nothing new.** The
  container's QC and publish flags are copied from the live Actions variables at cutover,
  re-checked then rather than taken from a stale snapshot. Turning publish on for the first
  time is a separate decision with its own sign-off, never a side effect of moving
  infrastructure.
- **Cutover in one sitting.** Disarm one runner and enable the other in the same session,
  and verify both states before ending it. Otherwise an interrupted session leaves neither
  runner armed, a silent gap. Then a one-week bake-in, with the old crons kept as
  `workflow_dispatch`-only and a direct check that publish wrote rows whenever it was armed.
  Rollback is two commands.
- **Frame the reason honestly.** "Actions minutes exhausted" stops being a measured limit
  once a planned spend cap restores the minutes. So the move was recorded as a deliberate
  amendment to the infrastructure decision, not as meeting its "measured limit, never by
  credits" trigger. That kept the trigger rule intact for every other decision.

## Details that made the guard safe

- **Skipped is distinguishable from "ran and did nothing".** An `if:`-gated step renders as
  *Skipped* in the Actions UI. A step that ran and printed "0 published" looks different. No
  extra code is needed, and the workflow comment says so, so nobody adds a redundant status line.
- **A `vars.` reference is not an env read.** The env-inventory gate scopes to `process.env`
  reads and workflow `env:` keys. A variable inside an `if:` expression is neither, so it needs no
  inventory row ([[Env Inventory Gate Enforced in One Direction]]).
- **The disarmed steps are complete.** Right CLI, `--write --confirm-production`, right env vars,
  right position in the cadence (import → publish → archive). Disarmed means "will not fire", not
  "unfinished".
- **The log is the CLI's own printed report.** No run-history table was added. The per-row
  `BLOCKED ... qc:unevaluated` lines name why events do not publish, and the cross-run signal is
  an existing pipeline-health alarm. A second record of the same fact would drift.
- **Name the case where a dispatch cannot run at all.** An org-wide Actions-minutes exhaustion
  could leave the step unexercised for weeks. The plan named it as a risk so that no observed
  runs would not be read as a broken step.

## See Also
- [[Atomic Archive-Then-Delete for Irreversible Retention]] — related (the destructive-risk convention in full)
- [[Publish Automatically, Sample for Review]] — related (what the armed publish step feeds)
- [[Advance-Only Machine Writes on a Shared Lifecycle]] — related (the guard on what the machine writer may write once armed)
- [[Resumable Scheduled Batch Sweep]] — instance-of (the spend-risk workflow)
- [[Single-Subject End-to-End Trace]] — related (instruments that shipped green but were never armed)
