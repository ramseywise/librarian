---
title: Silence Reads as Clean
tags: [patterns, infra, pattern]
summary: The recurring defect where a job that never ran, a command that failed with swallowed stderr, or a channel that stopped firing produces output indistinguishable from "healthy, nothing to report" — and the design rule that absence must be a distinct, observable state.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-04-dis60-lighthouse-ci.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-04-dis60-lighthouse-ci.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-04-dis60-lighthouse-ci.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-04-dis60-lighthouse-ci.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-04-dis60-lighthouse-ci.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-04-dis60-lighthouse-ci.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-04-dis60-lighthouse-ci.md
  - data/raw/claude-docs/guacamayo/docs/plans/2026-08-19-telemetry-decision-log-and-hypothesis-skill.md
  - data/raw/claude-docs/guacamayo/docs/research/2026-08-15_GUA-119_synthesis.md
  - data/raw/claude-docs/guacamayo/docs/research/2026-08-15_GUA-119_event-transport.md
  - data/raw/claude-docs/guacamayo/docs/research/2026-08-09_friction-learning-loop_hook-emission.md
  - data/raw/claude-docs/guacamayo/docs/research/2026-08-19_claude-setup-telemetry-review.md
  - data/raw/claude-docs/galactus/skills/proto-review/SKILL.md
  - data/raw/claude-docs/galactus/skills/review-shared/SKILL.md
  - data/raw/claude-docs/galactus/skills/review-defense/SKILL.md
  - data/raw/claude-docs/guacamayo/docs/research/2026-08-20_git-activity-granularity.md
  - data/raw/claude-docs/guacamayo/docs/research/2026-08-20_tencentdb-memory_parity.md
  - data/raw/claude-docs/guacamayo/skills/meta-retro/SKILL.md
  - data/raw/claude-docs/galactus/docs/plans/2026-08-09-prototyping-review-subsystem.md
  - data/raw/repos/galactus/.claude--docs--plans--2026-08-09-prototyping-review-subsystem.md
  - data/raw/repos/guacamayo/README.md
  - data/raw/claude-docs/galactus/docs/plans/2026-08-14-orchestrator-design.md
  - data/raw/repos/galactus/.claude--docs--plans--2026-08-14-orchestrator-design.md
  - data/raw/claude-docs/guacamayo/docs/plans/2026-08-12-wake-consistency-check.md
  - data/raw/repos/guacamayo/.claude--docs--plans--2026-08-12-wake-consistency-check.md
  - data/raw/claude-docs/guacamayo/docs/plans/2026-08-15-gua-113-board-contract.md
  - data/raw/repos/guacamayo/.claude--docs--plans--2026-08-15-gua-113-board-contract.md
  - data/raw/claude-docs/guacamayo/docs/plans/2026-08-19-meta-feedback-liveness-signal.md
  - data/raw/repos/guacamayo/.claude--docs--plans--2026-08-19-meta-feedback-liveness-signal.md
  - data/raw/claude-docs/guacamayo/docs/plans/2026-08-18-gua-137-dashboard-facelift.md
  - data/raw/repos/guacamayo/.claude--docs--plans--2026-08-18-gua-137-dashboard-facelift.md
  - data/raw/repos/librarian/.claude--docs--plans--2026-08-02-review-LIB-60-cron-fail-loud.md
  - data/raw/repos/librarian/.claude--docs--plans--2026-08-03-LIB-94-cron-output-and-stall-detection.md
  - data/raw/repos/librarian/.claude--docs--plans--2026-08-04-LIB-110-restructure-shared-extraction.md
---

# Silence Reads as Clean

Across guacamayo's telemetry, review, and scheduling work the same defect was found in
at least five independent places, which is what earns it a name. In each, the system had
two states — *healthy with nothing to report* and *not running at all* — and emitted the
same bytes for both.

## Observed instances

