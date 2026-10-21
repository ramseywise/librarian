---
title: Paired Input-Perturbation Eval
tags: [eval, pattern]
summary: "To decide whether a skip gate may ignore a field, perturb only that field on real rows with everything else held fixed, run the production prompt on both copies, and diff the outputs: report material vs immaterial changes separately for a shift that stays inside an output bucket and one that crosses it, state the real N, and name the missing same-input noise control as a limitation."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-22-dis281-stage2b-schedule-sensitivity-eval.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-22-dis281-stage2b-schedule-sensitivity-eval.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-22-dis281-stage2b-schedule-sensitivity-eval.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-22-dis281-stage2b-schedule-sensitivity-eval.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-22-dis281-stage2b-schedule-sensitivity-eval.md
---

# Paired Input-Perturbation Eval

An enrichment pipeline skipped the paid model call when a row's content hash was
unchanged. Recurring events changed dates on every re-crawl, so the open question was
whether dates could be dropped from the hash. [[Shadow Signal Before Gate Change]] counts
*how often* a re-enrichment is date-only. That leaves a second question: **does the model's
output actually depend on the date?** If it does, dropping dates from the hash would
freeze stale tags. The akira plan (#281 Stage 2B) answered it with a paired perturbation
run.

## The design

1. **Sample real rows** with the existing stratified sampler from the
   [[Offline Prompt Experiment Runner]]: up to 5 per completeness bucket, frozen into a
   manifest so the run can be repeated.
2. **Make three copies of each row:** the baseline, a shift that stays inside one output
   bucket (+1h, still the same evening), and a shift that crosses a bucket (+4h, moving
   from the "after work" bucket toward "late night", which the prompt's own vocabulary
   rules separate).
3. **Perturb only the fields that reach the prompt.** The hash's list of date fields was
   broader than what the prompt builder reads. For events, only `start_at`, `end_at`, and
   their `raw_data` mirrors are shown to the model. Perturbing keys the model never sees
   adds only noise that the diff then has to explain away.
4. **Call the gateway and the pure pipeline directly**, never the run-and-write entry
   point. The harness is read-only by construction rather than by a dry-run flag.
5. **Diff the flattened outputs field by field.** Changes to the fields the prompt tells
   the model to derive from time of day (context tags, vibe tags, energy) count as
   **material**. Every other changed field is still reported. A nonzero rate on fields
   that should not move with the date is a finding in its own right, not noise to
   average away.

## Scoping and honesty rules

- **Scope to the input shape that actually carries the signal.** Only events had a clean
  start/end datetime in the prompt. Activities had one free-text availability line and
  bars had raw opening hours, so perturbing them would not test the question.
- **The bucket boundaries are tunables, not facts.** No day-part constant existed
  anywhere in the code, because the model infers day part from the raw datetime. That is
  why the boundary has to be measured. The plan labels its +1h/+4h deltas as a starting
  default that the gate decision may revise.
- **Report the actual N and never pad it.** The cap was 15 events × 3 variants = 45
  calls, well under $1, with a spend-ledger ceiling as well.
- **Name what the design cannot see.** At temperature 0.2, a "changed" field may be
  sampling noise. Without a baseline-vs-baseline control, sensitivity cannot be separated
  from [[Eval Non-Determinism]]. The plan records this as a limitation and leaves a
  temperature-0 repeat control to the gate decision. A synthetic ±h shift is also not
  the same distribution as a real schedule correction, so the real re-import ratio stays
  the cross-check.

## Why it is a separate stage

The gate decision needs two numbers. **How often** the field changes alone comes from the
shadow hash. **Whether it matters** to the output comes from this eval. Each is cheap
alone. Combining them into one "just try excluding dates" change would ship a gate whose
effect on output quality nobody measured.

## See Also
- [[Shadow Signal Before Gate Change]] — extends (the frequency half; this is the sensitivity half)
- [[Spend Gate Before the Model Call]] — prerequisite-for (the gate whose key is in question)
- [[Offline Prompt Experiment Runner]] — extends (same harness; pairs are input variants, not prompt variants)
- [[Eval Non-Determinism]] — related (the missing same-input control)
- [[Ranker Weight Sensitivity Sweep]] — alternative-to (perturbing parameters of a pure function instead of inputs to a model)
