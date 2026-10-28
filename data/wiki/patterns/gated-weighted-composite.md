---
title: Gated Weighted Composite Score
tags: [eval, pattern]
summary: "A maturity or readiness score built as a weighted points total plus one hard cap from the single dimension that cannot be averaged away, an independent mandatory-flag rule that forces weak critical dimensions into the plan by name, and a scoping rule that turns two or more flags into a remediation-only plan."
updated: 2026-10-17
sources:
  - data/raw/repos/nonprofit-success-ai/docs--architect-design.md
  - data/raw/repos/nonprofit-success-ai/README.md
---

# Gated Weighted Composite Score

From the design of an assessment agent in the nonprofit-success-ai repo. The agent scores an
organisation's data maturity from an 18-question staff-run assessment and uses the result
to shape a project charter and a 90-day plan. The scoring design is reusable anywhere a
composite score drives a go/no-go or a scope decision.

## The problem with points alone

A plain weighted sum lets strength in some dimensions hide a gap in the one that matters.
In this case, an organisation with good tooling, a strong data culture and capable staff
but siloed data scored "Established" on points. That score would approve an ML project
its data could not support. Using the minimum score has the opposite problem: one weak
dimension wipes out real capacity everywhere else.

## The four-step design

1. **Score each dimension** on a fixed rubric (here five dimensions, 1/2/3).
2. **Weighted composite.** The critical dimensions get double weight (here data
   infrastructure ×2 and governance ×2, the other three ×1, max 21). The total maps to
   bands (7–11 / 12–16 / 17–21).
3. **One override, on one dimension only.** If the dimension the work physically depends
   on is at the floor, the composite is **capped one band up from the floor**, whatever
   the points say. "You can't run a project on data that doesn't exist." The second
   critical dimension (governance) deliberately gets **no** override. A reporting gap is
   a real problem, but it does not stop the work from starting.
4. **A mandatory flag, separate from the override.** If either critical dimension is at the
   floor, it becomes a **required, named workstream** in the plan, never folded into a
   generic "areas to improve" line. This applies even when the override did not trigger,
   so a governance gap that does not cap the score still cannot be quietly skipped.

Then a **scoping rule** maps flags to plan shape. One flag: the remediation workstream
runs alongside a scoped deliverable. Two or more flags: the plan is **remediation-only**.
The flagged workstreams are the deliverable, and the stretch project moves to a later
phase that starts only once the flags clear.

## Why separate the cap from the flag

They answer different questions. The cap protects **the score's meaning** (can this
organisation honestly be called Established?). The flag protects **the plan's content**
(will the weakness actually get fixed?). If they were merged, either every critical
dimension would get a cap (too harsh, and it erases real capacity) or the plan would
only fix dimensions that happen to cap the score.

## Validate with edge-case profiles

The spec pins four synthetic profiles as test vectors, each written to exercise one rule:

| Profile | What it proves |
|---|---|
| All dimensions at the floor | The floor case is consistent and both flags fire |
| Mixed, governance weak | Points keep real capacity visible; the flag names the gap |
| Well-resourced but siloed data | **The override catches what points alone get wrong** (17 → capped) |
| Two critical gaps, strong capacity | The scoping rule stops an unrealistic 90-day plan |

## A mechanical rubric is not a fallback

In the same repo, the intake router has a deterministic heuristic that stands in **when
the model call fails** (see [[Dual Parser with Shared Shape]]). This scorer has no model
in it. The spec defines it as a mechanical rubric, so the deterministic code **is** the
implementation. Keep the two cases separate. A fallback is graded against the model it
replaces. A rubric engine is graded against its own spec vectors.

A downstream **cross-check** catches disagreement between stages. A floor-maturity
organisation that the intake stage routed to an ML bucket raises a "redirect before
chartering" warning. It does not get chartered around.

## See Also
- [[Six-Pillar Agent Engineering Assessment]] — alternative-to (its weakest-pillar rule caps the composite relative to the weakest dimension instead of naming one gating dimension)
- [[Relevance Is the Score, Enrichability Is the Gate]] — extends (separating the ranking number from the hard gate)
- [[Provenance-Tiered Confidence Gate]] — extends (a hard gate layered over a graded signal)
- [[Dual Parser with Shared Shape]] — alternative-to (a deterministic path that stands in for a model, versus one that is the real implementation)
