---
title: Canonical Document IR for Ingest
tags: [rag, pattern]
summary: Normalise every source (PDF, HTML, JSON API, CSV ledger) through a slim adapter into one typed Document schema — sections with type, content and provenance span — so the LLM layer is source-blind; for small multimodal corpora send page images to a vision model and skip the vector store, but thread provenance from ingest and validate citations before rendering.
updated: 2026-10-16
sources:
  - data/raw/claude-docs/sisyphus/docs/research/2026-08-08_ml6-prototyping_ingest-layer.md
  - data/raw/claude-docs/sisyphus/docs/research/2026-08-08_ml6-prototyping_io-boundary.md
---

# Canonical Document IR for Ingest

From research for a document-generation take-home (two company PDFs in, one templated
document out, with "add HTML pages and financial ledgers later" as the extensibility
question). Medium-confidence web research; the architecture is the reusable part.

## Hub-and-spoke, borrowed from compilers

Like a compiler IR, a canonical intermediate decouples N sources from M consumers. Each
source gets a slim adapter; every adapter emits the same type; the generation layer never
knows where content came from:

```
Document { id, source_type: pdf|html|api|csv, title,
           sections: [{ type: heading|text|table|image, content,
                        metadata: { source_span, confidence } }],
           images:   [{ path, alt_text, provenance_span }],
           metadata: { extracted_at, page_count, language } }
```

The contract between ingest and orchestration is a pair of typed models: a **context
payload** (the Documents) and a **generation template** (field names, limits, layout
constraints). Validate at the boundary; swap extraction libraries without touching the
generator. Keep it minimal — no pre-chunking, pre-embedding or indexing in the IR.

## Choosing the PDF adapter

| | Vision-native (page images → multimodal model) | Parse-first (layout parser → typed elements) |
|---|---|---|
| Strength | Text, images and tables in one pass with spatial context | Higher precision on born-digital text; cheap CPU at scale |
| Weakness | Layout confusion, missed strikethrough, poor bounding-box citations | **Tables** — borderless, merged-cell and multi-page tables break most parsers |
| Fit | Mixed-modality inputs, small volume | Clean text-dominant documents, high volume |

Rule: use vision for scanned or image-embedded tables, but **parse machine-generated
tables (JSON, CSV, HTML) natively** — don't route well-formed data through a model that can
transpose digits or drop rows. Spot-check vision-extracted tables; for financial data the
risk is not acceptable. OCR errors propagate into everything downstream, so flag
suspicious character patterns or low-confidence extractions.

Images are metadata, not content: extract them with source page and format, caption via
the vision model, keep vector logos lossless, and let the generator choose.

## Full context beats RAG at this size

Two PDFs is ~10k tokens. Put them in context and use **grep** to highlight sections —
cheaper, simpler and inspectable. A vector store becomes justified around >1M tokens,
>50 documents, or high query volume over the same corpus. The interview answer to "don't
you need a vector store?" is the corpus size plus the trigger that would change it.

## Provenance is threaded, not bolted on

Every extracted section carries `{doc_id, page, char_span, confidence}` from the moment of
ingest. The generator is asked to cite in that vocabulary (e.g. `[sender:3:150]`), and
**every citation is validated against a real span before rendering** — hallucinated
citations exist syntactically but don't contain the claim. Native PDF bounding boxes are a
stronger anchor than text references because they can't drift. Emit per-field
factuality confidence and route uncited facts to human review.

## See Also
- [[RAG Knowledge Preparation]] — extends (the ingest step before any retrieval decision)
- [[Length Limits Are a Fit Layer, Not a Prompt]] — prerequisite-for (the generator side of the same typed boundary)
- [[Evidence-Labelled Generation with Deterministic QC]] — extends (label-then-cite, validated by code)
- [[Grounding Claim Methodology]] — extends (citations checked against source spans)
- [[RAG Architecture Selection]] — alternative-to (when the corpus outgrows full context)