| Where | What silence looked like | What it hid |
|---|---|---|
| Scheduled telemetry jobs | exit 0, empty report | 12 missed daily windows — "a job that never starts and a healthy job look the same" |
| `gitstore.py:108` git/`gh` wrapper | returned `""` on nonzero exit, no log line | an expired token read as *zero PRs merged* |
| Hook log writers (`lib.sh`) | `log_event ... \|\| true` | log-write failures masked; recurrence counts under-report |
| Advisory hooks | 100% silent on success, no pass entry | three hooks invisible to recurrence analysis; no way to tell "never fired" from "fired, nothing to say" |
| Proposed state-branch event channel | branch simply stops growing | a workflow that stops firing is indistinguishable from "no events happened" |
| Proposed hook-level branch collector (rejected) | no event for branches created outside agent sessions | "no mismatched branches" and "never observed" became the same answer |
| MCP server documented in three files, configured in none | skills' MCP calls fell back without error | retrieval silently degraded to the human narrating context |
| Recurrence counted from a rotating pass log | rows older than the ~5-day rotation simply absent | anything older was undercounted; the durable findings sink was the right source |
| Lighthouse CI report upload (akira) | job green, artifact uploaded | `actions/upload-artifact` defaults to `include-hidden-files: false`, so the `.lighthouseci/` dot-directory was dropped — four green runs computed scores nobody could read; fixed with `include-hidden-files: true`, but those runs' data was gone |
| Plan-to-issue join in a consistency check (guacamayo) | `unmatchable=106` as a footnote | the regex matched only `#N`; every doc following the newer URL convention joined to nothing, so the compliant docs were the invisible ones |
| Board column derivation (guacamayo) | undetermined items fell into `backlog` | the default bucket absorbed every failed join; fixed by rendering `?` and making `skipped_repos` a required key |
| Pipeline-stage cell for a manual gate (guacamayo) | hardcoded literal | structurally incapable of change; the resolver now returns `None`, rendered as grey "never run", never 0 |
| Dashboard marker injector (guacamayo) | missing marker skipped silently | a region vanished without error; a test now asserts that each marker exists exactly once |

The event-transport research weighted *failure visibility* as the heaviest axis in its
comparison precisely because this defect had recurred across three prior issues.

## Design rules that follow

1. **Absence is a state, not an empty value.** A signal that could not be observed
   resolves to `None`/`unobservable`, never to `0`/`false`. The signal registry pattern
   ([[Signal Registry with Resolution States]]) makes this a type: missing repo → `None`,
   never a false absence.
2. **Nonzero exit must leave a trace at the moment of failure.** Log the exit code and
   stderr before returning a fallback; never return the fallback bare.
3. **Everything that runs logs that it ran.** A pass entry per hook invocation costs a
   line and converts "never fired" into a measurable count.
4. **Prefer channels whose health is observable locally.** Pull-based transports
   expose `gh` exit codes and HTTP status at the call site ([[Pull-Only Event Transport]]);
   push-based channels fail by stopping, which looks like quiet.
5. **Record skips, not just results.** A reporter that did not run says so with its
   reason ([[Scope-Gated Reporter Dispatch]]) — the same rule at the review layer.
6. **Review for it explicitly.** [[Rationale-Blind Worst-Case Review]] pass 1 asks of
   every step "is nothing distinguishable from success?" because this defect is
   invisible to reviewers who read the happy path.

7. **Test the diagram with last-fire timestamps.** In the guacamayo dashboard an
   Overview tab asserts the three-plane architecture and a separate Loop Health tab shows
   when each stage (capture, insights, retro) last fired. A stage with no recent timestamp
   means the loop is broken there, *regardless of what the diagram claims* — the
   architecture document becomes a testable claim instead of a description.

## Why it recurs

Every instance was a reasonable local choice: `|| true` keeps a hook from blocking a
tool call; returning `""` keeps a caller from crashing; exit 0 keeps a scheduler from
alerting on an idle day. Each trades a loud failure for a quiet one, and quiet failures
are only discovered by someone checking whether the data has stopped — which is why
the first observation was a 12-window gap, not an alert.

## Silence from poison vs silence from clean

