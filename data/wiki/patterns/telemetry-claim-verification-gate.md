---
title: Telemetry Claim Verification Gate
tags: [eval, infra, pattern]
summary: Treat every dashboard number as a claim and recompute it independently from the raw corpus before it can drive a hook or rule — each claim gets one verdict (confirmed, overstated, inverted, phantom, unmeasurable), and only verified claims may become behaviour changes; the rest become metric bugs.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/guacamayo/skills/meta-feedback/SKILL.md
  - data/raw/claude-docs/guacamayo/skills/meta-insights/SKILL.md
  - data/raw/repos/guacamayo/README.md
---

# Telemetry Claim Verification Gate

guacamayo runs a three-skill loop: **insights measures, feedback verifies, retro enforces.**
The middle skill exists because a dashboard number is a *claim*, not a finding — and claims
that reach the retro unverified become enforcement (hooks, rules) built on miscounts.

## The gate

Harvest discrete claims from every monitoring surface (insights log, factstore, recurrence
report, dashboard tiles, and anything the user pasted — which gets no deference). Then, for
each claim, **compute the number independently from the raw transcripts, not from the tile
that asserted it.** The dashboard is the thing under test; it cannot be its own witness.

State corpus bounds before measuring (file count, size, retention ceiling of ~15 days — a
signal reaching further back is computed over rows whose raw text is gone; say so).

### Verification obligations

- **Count the right unit.** Per-command vs per-occurrence-within-command is the classic
  break: one compound shell call (`echo X && ls && for d in */`) is good practice but
  inflates a per-occurrence counter. When magnitude is implausible relative to the
  denominator, check this first.
- **Establish the denominator.** Always report `n / total (pct)`.
- **Check the string exists.** A grep for a marker that only appears in your own analysis
  text measures nothing; exclude the current session from corpus scans.
- **Test causal direction** for "X prevents Y": split on X, compare Y in both arms.
  Correlation frequently runs opposite to the hypothesis.
- **Separate substitutable from non-substitutable.** For tool-choice claims count only what
  the alternative can express (a dedicated read/search tool cannot aggregate or range-extract).
- **Cross-check session counts** between the insights engine and the factstore before
  computing any per-session ratio.

### Verdicts

| Verdict | Meaning | Routes to |
|---|---|---|
| CONFIRMED | independent count within ~10% | recommendation |
| OVERSTATED | real but materially smaller | recommendation scoped to the true slice + metric fix |
| INVERTED | data runs opposite | retraction finding |
| PHANTOM | signal does not exist in corpus | metric fix only — never enforcement |
| UNMEASURABLE | no column/signal can score it | register a signal, don't hand-derive a verdict |

**A claim that fails the gate cannot appear as a behaviour change.** That is not a lesser
outcome: a miscounted metric that drives a hook is worse than no metric.

## Operating rules

- **Provenance:** every recommendation carries the re-runnable command and corpus. A number
  without one is not evidence.
- **Cluster to causes** before recommending — several symptoms often share one mechanism.
- **Propose-only:** the loop writes exactly one record and never touches hooks, settings or
  identity files.
- **Verdict distribution is the health metric.** A rising PHANTOM/OVERSTATED share means
  the monitoring layer is drifting. A claim marked PHANTOM that reappears unchanged means
  the metric was never fixed — escalate as a measurement finding rather than re-verifying.

## See Also
- [[Monitor the Gate, Not the Stage]] — related (trust numbers per automated gate)
- [[Re-Derive, Never Re-Read]] — extends (the provenance rule generalised from ledger to dashboard)
- [[Signal Registry with Resolution States]] — prerequisite-for (UNMEASURABLE routes to a registry entry)
- [[Falsifiable Hypothesis Gate]] — extends (the same discipline at hypothesis-authoring time)
- [[Friction Promotion Ladder]] — prerequisite-for (only verified claims may climb the ladder)
- [[Hardcoded Dashboard Cells Are Expiring Claims]] — extends (hand-typed numbers are unverifiable claims by construction)
- [[Unit Tests Encode the Checker's Assumption]] — related (verify the checker against the live corpus too)
- [[Dark Outcome Tier]] — related (verify the claim, and also ask whether it is the claim that matters)
