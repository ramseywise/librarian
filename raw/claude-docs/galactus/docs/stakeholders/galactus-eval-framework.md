# Galactus Eval Framework

**Last updated:** May 2026

---

## What it is

Galactus is our internal eval framework for measuring VA agent quality. It takes raw conversation data — from our historical CS agent (BKH), VA staging, or local test agents — and produces graded reports that answer: *Is the agent giving correct, complete, grounded answers?*

We run two kinds of checks:
- **Free (heuristic):** Did the agent cite sources? Did the user seem satisfied? How often did it escalate? These run on every dataset automatically.
- **Paid (LLM judges):** Is the answer actually correct? Is it grounded in retrieved content? These use Gemini and cost money, so we cap them on first runs.

---

## Our data

| Dataset | What it is | Human ratings |
|---------|-----------|:---:|
| **BKH** | ~69K turns from Bookkeeper Hero, our historical Intercom CS agent on Billy KB | ✅ sparse (1.7% of turns rated) |
| **VA golden** | 597 rated turns from VA staging on Shine KB | ✅ 597 turns |
| **VA staging** | Live VA smoke runs | — |
| **hc_* ablation** | Local agent test runs (hc_adk, hc_lg, hc_rag) | — |

**BKH is our regression baseline** — the bar VA must beat. It's the only dataset with meaningful human like/dislike coverage, but ratings skew toward friction cases, not a random sample.

---

## How we measure

### Layer 1 — Free metrics (run these first)

Computed from conversation structure alone — no LLM calls.

- **Satisfaction rate** — turns marked liked / total rated
- **Has sources** — agent cited at least one URL
- **Unknown response rate** — agent returned no KB result
- **Retrieval proxy** — precision, recall, F1 from (liked/disliked × has_source)
- **Ranked retrieval** — MRR, NDCG, P@k against expected URLs

### Layer 2 — LLM judges (cap at 20–50 on first run)

| What we measure | Why it matters |
|-----------------|---------------|
| **Grounding** | Are claims supported by what the KB actually returned? Catches hallucination. |
| **Completeness** | Did the answer address everything the user asked? |
| **Answer relevancy** | Was the response on-topic? |
| **Escalation** | When the agent handed off to a human — was that the right call? |
| **Empathy / professionalism** | Tone quality (EPA score) |
| **Friction** | Across a multi-turn conversation, was the issue resolved without unnecessary back-and-forth? |

We cross-check our custom judges against **DeepEval** and **RAGAS** to catch calibration drift.

---

## The URL problem (and how we solved it)

BKH expected URLs use `billy.dk/support/...`. VA cites `help.shine.co/da/articles/...`. These point to the same articles — only the domain differs.

Without normalization, a VA response citing the correct Shine article would score **zero** against a Billy expected URL. This inflated failure rates artificially.

We built a URL mapping layer (`core/preprocessing/kb_url_resolve.py`) that resolves Billy ↔ Shine via title matching, slug matching, and TF-IDF fallback. 182 of 268 Shine URLs are now mapped. Results split into:

- **v1** — raw, strict URL match (pre-normalization)
- **v2** — calibrated, with URL aliasing applied

The 34% → 78% grounding jump in the May demo was almost entirely a v1→v2 calibration fix, not a model change.

---

## PII handling

Customer conversation data is scrubbed **at collection time** before any eval runs. Graders never see raw PII. Tokens like `[EMAIL]`, `[CPR]`, `[NAME]`, `[PHONE]` are substituted at ingestion.

---

## For engineers — running the pipeline

For current flags and output paths, use [`evals/README.md`](../../evals/README.md)
as the canonical runbook.

```bash
# Step 1: heuristic stats (free, CI-safe)
uv run python -m evals.pipelines.run stats --dir data/datasets/bkh/eval_sets/

# Step 2: LLM graders (cap first run)
uv run python -m evals.pipelines.run quality --dataset <responses.jsonl> --tier calibrated --limit 20

# Resume a partial run
uv run python -m evals.pipelines.run quality --dataset <responses.jsonl> --tier calibrated --resume

# Re-render HTML without re-grading
uv run python -m evals.pipelines.run render <report-data.json>

# LangFuse experiment
uv run python -m evals.pipelines.run langfuse --run-name hc-adk --dataset hc-support-agents-golden-597 --endpoint http://localhost:8011/chat
```

### Report outputs

| Path | Contents |
|------|----------|
| `evals/reports/bkh/` | BKH heuristic stats + suite |
| `evals/reports/golden/` | VA golden stats + LLM quality |
| `evals/reports/figures/` | SVG charts |
| `evals/reports/demo/eval_framework_tabs.html` | Interactive 10-tab reference (VIR-193) |

### Key modules

```
evals/
├── graders/          heuristic stats, LLM judges, retrieval metrics
├── metrics/          thresholds (TIER_THRESHOLDS), PassRateMetric
└── pipelines/
    ├── eval_stats.py       ← free runner
    ├── eval_quality.py     ← LLM runner
    └── utils/              normalize_urls, enrich_passages, report_*

core/preprocessing/
├── bkh/bkh_prep.py         ← BKH ingestion + feature extraction
├── bkh/qa_preprocessor.py  ← post-agent-call prep
└── kb_url_resolve.py       ← Billy ↔ Shine URL normalization
```

Grader interface contract: `docs/evals/grader_interface.md`
