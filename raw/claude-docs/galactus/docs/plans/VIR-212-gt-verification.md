# Eval Calibration & Ground Truth Finalization

> **Date:** 2026-05-30
> **Target:** May 29–June 6, 2026
>
> **Goal:** Establish verified ground truth, fix three silent pipeline defects that make grader
> scores unreliable, grade the ungraded BKH pool, and produce the edge case study that confirms
> graders are ready for v1.0 release.
>
> **Why in this order:** GT verification is the prerequisite. Fixing grader bugs on top of
> unverified data compounds noise. Verify first, then calibrate.

---

## Root cause findings

### 1. RAGAS is silently degrading, not skipping

In `eval_quality.py`:
```python
context = task.retrieved_passages or task.expected_urls or None
```
When `retrieved_passages=[]` (every VA golden and showdown run), the pipeline falls back to
`expected_urls` — URL title strings like `"What is a fee? (https://...)"`. RAGAS receives these
as passage context.

Consequence: **RAGAS Faithfulness** scores near zero because a URL title has almost no content.
The reported 55% liked+failed rate on Faithfulness is largely this artifact.

### 2. Billy → Shine URL mismatch inflates grounding edge cases

`expected_urls` in the golden set are a mix of `help.shine.co` (165) and `help.billy.dk` (92).
The `GroundingGrader` does URL overlap matching without domain normalization — a Shine URL fails
against a Billy `expected_url` even when they point to the same article. This inflates the
58% liked+failed rate on Grounding and accounts for most of the 73 "ungrounded_response" edge cases.

### 3. Article text is available but unused

`data/datasets/article_cache.json` has full text for 277 articles (112 of the 257 golden
expected_urls are cached). RAGAS could run faithfulness against real article content today.

### 4. The BKH pool has no grader scores

860-item BKH pool (500-item sample + 360-item supplement) = 669 rated items with zero LLM grader
scores. Grading these would triple the calibration pool without any new data collection.

### 5. BKH ground truth is unverified against Intercom source

BKH `expected_urls` are a mix of Billy and Shine domains with ~92 unresolved Billy URLs. Some
items have URLs that 404 or redirect, and some conversation IDs may not match the stored response.
Grading on top of unverified ground truth compounds noise.

---

## Phase 1 — Ground truth verification (target: June 2)

### Task 1 — URL health audit

For every unique `expected_url` across both BKH eval sets:
1. Normalize via `core/preprocessing/kb_url_resolve.py` → canonical Shine URL
2. HTTP HEAD check — reachable? (200 vs 404/redirect)
3. Bucket: `verified` / `stale_redirect` / `dead`

Output: `data/datasets/bkh/gt_audit/url_health.json`

```makefile
gt-url-audit:
	uv run python -m core.preprocessing.bkh.gt_url_audit \
	    --input  data/datasets/bkh/eval_sets/sample_for_llm_graders.jsonl \
	    --input2 data/datasets/bkh/eval_sets/rated_supplement.jsonl \
	    --output data/datasets/bkh/gt_audit/url_health.json
```

### Task 2 — Cross-reference with Intercom conversations

For BKH items where `conversation_id` is present:
1. Look up the conversation in Intercom parts data
2. Compare BKH `response` field against actual agent turn body
3. Flag `conversation_verified` if they match, `needs_human_review` if not

Output: `data/datasets/bkh/gt_audit/conversation_match.json`

### Task 3 — Produce clean GT annotations

Merge url_health + conversation_match → one annotation record per BKH item:

```json
{
  "task_id": "...",
  "gt_status": "verified" | "url_stale" | "url_dead" | "needs_human_review",
  "url_normalized": true | false,
  "conversation_matched": true | false | null
}
```

Write to `data/datasets/bkh/gt_audit/gt_annotations.jsonl`.
Merge into clean eval sets: `sample_for_llm_graders_gt.jsonl`, `rated_supplement_gt.jsonl`.

### Task 4 — Human review batch

Export ≤50 priority `needs_human_review` items (prioritize: `url_dead` + `liked=True`) as CSV
for hand-labelling: `data/datasets/bkh/gt_audit/human_review_batch.csv`

**GT success criteria:**
- ≥60% of 860-item pool reaches `gt_status == verified`
- Dead URLs removed from grader context (100%)
- `url_normalized` applied to all items

---

