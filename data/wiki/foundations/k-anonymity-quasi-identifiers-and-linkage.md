---
title: "K-Anonymity, Quasi-Identifiers and Linkage Attacks"
tags: [foundations, concept]
summary: "Removing names does not anonymise a table: combinations of quasi-identifiers single people out, k-anonymity measures it, and l-diversity covers the inference it misses."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--07-architecture-and-governance--notes--02-access-control-pii-gdpr.md
---

# K-Anonymity, Quasi-Identifiers and Linkage Attacks

**Quasi-identifiers** are columns that identify only in combination. **k-anonymity** requires every combination of their values to be shared by at least k records. Generalising (coarser postcode, birth decade) trades detail for group size.

Measured on 5,000 synthetic people:

| Columns | k | Share unique |
|---|---|---|
| postcode, birth date, sex | 1 | 99.8% |
| postcode, birth year, sex | 1 | 48.1% |
| 3-character postcode prefix, birth decade, sex | 211 | 0% |
| prefix, decade | 427 | 0% |

The later rows flatter because all synthetic postcodes shared the same first three digits, so that column stopped distinguishing anyone; real data has more spread and lower k.

## Linkage

Uniqueness matters because a release can be joined to a public list carrying the same attributes. In a synthetic run a 500-person public list matched all 500 uniquely against the "anonymised" release, revealing an invented sensitive flag for 6. The mechanism is the real result: in a published study of a movie-rating dataset of 500,000 subscribers, eight ratings (two may be wrong) with dates within 14 days identified 99% of records, and two ratings with dates within three days identified 68%. Any sufficiently detailed behaviour, such as trip history, is a quasi-identifier.

## Where k-anonymity fails

If everyone in a group shares one sensitive value, you learn it without singling anyone out. That fails the inference test. **l-diversity** requires several distinct sensitive values per group: a group with k=3 and l=1 means anyone known to be in it visited the clinic, while a group with k=3 and l=3 does not leak that way. Usual mistakes: missing a quasi-identifier, using a small k, weighting attributes equally when they reveal unequally. Location coordinates rounded to three decimals (around a hundred metres) are strong quasi-identifiers; publish a coarse area or drop them and re-test k.

## See Also
- [[Pseudonymised Is Not Anonymised: Hashing Attacks and Keyed Pseudonyms]] — prerequisite-for
- [[Access Control Below the User, Audit Logs and Breach Scope]] — related
