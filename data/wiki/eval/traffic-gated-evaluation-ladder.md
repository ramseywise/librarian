---
title: Traffic-Gated Evaluation Ladder
tags: [eval, rag, pattern]
summary: For a pre-launch recommender, each evaluation method unlocks at a minimum data volume and can decide only certain questions — human blind rating now, LLM judge, offline replay (ranking only, never retrieval), interleaving, then A/B — so you climb the ladder instead of waiting for the top rung.
updated: 2026-10-16
sources:
  - data/raw/claude-docs/akira/docs/technical-feasibility.md
  - data/raw/claude-docs/diskoe/docs/technical-feasibility.md
  - data/raw/claude-docs/playground/docs/technical-feasibility.md
  - data/raw/claude-docs/kiez-archive/docs/technical-feasibility.md
---

# Traffic-Gated Evaluation Ladder

A feasibility study for an events recommender (repo akira) asked "how do we evaluate before
we have users?" The answer was not one method but a ladder: each rung has a **minimum data
requirement** and a list of questions it **can and cannot decide**. "Do not wait for a rung"
— run the one you can afford now and design it so the next one is possible.

| Rung | Minimum data | Decides | Cannot decide |
|---|---|---|---|
| Human blind rating | available now | whether output beats the incumbent | anything about ranking; the monotone-gap thesis needs ~356 per stratum |
| LLM-judge offline eval | calibrated gold set (see [[Synthesize the Cheap Half]]) | scaled quality scoring | dimensions where the judge fails calibration |
| Offline replay | 500 logged tuples floor, 2000 comfortable (paired difference) | **ranking** changes | **retrieval** changes — a candidate never shown has no logged outcome |
| Interleaving (team-draft) | ~2.6k sessions for a 5% effect | ranking AND retrieval changes | absolute rates, retention |
| Online A/B | ~23.6k sessions for the same effect; post-launch, 12–18 months out | retention, absolute decision rate, guardrails | — but never use it for weight tuning |

## Non-obvious mechanics

- **Replay evaluates ranking, never retrieval.** It only scores items the logged policy
  showed. It is also position-confounded: unbiased IPW-NDCG needs a ≥5% position-randomized
  slice, and that slice must be designed into the *first* ranker — it cannot be added
  retroactively to logs that already exist.
- **Interleaving is ~9× cheaper than A/B** (2608 vs 23581 sessions for a 5% effect) and,
  unlike replay, covers retrieval changes. Its sensitivity favours large-stepped experiments
  over fine weight sweeps.
- **The decisive human test compares against the incumbent.** Three arms — floor /
  incumbent / proposal — where only proposal-vs-incumbent is decision-relevant. Allow ties
  and score wins ÷ (wins + losses), use item-level majority as the primary statistic, and
  replace a fixed "≥70% preferred" bar with a confidence-interval-bound gate (at n=67 the CI
  is ±11 points). A monotone dose-response claim gets a trend test (Jonckheere–Terpstra).
- **Length-match the arms.** Otherwise raters reward verbosity and the experiment measures
  output length. Rater recruitment is the largest validity risk.
- **The experiment's data becomes the permanent regression set** — the decisive test is
  also the first golden suite.

## See Also
- [[Eval Ladder]] — extends (the same climb, gated on traffic instead of maturity)
- [[Ship Logging Before Features]] — depends-on (replay and IPW need the logged result set and randomized slice)
- [[Synthesize the Cheap Half]] — related (what may be synthesized to fill the lower rungs)
- [[Human Agreement Ceiling Protocol]] — related (the rater-side statistics for the first rung)
- [[Q0–Q5 Quality Ladder]] — alternative-to (a per-feature quality ladder rather than a traffic-gated one)
