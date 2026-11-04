---
title: "Access Control Below the User, Audit Logs and Breach Scope"
tags: [foundations, pattern]
summary: "A control the subject can alter is no control: enforce access below the user, log who read what with purpose, and keep an inventory so breach scope is a lookup."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--07-architecture-and-governance--notes--02-access-control-pii-gdpr.md
  - data/raw/repos/learn-ai-engineering/data-engineering--07-architecture-and-governance--README.md
---

# Access Control Below the User, Audit Logs and Breach Scope

Engineering guidance, not legal advice; real cases go to a data protection officer.

## Inventory first

You cannot protect a column you do not know is personal. Personal data (GDPR Art. 4(1)) is anything relating to an identified or identifiable person; the US term PII is information that can distinguish, trace or is *linkable* to one. Three working classes: **direct identifiers** (name, email, phone), **quasi-identifiers** (postcode, birth date, sex; identifying in combination, see [[K-Anonymity, Quasi-Identifiers and Linkage Attacks]]) and **pseudonyms** (an ID standing in for a person). Special categories such as health data carry a stricter rule, so label them.

Column names are not enough: a free-text notes column labelled as non-personal held an email a user had typed to support, copied everywhere the table went. Scan values as well as names. A sampled regex scan finds easy cases and misses names in prose, so a clean result means "found nothing". Keep the result in the catalog ([[Data Catalog Metadata: Push, Pull and Measuring Adoption]]).

## RBAC and ABAC

RBAC grants permissions to roles and is easy to audit by reading grants. ABAC decides each request from subject and object attributes, environment and policy, and scales past a role per region per purpose. Use RBAC for which tables at all, attributes for row and purpose rules. Purpose is the attribute most systems forget: GDPR purpose limitation means a table readable for tax reporting is not automatically readable for marketing.

Warehouse rules that catch people out: Postgres row security with no policy is default deny, but the table owner usually bypasses it unless forced, and superusers always do; BigQuery row policies hide rows from any grantee not listed once any policy exists; column policy tags need both dataset and tag permission; Snowflake masking applies at query time and is set by a security officer, not the object owner. See also [[RLS Gates Rows, Not Columns]].

## Enforcement must sit below the user

In an embedded engine a view masked columns and a view filtered rows by a session variable, yet the same connection could read the base table and could set its own region variable. DuckDB has no users, roles or GRANT and runs SQL with the privileges of the process. Attack your own masking as the user. The fix is a boundary the process cannot cross: publish a masked copy to a separate directory and give the analyst a connection with allowed directories set, external access off and configuration locked (the lock matters, or the analyst re-enables access). Those settings are defence in depth, not a substitute for OS sandboxing; real boundaries are separate files and permissions.

## Audit log and the 72-hour breach clock

Access control says who *may* read; only a log says who *did*. Wrap the connection so each query records user, purpose, tables, SQL and row count. A contractor's query returned 5,000 riders' contact and location data with purpose `unknown`; breach scope (categories and approximate number of subjects, Art. 33(3)) came from a lookup. A purpose of unknown is worth an alert itself.

Art. 33: notify the supervisory authority without undue delay, where feasible within 72 hours of becoming aware, unless a risk is unlikely; all breaches must be documented. Guidance clarifies that "aware" means reasonable certainty that personal data was compromised, so a short prompt investigation is allowed, but sitting on an alert does not stop the clock. A breach includes *loss*, such as data encrypted with a key no longer held; that matters for [[Erasure on Immutable Storage: Vacuum, Crypto-Shredding and the Ledger]], where key destruction must be deliberate and logged. A processor tells the controller without undue delay.

## GDPR principles as engineering mechanisms

| Principle | Mechanism |
|---|---|
| Lawfulness, transparency | Legal basis recorded per purpose |
| Purpose limitation | Purpose attribute in access decisions and the audit log |
| Minimisation | Drop columns at ingest, publish masked views, no SELECT * into features |
| Accuracy | Quality tests, correction flows |
| Storage limitation | Retention jobs on every copy |
| Integrity and confidentiality | Encryption, access control, tested restore |
| Accountability | Records, logs, test results |

There are six lawful bases (consent, contract, legal obligation, vital interests, public task, legitimate interests); the basis decides what can happen later, since consent can be withdrawn. The controller sets purposes and means; a cloud warehouse is usually a processor and the controller stays responsible. Transfers outside the EU need an adequacy decision or safeguards, surfacing as storage region, replication targets and where support staff sit.

A **record of processing activities** (Art. 30) is best kept as data with a required-fields test (purpose, basis, subjects, categories, recipients, transfers, erasure period, security). A model-training activity failed it for a missing retention limit and lawful basis. Under 250 employees there is a narrow, conditional exemption.

## Pitfalls
- Masking in a view on a connection that can read the table; a filter on a variable the user can set.
- Free text left out of the inventory; non-production copies (dev datasets, notebooks, exports, feature tables) outside the coverage check.
- Reading "72 hours" as a deadline to start work, and building the log after the incident.

## See Also
- [[Pseudonymised Is Not Anonymised: Hashing Attacks and Keyed Pseudonyms]] — extends
- [[K-Anonymity, Quasi-Identifiers and Linkage Attacks]] — extends
- [[Erasure on Immutable Storage: Vacuum, Crypto-Shredding and the Ledger]] — extends
- [[PII Masking Approaches]] — related
- [[RLS Gates Rows, Not Columns]] — related
- [[Data Mesh as an Ownership Model and Federated Governance]] — prerequisite-for
