---
title: Differential Parity Testing Against the Original
tags: [eval, llm, pattern]
summary: When porting logic from one runtime to another, fixtures encode what the author believed the old behaviour was — the same belief that produced the port — so only executing the original implementation against the port over randomised payloads can disagree; three shipped defects sat behind a fully green suite until that was done.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/diskoe/docs/research/2026-08-27-n8n-port-parity.md
  - data/raw/claude-docs/playground/docs/research/2026-08-27-n8n-port-parity.md
  - data/raw/claude-docs/diskoe/docs/research/2026-08-28-src-scripts-review.md
  - data/raw/claude-docs/playground/docs/research/2026-08-28-src-scripts-review.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-05-dis26-parity-coverage.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-05-dis26-parity-coverage.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-05-dis26-parity-coverage.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-05-dis26-parity-coverage.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-05-dis26-parity-coverage.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-03-dis26-parity-coverage-gap.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-03-dis26-parity-coverage-gap.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-03-dis26-parity-coverage-gap.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-03-dis26-parity-coverage-gap.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-03-dis26-parity-coverage-gap.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-03-dis26-parity-coverage-gap.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-03-dis26-parity-coverage-gap.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-03-dis90-parity-testtimeout.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-03-dis90-parity-testtimeout.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-03-dis90-parity-testtimeout.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-03-dis90-parity-testtimeout.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-03-dis90-parity-testtimeout.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-03-dis90-parity-testtimeout.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-03-dis90-parity-testtimeout.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-03-dis90-parity-testtimeout.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-03-dis90-parity-testtimeout.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-03-dis90-parity-testtimeout.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-03-dis90-parity-testtimeout.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-03-dis90-parity-testtimeout.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-03-dis90-parity-testtimeout.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-03-dis90-parity-testtimeout.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-23-dis371-enrichment-vocabulary.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-23-dis371-enrichment-vocabulary.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-23-dis371-enrichment-vocabulary.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-23-dis371-enrichment-vocabulary.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-23-dis371-enrichment-vocabulary.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-23-dis371-enrichment-vocabulary.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-23-dis371-enrichment-vocabulary.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-23-dis371-enrichment-vocabulary.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-23-dis371-enrichment-vocabulary.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-23-dis371-enrichment-vocabulary.md
---

# Differential Parity Testing Against the Original

Found while porting four low-code workflow exports (24 JavaScript code nodes) into an
in-process TypeScript enrichment chain in the diskoe repo. The port had unit tests, the
tests were green, and three defects had shipped anyway.

## The mechanism

**The original is the reference; the port is the thing under test.** This direction is
not aesthetic. The old workflows had already written hundreds of rows at a given
`enrichment_version`. If port and original disagree, the port is wrong *by definition*,
because a port that "improves" on the original silently splits the column: rows written
before the cutover mean one thing, rows after mean another, and nothing in the schema
records which is which.

**Fixtures cannot find transcription errors.** A fixture test encodes the author's belief
about the old behaviour. The port encodes the same belief. Both go green together. The
only instrument that can disagree is the original itself: load each original code node
into a `vm` sandbox, feed the same randomised payloads (1,200 per node) to both, and diff
the outputs.

## What it found

Three defects, none visible to code review, each covered by a green fixture:

- A hard-coded `content_type = "activity"` line one vertical had and the others did not —
  omitted entirely; 914/1200 payloads diverged.
- Three per-vertical `normalizeDiskoeFit` functions had visibly different *maps* (ported
  as a table) and invisibly different *fallbacks* (`null` + raw passthrough vs. always
  `'standard'`) — unified onto one rule.
- One vertical wrapped scalars into arrays and used `||`; the others used `??` — unified
  onto `??`, so bare strings reached `text[]` columns and empty strings reached scalar
  columns the original had always nulled.

The shared root cause: **the port unified on the axis that obviously differed and silently
unified the axes that also differed.** Boilerplate is exactly where a transcription port
goes wrong, because nobody reviews boilerplate.

## Practices that fell out

- **Order can be load-bearing.** A `blocking_reasons` array was joined into a string and
  persisted, so the *order* flags were appended in — which differed per vertical — had to
  be transcribed. Key order inside a `jsonb` payload, by contrast, carries no meaning; the
  test sorts keys before comparing. Decide per field which it is.
