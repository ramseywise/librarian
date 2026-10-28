---
title: Generation-Under-Contract Eval Harness
tags: [eval, pattern]
summary: "A third kind of eval, separate from retrieval and interaction grading: the harness itself drives a producer through generate → validate → repair → fallback and measures process facts (first-pass validity, repair convergence, fallback rate). Two things make it work: a producer contract that returns those facts, and a scripted dry-run provider whose results vary across cases."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/galactus/docs/plans/2026-08-11-gal-4-phase3-ai-evals-extraction.md
  - data/raw/repos/galactus/.claude--docs--plans--2026-08-11-gal-4-phase3-ai-evals-extraction.md
---

# Generation-Under-Contract Eval Harness

This page comes from moving galactus's case-study eval harness into the shared project
template. The template already had an `evals/` tree of about 40 files, and the obvious
question was whether the new harness duplicated it. It did not. The two share the words
"eval", "metrics" and "reports" and almost nothing structural.

## Two eval kinds

| | Grading suite | Generation-under-contract harness |
|---|---|---|
| Input | recorded rows, golden answers | *briefs*, not outputs |
| Who produces the output | the system, earlier, out of band | the harness, during the run |
| Loop | none: one grade per row | generate → validate → repair × N → fallback |
| Unit measured | per-row correctness | per-case **process facts** |
| No API key | judge returns `None`, metric skipped | scripted provider, full metrics |
| Gate | thresholds file | exit 1 unless contract-valid rate is 100% |

The template already separated two grading kinds (retrieval golden-QA and interaction
evals) inside one root. The harness is a third kind by the same reasoning, so it went in
as a **sibling sub-package under the existing eval root**, not as a competing `ai/evals/`
root. The issue's literal path was shorthand, and copier's own config said evals are a
sibling of every source root, not part of one.

## The four metrics, and why they constrain the producer

`contract_pass_rate` (validity on the *first* generation), `repair_convergence`,
`fallback_rate`, `grounding_rate`, plus a hard gate on `contract_valid_rate`.

First-pass validity **cannot be rebuilt from the final result**. A run with zero repair
attempts could be a clean first pass, or a run that was given no repair budget. The
original harness read these facts from a mutated pipeline-state object. So the extracted
producer contract has to return the process facts along with the artifact:
`(output, first_pass_valid, repair_attempts, used_fallback)`. If you type the producer as
a plain `case -> output` callable, two of the four metrics silently disappear. This is the
harness-level version of [[Write-Only Fields and the Reader Map]]: decide what the reader
needs before you define the interface.

Only three parts of the original runner were case-specific: turning a case into a
contract, running a producer against it, and validating the output. Those became three
callables, a Protocol for each. Metrics, reporting, the grounding heuristic, and the
case loader's validation were already generic.

## The dry-run provider is the asset, and the risk

The template's way of degrading was graceful **skipping**: no key, so judges are
unavailable and the metric reads "n/a". That is a reasonable contract for a judge. It is
fatal for a harness whose claim is "runs with no key and no spend", because a run that
skips everything reports nothing.

The galactus scripted provider was deliberately *not* a stub returning one canned draft:

- It reads the requested limits from the contract and overshoots them only on cases
  marked `hard`.
- It tightens its output when asked to repair, except for cases marked `stubborn`, which
  never converge and so exercise budget exhaustion and fallback.
- A **stress-profile table** gives each hard case a *different* breach class (word count,
  colour reference, budget exhaustion), so each repair path runs separately.

The property that has to survive is **variation across cases**. An extraction whose
scripted provider passes every case has technically kept `--dry-run` and actually
destroyed it: it reports a meaningless 100%. A test that asserts the results are not all
the same (`test_dry_run_spread_is_not_degenerate`) is what catches this, and the plan
called it the phase's main failure mode. See [[Eval Falsifiability]] for the general rule
that scripted providers must respond to their inputs.

## Byte-identical baseline as the regression contract

Before anything moved, one dry run was captured as eight numbers (cases, the four rates,
contract-valid rate, errors, total LLM calls). Moving the code had to reproduce them
exactly. Sources of nondeterminism were checked first: no RNG, deterministic indexing,
sequential runs. The only environment coupling (log level) affected stderr only, so the
assertions read stdout only. The baseline was then pinned as a test in the case study, so
a refactor that moves any number fails right away.

## Decoupling by projection, not by upgrade

An earlier phase had deliberately typed the run registry's eval adapter as a plain
`dict[str, float]` plus a named headline metric, so the registry would not depend on this
harness. The tempting move is to "upgrade" that adapter to the new result type. That
would reverse a decision made on purpose. Instead the harness offers a one-line
`metrics_dict()` projection. Two values needed care: `repair_convergence` can be `None`,
and projecting it to `0.0` would read as "converged instantly", so it maps to a
not-applicable sentinel instead.

## See Also
- [[Eval Falsifiability]] — extends (scripted providers must vary with their inputs)
- [[Build the Checker Before the Generator]] — extends (the validator that the repair loop runs against)
- [[Eval vs Test Distinction]] — extends (a third eval kind beside grading suites)
- [[Experiment Tracking Schemas]] — extends (the registry the harness projects into)
- [[Write-Only Fields and the Reader Map]] — instance-of (a producer type that drops the facts the metrics read)
- [[Gate Pass Rate Measures Effort, Not Readiness]] — related (first-pass vs final-pass measurement)
- [[Eval Ladder]] — instance-of
