# BKH Baseline Findings & VA Demo — May 2026

**Demo date:** May 19, 2026  
**Presenter:** Ramsey Wise — agentic eval framework (VIR-193)  
**Last updated:** May 2026

---

## The short version

We evaluated the new VA agent against a historical baseline (BKH) using ~500 rated conversations and a 597-turn golden set. On calibrated metrics, **VA performs at least as well as the BKH baseline** — enough for leadership to authorize go-live.

Absolute scores are low on both. That's expected: both agents handle the hardest, most friction-heavy queries. The comparison matters more than the absolute numbers.

---

## What BKH is and why it matters

BKH (Bookkeeper Hero) was our previous CS agent on the old Billy KB, trained on ~69K Intercom conversations. It's our regression baseline — the historical bar.

| Slice | Turns | Rated | Coverage |
|-------|------:|------:|---------|
| Full corpus | 69,198 | 1,145 | 1.7% — skew toward friction cases |
| LLM grader sample | 500 | 400 (80%) | Used for calibration runs |
| VA golden set | 597 | 597 (100%) | Used for VA comparison |

This sets the product context: our product priority is **recall over precision**. Missing a retrieval is worse than a slightly imprecise one.

Key EDA findings (full 69K corpus):
- **17% "unknown" responses** — no KB result found (top eval target)
- **Shorter responses → more dislikes** (~350 vs ~450 chars avg)
- **Customer & Supplier Management** — 37% escalation, ~40% source rate (KB gap hotspot)

---

## BKH baseline metrics (500-task sample)

| Metric | Value | Notes |
|--------|------:|-------|
| Satisfaction rate | **25%** | 1 in 4 turns rated positively |
| Dislike:like | **3:1** | High friction baseline |
| Sources cited | **75%** | Agent usually provided a link |
| No result ("unknown") | **12%** | KB gap or out-of-scope query |
| Retrieval precision | **27%** | Low — cites sources but not always the right ones |
| Retrieval recall | **89%** | High — rarely misses a relevant source entirely |
| Weighted resolution | **22%** | Combined satisfaction + resolution signal |

Full-corpus proxy (all 69K rated turns): P **30.4%**, R **78.5%**, F1 **43.8%**.

---

## VA vs BKH — the comparison

On the same 597 rated turns (VA golden set):

### Heuristic metrics

| Metric | BKH | VA (after calibration) |
|--------|----:|----------------------:|
| Satisfaction | 24% | **28%** |
| Retrieval precision | 30% | **40%** |
| Retrieval recall | 79% | **90%** |
| Retrieval F1 | 44% | **55%** |

### LLM judge pass rates

| What we measured | BKH | VA before fix | VA after fix |
|------------------|----:|--------------:|-------------:|
| Completeness | 68% | 86% | **87%** |
| Answer relevancy | 72% | 74% | **76%** |
| Grounding | 0%* | 34% | **78%** |

*BKH grounding scores 0% because the eval pipeline couldn't retrieve article text for Billy URLs at scoring time — a known limitation, not a model quality issue.

---

## The calibration story (v1 → v2)

The biggest number in the demo — grounding jumping from 34% to 78% — needs context.

BKH expected URLs use `billy.dk/support/...`. VA responses cite `help.shine.co/da/articles/...`. The same article, different domain. Before we built a URL mapping layer, VA would cite the correct article and still score zero because the URL didn't match the expected Billy URL literally.

**The 34% → 78% jump is mostly a measurement fix, not a model improvement.** We built a Billy ↔ Shine URL resolution layer (182 of 268 Shine URLs now mapped) that correctly credits VA for citing the right content. Results labelled "v2" use this mapping.

This also means our historical BKH scores are lower-bound estimates — some BKH failures were the same measurement artifact.

---

## Decisions made at the demo

| Decision | What it means |
|----------|---------------|
| **Go-live authorized** | VA quality is at least as good as BKH on calibrated metrics — sufficient basis for launch |
| **Intercom data for future evals** | We'll move from BKH-only historical data to Intercom conversations + MVP traces |
| **Comparison framing stays** | Absolute scores treated cautiously; relative comparison is the signal |

**Acknowledged limitations:** BKH ratings cover only 1.7% of the corpus and are skewed toward friction cases. Source data quality is uncertain. These are known and accepted.

---

## What's next

| Owner | Action |
|-------|--------|
| Anders Dehn | Human verification of URL mappings |
| Yan | Intercom data through feature extraction + eval pipelines |
| Marco E.Z. | EDA on Billy Bedrock ingestion quality; synthetic MCQ from Intercom |
| Ramsey | Verify BKH ground truth via Intercom conversations (May 29) |

---

## For engineers — artifacts

| Artifact | Path |
|----------|------|
| Interactive report (10 tabs) | `evals/reports/demo/eval_framework_tabs.html` |
| VA golden stats | `evals/reports/golden/golden_all_responses_stats.html` |
| VA golden quality | `evals/reports/golden/golden_all_responses_eval.html` |
| BKH suite | `evals/reports/bkh/eval_suite/llm_graders_suite.html` |
| Demo figures | `evals/reports/figures/` |

Regenerate: `make figures && make demo`