The galactus review verdict ladder has a rung *above* "any dispatch failed": **rung 0 fires
on the conjunction of a prompt-injection hit and at least one completed-but-empty
dispatch.** A reporter that read injected content may have been told to return nothing, so
its empty array cannot be trusted as clean when an injection was detected in the same diff.

This only works if an empty array is recorded as `completed`, never `failed`. Marking an
empty-but-honest reporter as failed trips rung 1 (unconditional), rung 0 never evaluates,
and "a poisoned review gets the same verdict as a busy one." Telling the two silences apart
is left to `verdict.py`, computed from injection hits plus the completed-empty set, and
never pre-judged by the orchestrator. The plan war game applies the same rule: an attacker
that failed to dispatch makes the read `incomplete`, because attacker silence is a dispatch
result, not a clean bill (see [[Adversarial Plan War Game]]).

## When the poison rung dilutes itself

The first real review the galactus subsystem ran was of its own plan, and rung 0 fired on
the subsystem itself. The injection detector matched the review code's own pattern lists
and fixtures, and two dimensions came back legitimately empty. Two counterfactual runs
narrowed it down. With injection hits removed, the same payload returned
`request_changes`, and after those blockers were fixed it returned `comment`. So the
ladder did exactly what it was written to do, and what it found was a flaw in itself:

- The second condition ("at least one completed dispatch returned nothing") is an
  **existential over dispatches**. Each new always-on dimension makes it easier to
  satisfy and never harder. At seven always-on dimensions, one of them designed to be
  usually empty, the condition is close to always true.
- The plan had justified deliberately loose injection patterns with *"a false-positive
  hit alone changes no verdict"*. That argument stops holding once the second condition
  is nearly guaranteed. The signal then gets "trained into noise", and operators learn to
  ignore it even when it fires correctly.
- The fix changes the rung's meaning: exclude hits in the reviewed subsystem's own files,
  or require the empty dispatch to be one the payload could plausibly have targeted. The
  review left that decision to the plan, because *"a review does not get to quietly
  rewrite the ladder it is judged by."*

Two related lessons came from the end-to-end runs:

- **Live runs may never reach the defence.** In both injection runs, every dimension
  still returned findings, and agents said outright that the embedded text did not bind
  them. So rung 0 never fired, and the runs could not show the defence works. A
  counterfactual payload, with findings removed and those dispatches set to
  `finding_count: 0`, did return `insufficient_context`. Whether a payload can silence an
  agent is a property of the agents, not of the verdict code. It can regress with no code
  change, so only re-running the corpus will notice.
- **The clean diff has to approve.** The third run was a docstring typo fix with no
  payload, and it was expected to return `approve`. *"A subsystem that cannot approve
  anything is not conservative, it is broken."* This run is the only place that shows up.

## Every phase output is three-way

The galactus control-plane design promoted this to a core invariant binding every phase
transition: **succeeded**, **ran and found nothing**, **failed to run**. "No output" can mean
the check passed, the agent found nothing, the agent never ran, retrieval returned nothing,
context was empty, a tool call failed, the model failed, or the evaluator failed —
collapsing them makes an orchestrated pipeline *less* trustworthy than a manual one, because
a silent skip looks like a pass. Corollaries for dispatch: empty is `completed` not `failed`
(marking a clean dimension failed short-circuits the ladder past the injection check), and
**empty input is an error, not an empty result** — a reporter handed nothing returns no
findings, so a broken diff command reads as approval.

## Three more librarian instances (2026-08)

| Instance | Why it read as clean |
|---|---|
| Insights cron on empty input wrote a 67-byte "No session data available" report and exited 0 | Byte-for-byte a healthy run from outside |
| The fail-loud guard that replaced it checked the destination directory | After the first derivation populated it, the guard could never fire again, and a stalled source reported `sessions_synced: 0, problems: []` (see [[Guard the Source, Not the Destination]]) |
| A launchd plist pinned the repo's absolute path | Moving or renaming the directory breaks the scheduled job with no error anyone sees; a restructure plan listed it as a manual step in the PR body because no test can catch it |

