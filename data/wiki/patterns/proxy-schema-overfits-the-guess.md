---
title: Proxy Schema Overfits the Guess
tags: [patterns, mcp, pattern]
summary: A schema and synthetic generator built before the real source arrives turn guesses into required fields; when the real data turns out thinner, a strict never-drop validator rejects every row, so make guessed field groups optional and derive or sentinel-code the gaps.
updated: 2026-10-17
sources:
  - data/raw/repos/datathon_mcp/.claude--docs--research--awo-welfare-data-harvester.md
  - data/raw/repos/datathon_mcp/.claude--docs--plans--harvester-integration.md
  - data/raw/repos/datathon_mcp/.claude--docs--research--federated-data-pool-mcp-prep.md
  - data/raw/repos/datathon_mcp/CLAUDE.md
---

# Proxy Schema Overfits the Guess

This failure came from a data-pool MCP prototype (datathon_mcp). The query tools and the
harmonized model were built first, against a **synthetic proxy source** generated from a guessed
schema: service-type codes, a regional key, quantitative indicators, target groups and capacity.
When the real source finally arrived, a scraped facility directory, it was **thinner** than the
guess. It had no service classification, no regional key (only postcode and city) and no
indicators at all.

The harmonizer followed a correct rule: never drop a row silently, and raise a row error on an
unknown key. Because the regional key and the service code were *required*, it would have
**rejected every harvested row**. The never-drop rule was right. What was wrong was making those
fields required. A guess had hardened into a contract.

## Why it happens

A generator invents every field the downstream tools want, so the tools and the validator grow
around fields that no real source has promised. Nothing fails until real data arrives, and then
everything fails at once. The indicators were pure invention, and the tool that aggregated them
had no data behind it at all.

## Fixes

- **Treat the real writer code as the schema.** The source repo's docs described a richer
  entity/address/contact/service model with a category field. The code wrote two flat CSVs. The
  columns were read from the writer functions, not from the README.
- **Derive what is derivable.** The regional key was looked up from the postcode. Unknown postcodes
  still raise a reported, non-zero-exit row error.
- **Add a sentinel instead of a requirement.** An `UNK` ("not classified") code lets an
  unclassified row load and stay visible as unclassified.
- **Make guessed field groups optional in the mapping contract.** Indicators, generator hints and
  the various code maps all became optional, and a `source_kind` field records whether a record
  came from an organization export or a scraped directory.
- **Hand-write fixtures in the exact real column set** while waiting for a sample. One fixture
  should be shared by tests and the data build.
- **Degrade tools honestly.** Region comparisons kept working as *facility counts*, not service
  counts, with a `note` saying so. The indicator tool listed which sources have no indicators.
- **Re-ask what the data can answer.** The real data carried data-quality signal: single-source
  records, missing contact fields, merge rules. A new `data_quality_by_region` tool answered the
  stakeholder's actual question (how good is the facility database?) better than the invented
  indicators did.

## See Also
- [[Synthetic Dataset Generation]] — extends (the generator side, when the synthetic source defines the schema)
- [[Silence Reads as Clean]] — alternative-to (the opposite failure: a lax check passes absent data)
- [[Data Sufficiency Refusal]] — extends (tools that say what the data cannot support)
- [[REST-First, MCP as Adapter]] — related (the thin-facade architecture of the same prototype)
