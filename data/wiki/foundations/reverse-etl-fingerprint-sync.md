---
title: "Reverse ETL Fingerprint Sync"
tags: [foundations, pattern]
summary: "Copy modelled data into a downstream tool by upserting on a stable ID, sending only records whose fingerprint changed, and recording each send only after it succeeds, so a crash costs nothing and a rerun sends only the rest."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--05-quality-and-observability--notes--06-dataops.md
---

# Reverse ETL Fingerprint Sync

Reverse ETL copies modelled warehouse data into tools where people work (a CRM, an ad platform). The pieces are source, model, sync and destination. You do not own the destination's schema or API, so compare current values with what you previously sent.

## Behaviour (stand-in destination that fails on demand)

| Run | Records sent |
|---|---|
| First sync | 1000 |
| No changes | 0 |
| 33 tier changes | 33 |
| Crash after 10 sends, then rerun | rerun sent 23; destination matches the warehouse |

Three properties make it restartable: upserts by a stable ID make a repeated send harmless, the fingerprint makes an unchanged record skippable, and **the send happens before the record of it**. Reverse the order and a crash leaves a fingerprint recorded for a record never sent: in the lab variant one record stayed wrong for good and the rerun looked healthy. A repeated upsert is harmless; a lost one is silent.

## Real destinations

Expect rate limits, batch endpoints and fields people edit by hand; decide which side wins each field. The sync is an operational dependency, since people act on what is in the destination: give it an owner, an SLO and an alert ([[Data SLOs, Error Budgets and Paging on the Symptom]]).

## See Also
- [[Idempotent Backfills and Dated Corrections]] — related
- [[Data SLOs, Error Budgets and Paging on the Symptom]] — related
- [[Metric Definitions, Exposures and a Manifest Catalog]] — related