## Phase 2 — Grader pipeline fixes (target: June 4)

**Run these against `*_gt.jsonl` outputs from Phase 1.**

### Fix 1 — URL normalization in eval pipeline ✓ MERGED — 2026-06-02

`normalize_task_urls()` + `_normalize_url_string()` added to `eval_quality.py`. Uses
`resolve_billy_to_shine()` (human-validated + auto map) with domain-swap fallback for
unmapped entries. Called in `run_quality_file()` before `enrich_passages`. No separate
`utils/normalize_urls.py` needed — logic lives in `kb_url_resolve.py`, only thin
wrapper added to eval pipeline.

**Impact on `bkh_qa.jsonl` (597 tasks):** 432 tasks normalized; residual "billy" strings are
Shine slugs with "-i-billy" in article name — correct, untouched.

~~Add `evals/pipelines/utils/normalize_urls.py`~~:

```python
BILLY_TO_SHINE = {
    "help.billy.dk": "help.shine.co",
    "www.billy.dk/support": "help.shine.co",
}

def normalize_url(url: str) -> str:
    for billy_host, shine_host in BILLY_TO_SHINE.items():
        if billy_host in url:
            return url.replace(billy_host, shine_host)
    return url

def normalize_expected_urls(urls: list[str]) -> list[str]:
    return [re.sub(r'https?://[^\s)]+', lambda m: normalize_url(m.group()), s) for s in urls]
```

Apply in `eval_quality.py` before grader dispatch:
```python
task.expected_urls = normalize_expected_urls(task.expected_urls or [])
context = task.retrieved_passages or task.expected_urls or None
```

No LLM calls — run against existing data to see the grounding score shift immediately.

### Fix 2 — Passage enrichment from article cache

Add `evals/pipelines/utils/enrich_passages.py`:

```python
def enrich_passages(
    expected_urls: list[str],
    cache: dict[str, str],
    fallback_to_url_string: bool = True,
) -> list[str]:
    passages = []
    for raw in expected_urls:
        url_match = re.search(r'https?://[^\s)]+', raw)
        if not url_match:
            continue
        url = url_match.group()
        shine_url = normalize_url(url)
        text = cache.get(shine_url) or cache.get(url)
        if text:
            passages.append(text)
        elif fallback_to_url_string:
            passages.append(raw)  # graceful degradation for uncached URLs
    return passages
```

Integrate into `eval_quality.py` so RAGAS receives article text instead of URL strings.

### Fix 3 — Grade the BKH baseline pool ✓ MAKEFILE ADDED — 2026-06-02

**Actual data path:** `evals/data/gt/bkh_baseline_raw.jsonl` (413 rows, all `help.shine.co` URLs).
The originally planned `data/datasets/bkh/eval_sets/` path never existed.

```makefile
# Non-RAGAS graders — run now, no passage text required
make grade-bkh-baseline

# RAGAS graders — run after expand-article-cache
make grade-bkh-baseline GRADERS=ragas_context_precision,ragas_faithfulness
```

**Immediate GT VA scoring sequence (2026-06-02):**
```bash
make gt-grade-new       # grade 300 new VA rows (combined_va + RAGAS w/ passage enrichment)
make gt-quality-merge   # merge remapped 112 + new 300 → quality.json
make gt-cohort && make gt-stats && make gt-report
```

### Fix 4 — Expand article cache (before BKH RAGAS run)

**Actual cache:** `data/articles/article_cache.json` (277 articles, not `data/datasets/article_cache.json`).
`ArticleLoader` uses kb_url_map slug aliases for Billy↔Shine resolution — effective coverage may
be higher than the 53 raw misses (69/122 cached) suggest.

```makefile
make expand-article-cache   # warm missing Shine URLs; prints hit/fetched/error summary
```

**Deferred:**
- Bedrock → Langfuse tracing: once VA traces surface chunks Bedrock actually used, `retrieved_passages`
  will come from the TS API directly and passage enrichment won't be needed.
- Blog/billypedia edge cases: needs a separate extraction from the broader Intercom dump
  (this GT export only sampled `bkh_source_type=Support`).

---

## Phase 3 — Edge case study ✓ NOTEBOOK WRITTEN — 2026-06-03

### `03_golden_traces.ipynb` — superseded (in `nbks/sa/old/`)

Simplification not needed — the new notebook covers all required analysis.

