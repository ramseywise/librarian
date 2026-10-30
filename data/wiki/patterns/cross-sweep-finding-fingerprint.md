---
title: Cross-Sweep Finding Fingerprint
tags: [patterns, eval, pattern]
summary: Giving every review finding a stable fingerprint — sha256(file + symbol_scope + category + normalized_title)[:12] — so findings can be tracked across sweeps and repos into new/persistent/recurring/resolved/regressed states, with deterministic, advisory promotion rules (count, age, spread, unmoved, regression) instead of an LLM deciding what matters.
updated: 2026-10-30
sources:
  - data/raw/claude-docs/guacamayo/docs/research/2026-07-27-cross-repo-intelligence.md
  - data/raw/claude-docs/guacamayo/docs/research/2026-07-29_dashboard-tabs_review.md
  - data/raw/claude-docs/guacamayo/docs/research/2026-08-09_friction-learning-loop_telemetry-sinks.md
  - data/raw/repos/nonprofit-success-ai/.claude--docs--research--2026-08-18_dssg-second-brain_codemap-review.md
---

# Cross-Sweep Finding Fingerprint

A review sweep produces findings; the next sweep produces findings again. Without an
identity for a finding there is no way to say "this one is still here", "this one came
back", or "this one has now appeared in three repos". The guacamayo cross-repo
intelligence design supplies that identity and the rules that act on it.

## Source of truth is the JSON, not the Markdown

The sweep writes a JSON file per run; the Markdown report is a **rendered view** of it.
Every trend computation reads JSON. This matters because the Markdown is what humans
edit and annotate, and an annotated report is no longer a faithful record of what the
scanner found. (A later schema audit found the opposite drift in the findings JSONL: it
had quietly dropped `id`, `source`, `evidence.state`, `merge_impact`, and `symbols`
relative to the canonical finding schema — the JSON must actually carry the schema for
this to hold.)

## The fingerprint

```
FindingFingerprint = sha256(file + symbol_scope + category + normalized_title)[:12]
```

- `file` and `symbol_scope` pin it to a location that survives line-number churn. *(Design intent; the shipped digest keys on `start_line` instead. See "As built" below.)*
- `category` (the scanner dimension) and a `normalized_title` (lower-cased, whitespace-
  and number-stripped) pin it to a defect class without being sensitive to wording.
- Twelve hex characters is enough for a per-repo namespace and short enough to quote.

A finding whose fingerprint changes because the symbol was renamed is, correctly, a new
finding — the old one resolves. That is a known cost, accepted over fuzzy matching
because fuzzy matching makes the trend states non-deterministic.

## Trend states

Each fingerprint carries a `TrendEntry` with one of:

| State | Meaning |
|---|---|
| `new` | first sweep in which it appears |
| `persistent` | present in consecutive sweeps |
| `recurring` | present, absent, present again |
| `resolved` | absent after being present |
| `regressed` | was `resolved`, now present again |

## Promotion rules — deterministic and advisory

Promotion changes the finding's displayed severity; it never auto-fixes or auto-files.

| Rule | Trigger |
|---|---|
| Count | seen in N = 3 sweeps → suggestion becomes important; N = 5 → blocker |
| Age | open > 30 days |
| Spread | same fingerprint-class in 3+ repos |
| Unmoved blocker | a blocker unchanged across 2 sweeps is escalated to the operator |
| Regression | `regressed` state auto-promotes one level |

All rules are pure functions of the trend history, so the same JSON always yields the
same promotions and a reviewer can recompute them by hand. The design gates the trend
stage behind **three real sweeps** before any rule fires — a rule tuned on synthetic
history would promote the wrong things.

## Disposition is the missing half

Fingerprints say whether a finding is still present; they do not say whether anyone
*decided* anything about it. A dashboard audit found zero findings with a disposition
because the workflow is asynchronous: review runs before commit, and the operator — never
an agent — commits. Disposition (`fixed | accepted | rejected | deferred`) is therefore
only knowable at commit or PR-merge time, which argues for a post-merge hook that writes
it back against the fingerprint rather than asking the reviewer to guess at review time.
Until that exists, "true positive rate" cannot be computed, only "still present rate".

## As built: the digest has no repo namespace (2026-08 code review)

A code review of the guacamayo implementation found the digest key is
`file_path|start_line|category|reporter|title` (sha256). It has **no repo or user
component**, and it differs from the design formula above. It uses `start_line` rather than
`symbol_scope`, so a finding whose line shifts gets a new fingerprint and reads as
resolved-plus-new rather than persistent. The trend states only survive line churn once
the digest follows the design. Today this
is contained one layer up, not by the digest. Sweep files are named `{repo}-{date}.json`, and
the previous-sweep lookup globs `{repo}-*.json` before any set-difference. So two repos with
an identical `file:line|category|reporter|title` never meet in one comparison.

It breaks as soon as anything aggregates fingerprints *across* repos into one set, for
example a shared findings log deduped by fingerprint alone. Folding `repo` into the digest
needs no structural migration, because `repo` is already a sibling field on the sweep record.
But every digest value changes, so the **transition sweep reports 100% new and 100% resolved
for identical findings**. That is a one-time trend blip, not data loss. Plan for it: run the
cutover between sweeps and mark the transition run as non-comparable in the trend.

## See Also
- [[Parallel Dimension Scanner Architecture]] — extends (the sweep whose findings get fingerprinted)
- [[Deterministic Review Substrate]] — extends (deterministic trend rules over deterministic findings)
- [[Merge Impact and Evidence State]] — prerequisite-for (the fields the JSON must carry for rules to act)
- [[Falsifiable Hypothesis Gate]] — prerequisite-for (`pattern_key` on friction rows points into this corpus)
- [[Deterministic Signal Detection for Dispatch]] — extends (same preference for regex over LLM judgement, at dispatch time)
- [[Trend on Occurrence Date, Not Run Date]] — extends (which date the trend states bucket on)
- [[Category Is a Bucket, Not a Recurrence Signature]] — extends (per-run ids as a primary key collapsed history 125 → 36)
