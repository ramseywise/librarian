---
title: A Sentinel Catches Forgetting, Not Asserting
tags: [eval, foundations, pattern]
summary: "A typed `NotApplicable(reason)` sentinel with null-rejection on decode stops a run record from silently omitting a field, but a sentinel carrying a false reason round-trips cleanly — a seeded clustering run tagged `seed=NotApplicable` would have passed every guard; verify the claim behind the sentinel by grepping for consumers of the value it says does not exist."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/galactus/docs/plans/2026-08-18-ml-parity-consolidated.md
  - data/raw/repos/galactus/.claude--docs--plans--2026-08-18-ml-parity-consolidated.md
  - data/raw/claude-docs/galactus/docs/plans/2026-08-16-segmentation-parity.md
  - data/raw/repos/galactus/.claude--docs--plans--2026-08-16-segmentation-parity.md
---

# A Sentinel Catches Forgetting, Not Asserting

From an ML prototyping repo (galactus) giving a k-means segmentation run the same run
record as its supervised siblings.

## The record shape

The experiment registry types optional fields as `X | NotApplicable`, e.g. `seed: int |
NotApplicable` and `folds: str | NotApplicable`. The serializer refuses a bare `null`:
*"null is never a valid value for an optional field"*. The only legal absence on disk is
`{"not_applicable": {"reason": ...}}`. The design worry was that forcing an unsupervised run
into a supervised-shaped record would produce a dishonest `NotApplicable`. The plan argued
that this guard made the shape fit: the absence must be stated, with a reason.

## What the guard does not catch

A readiness review settled it with a grep. The segmentation run **is seeded**. `RANDOM_STATE`
feeds the KMeans `random_state`, the random-partition baseline's RNG and the silhouette
sample. The plan's step would have written `seed=NotApplicable("no seed concept")`. That
claims the field has no meaning for this kind of run, about a run whose headline metric and
whose baseline both move with the RNG.

The null-rejection guard catches **forgetting**: a field left out or written as null. It
cannot catch **asserting**: a tagged sentinel with a false reason serialises, deserialises
and validates like a true one. So the guard that "is the reason the shape fits" was never a
guard against the failure being feared.

The fix was narrow. `seed=RANDOM_STATE`, with a test asserting it against the imported
constant. `folds=NotApplicable(...)` stayed, because a k-means sweep genuinely has no fold
plan, and the registry's docstring names runs with no seed or split concept as the
intended case.

## The rule

- A sentinel's *reason* is a claim. Check it like one. For "this run has no X", grep for
  consumers of X before writing the tag.
- Where it is cheap, make the claim checkable in a test: assert the populated value against
  its source constant, so changing the code without changing the record fails.
- What an unsupervised record honestly carries is an internal-validity index, such as
  silhouette against a random-partition baseline. It is not a claim a second party can
  refute the way "nothing beats the logistic baseline" can. Label it as that, instead of
  borrowing the supervised `metric` slot. See [[Data Sufficiency Refusal]].

## See Also
- [[Data Sufficiency Refusal]] — extends (the unsupervised record shape this sentinel serves)
- [[Clustering Validation Against Named Baselines]] — prerequisite-for (why the seed moves the metric)
- [[Hash the Frame as Fitted, Not the Source File]] — extends (another run-record field that can certify the wrong thing)
- [[Tested Decision, Untested Expression]] — extends
