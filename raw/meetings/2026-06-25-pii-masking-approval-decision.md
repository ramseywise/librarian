---
source: google_drive
source_id: 1YtaSkNnHDv44LHapkNskGWTSRfOQ6RWyEKJ80cKI1SQ
source_url: https://docs.google.com/document/d/1YtaSkNnHDv44LHapkNskGWTSRfOQ6RWyEKJ80cKI1SQ
type: decision_doc
date: 2026-06-25
author: Yan Zhang
tags: [pii, gdpr, privacy, intercom, masking, compliance, evaluation-pipeline]
status: pending_legal_signoff
tickets: [VIR-115, VIR-116]
---

# PII Masking — Decision & Approval Request

## Purpose

Notifies Legal/Ops of the VA team's chosen PII masking approach for Intercom conversation data used to build the evaluation dataset. Requires written sign-off before any pipeline deployment proceeds.

**Scope**: Historical Intercom conversation data only. Not a production pipeline. Does not process live/real-time customer data.

## Masking Pipeline (4 stages)

| # | Stage | What it does |
|---|-------|--------------|
| 1 | Regex masking | Deterministic rules: EMAIL, CVR, CPR, IBAN, SWIFT, PHONE, IP, name sign-offs |
| 2 | spaCy NER | Masks PER entities using Danish model (`da_core_news_lg`), excluding company blocklist |
| 3 | Contact-name matching | Exact lookup against contacts CSV; greedy multi-word first, then single first-name fallback |
| 4 | DAWA address masking | Fetches Danish postcode/city data from Dataforsyningen API; masks postcode+city pairs and standalone city names |

Masking applied at ingestion — raw PII never reaches downstream storage or LLMs.

## PII Types Covered

`[EMAIL]` `[CVR]` `[CPR]` `[IBAN]` `[SWIFT]` `[PHONE]` `[IP]` `[NAME]` `[ADDRESS]` `[CITY]`

## Evaluation Results (100 high-risk rows)

| Metric | False Negatives (missed PII) | False Positives (over-masking) |
|--------|------------------------------|-------------------------------|
| Affected rows | **6 (6.0%)** | **8 (8.0%)** |
| Affected spans | 9 spans | 12 spans |
| Primary type | NAME (8), TOKEN (1) | [NAME] (12 spans) |

### Missed PII (6%)
- 8 × NAME: single first names not caught by NER or sign-off keyword (Mikkel, Cornelius, Peter, Rasmussen, ARTEM)
- 1 × TOKEN: session token — out of scope currently

### Over-masking (8%)
- All [NAME] false positives: city names (Aarhus, Aalborg, København), domain names (billy.dk), company names, common Danish words (Jep, erhverskonto)
- Over-masking affects readability only, not privacy compliance

## Residual Risk

| Risk | Likelihood | Compliance Impact |
|------|-----------|-------------------|
| Missing PII (6% of high-risk rows — primarily isolated first names) | Low–Medium | Medium |
| Over-masking (8% of high-risk rows — readability only) | Low–Medium | Low |

Team acknowledges residual false-negative rate. Legal must explicitly accept this as part of sign-off. Future iterations will expand evaluation sets and reduce false negatives.
