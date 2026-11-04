---
title: "Pseudonymised Is Not Anonymised: Hashing Attacks and Keyed Pseudonyms"
tags: [foundations, concept]
summary: "Hashing a low-entropy identifier is pseudonymisation at best; a keyed hash with the key outside the lake, scoped per domain, is the minimum."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--07-architecture-and-governance--notes--02-access-control-pii-gdpr.md
---

# Pseudonymised Is Not Anonymised: Hashing Attacks and Keyed Pseudonyms

Under GDPR (Art. 4(5), Recital 26), pseudonymised data can be attributed to a person with separately kept additional information, so it is still personal data; identifiability is judged by the means reasonably likely to be used (cost, time, technology). Only truly anonymous data is out of scope. The Article 29 Working Party opinion lists "pseudonymised means anonymised" as a common mistake and gives three anonymisation tests: can you still **single out** a person, **link** records about them, or **infer** something about them? Any ID stays personal data as long as anyone holds the mapping.

## Why a plain hash fails

A phone number has few possible values, so an attacker hashes them all. Against 2,000 leaked SHA-256 hashes of phone numbers (a 10,000,000-value space), all 2,000 were reversed in 3.6 s. One salt shared across the column, stored beside the data, reversed 2,000 of 2,000 in 3.5 s because it costs the attacker nothing extra. A per-record salt forces a fresh search per target; a simple multiplication of the timing gives about two hours for these 2,000 on one laptop, an unmeasured estimate and not a defence.

An **HMAC** with a key held in a key management service and never in the lake resisted: 0 hits in 200,000 guesses without the key.

## Scope the key

One key across databases makes them joinable: with one shared key, 1,000 of 1,000 records linked across two domains; with one key per domain, 0 linked. Sharing a key is a decision to allow joining on that person and should be made on purpose. A **vault token** has no mathematical link to the value, at the cost of a lookup service everything depends on.

| Technique | Reversible by | Status |
|---|---|---|
| Plain hash of phone/email | Anyone, by enumeration | Treat as exposed |
| Salted hash | Anyone with the salt and time | Pseudonymised |
| HMAC, key in a KMS | Key holder | Pseudonymised |
| Vault token | Vault operator | Pseudonymised |
| Generalised and aggregated, tested | Should be nobody | Possibly anonymous if it passes all three tests |

Pseudonymisation is still worth doing: Art. 25 and 32 name it as a measure because it reduces what a leak exposes, but it does not take data out of scope. Default to "still personal data" and let the DPO argue it down.

## See Also
- [[K-Anonymity, Quasi-Identifiers and Linkage Attacks]] — prerequisite-for
- [[Access Control Below the User, Audit Logs and Breach Scope]] — related
- [[PII Masking Approaches]] — related
