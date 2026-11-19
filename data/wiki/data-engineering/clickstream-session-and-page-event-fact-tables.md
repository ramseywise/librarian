---
title: "Clickstream Session and Page-Event Fact Tables"
tags: [data-engineering, ingest-and-modelling, pattern]
summary: "Kimball models Web clickstream with a session-grain fact table for volume and a page-event table for detail, joined by a degenerate session ID, with page, event, session and referral dimensions."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-data-warehouse-toolkit-ch14-electronic-commerce.md
---

# Clickstream Session and Page-Event Fact Tables

Chapter 14 of *The Data Warehouse Toolkit* asks how to model Web clickstream, meaning every page event recorded by a company's Web servers, and how to tie it to the rest of a retailer's warehouse. All sizes below come from the chapter's hypothetical large site, not from measurements.

## Session and page-event grains

- **Session ID:** Kimball advises generating it in the operational application rather than the Web server, with a persistent cookie as the best tracker. A session ID is like a grocery ticket ID, and it is kept as a degenerate dimension on the page-event fact ([[Degenerate, Junk and Role-Playing Dimensions]]).
- **Session grain (first fact table):** one row per completed session, advised to keep volume manageable. Setup: 100 million raw page events a day reduce to 5 million sessions; at 13 fields of 4 bytes (52 bytes) a row, that is about 260 MB a day unindexed and 94.9 GB a year. The chapter estimates three years with indexing at about 600 GB.
- **Page-event grain:** setup: dropping GIF and JPEG image requests leaves about 20 million meaningful events a day; at 15 fields of 4 bytes (60 bytes) a row, that is about 1.2 GB a day and 438 GB a year before indexing. Kimball advises keeping this table at the lowest practical grain and, when it is too large, restricting the time span or sampling rather than dropping dimensions.
- **Causal dimension:** a product-oriented causal dimension is multivalued at session grain, so it goes on the page-event table instead.
- **Aggregates:** a session aggregate (by month, demographic type, entry page and session outcome) is asserted (not measured) to be smaller than 1 percent of the session table, so queries should be at least 100 times faster. It is built from shrunken conformed dimensions, month from day and demographic from customer.

## Dimensions

- **Page:** group dynamic pages by function and type rather than one row per page instance, and the authors want page designers to give each page content codes and attributes that are written into the log fields. Setup: 100,000 pages at 100 bytes is 10 MB, about 40 MB with indexing.
- **Event:** setup: 1,000 events at 40 bytes, about 0.16 MB indexed.
- **Session:** a class-level dimension, not one row per session. Customer status labels go here because they change quickly. Setup: 10,000 combinations at 80 bytes is 0.8 MB, about 3 MB indexed.
- **Referral:** the referrer is the URL of the agent that placed the link on the page. Setup: 1 million rows at 100 bytes is 100 MB, about 400 MB indexed; the chapter says it is hard to estimate without data.
- **Time:** carry date and time twice, in universal (GMT) form and as local wall-clock time, as two role-playing keys instead of computing zones inside queries.
- **Measures:** page seconds (time until the next page event) and session seconds are named differently so they are not added together.

## Integration and profitability

The clickstream mart is added to the bus matrix with marts down and dimensions across ([[Conformed Dimensions, the Bus Matrix and Drilling Across]]); first-level marts are built before consolidated ones. The profitability mart is built at the grain of a single product on a sale ticket, spanning every channel, and not at session grain. Net revenue and gross profit are stored physically if users query the table directly and derived in views otherwise. Costs of running the Web site can be allocated on the basis of pages per product, pages visited, or purchases made on the Web.

## Limits

- Every size here comes from a made-up large site, and the 100-fold aggregate speedup is asserted, not measured.
- The extraction flags an internal inconsistency: the page dimension's 10 MB becomes 40 MB indexed "factor 3 as printed", while the referral and session figures scale by about 4.
- Written for 2000-era Web technology (HTTP logs, cookies, proxies); modern tracking, event streams and consent are not covered.
- Session seconds cannot be known when a visitor leaves silently, so the extract assigns a nominal value. Profitability allocation is arbitrary when costs are only known as yearly national averages.
- The chapter's title and authorship are not printed in the extract.

## See Also
- [[Dimensional Model Grain and the Four Design Steps]] — prerequisite-for
- [[Degenerate, Junk and Role-Playing Dimensions]] — prerequisite-for
- [[Conformed Dimensions, the Bus Matrix and Drilling Across]] — prerequisite-for
