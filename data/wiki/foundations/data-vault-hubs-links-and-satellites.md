---
title: "Data Vault Hubs, Links and Satellites"
tags: [foundations, concept]
summary: "Data Vault splits each source entity into insert-only hubs (keys), links (relationships) and satellites (attribute history) so new sources cost a table each; the price is several joins per attribute, so readers get marts on top."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--02-ingest-and-modelling--notes--03-data-vault-and-obt.md
---

# Data Vault Hubs, Links and Satellites

Data Vault sits at one end of a range, with the star in the middle and a single wide table at the other end. It is an integration and audit layer more than a rival to the star. This page rests on a secondary overview of the method, so treat it as the shape of the idea.

## Structure

- **Hub:** business keys and nothing else: each key once, with first-seen time and record source.
- **Link:** a relationship between hubs (this trip was in this zone).
- **Satellite:** descriptive attributes and their history, attached to a hub or link. A change adds a row.

Keys are hashes of the business key, so any loader computes them without a sequence lookup. Rows are only ever inserted. A satellite stores a `hash_diff` and inserts a row only if the incoming hash differs from the latest one, so a retry adds nothing. "Current" is the row with the latest load time.

Same boundary change as in [[Slowly Changing Dimensions Types 1, 2 and 3]]: same history, but nothing updated. Counts: 250 hub rows and 251 satellite rows. Loads are mechanical (every hub the same way, every satellite the same way), so they can be generated from metadata for hundreds of source tables. A new source of attributes is a new satellite and no existing table changes; on a star it means altering a dimension or conforming two sources into one row first.

## The bill

A question the star answers with one join needed three joins plus an aggregate over the satellite for current values. Results matched exactly; in one run on a busy laptop it took 28 ms against 3 ms (about ten times). One machine and small data, so the shape matters, not the ratio: nobody should query it directly. Practice publishes information marts (usually stars) on top, plus point-in-time and bridge tables for read speed.

## When it pays

Many overlapping sources, sources that change often, and an obligation to show auditors exactly what was received and when. It does not pay for a small team with six source tables: that is the star plus a layer nobody reads. An insert-only raw staging layer gives most of the audit benefit at a fraction of the design cost.

## Pitfalls

- Choosing a vault for reputation.
- Querying it directly instead of building marts.
- Hash collisions: a 64-bit hash is fine for a demonstration; use a wider digest, and pick an explicit algorithm because some engines' default `hash` is not stable across versions.

## See Also
- [[Dimensional Model Grain and the Four Design Steps]] — alternative-to
- [[One Big Table versus Star Schema]] — alternative-to
- [[Slowly Changing Dimensions Types 1, 2 and 3]] — related
- [[Data Engineering Foundations]] — related
