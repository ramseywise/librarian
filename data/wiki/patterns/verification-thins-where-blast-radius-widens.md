---
title: Verification Thins Where Blast Radius Widens
tags: [patterns, eval, pattern]
summary: "In a self-improving agent setup, the changes with the widest blast radius (global rules, hooks, skills) were the ones with the thinnest automated check: the eval harness validated only that inputs route to the right skill, logged behavioural cases as skipped, and reported a 99% pass rate. A bad rule was caught only by a human."
updated: 2026-10-17
sources:
  - data/raw/repos/guacamayo/README.md
---

# Verification Thins Where Blast Radius Widens

Found in the guacamayo metacognition loop. The loop reads session telemetry, derives
patterns, verifies them against the raw corpus, and proposes config diffs to rules, skills,
and hooks. A human approves each diff. The loop's own README names one link as its weakest:
the changes it graduates.

## The mechanism

A cross-repo eval runner discovers every skill's `evals.json` and writes pass/fail rows. The
runnable format is a set of `{"input", "expected"}` trigger cases. The runner checks only
whether an input string *would route to* that skill. Anything that needs fixtures, an LLM
judge, or multi-step execution is recorded as `needs-harness` and **skipped**. At the last
run the tally was 366 rows, 363 pass and 3 skip, across 51 skills in 7 repos.

Three properties combine:

1. **The check is structural, not behavioural.** It validates routing, not judgment. A skill
   whose body has become wrong still routes correctly and still passes.
2. **The gradient is inverted.** Code changes in one repo get unit tests and a review ladder.
   A Plane 3 change (a rule or hook that every future session loads) has the *widest* blast
   radius and the *thinnest* automated verification. A bad rule lands, a human catches it,
   and a human undoes it by hand.
3. **The pass rate reads as health.** "363/366" looks like a strong suite. It is a strong
   *routing* suite. The behavioural cases that would have failed never ran, so they do not
   count against the score ([[Silence Reads as Clean]],
   [[An Unrun Scan Is Not a Clean Scan]]).

## What follows

- **Rank verification by what a change can break, not by where tests are easy to write.**
  [[Size the Gate to the Blast Radius]] applies the same rule at plan time: anything every
  future session loads goes to the full gate regardless of file count. The eval layer needs the
  same escalation.
- **Report the skip count beside the pass rate.** A `needs-harness` row is a coverage gap
  with a name. Count it as one rather than leaving it out of the denominator
  ([[Telemetry Claim Verification Gate]]).
- **Separate trigger evals from output evals, and do not let the first stand in for the
  second.** Routing accuracy belongs to [[Skill Discovery Failure Modes]]. Whether the
  skill's output is any good needs the behavioural harness in
  [[Skill Eval Pipeline (Blind Comparison + Grading)]].
- **Make write authority mirror verification strength until the gap closes.** The same loop
  narrows what it may write as blast radius widens: memory files are loop-writable, skills
  need per-diff approval, and global hooks and settings are never loop-written. Human
  approval stands in for the missing behavioural gate. That substitute is explicit, not
  accidental ([[Friction Promotion Ladder]]).

## See Also
- [[Size the Gate to the Blast Radius]] — extends (the plan-time version of the same scaling rule)
- [[Silence Reads as Clean]] — instance-of (skipped cases missing from the score)
- [[Skill Eval Pipeline (Blind Comparison + Grading)]] — alternative-to (the behavioural harness the routing check stands in for)
- [[Skill Discovery Failure Modes]] — extends (trigger accuracy as a separate axis)
- [[Telemetry Claim Verification Gate]] — extends (a number without its denominator is not reportable)
- [[Friction Promotion Ladder]] — extends (the levers whose changes go unverified)
