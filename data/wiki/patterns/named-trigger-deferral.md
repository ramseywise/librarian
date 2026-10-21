---
title: Named-Trigger Deferral
tags: [patterns, llm, pattern]
summary: When research shows a feature is not yet worth building, do not close or defer vaguely — rewrite the issue's trigger into a measurable condition, record the one fact that would flip the decision, and park it.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/research/2026-09-03-dis41-expired-event-sweep.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-03-dis41-expired-event-sweep.md
  - data/raw/claude-docs/akira/docs/research/2026-09-03-dis43-anonymous-rate-limiting.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-03-dis43-anonymous-rate-limiting.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-03-dis43-anonymous-rate-limiting.md
  - data/raw/claude-docs/playground/docs/research/2026-09-03-dis43-anonymous-rate-limiting.md
  - data/raw/claude-docs/akira/docs/research/2026-09-04-dis62-desktop-decision.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-04-dis62-desktop-decision.md
  - data/raw/claude-docs/akira/docs/research/2026-09-16-dis280-continuous-run-classifier.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-16-dis280-continuous-run-classifier.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-16-dis280-continuous-run-classifier.md
  - data/raw/claude-docs/akira/docs/research/2026-09-14-listing-text-extractor.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-14-listing-text-extractor.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-03-dis41-expired-event-sweep.md
  - data/raw/claude-docs/playground/docs/research/2026-09-03-dis41-expired-event-sweep.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-04-dis62-desktop-decision.md
  - data/raw/claude-docs/playground/docs/research/2026-09-04-dis62-desktop-decision.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-14-listing-text-extractor.md
  - data/raw/claude-docs/playground/docs/research/2026-09-14-listing-text-extractor.md
---

# Named-Trigger Deferral

A disposition for research issues whose honest answer is "not now". Observed repeatedly
on one product's research lane (akira): an expired-event sweep, anonymous rate limiting, a
desktop layout, a continuous-run classifier, an LLM extraction tier.

## The shape

1. **Do the research anyway.** The investigation is cheap relative to re-deriving it later,
   and it is what turns a vague "later" into a specific condition.
2. **Rewrite the trigger so it is measurable.** "When stale events hurt results" becomes
   "when >N% of served items are past their end date". "When abuse appears" becomes "when
   the unauthenticated sink exceeds X requests/min from one identity". "When desktop
   matters" becomes "when desktop share of sessions exceeds Y" — and if, as here, no
   telemetry exists to measure Y, *that* is the first task and the deferral says so.
3. **Record the one fact that would flip it.** A decision brief is two paragraphs:
   reversibility, and the single observation that would change the answer. For the
   classifier, the flip fact was "an exhibition stored as one row spanning its run" — none
   existed, so the finding was "not yet buildable: an extraction gap, not a classification
   gap", with the precondition stated as a falsifiable D-row.
4. **Park the issue with the brief attached**, rather than closing it (loses the research)
   or leaving it open-undated (becomes backlog noise).

## Decision rules worth keeping

- **Convergent negatives are stronger than any single measurement.** Four independent
  signals (series column, occurrence density, date span, stored text) each returned
  "no example of the target case exists"; the convergence is the evidence.
- **Measure the cheap tier before adding the expensive one.** For a listing extractor the
  rule was: ship the structural tier, measure yield and precision on a hand-checked sample
  at the existing ~87% bar; add an LLM tier only if yield on the tractable set is below
  ~70% at ~80% precision, and then only for the bucket a structural heuristic cannot reach.
  Cost was not the constraint (under a dollar); complexity and a non-debuggable failure
  mode were.
- **Name the trigger's instrument.** If the measurable condition has no telemetry, the
  deferral is really a telemetry task.

## See Also
- [[Deferred Decision Status]] — extends (the plan-doc status this disposition produces)
- [[Deadline-Scope Isolation]] — complements (why triggered work stays out of dated PRs)
- [[Context Graph Is Not an Execution Graph]] — instance-of (an agent-runtime adoption deferred behind a named trigger)
- [[Rate-Limit Keying: Identity Over IP]] — instance-of (rate limiting researched, trigger rewritten, parked)
- [[Profile Then Select]] — extends (the same rule applied to ML config questions)
- [[Listing Pages Masquerading as Records]] — related (the structural-tier measurement that preceded any LLM extractor)
- [[Observe-Mode Gate With a Named Enforce Trigger]] — extends (the trigger rule applied to a gate's strictness)
- [[Dropped Filter Flips the Truncation Direction]] — instance-of (an existing cap-hit log as the revisit trigger)
- [[Argued Carve-Out with a Stop Condition]] — related (the converse: build a scoped exception now, with a condition for stopping)