### `04_edge_case_study.ipynb` ✓ WRITTEN — 2026-06-03 (`nbks/sa/04_edge_case_study.ipynb`)

Answers: *where do graders and humans disagree, and why?*

```
§1  Setup — load BKH graded (413 rows) + raw (ratings + expected_urls)
§2  Grader coverage matrix (total_n, rated_n, liked_n, disliked_n, mean, pass_rate)
§3  URL provenance analysis — Billy vs Shine, grounding cross-tab → AC5
§4  Per-item multi-grader agreement (edge case catalogue)
§5  Cross-grader agreement heatmap
§6  Threshold calibration — Cohen's d, box plots, F1 @ 0.7 + macro-F1 → AC6
§7  Ensemble analysis — majority-vote 2-of-N / 3-of-N / 4-of-N → AC7
§8  Edge case taxonomy — URL_MISMATCH | THRESHOLD_NOISE | GENUINE_AMBIGUITY | LAYER4_FAILURE
§9  Friction proposals → evals/data/gt/grader_friction_signals.json
```

**Key findings (pre-verified against data):**
- AC5: grounding liked+failed = **15.3%** (target <30%) ✅
- AC6: **4 graders** with Cohen's d ≥ 0.4 (answer_relevancy d=1.35, escalation d=0.91, deepeval d=0.81, completeness d=0.80) ✅
- AC7: best majority-vote ensemble F1 = **0.916** (4-grader, require=2) ✅
- Class imbalance note: 249 liked : 26 disliked — F1-optimal threshold degenerates; Cohen's d is primary signal; macro-F1 shown alongside binary F1

**VA quality_new.json blocker:** 300 new VA rows have all-0 scores (Vertex AI ADC not set at grade time). Re-run `make gt-grade-new` after `gcloud auth application-default login`.

---

## Data sufficiency

| Question | Now | After Fix 3 |
|---|---|---|
| Custom + DeepEval calibration n | 547 rated | ~1,400 rated |
| RAGAS calibration n (real text) | ~112 | ~257 (after Fix 4) |
| Liked group total | 154 (golden) | ~372 ✅ |
| Disliked group total | 393 (golden) | ~844 ✅ |

Target for v1.0: 110/group minimum. After Fix 3 both groups exceed this comfortably.

---

## What to defer

- **New VA agent runs:** URL normalization (Fix 1) handles the Billy URL artifact; validate on existing data before generating more.
- **Separate sourcing comparison notebook:** Once Fix 1+2 are in and §3 shows which items remain genuinely ambiguous, not before.
- **Billypedia URL mapping:** No Shine equivalent exists. Exclude from grounding URL overlap check. Flag separately in §3.
- **Full corpus BKH verification (69K):** Only the 860-item eval pool. Full corpus is a data engineering project.
- **LLM re-rating of human labels:** Risky without a calibrated grader. Flag for human review only.

---

---

## Session log — 2026-06-02

### Completed

**GT pipeline fixes:**
- `gt_quality_merge.py` — fixed `remap()` to join `expected_urls` from `regression.jsonl` into `va_responses_new_only.jsonl` (was missing, causing 0 RAGAS scores on new rows)
- `grade-bkh-baseline` + `expand-article-cache` Makefile targets added; BKH_GRADE_GRADERS updated to use voted graders + RAGAS
- Article cache expanded: 277 → 331 articles; 73/130 unique GT URLs cached (56%), 50 more resolvable via kb_url_map
- VA staging blocked by Google auth error (ADC missing in deployed agent) — `gt-va-call` deferred

**Grader improvements:**
- `EscalationGrader` → `escalation_v3`: added 12 Danish keywords, `@` email regex (soft escalation signal), KB coverage gap signal from empty `context`; new dimensions: `kb_coverage_gap`, `email_contact_present`
- Registry: added voted variants `answer_relevancy_voted`, `completeness_voted`, `escalation_voted`, `grounding_voted` (LLM graders only — `f1_correctness` and `boundary_adherence` are deterministic heuristics, voting adds nothing)
- `GOOGLE_GENAI_USE_VERTEXAI` + duplicate `GOOGLE_API_KEY` in `.env` were causing silent 0 scores — resolved

