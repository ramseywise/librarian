---
title: Plan Epistemic State Axis
tags: [meta, pattern]
summary: A plan doc carries an Epistemic field (UNTESTED / NO_CONFLICT / CONFLICTED / BLOCKED) separate from Status, with Epistemic-by distinguishing "skipped on purpose" from "dispatch failed" — NO_CONFLICT requires the advisor actually ran, freshness is guaranteed by the writer, and UNTESTED + READY is legal and visible instead of hidden behind compliance theater.
updated: 2026-10-16
sources:
  - data/raw/claude-docs/galactus/skills/proto-refine/SKILL.md
---

# Plan Epistemic State Axis

`Status:` says where a plan is in the lifecycle. It says nothing about whether anyone
adversarially checked the plan. The galactus readiness gate (`/proto-refine`) writes a
second axis before it issues a verdict:

```
Epistemic: UNTESTED | NO_CONFLICT | CONFLICTED | BLOCKED
Epistemic-by: <capability> | skipped — <reason> | dispatch failed — <reason>
Epistemic-at: YYYY-MM-DD
Epistemic-findings: <count>
```

| Outcome | Value |
|---|---|
| Advisor ran, nothing unresolved | `NO_CONFLICT` |
| Advisor ran, open findings | `CONFLICTED` |
| Advisor ran, a finding severe enough that advancing is a mistake | `BLOCKED` |
| Skipped (plan not risky) | `UNTESTED` |
| Advisor did not resolve, or dispatch failed | `UNTESTED`, **never** `NO_CONFLICT` |

## Rules

- **NO_CONFLICT requires that the advisor actually ran.** Never upgrade "the check did not
  run" into "nothing was found," and never upgrade "nothing was found" into "this is sound."
- **Same value, different facts.** Skipped and dispatch-failed both write UNTESTED, but
  `Epistemic-by:` keeps them apart. "Nobody checked, deliberately" is different from "the
  check was supposed to run and didn't." Collapsing them loses the only signal that the
  mechanism is broken rather than just unused.
- **Freshness is guaranteed at the writer.** READY needs an Epistemic value from *this* run.
  A hook enforces coherence (it rejects READY + CONFLICTED/BLOCKED), but it cannot tell
  fresh from stale, so that guarantee lives in the skill.
- **UNTESTED + READY is legal and deliberately visible.** It is the honest record of "ready
  by default, nothing checked it." Making the field required would push people to fill it
  with something, which is compliance theater.
- The advisor sees the plan only, never the caller's assessment of it. A substituted
  dispatch (doing the advisor's job inline) is a failed dispatch.

## See Also
- [[Plan-Doc Status Enum]] — extends (a second axis beside Status:)
- [[Silence Reads as Clean]] — instance-of (dispatch-failed must not read as no-conflict)
- [[Size the Gate to the Blast Radius]] — extends
- [[Rationale-Blind Worst-Case Review]] — extends (the advisor whose result this records)
- [[Compression Strips the Epistemic Frame]] — extends (keeping "unchecked" from becoming "true")
- [[Deferred Decision Status]] — extends
