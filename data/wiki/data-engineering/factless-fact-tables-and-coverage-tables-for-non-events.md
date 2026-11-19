---
title: "Factless Fact Tables and Coverage Tables for Non-Events"
tags: [data-engineering, ingest-and-modelling, pattern]
summary: "Kimball and Ross model an event with no measurements as a keys-only fact table, and model things that did not happen with a coverage table of every possible combination, queried by set difference."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-data-warehouse-toolkit-ch12-education.md
  - data/raw/papers/2026-11-08-data-warehouse-toolkit-ch15-insurance.md
---

# Factless Fact Tables and Coverage Tables for Non-Events

A fact table normally holds numbers. Chapter 12 of Kimball and Ross (a university case study) covers two table shapes that hold only keys, and the question of how to analyse events that did not occur. The general fact-table kinds are on [[Transaction, Periodic and Accumulating Snapshot Fact Tables]].

## Event tables

An event with no numeric measurement is stored as one row of keys, one key per participating dimension. Counting replaces summing.

- Registration grain: each row is a course a student registered for in a given term. The term dimension has to conform to the calendar date dimension and share its common attributes exactly.
- Counting any key column returns the same answer, since every row has every key. A unique count of instances needs COUNT DISTINCT.
- The authors advise adding a column that always holds 1, so the SQL can sum a real column.
- Adding real facts (tuition, credit hours, grade) is allowed only when they fit the grain, and the table is then no longer factless.
- Frequently changing student attributes such as major and class level are advised as minidimensions ([[Minidimensions for Rapidly Changing Monster Dimensions]]).
- Chapter 15 uses the same shape for insurance accident events: a count fixed at 1, with bridge tables optional so the grain is kept.

## Coverage tables

A coverage table is a keys-only fact table with a row for every combination that could occur, whether or not it did. Setup: a facility-utilisation table with a row for each facility per hourly block per term, used or not.

The promotion case: a coverage table lists the products on promotion. Products that were promoted but did not sell are the coverage rows minus the products found in the sales fact table. The authors say this table is far smaller than adding zero rows to the sales fact.

## Other ways to show a non-event

- **Explicit zero rows:** the authors advise these only when the non-events share the dimensionality of the events and are few. Attendance fits (no-shows, an attendance flag of 1 or 0); flights not taken do not.
- **NOT EXISTS:** needs no extra design, but the authors call it slow and limited by tools, and say products that never sold in the window are not found.
- **OLAP cubes:** multidimensional cubes handle sparsity, so non-events can be analysed without storing zeroes.

## Limits

- Design guidance from a hypothetical university with no measurements or benchmarks; the extraction notes the SQL for non-events is 2002-era, relational and OLAP only.
- Page 246 of the chapter extract is scan noise.
- The accident-event point from chapter 15 comes from an illustrative case study of one fictional insurer.

## See Also
- [[Transaction, Periodic and Accumulating Snapshot Fact Tables]] — prerequisite-for
- [[Dimensional Model Grain and the Four Design Steps]] — prerequisite-for
- [[Conformed Dimensions, the Bus Matrix and Drilling Across]] — related (the term dimension must conform to the calendar)
