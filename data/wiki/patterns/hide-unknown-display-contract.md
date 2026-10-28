---
title: Hide-Unknown Display Contract
tags: [patterns, prompting, pattern]
summary: A content-display contract where uncertain or missing optional fields are hidden rather than shown as "Unknown", never block publishing, and user-facing labels (CTAs, price display) are derived at read time by resolvers from stored source fields, never stored, so they cannot drift.
updated: 2026-10-16
sources:
  - data/raw/claude-docs/akira/docs/research/2026-10-09-notion-content-data-contract.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-10-09-notion-content-data-contract.md
  - data/raw/claude-docs/akira/docs/research/2026-10-09-notion-vertical-data-requirements.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-10-09-notion-vertical-data-requirements.md
  - data/raw/claude-docs/diskoe/docs/research/2026-10-09-notion-content-data-contract.md
  - data/raw/claude-docs/diskoe/docs/research/2026-10-09-notion-vertical-data-requirements.md
  - data/raw/claude-docs/diskoe/docs/research/2026-10-09-notion-content-data-contract-pages.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-10-09-notion-content-data-contract-pages.md
---

# Hide-Unknown Display Contract

Distilled from the product's per-vertical card requirements and its content data
contract in an events-discovery product (repo akira, mirrored 2026-10-09 from May–June
2026 product docs). The field lists were superseded by the schema. The rules below are
what held.

## Publish means "the whole flow works"

An item is visible only if it supports the complete user flow: **preview → detail →
decide / save / share / external action**. So the publish minimum is preview minimum +
detail minimum + CTA/source minimum, and nothing more. **Optional enrichment fields and
images never block publishing.** Unknown price doesn't block, and "paid with no amount"
is review-only.

## Hide, don't say "Unknown"

- Never show `Unknown`, `N/A`, empty strings or placeholders. Hide the field.
- Hide optional fields that are low-confidence (`data_confidence`) or unreliable. Do not
  guess.
- If a whole section has no reliable fields, hide the section.
- Show **one** price signal, the most useful available one, via a fallback ladder
  (range → "from" → price level → explicit "Free" → hide and rely on the source link).
- Preview pills are concrete decision signals (up to 3; show 1 if only 1 is reliable),
  never vibe tags. Tags are for browsing and never replace a core field.
- Action links (tickets, booking, reservation) are CTAs, not text rows. An inactive CTA
  is not shown. Without one, fall back to the official page.

This is the display-side counterpart of abstention in the enrichment contract (see
[[Graded-Uncertainty Enrichment Contract]]): the model may say "unknown", but the user
never sees it.

## Derived labels are resolver-owned, never stored

Stored columns are for fields that publish validation needs, that are queried or
sorted, that are stable source data, or that drive moderation. **CTA labels, CTA
URLs/types and `price_display` are derived by resolvers** from stored inputs and are not
columns, so they can't drift from their inputs. That is the cheap way to avoid a
[[Cached Derivation Without a Recompute Path]]. Availability overrides run before action
CTAs: `sold_out`, `expired` and `closed` suppress the action CTA, while `limited`,
`unknown` and null do not.

Related rules that kept the derivation honest:

- `source_url` (technical provenance) is not the public CTA fallback. `official_url` is.
  The model must not invent URLs.
- A strategic source registry and a technical scraper config are separate tables.
- Tri-state beats boolean when the middle state matters: `reservation_required` takes
  `required / recommended / unknown`, not true/false.
- Teasers are generated **only** from source-backed data, with a stable-facts-only
  fallback when sources conflict (see
  [[Evidence-Labelled Generation with Deterministic QC]]).

## Mirror docs are not contracts

Both source docs called themselves "source of truth". By the time they were mirrored,
the schema, migrations and resolver code had superseded them (two status columns had
already been dropped). Mirrors were kept as history, with a header naming the
contract of record, the code, which wins on disagreement.

## See Also
- [[Cached Derivation Without a Recompute Path]] — complements (derive at read time instead of caching)
- [[Graded-Uncertainty Enrichment Contract]] — complements (abstention upstream, hiding downstream)
- [[Hotlink-Not-Copy Image Posture]] — related (image fallback ladder)
- [[Kiez Project]] — instance-of
- [[Three-Level Duplicate Classification]] — related (duplicates hidden through the same review-status gate)
