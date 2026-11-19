---
title: "Core and Custom Schemas for Heterogeneous Products"
tags: [data-engineering, ingest-and-modelling, pattern]
summary: "When product lines have different facts and attributes, Kimball and Ross keep a core fact and product dimension for the common measures and a custom schema per line that reuses the core's keys."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-data-warehouse-toolkit-ch09-financial-services.md
  - data/raw/papers/2026-11-08-data-warehouse-toolkit-ch03-inventory.md
---

# Core and Custom Schemas for Heterogeneous Products

A retail bank sells accounts whose facts and attributes differ by product line. Chapter 9 of Kimball and Ross splits the model in two.

## Mechanism

- The **core** fact table and product dimension hold the facts and attributes every line shares. Setup: the bank's monthly account snapshot, one row per account per month, ends with six dimensions in the core: month-end date, account, household, branch, product and status.
- Each line of business gets a **custom** schema containing the core facts plus its own special facts and attributes.
- A custom product dimension is a row subset of the core product dimension and reuses the same surrogate keys, so the dimensions stay conformed ([[Conformed Dimensions, the Bus Matrix and Drilling Across]]). Users analysing across products use the core; users analysing one line use that line's schema.
- Where lines share table space, an extended fact table links to the core fact through a special join key, and the optimiser has to resolve the core constraints first.
- Line-specific attributes can sit in an extended-product outrigger that the base product dimension points to, exposed through one view per product type (the authors call it context-dependent). The same device covers account-specific attributes such as a mortgage's property details.
- When the facts are at transaction grain, one core fact table is enough; the choice between core and custom product dimension then follows whether the analysis is across or within product lines.

The inventory chapter defers heterogeneous products to this chapter.

## Limits

- By its own account the chapter's schemas are partial and not complete industry solutions; it covers retail banking only.
- The optimiser-ordering advice was not measured; all examples are illustrative. The text is early-2000s (the extraction infers the 2nd edition, 2002), and the extraction dates its Sybase IQ fact-indexing note to that period.
- The extraction records the pattern as guidance with no performance numbers.

## See Also
- [[Conformed Dimensions, the Bus Matrix and Drilling Across]] — prerequisite-for
- [[Dimensional Model Grain and the Four Design Steps]] — prerequisite-for
- [[Minidimensions for Rapidly Changing Monster Dimensions]] — related
