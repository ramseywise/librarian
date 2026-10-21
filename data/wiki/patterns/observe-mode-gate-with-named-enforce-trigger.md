---
title: Observe-Mode Gate With a Named Enforce Trigger
tags: [patterns, infra, pattern]
summary: "When a new gate's strict reading would fail on data nobody has reviewed yet, ship it in observe mode — fail only on the invariant that holds today (often vacuously), print the full breakdown unconditionally, and write down the countable condition that flips it to enforce — because the strict version turns the shared gate permanently red and blocks every unrelated branch."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-10-dis223-source-rights-posture.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-10-dis223-source-rights-posture.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-10-dis223-source-rights-posture.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-10-dis223-source-rights-posture.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-10-dis223-source-rights-posture.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-10-dis223-source-rights-posture.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-09-dis220-legal-gating.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-09-dis220-legal-gating.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-09-dis220-legal-gating.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-09-dis220-legal-gating.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-09-dis220-legal-gating.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-09-dis220-legal-gating.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-09-dis220-legal-gating.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-10-dis223-source-rights-posture.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-06-dis168-skip-link-targets.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-06-dis168-skip-link-targets.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-06-dis168-skip-link-targets.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-06-dis168-skip-link-targets.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-06-dis168-skip-link-targets.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-06-dis168-skip-link-targets.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-06-dis168-skip-link-targets.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-07-dis60-lighthouse-ci.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-07-dis60-lighthouse-ci.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-07-dis60-lighthouse-ci.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-07-dis60-lighthouse-ci.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-07-dis60-lighthouse-ci.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-07-dis60-lighthouse-ci.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-07-dis60-lighthouse-ci.md
---

# Observe-Mode Gate With a Named Enforce Trigger

## The situation

An events-discovery product (repo akira, 2026-09) added a per-source `image_posture`
column, default-deny (`review_needed`) on all 92 sources. Assigning a real posture to each
source was a human review (~10 minutes per source) that had not started. The natural gate
is "no event renders an image unless its source is `licensed`". With 92 of 92 sources
still at `review_needed`, that gate is red on day one. It stays red until the review
finishes, and because it runs inside the shared `make gate`, it blocks **every unrelated
branch** for the whole time.

That is the [[Always-Red Check Carries No Signal]] failure, arrived at deliberately.

## The shape

The repo already had a precedent for this: a crawl gate on a `legal_posture` column ran
in observe mode for the same reason. The image gate copied it:

- **Fail on one assertion: the invariant that must hold even before review.** For any
  source that *is* `licensed`, the image URL's host must be first-party storage, never the
  origin host ("licensed means copied, never hotlinked"). Zero sources were `licensed`, so
  this was vacuously true. That is fine. It protects the first source anyone marks
  licensed, from that moment on.
- **Print the breakdown unconditionally, without failing.** Image presence by posture
  value (`review_needed: N`, `licensed: 0`, …) is printed on every run, so the distance to
  enforcement is visible in every gate log.
- **Name the flip condition as a count, and record it outside the plan.** Enforcement
  (fail on any non-`licensed` source with an image) turns on when the `review_needed`
  count in that breakdown reaches 0. The condition went into the roadmap row for the
  feature, not only the plan file, so it survives the plan being deleted.

The product stays correct during observe mode because the **render path** is
default-deny on its own: an image is suppressed unless its source is licensed, whatever
the gate says. The gate checks the invariant. It is not what keeps the product safe.

## Why not the alternatives

- **Strict from day one:** permanently red shared gate. People learn to ignore it or
  route around it.
- **No gate until review finishes:** the "licensed means copied" invariant is unguarded
  at the exact moment it first matters.
- **Observe mode with no trigger:** observe mode becomes permanent. This is the same move
  as [[Named-Trigger Deferral]], applied to a gate's strictness instead of to a feature.

## The precedent: the crawl gate (runtime, not CI)

The `legal_posture` crawl gate this copied is the same move applied to a *runtime*
filter rather than a CI check. Every one of 92 sources sat at the `review_needed`
default, so an enforced gate would have made the next scheduled ingestion import
**nothing**, for an open-ended period — and an empty run reads as an outage. Its locked
requirements are a checklist for any runtime observe mode:

- **Named reasons, not a boolean.** The predicate returns `missing_source` /
  `not_reviewed` / `prohibited` (or null), so observe mode logs one structured line per
  would-be-excluded source (id, posture, reason) and the blast radius is queryable before
  the flip. A missing joined row excludes — a broken join fails closed.
- **The switch is a reviewed code constant, not an env var** that silently defaults to
  permissive; a normalizer treats anything other than the exact string `'observe'` as
  `'enforce'` ([[Unfinished Work Must Fail Closed]]).
- **Mode is a parameter defaulting to the constant**, and the regression test asserts both
  directions: observe → a known `Disallow: /` source is logged *and still fetched*;
  enforce → excluded. Testing one mode leaves the flip unverified
  ([[Execute Every Toggle Configuration]]).
- **Durable evidence vs. process cache.** An in-memory per-origin robots.txt cache (one
  run) and a `robots_policy` column (forever, read by the human doing the terms review)
  looked like a "no schema" vs. "add a column" conflict until their different readers and
  lifetimes were named; both shipped ([[Every Column Names Its Reader]]).

## Related move in the same plan: don't add a metric that cannot be measured

The same plan added a new value (`business`) to a vocabulary that three already-gated
eval metrics read generically. A fourth "is `business` accepted" metric would have shipped
UNGATED forever, since there was no new pass rate to observe. The plan added fixture cases
to the three existing metrics instead. See [[UNGATED Metric Convention]].

## See Also
- [[Monitor the Gate, Not the Stage]] — related (the precision n≥30 / stable fire rate bar a gate meets before enforcing)
- [[Always-Red Check Carries No Signal]] — prerequisite-for (the failure observe mode exists to avoid)
- [[Named-Trigger Deferral]] — extends (a countable flip condition, recorded where it will be read)
- [[Shadow Signal Before Gate Change]] — related (compute the new key without gating, before changing a gate)
- [[Hotlink-Not-Copy Image Posture]] — instance-of (the `image-hosts` gate this was applied to)
- [[UNGATED Metric Convention]] — related (a threshold is written only from an observed rate)
- [[Unfinished Work Must Fail Closed]] — related (the mode normalizer fails toward enforce)
- [[Execute Every Toggle Configuration]] — related (both modes tested)
- [[Backfill Without the Forward Path]] — related (fix the writer, backfill, then ratchet the gate)
