---
title: Reversibility Cliff
tags: [patterns, infra, pattern]
summary: Drawing the autonomous-action boundary at the step whose effects cannot be undone — which for an unattended agent sits at notification, not at mutation — with the empirical case that operator approval is the least reliable component (≈9–60% of proposals ever acted on) and that the two "obviously safe" auto-mutations failed on the repo's own data.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/guacamayo/docs/research/2026-08-15_GUA-119_propose-vs-mutate.md
  - data/raw/claude-docs/guacamayo/docs/research/2026-08-15_GUA-119_synthesis.md
  - data/raw/claude-docs/guacamayo/docs/research/2026-08-15_GUA-119_evaluator-host.md
  - data/raw/claude-docs/guacamayo/docs/plans/2026-08-16-gua-119-autonomous-dispatch.md
  - data/raw/repos/guacamayo/.claude--docs--plans--2026-08-16-gua-119-autonomous-dispatch.md
---

# Reversibility Cliff

A design question for any unattended agent: which actions may it take without an
operator in the loop? The default answer — "propose everything, mutate nothing" — is
safe and was the standing policy in the guacamayo loop. A research pass steel-manned
both widening and holding the boundary and concluded that the line was drawn in the
wrong place for the wrong reason.

## The case for widening: the proposal queue does not drain

Propose-by-default assumes someone acts on proposals. Measured:

- 40 `hypothesis` rows vs 13 `applied` in the tooling ledger; 18 past due on the audit day.
- Growth-log entries acknowledged: 3 of 35 (8.6%).
- Retro recommendations acted on: ~60% in the best round.
- A cross-repo template change landed in 4 of 9 repos — silently, with no record of
  which.
- The `retro_acked` key the loop was supposed to set did not exist in the state file.

**Operator approval is the system's least reliable component.** A boundary that routes
everything through it is not a safety boundary; it is a place where work goes to rot,
and rot is invisible while mutation is visible.

## The case for holding: the system was recently, confidently wrong at scale

The two auto-mutations proposed as "obviously deterministic" were tested against the
repo's own history:

- **A — "close an issue whose branch is an ancestor of `origin/main` when the merging
  PR says `Closes #N`."** `Closes #N` appeared in 3 of 33 merged PRs (9%), 0% recently;
  and the ancestor test returned the wrong answer for a live branch (local branch not an
  ancestor of `origin/main` despite a merged PR — squash merges break it).
- **B — "correct a label that contradicts observed board state."** Already happening:
  `issue_label_sync.sh` mutates labels unattended today, so the boundary was never
  where the policy said it was.

Both fail: A on data, B on premise. "Deterministic" was asserted from the rule's shape,
not checked against the corpus — the same error [[Falsifiable Hypothesis Gate]] exists to
catch in experiment rows.

## Re-cutting the line

Classify each candidate action by what undoes it:

| Action | Undo | Side of cliff |
|---|---|---|
| Edit a label | re-edit; full audit trail in issue history | reversible |
| Close an issue | reopen; trail preserved | reversible |
| Append to a ledger / state file | revert the commit | reversible |
| Push, merge, delete a branch | sometimes recoverable, often not | cliff |
| **Send a notification** (comment that pings, email, Slack) | cannot be unsent; attention already spent | **irreversible** |

The cliff sits at **notification**, not at mutation. A label flip nobody is told about
costs nothing if wrong; a wrong notification costs operator trust, which is the scarce
resource the whole propose-path depends on. So: automate reversible mutations with an
audit trail; keep anything that *reaches a human* behind the propose gate.

## The missing instrument

Neither side could be adjudicated well because the ledger had no `rejected` status —
a proposal that was looked at and declined was indistinguishable from one never read.
Proposed: a `proposal-log.jsonl` with `proposal_id, disposition (accepted|rejected|
expired), correct (bool, filled later), latency_days`. With that, "was the proposer
right?" becomes a measurable ratio and the boundary can move on evidence.

## Host and permission consequences

- The triage half (label sync, DoR checks, ledger acknowledgement) is string/JSON work
  over `gh` output — host it on a scheduler with plain shell, **no LLM**, no token spend,
  no permission surface.
- The review half already exists as a standalone headless driver (`review-cli run`);
  wrapping it in an interactive `claude -p` session would add an outer LLM that
  duplicates orchestration Python already does, and would route the review through the
  lightweight CI profile that strips the substantive findings.
- `allowed_tools` hardcoded in the driver source is a stronger boundary than any
  policy document — it is enforced on every call, not read at session start. No hook
  fires on a timer, so a scheduled run has *only* the boundaries compiled into it.

## What shipped (GUA-119 plan)

- **The evaluator is a pure function.** A test asserts its import set contains no
  `subprocess` or `os`, so the proposal path *cannot* mutate. This is a structural guarantee,
  not a convention.
- **Mutations decline by default.** Every mutation returns a `Declined` record with a reason
  unless it is explicitly enabled. `--act` defaults off.
- **`actions.jsonl` is append-only.** An acceptance-rate tile renders its denominator, so a
  retro can propose promoting an action class on evidence rather than on mood.
- **Unattended spawns** use a lockfile, a once-per-day stamp, and verify-then-ack.
  Two known gaps:
  - A spawn with no timeout holds the lock forever.
  - A dead evaluator rule reads as "no proposals" unless the evaluator writes a
    `rule_errors` marker.

## See Also
- [[Rollback Restores Code Only]] — instance-of (deploy rollback reverses code, not schema or rows)
- [[Execution Boundaries and Guardrails]] — extends (where to put the boundary, with evidence)
- [[Bounding Agents Rather Than Trusting Them]] — instance-of (encoded bounds over documented ones)
- [[Rationale-Blind Worst-Case Review]] — extends (pass 3 names the rollback; this page turns it into policy)
- [[Pull-Only Event Transport]] — extends (the transport decision from the same research)
- [[Silence Reads as Clean]] — extends (rot is invisible; mutation is visible)
- [[Admit at Low Prior, Don't Exclude]] — extends (scope exclusion as an irreversible step)
- [[Due-vs-Acked Trigger Counters]] — extends (the ack mechanism whose missing key is cited above)
- [[Test-Gated Auto-Fix with Per-Hunk Revert]] — related (auto-mutation kept on the reversible side: working tree only, never committed)
- [[Server-Derived Autonomy Tier]] — instance-of (agent may act alone only on reversible effects)
