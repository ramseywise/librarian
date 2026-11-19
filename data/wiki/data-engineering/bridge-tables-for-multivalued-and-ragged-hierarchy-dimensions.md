---
title: "Bridge Tables for Multivalued and Ragged Hierarchy Dimensions"
tags: [data-engineering, ingest-and-modelling, pattern]
summary: "A bridge table between fact and dimension lets plain SQL roll facts up a ragged hierarchy or share them among several dimension members, at the price of an overcounting risk."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-data-warehouse-toolkit-ch06-customer-relationship-management.md
  - data/raw/papers/2026-11-08-data-warehouse-toolkit-ch07-accounting.md
  - data/raw/papers/2026-11-08-data-warehouse-toolkit-ch08-human-resources-management.md
  - data/raw/papers/2026-11-08-data-warehouse-toolkit-ch09-financial-services.md
  - data/raw/papers/2026-11-08-data-warehouse-toolkit-ch13-health-care.md
  - data/raw/papers/2026-11-08-data-warehouse-toolkit-ch15-insurance.md
---

# Bridge Tables for Multivalued and Ragged Hierarchy Dimensions

A dimension should take one value per fact row ([[Dimensional Model Grain and the Four Design Steps]]). Two cases break that: a hierarchy of unpredictable depth, and a fact row tied to several dimension members. Kimball and Ross handle both with a **bridge table**.

## Variable-depth hierarchies

Fixed-depth hierarchies are plain level attributes in the dimension, with lower-level values repeated upward for shallow customers. For a ragged one (a parent company and its subsidiaries) the authors advise a bridge, not a recursive pointer.

- The bridge holds a row for every path from a node down to each subsidiary, plus a zero-length row from a node to itself, with level, bottom and top flags.
- The fact joins to the bridge on the subsidiary key; the customer dimension joins on the parent key, so a constraint on any node sums revenue across everything beneath it.
- Row count is the nodes at each level times that level's depth, summed. Setup: the book's 8-customer, 4-level example, with 1, 2, 3 and 2 customers per level, has 22 rows (1+4+9+8). The chapter says such a bridge usually outgrows its dimension severalfold.
- To avoid double counting, constrain to one parent, or select distinct subsidiary keys in a subquery. Effective and expiration dates, and weighting factors, are added if needed.
- Chapter 7 uses bridges for ragged organisation hierarchies in the ledger and, for uneven category hierarchies, copies the category name into the subcategory column so no Not Applicable bucket appears.

## Multivalued dimensions

- **Account holders:** the bank chapter uses an account-to-customer bridge with a weighting factor when one account has several customers; there is no bridge when the fact is at customer grain. Households are a separate dimension, built from business rules and algorithms, often with specialised matching products.
- **Employee skills:** a skills-group key on the employee row maps to one row per keyword in a skills outrigger. An OR query is simple; an AND needs a union-and-intersection style of SQL, which the authors hide behind an interface. The alternative is one delimited string per skills list, queried with LIKE on each keyword, so AND and OR are single statements. Case is normalised, and the string is pinned in memory or given a pattern index when slow.

## Diagnosis groups and other multivalued cases (chapters 13 and 15)

- **Diagnosis group (ch13):** the authors say a billing organisation can meet patients with over 50 diagnoses, which rules out a fixed set of slots, and a finer grain is rejected too. The fact carries a diagnosis group key; the bridge has one row per diagnosis in the group with a weighting factor, and the weights within a group have to add up to exactly 1.00 for allocated totals to reconcile.
- **Two views:** one view over fact and bridge applies the weights (the correctly weighted report); the other omits them (the impact report, summarising by diagnosis regardless of allocation).
- **Joins and reuse:** if a modelling tool demands primary-key and foreign-key joins, a diagnosis group dimension goes between fact and bridge. A standard portfolio of groups is reused at high volume; for hospital stays the groups are unique per patient, handled as type 2, with begin and end dates on the bridge.
- **Complex events:** mix role-playing with multivalued dimensions and leave out the weights, giving impact reports only.
- **Insurance (ch15):** bridges for an SIC group and for the insured driver, with a weighting factor, optional begin and end dates and an Unknown row.

## Limits

- The chapters call bridge tables not for the faint of heart and warn of overcounting; a huge parts explosion may make the bridge enormous.
- The authors concede that LIKE searches starting with a wildcard over the delimited skills list run slowly on a large dimension.
- The text is early-2000s (the extraction infers the 2nd edition, 2002): the recursive-pointer comparison refers to Oracle's CONNECT BY, and the extraction notes nonrelational OLAP tools handle built-in hierarchies for dimensions under 64,000 members.
- No benchmark numbers; the row count is a single worked example and the other detail is deferred to chapter 13, which is not in this batch.
- The extraction notes that cost and weighting-factor allocation is conceded to be controversial and arbitrary. Chapter 13's code sets (ICD-9-CM, CPT-4, HCPCS) have since moved on (the extraction cites ICD-10), and the chapter's own year and authors are not printed.

## See Also
- [[Dimensional Model Grain and the Four Design Steps]] — prerequisite-for
- [[Conformed Dimensions, the Bus Matrix and Drilling Across]] — related (the same silent overcounting hazard as a grain violation)
- [[Minidimensions for Rapidly Changing Monster Dimensions]] — related
- [[Slowly Changing Dimensions Types 1, 2 and 3]] — related (bridge rows can carry effective and expiration dates)
