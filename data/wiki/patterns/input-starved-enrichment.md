---
title: Input-Starved Enrichment
tags: [patterns, prompting, pattern]
summary: When an enrichment prompt gets no descriptive text, the model returns empty tags and the item scores zero on every dimension that reads them — check what the payload actually contains before tuning the prompt, and never feed provenance fields like operator notes as content.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/research/2026-09-19-per-vertical-prompts-scoring-and-intake.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-19-per-vertical-prompts-scoring-and-intake.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-19-per-vertical-prompts-scoring-and-intake.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-14-dis264-enrichment-input-shaping.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-14-dis264-enrichment-input-shaping.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-14-dis264-enrichment-input-shaping.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-14-dis264-enrichment-input-shaping.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-14-dis264-enrichment-input-shaping.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-14-dis264-enrichment-input-shaping.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-14-dis264-enrichment-input-shaping.md
---

# Input-Starved Enrichment

From an akira audit of the per-vertical enrichment prompts (events, activities, bars and
restaurants) and how their output reaches intake scoring.

## The failure

The hospitality payload had **no description anywhere**. Its one free-text field was the
operator's sourcing `notes` ("Instagram: … | Event surface hint: instagram only"), and it
was shaped into the prompt as if it were content. In three real dry runs, both hospitality
rows returned **empty `vibe_tags` and empty `context_tags`**. Empty vibe tags mean the vibe
dimension scores 0; empty context tags mean the context dimension scores 0. Every bar was
invisible to mood-based intake, and nothing errored.

The model behaved correctly: with no evidence, the weak-evidence rule says emit nothing.
The defect was upstream in the payload. Prompt tuning would not have helped.

Fixes, in order:
1. **Stop feeding `notes` as content.** It is provenance. Exclude it or label it as such.
2. Give the prompt real descriptive input (a crawled description, or the page text).
3. Re-run one dry run per vertical and confirm non-empty tags before calling it fixed.

## One scoring vocabulary across verticals

The allowed-value lists for every field the ranker reads were identical across the three
verticals: the same 26 vibe tags, the same caps, the same weak-evidence rule. Templates
differ only in format, category and vertical-only fields. A shared vocabulary is what lets
an event, an activity and a bar compete in one slate, and it is why a single sanitize step
can drop an out-of-vocabulary value from any vertical.

Two consequences:
- **A new intake option and its mapping entry ship together or neither ships.** An option
  without a mood-to-tag map entry silently scores zero.
- **Sanitize hides what the model said.** QC returned issue codes outside the closed
  vocabulary; sanitize dropped them, so the stored verdict differed from the raw output.
  Log the raw output when debugging.

## Shape the input before the prompt reads it

A sibling akira plan measured the other half of the problem: prompt summary lines reading
`unknown` for fields the row **already had**, under a different key. Two input shapes (the
ingestion handoff and a `select('*')` row) reached one untyped prompt builder, so `Title`,
`Date` or `Location` resolved on one path and read `unknown` on the other. The fix was a pure
shaping function in front of the prompt, with these rules:

- **Move aliases, don't copy them.** The prompt sends both a summary and the full serialized
  content, so every copied alias adds another full copy of a value (descriptions reached ~20k
  characters).
- **Shape after the content hash.** The hash runs over the unshaped handoff, so shaping changes
  the prompt without invalidating any stored hash or forcing a re-enrichment.
- **The measurement tools must call the same shaping.** Most rows counted in the notebook were
  dev-tool projections, not database rows. Wiring only production call sites would change real
  prompts and leave the done-when number unmoved.
- **The notes trap has a second door.** The payload builder set `raw_description` to
  `description ?? notes`, so on a page with no description the handoff's description *was* the
  editorial note, and nothing downstream could tell them apart. A field with no column cannot be
  fixed by shaping; that needs a column, landed together with its reader.
- Embedding the venue in the content read is loud on failure (the read throws), which is the
  desired failure mode for a missing join.

## Dry runs must be readable

Two scripts promised a dry run that "prints what would be written" but printed only a
verdict. **A dry run whose output can't be read is a billed model call that answers
nothing.** Print the shaped payload and the full parsed response.

## See Also
- [[Starved Tag Triage: Edge, Prompt, or Supply]] — extends (adds a fourth cause: the payload carried no evidence at all)
- [[Parsed Then Dropped at the Insert Mapper]] — related (where the missing description went)
- [[Intake Option Separability via Reach Vectors]] — related (the intake side of the same vocabulary)
- [[Re-Crawl Adds, Never Overwrites]] — related (the same plan's no-overwrite write path)
- [[Prove Discovery Before Evaluating Enrichment]] — extends (the full pre-enrichment proof ladder, of which minimum evidence is one rung)
- [[Brand the Funnel's Output]] — prerequisite-for (the type-level guard that keeps callers on the shaping funnel)
- [[Advisory Enrichment Breaks Ties Only]] — extends (bounding what an external enrichment may change)
