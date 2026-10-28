---
title: A Sourcing Gap Is Not an Effect Problem
tags: [patterns, infra, pattern]
summary: "A depth-parallax clip experiment on venue photos worked technically and was rejected at a watch-it gate because the real goal — seeing a venue's interior and food — was absent from the source images; the follow-up catalogue measured each open source and licence policy before building, and found open photos reach landmark venues only, relaxing the non-commercial rule would add one venue, and zero-shot CLIP cannot enforce a no-people rule."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/kiez/docs/plans/2026-10-16-venue-clips-prototype.md
  - data/raw/repos/kiez/.claude--docs--plans--2026-10-16-venue-clips-prototype.md
  - data/raw/claude-docs/kiez/docs/plans/2026-10-16-venue-photo-catalogue.md
  - data/raw/repos/kiez/.claude--docs--plans--2026-10-16-venue-photo-catalogue.md
---

# A Sourcing Gap Is Not an Effect Problem

Two same-day plans in the kiez city-discovery app.

## The clip experiment

Goal: a 3–5 s looping hero clip per venue from one openly licensed photo (monocular depth
model on CPU + an inverse-parallax warp; no generative video in the first step). Step 0
counted the inputs before building: 702 images, about 5% of them food and drink venues —
and **all of those were exteriors or streets**. Some showed the neighbouring building, not
the venue; a clip "would make a wrong picture more convincing."

The build worked: 20 of 20 rendered, depth good on hard cases, 17 of 20 under the size
target. Incidental people in frame moved with the parallax and drew the eye more than in
the still. The gate was a person watching the clips side by side, and it **rejected** them:
motion sickness, and — the actual finding — the goal was to see what a venue is like
*inside*: food on the tables, the room. "That's a sourcing problem, not an effect." The
generative and web-integration steps were dropped before any spend.

## The catalogue: measure each source before building

The pivot plan collected Commons category files and probed a licence-aggregator API, then
classified with zero-shot CLIP into exterior / interior / food_drink / objects plus reject
labels (people, other). Every claim got a number before Phase 2 was allowed:

- **Open photos stop at landmarks.** Commons categories gave good interiors for clubs,
  historic restaurants, theatres and museums: at score ≥ 0.6, 39 of 114 sampled venues got
  an interior or food photo. For thousands of ordinary restaurants and cafés there was
  essentially nothing.
- **The aggregator did not reach the long tail.** 50 searches: 11 venues with an accepted
  hit, only 3 actually the venue — the rest name collisions (a bar named after a saint
  returned the saint). None showed an interior. Verdict: do not build that ingestion node.
  The aggregator also does not verify licences, so any hit must be re-checked at source.
- **Price the policy before changing it.** The project admitted only CC0/PD/BY/BY-SA. Rather
  than argue the non-commercial question in the abstract, Phase 1 counted what it excluded:
  NC was **61% of hits but would add about one venue**. The rule change was left to the
  owner with a number attached.
- **The threshold came from measurement.** 144 images hand-labelled, stratified by
  prediction: precision 0.96 exterior, 0.88 interior, ~0.63 food_drink/objects/people.
  Threshold 0.6 kept 94% of photos showable with 91% of showable labels right.
- **A zero-shot classifier cannot enforce a content rule.** At that threshold about 5% of
  kept photos still had people as the subject. The no-people rule needs a person detector or
  admin approval before publish — the classifier is a sorter, not a guard.

Conclusion recorded: the long tail of ordinary restaurants has **no open photo source**;
only a venue's written permission or first-party photos would cover it. No effect, model
or aggregator changes that.

## The general rule

When a presentation upgrade is proposed for content, check first whether the content the
upgrade needs exists. Count it (Step 0), name the cheapest gate that can reject the idea
(watch the output), and when a policy blocks a source, measure what the policy actually
costs before debating it.

## See Also
- [[Hotlink-Not-Copy Image Posture]] — extends (the licence and derivative rules these plans operate under)
- [[Kiez Project]] — instance-of
- [[Starved Tag Triage: Edge, Prompt, or Supply]] — related (a supply problem misread as a processing one)
- [[Fallback Mistaken for the Design]] — related (judge what the input actually contains before redesigning the surface)