**Architecture decisions:**
- `f1_correctness` and `boundary_adherence` stay as heuristics: `escalation_voted` + `completeness_voted` + `answer_relevancy_voted` cover the semantic side; LLM f1/boundary would duplicate those
- Retrieval stats (`source_match`, `url_coverage`, MRR, NDCG) stay as URL-matching heuristics — correct for what they measure
- OOS boundary detection tested via `boundary_adherence` + `escalation_voted` + `agent_behavior` — tests whether VA detects OOS before Bedrock loops, not just whether final response declines

### Queued — next sprint (Linear: Evaluation & Enablement project)

**OOS boundary eval — finalization (unblocked by VA staging auth fix)**
- `evals/data/gt/oos_boundary.jsonl` generated: 80 items (40 DA / 40 EN), 6 domains
  (action_request, account_specific, live_data, legal_tax_advice, edge_case, general_knowledge)
- Next: call VA agent against all 80 queries (`make gt-va-call` pointed at oos_boundary.jsonl),
  then `make grade-oos-boundary` → `escalation_voted + boundary_adherence + agent_behavior`
- Escalation grader measures two distinct things depending on dataset:
  - **BKH baseline (413 in-scope)** → specificity / TN rate (agent should NOT escalate)
  - **OOS boundary (80 OOS)** → sensitivity / TP rate (agent SHOULD escalate)
  - Combined F1 for escalation requires both datasets scored together
- **Email-not-URL cases (FN gap)**: responses where agent gives `@email` contact instead of a URL
  are a third escalation signal category — currently detected by `EscalationGrader` v3 via
  `_EMAIL_RE` regex, but the eval set has no labeled examples of this pattern.
  Source: Intercom conversations where BKH replied with support email — mine from friction JSONL
  and add as a separate `oos_domain="email_referral"` partition in `oos_boundary.jsonl`

**Intent grader HC topic expansion (enables per-domain failure analysis)**
- Add secondary `hc_topic` field to `IntentClassifier` output using 12 Intercom HC collections
  as taxonomy (`Getting Started`, `Bookkeeping Basics`, `Taxes & VAT`, `Bank Connections`, etc.)
- `hc_topic = null` when `intent == human_support | general_inquiry` (OOS intents)
- Connects to OOS eval: `intent == human_support` should correlate with `escalation_voted=pass`
  on those rows — use as cross-grader alignment check
- Use unrated BKH sample with topic labels as few-shot seed

**Friction analysis pipeline (conversation-level FN detection)**
- Run `FrictionGrader` against Intercom conversation JSONL (multi-turn) and BKH multi-turn data
- Friction signals that indicate unresolved OOS / missed escalation:
  - Repeated queries across turns (user rephrased same OOS request)
  - Language switches (DA→EN or EN→DA mid-conversation — common when user frustrated)
  - Conversations ending without a URL cite (no retrieval = possible OOS or coverage gap)
- Output: friction heatmap by `hc_topic` / `oos_domain` — identifies which domains generate
  most unresolved conversations → high-priority OOS cases to add to oos_boundary.jsonl
- Separate pipeline from QA eval set (friction is conversation-level, not single-turn)

**Priority before these:** ablation study (agent + RAG optimization) — see Linear Evaluation & Enablement project

---

## Acceptance criteria for v1.0

1. ✅ Phase 1 — GT verification metrics in `gt_verification_metrics.json`; `bkh_baseline_raw.jsonl` already all Shine URLs
2. ✅ Fix 1 merged — `normalize_task_urls()` in `eval_quality.py` (2026-06-02)
3. ✅ Fix 2 merged — `enrich_passages()` in `eval_quality.py`
4. ✅ BKH pool graded — `bkh_baseline_graded.json` (413 rows, 7 graders)
5. ✅ `04_edge_case_study.ipynb` §3 — grounding liked+failed = **15.3%** (target <30%)
6. ✅ `04_edge_case_study.ipynb` §6 — **4 graders** with Cohen's d ≥ 0.4
7. ✅ `04_edge_case_study.ipynb` §7 — best majority-vote ensemble F1 = **0.916** (≥0.70)
8. ✅ `GRADER_VERSION = "1.0"` added to `evals/graders/judges/experimental/quality.py` (2026-06-03)

**Remaining before archive:**
- [ ] Run `04_edge_case_study.ipynb` end-to-end in Jupyter (outputs + `grader_friction_signals.json` saved)
- [ ] Re-run `make gt-grade-new` after `gcloud auth application-default login` — deferred, not blocking archive
