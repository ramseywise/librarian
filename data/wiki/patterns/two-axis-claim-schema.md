---
title: Two-Axis Claim Schema
tags: [llm, pattern]
summary: Every claim from a decide-family skill carries confidence and decision_impact as orthogonal fields, a falsifiable statement, an if_wrong consequence, and a check whose "settles" criterion is mandatory — because the speculative × fatal cell is the highest-value one and the one teams rationalise away.
updated: 2026-10-16
sources:
  - data/raw/claude-docs/galactus/skills/decide-shared/references/claim-schema.md
  - data/raw/claude-docs/guacamayo/skills/review-defense/references/claim-schema.md
  - data/raw/claude-docs/galactus/skills/decide-shared/SKILL.md
  - data/raw/claude-docs/galactus/skills/assumption-audit/SKILL.md
  - data/raw/claude-docs/galactus/skills/fog/SKILL.md
  - data/raw/claude-docs/guacamayo/skills/review-defense/SKILL.md
---

# Two-Axis Claim Schema

The shared output contract for the decide family (`/assumption-audit` → `AA-`,
`/war-game` → `WG-`, `/fog` → `FA-`). It is the decide-side sibling of the review
family's finding schema in [[Merge Impact and Evidence State]]: the same insight — *how
sure* and *how much it matters* are different questions — applied to claims about a design
rather than findings about a diff.

```yaml
id: <source>-<NNN>
claim:
  title: short
  statement: falsifiable — someone could show it is wrong
  basis: what it rests on (quoted source, observed behaviour, inference)
  if_wrong: what stops working
confidence: certain | likely | speculative | unknown
decision_impact: fatal | costly | recoverable | cosmetic
check:
  method: read | grep | run | build-risky-part-first | ...
  cost: minutes | hours | days | unknowable-before-building
  settles: the observation that would resolve it   # required
recommendation:
  action: test | mitigate | accept | descope | escalate
```

## The two axes are orthogonal

`confidence` is how sure the author is that the claim holds. `decision_impact` is what
happens to the decision if it does not. Neither derives from the other. The grid:

| | fatal | costly | recoverable | cosmetic |
|---|---|---|---|---|
| **certain** | act now | act | note | ignore |
| **likely** | act now | check | note | ignore |
| **speculative** | **check first** | check | note | ignore |
| **unknown** | escalate | check | note | ignore |

The `speculative / fatal` cell is the one to look at hardest and the one most often
rationalised away. Teams work the `certain` column because it is legible — it produces
findings you can defend — while the cheap-to-check, catastrophic-if-wrong guess sits
unexamined. Expected cost is probability × consequence, and the consequence term has the
larger range, so a speculative fatal outranks a certain cosmetic.

## `settles` is required

A check without a settling criterion is activity, not a check. *"A criterion vague enough
that it cannot fail is not a criterion."* `cost: unknowable-before-building` is a legal
answer — it routes the recommendation to `mitigate` or `escalate`, never to an invented
check.

## Ranking

Impact-major, confidence-minor; cheaper check breaks ties. Within the same cell, the
cheaper check goes first because it buys the same information sooner. Every decide-family
report then closes with **"the one to check/fix first"** and **"what you could not see"**.

## See Also
- [[Merge Impact and Evidence State]] — alternative-to (same two-axis insight, review-side)
- [[Deferred Decision Status]] — extends (a deferral is a claim with a revisit trigger as its `settles`)
- [[Assumption Audit]] — instance-of (AA- claims)
- [[Collapse Site Detection]] — instance-of (FA- claims)
- [[Capability vs Phase Skills]] — prerequisite-for (the family whose output this governs)
- [[Adversarial Plan War Game]] — prerequisite-for (the war game whose threats use this schema)
- [[Evidence Classification Model]] — alternative-to
