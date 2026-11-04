---
title: "Data Catalog Metadata: Push, Pull and Measuring Adoption"
tags: [foundations, concept]
summary: "A catalog needs both push and pull ingestion, separates tier from certification, and should be measured by stale descriptions and reads on certified tables, not coverage."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--07-architecture-and-governance--notes--03-catalog-semantic-layer-and-contracts.md
  - data/raw/repos/learn-ai-engineering/data-engineering--07-architecture-and-governance--README.md
---

# Data Catalog Metadata: Push, Pull and Measuring Adoption

A **data catalog** is a searchable store of what data exists, what it means and who answers for it. It is not a table format's catalog (which tracks a table's current metadata file) and is more than one project's docs site.

## Two kinds of metadata, two arrival paths

**Technical metadata** (tables, columns, types, row counts, lineage) can be read from systems. **Business metadata** (meaning, owner, trust) comes only from people. Technical metadata arrives by **pull** (a crawler on a schedule) or **push** (the system emits an event on change). Each misses something: in a demo, a push saw a column added by a pipeline deploy at once but never saw a column added at a SQL prompt; the nightly pull found that one 11 hours later, and only pull can notice a column that vanished, because no event fires for an unplanned deletion (after both added columns were dropped, a crawl brought the catalogued count back to 15). Run both. A large-scale catalog uses non-invasive pull; its authors report more than 5% of datasets deleted daily, and that passing over the catalog with a thousand machines at one second per dataset would take about 300 days, so they prioritise annotated or high-lineage-centrality datasets. Counting downstream readers over-ranks widely consumed intermediate tables in search, so tune that signal and blend others.

## Tier, certification, inferred trust

| Signal | Claims | Set by |
|---|---|---|
| Tier | How much the data matters | Owner or producer |
| Certification | A named reviewer vouches for quality | Authorised reviewer |
| Inferred trust | Signals (quality, recency, usage, lineage) suggest it is good | The system |

A table can be tier 1 and uncertified; tier says what happens if it breaks, not that it is right. Certification needs a reviewer, a date and an expiry or review trigger. One glossary tool auto-approves terms when no reviewers are assigned.

## Measure staleness and use, not coverage

On a toy catalog, coverage was 4 of 15 columns (27%), but coverage counts presence: a column whose description predated a later meaning change still counted as done. Better measures:
- Descriptions older than their column's last change (needs the change to reach the catalog; a type-preserving change of meaning is invisible to a crawl, so it must arrive as a pushed contract version).
- Share of warehouse reads landing on certified tables (55 of 200, 28%, in the toy log), tier 1 tables with no reads, and the most-read uncertified table. Page views only show the tool is open.

No peer-reviewed measurement of catalog adoption or metadata staleness was found; self-reported figures are thin (one preliminary survey had 39% naming lack of adoption as a barrier, sample size unstated). Set targets from your own baseline.

## See Also
- [[Semantic Layer: Metrics Compiled at the Requested Grain]] — prerequisite-for
- [[Contract Change Impact Chain and the Same-Name Unit Change]] — extends
- [[Warehouse, Fabric and Lakehouse: Sizing the Physical Architecture]] — related
- [[Access Control Below the User, Audit Logs and Breach Scope]] — related (inventory)
