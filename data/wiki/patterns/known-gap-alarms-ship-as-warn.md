---
title: Known-Gap Alarms Ship as Warn
tags: [patterns, infra, pattern]
summary: "A new health check whose alarms are already true for tracked, known reasons must not ship red-by-default: give each alarm a block/warn severity, keep known-gap alarms at warn behind an escalation tunable that names the issue it waits on, let the fixer reuse the alarm's own predicate, and flip to block only after the first verified fix."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-15-dis276-pipeline-health-check.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-15-dis276-pipeline-health-check.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-15-dis276-pipeline-health-check.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-15-dis276-pipeline-health-check.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-15-dis276-pipeline-health-check.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-15-dis276-pipeline-health-check.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-15-dis276-pipeline-health-check.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-16-dis237-qc-runner.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-16-dis237-qc-runner.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-16-dis237-qc-runner.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-16-dis237-qc-runner.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-16-dis237-qc-runner.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-16-dis276-pipeline-health-check.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-16-dis276-pipeline-health-check.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-16-dis276-pipeline-health-check.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-16-dis276-pipeline-health-check.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-16-dis276-pipeline-health-check.md
---

# Known-Gap Alarms Ship as Warn

From akira's pipeline-alerting work: a failed or silently empty ingestion run reached no
one. The fix was a pure alarm engine (counts in, alarms out) and a thin CLI that exits
non-zero on alarm. Planning found that two of the eight alarms would fire **on every run
from day one**. QC had never been wired to a caller, so "QC rows = 0 while enriched rows > 0"
was always true. Published supply was far below the serve threshold, so "14-day servable
supply low" was always true too. Both gaps already had their own tracked issues.

A CLI that is red from the day it ships is noise, not an alarm. Operators learn to ignore
it, and then they ignore the real regression too. This is the mirror image of
[[Silence Reads as Clean]]: always-red hides signal just as well as always-green does.

## The mechanism

1. **Every alarm carries a severity, `block` or `warn`.** Every alarm is computed and
   printed on every run. Only `block` alarms drive the exit code, which is the part the
   "reaches no one" problem is about.
2. **Known-gap alarms default to `warn`.** They are listed in one tunable
   (`PIPELINE_ALERT_ESCALATE`, a comma-separated list of alarm ids) rather than a
   hard-coded skip list. Promoting one to `block` is an env change, not a code change.
3. **The alarm text and the tunables contract cite the issue the default waits on.** The
   risk of a warn default is that nobody remembers to flip it once the gap closes. Writing
   the issue number into the alarm message makes the link discoverable without tribal
   memory. The plan also recommended that whoever closes the blocking issue flips the
   default in the same PR.
4. **The fixer reuses the alarm's predicate.** The QC runner built later needed to select
   "future events whose current enrichment has no current QC verdict, or one that judged a
   superseded enrichment". The health check already computed exactly that in three private
   read helpers. Those helpers were moved into a shared module that both files import. One
   rule now serves as the alarm, the backlog selector for the runner, and the check that the
   runner worked. If two callers each derive the same gate, they drift.
5. **Escalate only after the first verified fix.** The QC-runner plan explicitly did *not*
   flip the escalation in its own change. Flipping before the backlog was actually cleared
   would have turned a known `warn` into a hard block on day one, for a condition that same
   PR was in the middle of fixing.

## When the alarm grows a notification step

The follow-up session wired the CLI into the ingestion workflow with a `--notify` flag:

- **Only `block` alarms file anything.** This matches the exit-code contract. A warn-only
  report does nothing, but its warnings are included in the issue body whenever a block
  alarm does fire.
- **One open issue per alarm label: comment on it, never overwrite its body.** A human may
  already be triaging it. A dated comment adds to the history instead of silently
  destroying their notes.
- **The alarm step runs `if: always()`.** Every other step runs `if: !cancelled()`. A fatal
  failure earlier in the run is exactly what this step exists to report, and a cancelled
  run may also have failed for a reason worth surfacing.
- **Pure content and a thin side-effect wrapper.** `buildAlertContent(report)` returns
  `null` or a title and body, so it can be tested with no `gh` binary. The `gh` runner is
  injected. Label creation uses `gh label create --force`, so the step is idempotent
  without an extra existence read.
- **Scope the token to the job.** `issues: write` is set at the job level, not the
  workflow level.
- **Do not import from a CLI file that runs `main()` at module scope.** The env parsing was
  shared by extending the existing CLI rather than adding a second one. Importing anything
  from the old file would have run the whole CLI on import.

## Smaller findings

- **Count-only queries avoid the row cap.** PostgREST's 1000-row page cap applies to rows
  returned, not to `select('*', { count: 'exact', head: true })`. Five of the eight alarms
  needed only a count. The two that needed row data reused an existing paginated-read
  shape rather than inventing a second one.
- **Some alarms cannot be built from today's schema.** A true "spend near the ceiling"
  early warning was impossible because spend was recorded only on runs that had already hit
  the cap. The plan shipped the "cap already hit" proxy and named the missing column as a
  follow-up instead of silently narrowing the alarm.
- **Move the classifier, don't fork it.** The last-run-health classifier lived under the
  admin dashboard because of the dependency rule (`core/` never imports `app/`). The
  alerting module could not import it from there. It was moved into `lib/`, shared
  substrate for both, rather than duplicated. A duplicate would have given two definitions
  of "stale" that disagree.

## See Also
- [[Silence Reads as Clean]] — alternative-to (the opposite failure: always-green instead of always-red)
- [[Layered Ingestion Failure Posture]] — extends (the run-grain alarm layer)
- [[The Run Record Belongs to the Process]] — related (the run rows these alarms read)
- [[UNGATED Metric Convention]] — related (the same "measure first, enforce later" stance applied to eval thresholds)
- [[A Capped Run Is Not a Clean Run]] — related (spend-cap state as an alarm input)
- [[Strict Parsers for Alarm Config]] — related (parser and exit-code contract of the same health check)
