---
title: Dashboard API Exposure and Payload Cost
tags: [foundations, pattern]
summary: A list endpoint returning the whole table is insecure and slow; return aggregates by default, filter fields with a response model, cap and keyset-paginate row-level routes, and enforce limits server-side.
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--05-visualisation-and-storytelling--notes--06-dashboard-stacks-from-python-to-frontend.md
---

# Dashboard API Exposure and Payload Cost

A first-draft endpoint that returns the full customer table works on a laptop. At 50,000 rows it sent 11,235 KB (1,418.7 KB gzipped) in a median 533.8 ms, with every column including email addresses, to anyone with the address.

## Four faults (OWASP API Security list)

- **No authentication** (API2).
- **No per-object permission** (API1): seeing a segment's size is a different right from seeing a named customer.
- **Every property returned** (API3): nobody excluded the email column.
- **No limit** (API4): one request does all the work the server can do.

## Fix

- `response_model` filters output to the named fields, so a column cannot leave by accident.
- `Depends` runs a key or role check before the function; 401 = no valid key, 403 = valid key without the right, 422 = request rejected by validation (for example over the `Query(le=500)` cap, a cap you choose).
- Real deployments verify a signed token from the sign-in provider. A key compiled into a front-end bundle is public, and a limit only in the front end does nothing against direct calls: keep credentials and limits on the server.
- **Keyset pagination** for row-level routes: request rows "after the last id seen". OFFSET still computes skipped rows, and keyset needs a unique sort order; the price is no jumping to an arbitrary page, no loss for an export.

## What a request costs (50,000 synthetic rows, in-process)

| Request | Rows | JSON KB | Gzip KB | Median ms |
|---|---:|---:|---:|---:|
| Every customer, every column | 50,000 | 11,235.3 | 1,418.7 | 533.8 |
| One row per segment | 4 | 0.5 | 0.2 | 3.8 |
| Map grid counts, cell 0.25 | 442 | 28.8 | 2.4 | 5.3 |
| One page of 100 customers | 100 | 8.5 | 1.1 | 2.2 |

The summary is about 140 times faster. Dropping columns is not enough (three columns still 2,496 KB), nor is column-oriented layout (1,520 KB); a chart of groups does not need a row per person.

## Privacy by aggregation

Count customers in grid cells and drop cells under five so no mark is one person. The map cells covered 1,632 of a region's 2,001 customers, so the table must carry the total and the caption say what the map omits. This reduces, not removes, disclosure: comparing filtered views can still reveal small counts.

## Cheap extras

`GZipMiddleware` (default minimum size 500 bytes); an `ETag` so browsers reuse an answer until the batch job writes a new table; mark per-person responses `Cache-Control: private`, since forgetting it can leak personal information.

## See Also
- [[Dashboard Stack Layers and Choosing a Route]] — prerequisite-for
- [[Precomputed Labels, Not Refits on Filter]] — related
- [[Rendering Many Points: WebGL, Datashader and Bundle Weight]] — related
