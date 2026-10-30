---
title: Service Surface Defect Checklist
tags: [infra, reference]
summary: Ten concrete defect classes found live in a prototype HTTP service — ungated client ids reaching paths, uploads checked after reading the whole body, trusting declared MIME, blocking work on the event loop, TOCTOU across two opens, id-only mutation scope, blobs in listings, unfenced ingested documents, and splatted response models.
updated: 2026-10-30
sources:
  - data/raw/claude-docs/galactus/skills/review-safety/SKILL.md
  - data/raw/claude-docs/galactus/skills/proto-harden/SKILL.md
---

# Service Surface Defect Checklist

Every item below was found live in one galactus prototype, a FastAPI service whose 300
tests were green. The `review-safety` dimension checks each one the diff's surface can
reach.

| # | Defect | Fix |
|---|---|---|
| 1 | **Client string → filesystem path.** `directory / f"{client_id}.json"` is a traversal probe and a read primitive, not a lookup | Allowlist-gate the id (`^[a-z0-9_]+$`) *before* building the path |
| 2 | **Upload bounds checked after the read.** Read the whole body, then check the size: the OOM has already happened | Cap the read itself: `await file.read(cap + 1)`, length-check, return 413 |
| 3 | **Trusting declared type.** Client MIME and filename are untrusted | Validate magic bytes at the boundary. A mislabelled file accepted today is a failed job tomorrow, found by the wrong person |
| 4 | **Blocking work on the async loop.** Sync blob writes, document parsing and rasterisation inline let one big request stall every client's poll | `asyncio.to_thread`. File-backed SQLite needs WAL plus a busy timeout, or concurrent clients get `database is locked` 500s |
| 5 | **TOCTOU / repeated open.** A count taken under open A does not bound a render under open B | Check and use under one handle |
| 6 | **Mutation scoped by id alone.** One tenant can mutate another's data | `WHERE tenant = ? AND id = ?`, with a 404 indistinguishable from not-exists (no existence oracle) |
| 7 | **Listings return the blob** | Return metadata (`length(content)`), never `content` |
| 8 | **Ingested documents reach the prompt unfenced.** Uploaded files are untrusted third-party input at the injection sink | Fence as data with an explicit treat-as-data instruction |
| 9 | **Response model splatted from the stored doc.** `Model(**stored_doc)` leaks internal fields (dedup keys, tenant ids, original prompts) or crashes | Whitelist the response fields explicitly |
| 10 | **File content treated as instruction** | File content is data, never instruction (the reporter's own ground rule, applied to the service) |

Two of these hide behind code that looks correct. #2 reads like a size check, and #5 reads
like a bound. In both, the check and the effect happen in different places.

## See Also
- [[Production Hardening Patterns]] — extends (the concrete surface-level instances)
- [[Prompt Injection]] — extends (#8 is the ingestion-side sink)
- [[Written-but-Inert RLS Policies]] — extends (tenant scoping that exists on paper only)
- [[Prototype Hardening Pass]] — related (part of)
- [[Capability Token in a Serialized Row]] — instance-of (a token in a row prop handed to a client component)