- **Assert intentional divergences.** Where the port is deliberately safer (returning
  `needs_human_review` where the original threw and silently wrote nothing), write a
  parity test that asserts the divergence, so it stays a recorded decision instead of
  drifting back into looking like a bug.
- **The reference artefacts are test input, not documentation.** The ~250KB of exported
  workflow JSON was deleted as "docs" once the port was "done"; the parity tests went with
  it, and the port carried its defects for two days behind green. Tests should read the
  originals directly and fail loudly when they are missing. The repo was also not under
  version control at the time, so the deletion was total — see
  [[The Untested Copy Wins]] for the sibling finding.
- **Coverage honesty.** Pure-function nodes (15 of 24) were differentially covered;
  orchestration nodes that reach back into earlier nodes (prompt assembly, stored-output
  preparation) had fixture coverage only — named as the obvious next place to look rather
  than counted as covered.
- **Check the data the original wrote.** 40 rows written by the original in the affected
  verticals were inspected for each defect's signature; all showed the values the *fixed*
  code produces. That independently confirms the fix direction and bounds blast radius.

## Third time: coverage expansion finds defects again

A follow-up issue extended differential coverage to nine low-code nodes that had only
fixture tests. The new suites execute the **original nodes in a vm** against 300
randomized payloads per vertical and compare line by line; with the fixes stashed, 6 of 15
new tests failed, restored all 15 pass. They found **4 more port defects** — the third
time new differential coverage surfaced defects behind a green fixture suite. Review
called it a lesson rather than an anecdote: fixture tests confirm what the port does;
only differential tests confirm what it is *supposed* to do. The defect classes:

- **`??` vs `||` are not equivalent.** `??` falls back only on null/undefined, `||` on any
  falsy value; the port's `??` let empty strings reach columns the original always nulled.
- **A fallback value that was never legal.** A `content_type` default of `bar_restaurant`
  where the original normalised to `["bar","restaurant"]` with default `restaurant`.
- **A vertical routed to the wrong helper** by a mistranscribed branch condition.
- **An over-general helper replacing per-vertical chains.** The prompt summary builder used
  one generic picker where each original input node had its own field-fallback chain; the
  existing test asserted structure, not chain detail, so it could not catch it.

**Version bump asked explicitly, answered no.** The prompt text changed, but the
enrichment version identifies the output *contract* (schema, enums, cardinalities), the
re-enrichment cache key uses `schema_version` rather than a prompt version, and the fixes
move the port *toward* fidelity — new rows are more faithful to what the version always
meant. **Honest remainders:** 5 QC nodes stay fixture-only and the record says so (9
uncovered → 5), and one divergence is asserted as a labelled intentional-divergence test.

## Planning the coverage expansion (akira DIS-26 plan, 2026-09)

The plan for that follow-up added three design rules:

- **Composite reference when the port merged several originals.** One ported function
  merged two original nodes ("prepare stored output" followed by "flatten row"). Testing
  only the second node would miss divergences, because the fallbacks and defaults lived
  partly in the first. The reference helper chains both original nodes exactly as the
  workflow wired them and diffs the result against one call to the port. **The defects
  live in the seam between merged originals.** The helper is a ~15-line wrapper around
  the existing sandbox loader, checked against a control payload before the fuzz run is
  trusted.
- **A manual trace is a head start, not evidence.** The plan traced candidate
  divergences by reading the node code beside the port. The refine pass then found one of
  those claims wrong by *executing* the original node, not re-reading it. One vertical
  wrapped scalars into arrays and did not null-coerce. Acting on the original claim would
  have applied one shared fix where two opposite per-vertical fixes were needed. The rule
  that came out of it: "do not skip writing the test and go straight to editing from this
  doc's prose."
- **Reachability decides whether "fix in place" is safe.** Each candidate was traced
  through the live pipeline order. Sanitize already narrows every affected field before
  the ported function runs, so the divergent paths were reachable only by calling the
  function directly with synthetic payloads, and none of the ~300 stored rows could have
  been written through them. Fixing the port therefore could not contradict existing data.
  The one escalation rule: a divergence in a field that sanitize does *not* narrow means
  stop and ask, naming whether anything downstream reads it.
- **Size payload counts by measurement, per file.** Chained nodes cost more per payload,
  so the new suites used fewer than 1,200 payloads. Timeouts were set per file under the
  repo's existing convention, never as a global bump.

