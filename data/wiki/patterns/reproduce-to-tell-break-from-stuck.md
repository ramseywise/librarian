---
title: Reproduce to Tell a Break From a Stuck Agent
tags: [eval, pattern]
summary: "An unattended pipeline run that stops without a verdict is ambiguous between 'the chain broke here' and 'the harness ran out of turns or quota here' — a stop only counts as a break when it reproduces from a recorded code+data state, with indeterminate and reproduction-unrunnable as first-class verdicts."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/galactus/docs/plans/2026-08-11-gal-4-phase4-dry-run-modes.md
  - data/raw/repos/galactus/.claude--docs--plans--2026-08-11-gal-4-phase4-dry-run-modes.md
  - data/raw/claude-docs/galactus/docs/plans/2026-08-15-gal-23-hitl-gradient.md
  - data/raw/repos/galactus/.claude--docs--plans--2026-08-15-gal-23-hitl-gradient.md
  - data/raw/claude-docs/galactus/docs/plans/2026-08-15-gal-23-proto-pipeline-dry-run.md
  - data/raw/repos/galactus/.claude--docs--plans--2026-08-15-gal-23-proto-pipeline-dry-run.md
---

# Reproduce to Tell a Break From a Stuck Agent

Found while designing an unattended "dry run" of the galactus prototyping pipeline
(research → plan → refine → execute → review driven by a worktree agent with no human).
The run's whole deliverable was *where the chain breaks* — and that turned out not to be
observable for free.

## Three terminal states, two modelled

An unattended run can end in:

1. **The chain broke** — a missing module, an unwired seam, a phase whose input never
   arrived.
2. **The run completed.**
3. **The harness stopped** — turn budget, quota, or the agent simply giving up.

Repos typically model only the first two. The third is the one that masquerades: account
or quota exhaustion surfaces from an agent SDK as `error_max_turns` or as silent empty
results, *indistinguishable from an agent logic failure at the API level*. A generous turn
budget does not fix this — it changes how often the ambiguity happens, not whether it is
ambiguous, and a rare ambiguous stop in a run whose only output is "where it stopped" is
worse than a common one, because nobody suspects it.

## The discriminator: reproduction from a recorded state

A missing module reproduces identically; a stuck agent does not. So a stop is a *finding*
only when it reproduces on a second run seeded from the first run's recorded state — code
identity (git SHA + dirty flag) and data identity (frame hash) from a run registry. The
concrete rule:

| Reproduction attempts (2) | Verdict |
|---|---|
| reproduces on both | **break** — file it |
| reproduces on neither | harness stop misclassified as a break |
| reproduces on exactly one | **indeterminate** — recorded as such, never rounded |
| reproduction itself cannot run | **reproduction-unrunnable** — a finding about the registry, not the pipeline |

The test of the registry is that the attempts run *from the recorded fields alone*; if a
human must supply anything by hand, that missing field is the finding. This is why the
run-registry dependency was load-bearing rather than nominal.

## Related hazards found in the same design

- **Record the resolution path, not just success.** The live break imported an external
  toolkit through an environment variable pointed at an unmerged branch of another repo.
  Pointed at a *stale* render instead, the import would succeed and produce wrong
  numbers — a silent break, strictly worse than the loud one.
- **A refusal scores as a failure to a naive runner.** A pipeline whose correct output is
  "declines to report" (see [[Data Sufficiency Refusal]]) is a success that an unattended
  runner grading on exit-shape will mark failed.
- **Pre-register the expected-null.** Once the known breaks were fixed, the successor run
  could legitimately find nothing. That has to be written down *before* the run as an
  expected-null outcome, or a quiet run gets read as the pipeline being proven when it
  was only untested (see [[An Unrun Scan Is Not a Clean Scan]]).
- **Name collisions hide non-exercise.** One harness's `--dry-run` meant *substitute a
  scripted model* while the plan's "dry run" meant *drive the whole pipeline*. Conflating
  them yields a step that reads as satisfied when nothing was exercised.
- **Don't tell the unattended agent it is being measured** — a primed agent is not the
  unattended baseline the run exists to measure.


## The evidence rule: cite what the agent did not author (galactus, 2026-08)

When reproduction is not yet available, there is a weaker fallback. An earlier plan
committed that unattended runs "may never report *chain broke*". That commitment was
**withdrawn as unfalsifiable**: the agent writing the report cannot emit a verdict it was
told to suppress, so a real break and a clean run read the same. The replacement binds
every [[HITL Gradient]] level equally. Every run classifies its terminal state as
**(a) chain broke**, **(b) harness stopped** or **(c) completed**, and cites evidence the
agent did not write: the hook-written transition ledger (furthest `Status:` reached), the
process exit code, and for (b) a max-turns error or empty result. Where none exists, the
run records **(d) undetermined**, a first-class outcome rather than a failure. Until a
run registry exists, (a) is claimed from that external signal. Once it lands, (a) can
require replay, which is this page's discriminator.

## See Also
- [[Silence Reads as Clean]] — extends (the harness-stop variant of absence-as-success)
- [[An Unrun Scan Is Not a Clean Scan]] — extends
- [[Loop Termination Design]] — prerequisite-for (exhaustion must be a typed result)
- [[Path-Verified Build State Markers]] — extends (structure that reads complete but is empty where it executes)
- [[Falsifiable Hypothesis Gate]] — extends (pre-registration)
- [[Hash the Frame as Fitted, Not the Source File]] — prerequisite-for (the recorded data state reproduction depends on)
- [[HITL Gradient]] — extends (the evidence rule binds all four attendance levels)
