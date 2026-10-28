---
title: Widen a Capped Vocabulary Without Displacing
tags: [patterns, foundations, pattern]
summary: "Merging a richer keyword list into a selector whose output is capped regressed 18 already-working sites by crowding real links out of the top N; the fix ranks matches on the legacy vocabulary first, so new vocabulary can only fill leftover slots and never displace an existing selection."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-14-listing-text-extractor.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-14-listing-text-extractor.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-14-listing-text-extractor.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-14-listing-text-extractor.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-14-listing-text-extractor.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-14-listing-text-extractor.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-14-listing-text-extractor.md
---

# Widen a Capped Vocabulary Without Displacing

Found while recovering venue calendars that a crawler's link discovery silently dropped
(repo akira, 2026-09). The detail-link selector filtered paths by a hand-typed 7-word
keyword list. A sibling module kept a richer, actively maintained 22-entry list for
scoring calendar links. The obvious fix was "one vocabulary, two readers": export the rich
list and derive the selector's allow-list from it. That recovered calendars under paths
like `/termine/`.

## The regression

An offline before/after run over the 557-site corpus showed 18 already-passing sites losing
52 kept events. The first diagnosis blamed the "weak" keywords (`news`, `aktuelles`,
`tickets`). Removing them recovered only part of the loss. Long-standing "strong" entries
were also crowding results. `kurse` matched a dance school's course pages, for example.

The mechanism was the **cap**. The selector feeds a downstream limit (8 links in the probe,
`MAX_DETAIL_LINKS` in the importer). A broader allow-list does not just add candidates. It
reorders the top N, and real detail links that used to make the cut get pushed out by
newly matching noise. A vocabulary is a ranking input whenever its output is truncated.

## The fix

1. **Filter on strong terms only.** The path filter derives from the strong list plus
   `event`. Weak terms stay as *scores* in the calendar finder, where they cannot crowd
   anything.
2. **Rank legacy matches first.** A `LEGACY_PATH_KEYWORDS` set holds the old 7 words. A
   candidate matching a legacy word sorts ahead of one matching only a new word, before the
   existing depth/order tie-break. The legacy subset sorts among itself exactly as before.
   Any page whose links were found by the old list keeps the **same top-N selection**.
   The new vocabulary can only fill leftover slots.
3. **Pin both directions with tests.** A capped page keeps its legacy links over new-only
   links. A page with only new vocabulary still gains links when nothing legacy competes.

Re-measured on the same corpus: net +1 kept event, **zero regressed sites** on both
`links_found` and `detail_kept`, and 64 sites went from 0 links found to more than 0.

## Measuring honestly offline

- **The harness throws on a cache miss** instead of fetching live. It shares the
  production planning and probe code and swaps only the fetcher. Newly found links whose
  pages were never cached cannot show a kept gain offline, so `links_found` is the honest
  offline proxy for recovery. A flat `detail_kept` is a property of the measurement, not
  evidence the fix does nothing.
- **Ask whether the regression metric can see the change.** A later date-parser fix
  produced a byte-identical per-site diff, because "kept" depends on title and page gates,
  not on `start_at`. Zero regressions on a metric blind to the defect says nothing about
  the defect ([[Guard at the Funnel, Fix at the Cause]]).
- **No feature flag existed for this seam.** Instead, the change shipped as its own PR,
  independently revertable, with the before/after corpus diff as the evidence a flag would
  otherwise give.

## See Also
- [[The Untested Copy Wins]] — extends (deduplicating two keyword lists is right, but the merge changes ranking)
- [[Listing Pages Masquerading as Records]] — related (the same crawler's link-selection repair)
- [[Red-Then-Green Proof for Fix-Stage Tests]] — related (the recovery test was shown red before the fix)
- [[Natural Key Without a Discriminator Collapses Rows]] — related (another defect found in the same build: synthetic keys collapsed by URL normalisation)
