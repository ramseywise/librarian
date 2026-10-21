---
title: Verify a Render by Text Extents, Not Pixels
tags: [patterns, infra, pattern]
summary: When an HTML-to-PDF render clips silently instead of reflowing, "it reports 1 page" proves nothing — measure fill from the PDF's own word bounding boxes (pdftotext -bbox) and probe for keywords at the end of each column, because raster scans read letterbox borders as content and word counts are non-monotonic across zoom levels.
updated: 2026-10-16
sources:
  - data/raw/claude-docs/sisyphus/skills/convert-cv/SKILL.md
---

# Verify a Render by Text Extents, Not Pixels

The sisyphus `convert-cv` skill renders a fixed-A4, two-column HTML template to PDF with
wkhtmltopdf. The template clips with `overflow: hidden` rather than reflowing, so every
failure mode is *silent*: the PDF is valid, is one page, and looks plausible at a glance.
Three of them were found the hard way.

## Failure 1 — the screen stylesheet wins

The template carries an `@media screen` block that unsets the fixed height and the
overflow clip so the file stays readable in a browser. Without `--print-media-type`,
wkhtmltopdf renders against the screen rules and the document spills to 7+ pages. A
dual-purpose (browser + print) template needs the print media type forced explicitly.

## Failure 2 — a renderer regression that still reports "1 page"

One installed wkhtmltopdf build (0.12.6 on Qt 4.8.7) laid the document out at roughly 75%
scale inside a correct A4 MediaBox — a ~60 mm dead band at the bottom and ~53 mm at the
right, page count still 1. `--zoom 1.28` compensates. The diagnostic that settled it was
re-rendering an *older* document's own HTML: it reproduced the same band, proving a
renderer regression rather than a CSS bug — and meaning a good PDF already on disk cannot
be regenerated without the flag. Known-good invocation:

```
wkhtmltopdf --page-size A4 -T 0 -B 0 -L 0 -R 0 --print-media-type --zoom 1.28 in.html out.pdf
```

## Failure 3 — measuring with the wrong instrument

| Method | Why it fails / works |
|---|---|
| Rasterise with `sips`/PIL, scan for the last inked row | `sips` letterboxes the page onto a taller canvas with pure-black fill; the scan reads the letterbox border or a clip boundary as a baseline — "confidently wrong numbers" |
| Compare `pdftotext` word counts across renders | Non-monotonic across zoom levels; not a signal |
| **`pdftotext -bbox out.pdf -`** and convert extents | Works: `yMax/842*297` = mm from top, `xMax/595*210` = mm from left. A healthy render lands within a few mm of the template's own print margins |
| **Keyword probe** near the end of each column (`pdftotext out.pdf - \| grep`) | Works: confirms clipped content actually survived |

## The general rule

When the output format can fail without erroring, verify with an instrument that reads
the artifact's *own* structure (text extents, embedded keywords) rather than a derived
representation (a raster whose canvas the converting tool chose). "Page count = 1" and
"looks fine" are both checks the broken render passes.

## See Also
- [[Evidence-Gated Skill Pipeline]] — instance-of (the render step at the end of the job-application pipeline)
- [[Verification Loops]] — extends (a concrete case of choosing the right verifier)
- [[Artifact Is Not Evidence: Push and Probe]] — extends (a produced PDF is not evidence it rendered correctly)
