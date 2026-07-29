---
title: Grounding Claim Methodology
tags: [eval, rag, pattern]
summary: Claims-based grounding — the "yellow highlighter" approach to RAG verification, where the agent extracts verbatim supporting quotes from retrieved documents before writing the final answer, creating a verifiable paper trail.
updated: 2026-07-06
sources:
  - raw/claude-docs/project-g/docs/support-agents/grounding-methodology.md
---

# Grounding Claim Methodology

In RAG-grounded agents the answer should come from retrieved passages — not from the model's training memory, guesses, or assumptions. Claims are the mechanism that enforces this.

## The Yellow Highlighter Metaphor

A **claim** is a specific fact the AI extracts from retrieved documents *before* it writes the final answer — in practice, copying the exact sentence or passage from the source that supports the answer.

```
1. Find the relevant pages       → RAG search retrieves document chunks
2. Highlight the exact sentences → AI marks these as claims
3. Write the answer from highlights → only after evidence is marked
```

Claims are a **yellow highlighter for AI**: they force the system to identify which facts it is using before it explains them.

---

## Why Claims Matter

1. **Claims anchor the AI to facts.** Without claims, an AI generates answers loosely connected to sources. Claims make the answer designed to be grounded in specific retrieved evidence. (Qi et al. 2024 show self-generated citations can be unreliable — claims reduce but don't eliminate this risk.)

2. **Claims create a verifiable paper trail.** Makes it possible to inspect the exact evidence behind an answer without reading full paragraphs. (Chen et al. 2025: sub-sentence citations reduce the verification burden.)

3. **Claims separate facts from presentation.** Source documents may use formal/technical/legal wording. The final answer can be friendlier — claims let us verify the factual basis independently of phrasing.

4. **Claims make debugging much easier.** If the AI gives a bad answer, the claim immediately identifies the failure type:
   - Wrong document retrieved → retrieval problem
   - AI highlighted wrong sentence → extraction problem
   - Right claim, wrong explanation → generation problem

---

## Connection to Grounding Tiers

Claims map directly to the grounding verification pipeline:

| Tier | What it enforces |
|---|---|
| Tier 1 | Top-level `citations[]` — IDs must come from the retrieved set |
| Tier 2 | Per-claim `citations` — every claim-level ID must be declared at top level. Closes the "valid IDs but training-memory answer" defeat case. |
| Tier 3 | `supportingQuote` — the verbatim excerpt must appear word-for-word in the cited passage. Zero token overlap = fabricated. |
| Tier 4 | Diagnostics — language mismatch, hallucinated suggestion URLs (log-only) |

**Why Tier 2 exists:** Tier 1 alone is defeatable. A model that learns which passage IDs were fetched can list only valid IDs at the response level while composing its answer entirely from training memory. The `claims` array forces the model to declare, per assertion, which passage it draws from and provide a verbatim excerpt. Tier 2 cross-checks that every claim-level citation was already declared in the top-level `citations` array.

---

## Quote Boundary Check (Tier 3 Detail)

The quote must match at word boundaries — not mid-word. A naïve `str.find()` stops at the first match, which may land mid-word (e.g. `"kvartal"` found inside `"kvartalsvis"` fails the suffix check). The correct approach searches **all occurrences**, verifying both prefix and suffix word boundaries at each position:

```python
start = 0
while True:
    idx = text_norm.find(quote_norm, start)
    if idx < 0:
        break
    before_char = text_norm[idx - 1] if idx > 0 else ""
    after_idx = idx + len(quote_norm)
    after_char = text_norm[after_idx] if after_idx < len(text_norm) else ""
    if (not before_char or not before_char.isalnum()) and \
       (not after_char or not after_char.isalnum()):
        quote_found = True
        break
    start = idx + 1
```

---

## Important Limitations

Claims are not magic. The system can still fail if:
- Wrong documents are retrieved
- The extracted claim is not actually relevant
- The final answer adds unsupported detail
- Source documents are outdated or incomplete

But claims make the system much easier to evaluate because they expose the evidence behind the answer. (Gao et al. 2023 ALCE benchmark: even strong systems often lack complete citation support.)

---

## See Also
- [[RAG Evaluation]]
- [[project-g Eval Architecture]]
- [[CRAG Retry Logic]]
- [[RAG Reranking]]
- [[Input Guardrails Pipeline]]
- [[Observability & Evaluation Glossary]] — grounding vs citation_hallucination vs grounding.hallucination_rate distinction
