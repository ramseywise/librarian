---
title: One-Sided Label Control
tags: [eval, pattern]
summary: A labelling UI that can only mark a value "wrong" makes precision = right/(right+wrong) zero or unmeasurable by construction and leaves affirmed-correct values indistinguishable from unreviewed ones — before a labelling session, check that the control can write both verdicts, that the sample is model output, that the surface can be scoped to the sample, and that a failed seed fails loudly.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/research/2026-09-28-dis414-venue-facet-labelling.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-28-dis414-venue-facet-labelling.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-28-dis414-venue-facet-labelling.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-28-dis414-venue-facet-labelling.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-28-dis414-venue-facet-labelling.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-28-dis414-venue-facet-labelling.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-28-dis414-venue-facet-labelling.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-28-dis414-venue-facet-labelling.md
---

# One-Sided Label Control

Found while researching an issue asking for "a UI to label venue facets", so that a
40-row sample could produce a measured per-facet precision number (repo akira,
2026-09-28). The issue's premise was mostly out of date: the chip UI, the label table
and a live precision report already existed on the working branch. The research then
found four narrower blockers, each of which would have wasted a full labelling session.

## 1. The control could only say "wrong"

Each facet chip had one toggle. Marking it POSTed `decision: 'wrong'`, and unmarking
DELETEd the row back to `null`. The store's type was `'right' | 'wrong'`, but **no code
path ever sent `right`**, and no test expected it to.

The report computed `precision = right / (right + wrong)` over rows where `decision is not
null`. As a result:

- every labelled row was `wrong`, so precision was 0 or undefined by construction, even
  after a perfect session;
- values the reviewer looked at and accepted stayed `null`, **indistinguishable from
  unreviewed**, and were excluded from `n`.

The precision math was correct. The input could only express one side of the
measurement. A precision label needs an explicit affirm as well as an explicit reject,
plus a third state for "not reviewed".

## 2. The sample was model input, not model output

The committed 40-row sample held only the probe's input JSON. It had never been run
through the prompt version under test, so the chips would have shown facets from an
older prompt, or none at all. Check that a labelling sample carries the outputs and
version stamps of the thing being measured (see
[[Frozen Version Stamps on Logged Results]]).

## 3. The surface couldn't be scoped to the sample

The review feed ranked about 5,300 city-wide rows and showed about 5–10 cards per load.
Whether any of the 40 sample rows appeared depended on the review-priority sort. The fix
is a candidate-id allow-list option on the feed (`candidateIds`). A labelling session
needs to present exactly the sample, not hope the sort surfaces it.

## 4. A failed seed was only logged

Label rows were seeded on render. A failed seed was `logger.error`'d, but the chip still
rendered, and clicking it returned `subject_not_found` (404). The reviewer would see a
chip that silently failed to save. This is the [[Silence Reads as Clean]] failure mode
applied to a human-labelling surface.

## What the plan built

The follow-up plan made the chip write both sides: `setVerdict('right' | 'wrong' | null)`,
with null meaning unreviewed. It added the `candidateIds` allow-list param to the feed,
which bypasses the shelf cap so the whole sample renders. For the sample problem, it
labelled the 185 existing rows already produced by the prompt version under test, rather
than enriching the stale 40-row manifest.

## Pre-session checklist

- Can the control write **both** verdicts, and does unreviewed differ from affirmed?
- Is the sample the **output** of the version under test?
- Can the surface be restricted to **exactly** the sample?
- Does a failed write or seed **fail visibly** to the reviewer?

## See Also
- [[Append-Only Human Labels]] — extends (the label store this control writes into)
- [[One Facet Per Fact]] — prerequisite-for (the per-facet precision acceptance these labels feed)
- [[Human Agreement Ceiling Protocol]] — related (what the labels are compared against once both verdicts exist)
- [[Silence Reads as Clean]] — related (the swallowed seed failure)
- [[Kiez Project]] — instance-of
- [[Quality-Gate Dashboard in Pipeline Order]] — related (the precision panel these labels feed)
- [[Review Preview Over the Production Pipeline]] — prerequisite-for (how the review feed was built on the production ranker)
