---
title: Vacuous Check Turns Backwards on Policy Change
tags: [infra, pattern]
summary: "A CI check that passes only because the population it inspects is empty can quietly encode the policy that a later decision reversed. The day the first qualifying row appears, it fails the gate for doing the right thing. When a decision amends what a concept means, re-read the predicate of every check that names that concept, and delete a backwards check instead of repurposing it."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-22-dis286-image-provenance-slices-3-6.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-22-dis286-image-provenance-slices-3-6.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-22-dis286-image-provenance-slices-3-6.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-22-dis286-image-provenance-slices-3-6.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-22-dis286-image-provenance-slices-3-6.md
---

# Vacuous Check Turns Backwards on Policy Change

## The case

An image-host drift check in akira had a rule, `hotlinkedDespiteLicensed`. It failed the
gate when an image from a `licensed` source was served from any host other than the
product's own storage domain. That encoded the original policy: licensed images get
copied to storage. A later decision amended the meaning of `licensed` to **hotlink from
the source, never copy** (see [[Hotlink-Not-Copy Image Posture]]). The decision's own row
assumed the check would simply stay inert until a source was licensed and then become
relevant.

Reading the predicate rather than the docstring showed it was **inert, then backwards**.
With 0 of 93 sources licensed, the check passed on an empty set. The first source a
reviewer marked `licensed` would make `make gate` fail for doing exactly what the new
policy required.

## Why it hides

- **An empty population passes every predicate.** A vacuous pass looks the same as a
  correct one. This is the mirror image of [[Scan-Floor Guard Against Silent No-Op Checks]]:
  that guard catches a check that scans nothing, while here the check scans correctly and
  asserts the wrong thing.
- **Decision rows describe intent, not predicates.** The amending decision named the check
  as "still owed" without anyone re-reading what it asserted.
- **The failure arrives far from its cause,** on a human review action (licensing a
  source), weeks after the policy change, as a red CI run on an unrelated PR.

## The move

1. When a decision changes the meaning of a value (`licensed`, `approved`, `public`), grep
   every check, gate and test that names that value and **re-read its predicate** against
   the new meaning. Do not trust its docstring.
2. If the check's job is now covered by something else, **delete it** rather than keep it
   "in case". Here, the existing unconditional unknown-host check plus a new
   blocked-tracking-host check covered host identity without needing the posture at all.
   A second, wrong check is the second-hand-maintained-list trap.
3. Record the correction as `origin: upstream-wrong` against the decision that assumed
   the check was safe.

## See Also
- [[Hotlink-Not-Copy Image Posture]] — instance-of (the policy change that inverted the check)
- [[Scan-Floor Guard Against Silent No-Op Checks]] — alternative-to (vacuous because nothing is scanned vs vacuous because nothing qualifies)
- [[Observe-Mode Gate With a Named Enforce Trigger]] — related (another gate whose behaviour changes when the first row qualifies)
- [[Audit the Class, Not the Instance]] — related
