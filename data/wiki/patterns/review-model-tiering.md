---
title: Review Model Tiering by Breadth and Severity Bias
tags: [eval, pattern]
summary: "A side-by-side run of the same review agent on three model tiers showed the tiers differ in breadth and in which way they bias severity, not just in depth. So the mid tier is the default, the top tier is added on paths where silent corruption costs money, the small tier is only a pre-filter, and when several models review the same code, findings they agree on are elevated while a finding only one model raised has to be verified."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/guacamayo/docs/plans/2026-07-22-akira-model-experiment.md
  - data/raw/repos/guacamayo/.claude--docs--plans--2026-07-22-akira-model-experiment.md
---

# Review Model Tiering by Breadth and Severity Bias

The experiment ran akira's scan mode (a defect finder) and wander mode (a question
generator) on small, mid and top model tiers. Each run covered the same files in about six
repos, and every finding was cross-checked. The answer to "which model should review"
turned out to have more than one dimension. The tiers differ on at least three axes, and
the routing rule follows from all three.

## What differed by tier

| Axis | Small tier | Mid tier | Top tier |
|---|---|---|---|
| Breadth | broad but surface-level | broad, mechanism-level | **narrower**: deepest on what it finds, but missed an inline system prompt, a route bounds check and a train/test contamination that the mid tier caught |
| Severity bias | **inflates** (it flagged two items as blockers on one repo) | calibrated | **deflates** (it called an inverted memory-store write a suggestion) |
| Unique catches | an off-by-one, a `zip(strict=False)` bug in cosine similarity | a duplicated LLM call, train/test contamination | a wrong index in a time-series model, a lagged strategy-history feature: both critical, both on financial/ML paths |
| Question mode | questions drifted toward defect reports ("is this a bug?") instead of design intent | sharp `file:line` questions | not tested |

Model choice therefore changes **which** findings appear, not only how good they are. The
severity bias also points in opposite directions at the two ends. A review merged from
several tiers needs calibration guidance in the scan prompt, or the small tier's blockers
and the top tier's suggestions will be read as if they used the same scale.

## Routing rule

- **Default to the mid tier** for routine scan and wander passes.
- **Add the top tier** on eval logic, ML and financial code, security-adjacent paths, and
  anything where *silent corruption has downstream cost*. Its unique catches were exactly
  the kind that never raise an error.
- **Small tier: bulk pre-filter only.** Discount its severity labels.
- Wander prompts must say "design intent and edge cases, not defects". Smaller models
  otherwise turn question generation back into bug hunting (see
  [[Wander — Question-Generating Review Agent]]).

## Cross-model merge rule

When more than one model reviews the same code:

- A finding confirmed by **2+ models** is elevated automatically.
- A finding **unique to one model** is verified explicitly before anyone acts on it.

This is the multi-model version of agreement-as-evidence: overlap between models is
treated as corroboration, and single-model output as a hypothesis. It fits the evidence
states in [[Evidence Classification Model]]. The top tier's lower breadth is the reason
"top tier only" is not a safe shortcut. The two critical bugs it found alone would have
been missed by a mid-tier-only run, and the mid tier's catches would have been missed by
a top-tier-only run.

## Untested and open

The plan left the auto-fix actuator (dao) and top-tier wander untested. Its hypotheses
were: mid tier as the minimum for dao, top tier for high-stakes documents, and top-tier
wander deepest on critical paths with the same breadth tradeoff. Treat these as
hypotheses, not results.

## See Also
- [[Parallel Dimension Scanner Architecture]] — extends (which model runs each scanner)
- [[Wander — Question-Generating Review Agent]] — extends (question-mode drift on small models)
- [[Evidence Classification Model]] — related (single-model findings stay hypotheses until verified)
- [[Confidence That Is Not a Probability]] — related (model tiering was one of the issues that assumed a calibrated number)
- [[Test-Gated Auto-Fix with Per-Hunk Revert]] — related (the untested dao tier)