## See Also
- [[Uptime Probe Asserts the Journey]] — instance-of (an alert path is done only when a test alert arrived)
- [[Verification Thins Where Blast Radius Widens]] — instance-of (skipped behavioural evals absent from a 99% pass rate)
- [[Silent Fallthrough in String-Keyed Discovery]] — extends (the same defect in skill-doc lookup: a miss returns a default)
- [[Scope-Gated Reporter Dispatch]] — extends (refusing to let an absent section mean a clean pass)
- [[Signal Registry with Resolution States]] — extends (typing unobservable as distinct from zero)
- [[Rationale-Blind Worst-Case Review]] — extends (the review pass that hunts for this)
- [[Pull-Only Event Transport]] — instance-of (transport chosen for failure visibility)
- [[Append-Only Log Writer Invariants]] — extends (post-write length check so a no-op cannot pass as a write)
- [[Collapse Site Detection]] — extends (the fog pass's four-row table for the same defect)
- [[An Unrun Scan Is Not a Clean Scan]] — instance-of (review dimension with no inputs)
- [[Silent Failure Catalogue]] — extends
- [[Adversarial Plan War Game]] — extends (incomplete ranks first)
- [[Plan Epistemic State Axis]] — extends (dispatch-failed must not read as no-conflict)
- [[Layered Ingestion Failure Posture]] — extends (per-grain failure posture for ingestion pipelines)
- [[Budget Without a Meter Is a Preference]] — related (unexported states shipped as guesses)
- [[Natural Key Without a Discriminator Collapses Rows]] — related
- [[Mutation Score Artifact from Zero-Test Runs]] — instance-of
- [[Single-Subject End-to-End Trace]] — related (one traced subject exposes the silences)
- [[Analysis Gap vs Collection Gap]] — extends (partial-coverage collectors rejected for this reason)
- [[Curl-Bridge Context Injection]] — extends (unconfigured-MCP fallback instance)
- [[Trend on Occurrence Date, Not Run Date]] — extends
- [[Build the Checker Before the Generator]] — extends (a green suite is silent about untested seams)
- [[Tested Decision, Untested Expression]] — extends (an anchor that matches nothing returns the input unchanged)
- [[A Check Must Say Why It Could Not Check]] — extends
- [[Execute Every Toggle Configuration]] — instance-of (an unexercised toggle path looks green)
- [[Verify CI Steps by Extraction, Not Retyping]] — instance-of (a retyped CI step passes while the real one fails)
- [[Reproduce to Tell a Break From a Stuck Agent]] — extends (harness stop masquerading as a verdict)
- [[Read-Side Retraction by Observer Vintage]] — extends (a crashed observer must record absence, not verified)
- [[In-Band Stream Errors Read as Bad Answers]] — instance-of (a 200-status stream carrying an error chunk)
- [[Degrade the Render, Surface the Failure]] — extends (a failed enrichment query rendered as a sparse page; fixed by logging where operators look)
- [[Audit the Class, Not the Instance]] — extends (a silent upstream defect masking a loud downstream one)
- [[A Capped Run Is Not a Clean Run]] — instance-of (a spend-truncated batch exiting 0)
- [[Log Drain Over Error Tracker at Pre-Scale]] — related (catch blocks logging to a line nobody reads)
- [[Known-Gap Alarms Ship as Warn]] — alternative-to (the opposite failure: an alarm red from day one is ignored like silence)
- [[Format Contract Lives in the Parser]] — instance-of (a broken log parser renders as a "no data" card)
- [[Control Plane Owns the Join, Not the Truth]] — extends (could-not-join as a first-class verdict)
- [[Unit Tests Encode the Checker's Assumption]] — extends (a 100%-noise table trains readers to skip real rows)
- [[Hardcoded Dashboard Cells Are Expiring Claims]] — instance-of (a literal cell for a manual gate)
- [[Guard the Source, Not the Destination]] — instance-of (a destination-emptiness guard that went dead after the first run)
