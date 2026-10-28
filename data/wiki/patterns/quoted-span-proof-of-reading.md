---
title: Quoted Span as Proof of Reading
tags: [llm, pattern]
summary: Every review finding must carry a quoted_span — the literal source text at the cited line, whitespace-normalised, within ±1 line — so a validator can mechanically reject findings from a reporter that never read the code it cites; convention claims add a spec_citation or must not invoke the spec at all.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/galactus/skills/review-shared/SKILL.md
  - data/raw/claude-docs/galactus/skills/review-shared/references/finding-schema.md
  - data/raw/claude-docs/galactus/skills/review-shared/references/evidence-model.md
  - data/raw/claude-docs/galactus/skills/review-intent/SKILL.md
  - data/raw/claude-docs/galactus/skills/review-correctness/SKILL.md
  - data/raw/claude-docs/galactus/skills/review-architecture/SKILL.md
  - data/raw/claude-docs/galactus/skills/review-runtime/SKILL.md
  - data/raw/claude-docs/galactus/skills/review-performance/SKILL.md
  - data/raw/claude-docs/galactus/skills/review-leakage/SKILL.md
---

# Quoted Span as Proof of Reading

The galactus review subsystem (vendored from Parallax) runs eleven dimension reporters.
Each finding cites a file and line range, and each **must** carry a `quoted_span`: the
literal text found at that line. `validate.py` normalises whitespace and checks the span
against the source within ±1 line. A mismatch rejects the finding.

The rule's stated rationale is one sentence: **a finding that cannot quote the code it
cites did not read it.** A model can produce a plausible file:line and a plausible claim
without opening the file. It cannot produce the literal text at that line without
reading it. This turns "did the reporter actually look?" from a judgement call into a
string comparison.

## Where to quote when there is no obvious line

Many defects are absences, so each dimension says which line holds the anchor:

| Finding | Quote |
|---|---|
| Stale documentation | the doc sentence that is now false |
| Missing test | the untested code |
| Prompt-only safeguard | the prompt sentence carrying the rule |
| Injection | the sink, not the source |
| Leakage ordering | the `fit` line |
| Group key not passed to the splitter | the splitter construction line that omits `groups=` |
| Missing leakage scan | the scoring call or reported-metric line that makes the gap matter |

The pattern is the same each time: quote the line that **makes the absence matter**.

## spec_citation — cite or don't invoke

A companion field covers convention claims. If a finding says code breaches a repo
convention, it must cite the spec file and section (`spec_citation`). If it cannot,
it must not appeal to the spec at all. It can still argue on its own merits. This
blocks "violates our conventions" findings that point at rules nobody wrote down.

## Interaction with the rest of the schema

- The id prefix (IN/CR/SI/TE/SF/AR/RT/SG/CT/LK/PF) must match the dimension. A
  mismatch means the reporter loaded the wrong skill (see
  [[Parallel Dimension Scanner Architecture]]).
- If validation fails, the reporter is retried once. After a second failure the
  dimension is recorded as `failed`, never hand-repaired by the orchestrator. Repairing
  a finding would launder an unread claim through a reader that did read.
- The quoted span is evidence of *reading*, not of *correctness*. Evidence state
  (`verified` / `hypothesis` / `question`) is still a separate axis (see
  [[Merge Impact and Evidence State]]).

## See Also
- [[Review Reporter Ground Rules]] — extends (a mechanical check under the trust rules)
- [[Merge Impact and Evidence State]] — extends (the schema this field sits in)
- [[Evidence Classification Model]] — prerequisite-for
- [[Derive the Gate, Don't Copy It]] — extends (a check computed from source, not asserted)
- [[Verbatim Evidence Quote Verification]] — alternative-to (the same span check applied to model tags)
