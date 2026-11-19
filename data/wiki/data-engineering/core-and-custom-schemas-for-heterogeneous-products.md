---
title: "Core and Custom Schemas for Heterogeneous Products"
tags: [data-engineering, ingest-and-modelling, pattern]
summary: "When product lines have different facts and attributes, Kimball and Ross keep a core fact and product dimension for the common measures and a custom schema per line that reuses the core's keys."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-data-warehouse-toolkit-ch09-financial-services.md
  - data/raw/papers/2026-11-08-data-warehouse-toolkit-ch03-inventory.md
  - data/raw/papers/2026-11-08-data-warehouse-toolkit-ch13-health-care.md
  - data/raw/papers/2026-11-08-data-warehouse-toolkit-ch15-insurance.md
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

## Related cases in chapters 13 and 15

- **Insurance lines (ch15):** for heterogeneous lines, each line of business gets its own dimension tables, while transactions need no per-line fact tables; snapshot facts that differ by line are split into separate physical tables rather than one table full of nulls.
- **Fact dimension (ch13):** for sparse, heterogeneous medical records, an entry-type dimension tells what each fact row stands for and which of its fact columns apply, next to generic columns for an amount, a flag, a comment key and a file name. Setup: an event with 10 numeric measurements becomes 10 fact rows instead of one. As the data gets denser, the authors say to revert to an ordinary fact table. Free text stays out of the fact table through a comment dimension, and image file names are stored rather than blobs, so other tools can read the images, at the cost of keeping a file store in step.

## Limits

- By its own account the chapter's schemas are partial and not complete industry solutions; it covers retail banking only.
- The optimiser-ordering advice was not measured; all examples are illustrative. The text is early-2000s (the extraction infers the 2nd edition, 2002), and the extraction dates its Sybase IQ fact-indexing note to that period.
- The extraction records the pattern as guidance with no performance numbers.
- Chapters 13 and 15 are illustrative designs with no data; the extraction places chapter 13 in the 1990s and 2000s relational era.

## See Also
- [[Conformed Dimensions, the Bus Matrix and Drilling Across]] — prerequisite-for
- [[Dimensional Model Grain and the Four Design Steps]] — prerequisite-for
- [[Minidimensions for Rapidly Changing Monster Dimensions]] — related