## A load-dependent flake in the parity suite

The parity tests later began timing out under full-suite load (5774ms against vitest's
5000ms default, about 1100ms in isolation). This suite exists because it caught defects a
green fixture suite missed, so a flake here teaches people to re-run and ignore a parity
red. Fixing that habit was the actual goal. The fix rules:

- **Fix the files on the same curve, not just the one that failed.** Measuring every file
  in the directory under load showed a second file 128ms from the limit and a third one
  step behind it. All three got the override. Two files two orders of magnitude under
  budget were deliberately left alone: don't set a number nothing measured.
- **Per-file, never global.** A per-`describe` `{ timeout: 15_000 }` was chosen over a
  config-level project override or a global `testTimeout` raise. A global raise would
  hide a real future hang in about 107 unrelated files. The per-file form also puts the
  number where a reader meets the failure.
- **Size from the measured worst case.** 15s is the smallest round number that clears
  the worst measured case by more than 2x, while a real hang still fails in seconds.
  Review re-measured under two concurrent suites, got 6389ms (2.3x headroom, not the
  2.6x the plan claimed), and recorded the conservative figure.
- **The rationale goes next to the number.** Review's one finding: the plan argued for
  per-file placement so the value would be visible where it fails, but the reasoning
  lived only in the plan, and the plans directory is gitignored. Each block now carries a
  comment with the measured range and the instruction to re-measure before lowering and
  never to raise the value to mute a flake.
- **One green run is weak evidence for a load-dependent fix.** The honest verification
  was that the value traces to the measured table, plus durations captured in at least
  one deliberately contended run.

## Narrowing a Type Must Not Shrink the Fuzz Alphabet (akira vocabulary refactor, 2026-09)

A refactor made the enrichment vocabulary's types match what the runtime enforces. It
removed `'rejected'` from the AI-status type, because no vocabulary table lists it, the
prompt never asks for it, and the sanitizer rewrites any unrecognized status to `'partial'`
before the review gate runs. The plan also removed `'rejected'` from the parity suite's fuzz
alphabet. Review sent that back. The parity harness calls the ported gate **directly**,
bypassing the sanitizer, and all three frozen originals still block on `'rejected'`. At the
harness's granularity the port and the original genuinely disagree. Deleting the value from
the alphabet hid the disagreement. It did not resolve it.

- **"Unreachable in production" is a claim about the pipeline, not about the harness.**
  The reachability argument above (sanitize narrows first) decides whether fixing the port
  is safe. It does not entitle you to stop fuzzing the value.
- **Record it as a named intentional divergence.** The fix restored `'rejected'` to the
  alphabet. A named, commented filter now skips those payloads from the structural
  comparison, because the affected fields cascade too far to rebuild as an output transform.
  A fourth `INTENTIONAL DIVERGENCE` test asserts that the original still blocks and the port
  no longer admits the value.
- **The plan missed it because its verification grep matched nothing.** The plan grepped
  for a function name that does not exist in the codebase. The empty result was read as
  "single call site", and so the planner never looked at the test that would have broken
  ([[Scan-Floor Guard Against Silent No-Op Checks]]).
- **A byte-identity proof for a no-behaviour refactor.** Composing about 130 transcribed
  vocabulary literals from shared tables was proved by three pinned prompt hashes. Every
  table renders into a hashed prompt template, so dropping one character anywhere changes a
  hash. The flattened exports remained the public surface, as the composition's *output*,
  so no consumer changed its imports.

## See Also
- [[Eval vs Test Distinction]] — extends (a parity suite is a test with an executable oracle, not a belief)
- [[The Untested Copy Wins]] — extends (the duplication class the port's unified functions were meant to prevent)
- [[TDD as Coding-Agent Harness]] — alternative-to (an author-written failing test vs. an executed original as oracle)
- [[Specification by Example]] — related (randomised payload diffs as examples the author did not think to write)
- [[A Fake That Conforms to a Broken Seam]] — alternative-to (fakes pinned to the port vs behaviour pinned to a reference)
- [[Comparable Tables, Not One Source]] — related (intentional divergence from one original node, recorded with a do-not-regenerate note)
- [[Cross-Surface Order Parity Test]] — related (parity between live surfaces sharing one derivation)
