---
title: Argued Empty List
tags: [foundations, eval, pattern]
summary: "An exclusion or findings list that is empty must carry its argument in code — the assumption that makes it empty, a named considered-and-kept set so the claim is falsifiable, and the trigger to revisit — otherwise review cannot tell 'checked and nothing qualified' from 'never checked'; the mirror rule for guards is that an empty findings list is not a pass unless the guard says it ran."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/galactus/docs/plans/2026-08-18-ml-frame-sourcing.md
  - data/raw/repos/galactus/.claude--docs--plans--2026-08-18-ml-frame-sourcing.md
  - data/raw/claude-docs/galactus/docs/plans/2026-08-16-segmentation-parity.md
  - data/raw/repos/galactus/.claude--docs--plans--2026-08-16-segmentation-parity.md
---

# Argued Empty List

From an ML prototyping repo (galactus). The credit run's leakage list was written fresh
against a new public frame.

## The case

Research named the candidate leakers ahead of time: the latest month's bill amount, payment
amount and repayment status, each dated the month before the label. Under the frame's
source-stated one-month horizon, those columns are the inputs the operating story predicts
*from*, not records made after the outcome. So the list came out **empty**, and an empty
list reads to review exactly like a check nobody did.

The plan's mitigation turned the emptiness into an argued decision:

```python
#: Empty, and that is the finding — not an oversight. Under the source's stated one-month
#: horizon (see HORIZON), the latest-month columns are the *inputs* to the next month's
#: label, not post-outcome records. They leak only if the operating story changes.
#: If HORIZON is ever restated, revisit this list first.
LEAKAGE_EXCLUDE: list[str] = []

#: Named so the claim is falsifiable rather than implicit: these were *considered* and kept.
CONSIDERED_AND_KEPT = [...]
```

It has three parts:

1. **The assumption that makes it empty**, linked to the constant it depends on (`HORIZON`).
2. **A considered-and-kept set.** It names what was examined, so a reviewer can attack a
   specific column instead of guessing at what was looked at.
3. **The revisit trigger.** It says which upstream change invalidates the emptiness.

The plan also routed the argument to the review dimension (leakage) that is supposed to
attack it. Rollback is a one-constant change if the horizon story is rejected.

## The mirror rule for guards

The segmentation run's leakage guard returns a list of `Finding` objects under a stated
contract: *an empty list is not a pass*. A guard has to show that it ran (rules evaluated,
inputs seen) before "no findings" means clean. The same research found a guard rule
implemented as a constant `True`. It asserted a contract rather than verifying one. A rule
that cannot fail is not a guard, and its "failing and clean twin" tests could not have
covered it both ways. See [[Data Sufficiency Refusal]].

Together: **an empty result is only evidence when it carries proof that the search
happened, and what the search covered.**

## See Also
- [[An Unrun Scan Is Not a Clean Scan]] — extends (the same rule for reviewers and scanners)
- [[Label Horizon vs Sampling Window]] — extends (the assumption this list is argued from)
- [[Data Sufficiency Refusal]] — extends
- [[Eval Falsifiability]] — instance-of (a rule that cannot fail measures nothing)
- [[Deferred Decision Status]] — alternative-to (recording what was not decided rather than what was considered)
