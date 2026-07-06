---
name: eval-docs
description: >
  Generate or update the VIR-193 Eval Framework canonical documentation from the galactus
  repo. Use this skill whenever someone asks to: refresh the eval documentation, sync the
  doc from latest eval reports, update the source-of-truth HTML, add new eval results to
  the documentation guide, regenerate charts from eval data, or export findings from
  evals/reports or notebooks to the documentation. Also use when asked to "update the
  eval doc from the latest run" or "add the new ablation results to the doc."
---

# eval-docs

Systematically generates and updates the **VIR-193 Eval Framework Source of Truth** —
a 10-tab interactive HTML document at `galactus/eval_framework_tabs.html` — by reading
from the canonical data sources in the galactus repo.

> Freshness note: this skill maintains a historical/stakeholder artifact. For
> current eval commands and output paths, read `evals/README.md` first and prefer
> `uv run python -m evals.pipelines.run ...` over old Makefile examples.

## Source → Target mapping

| Source | Content | Target tab(s) |
|--------|---------|---------------|
| `evals/reports/bkh/eval_suite/all_suite.html` + `.json` | BKH heuristic baseline (69K turns) | Tab 01 BKH Dataset, Tab 03 BKH Results |
| `evals/reports/bkh/eval_stats/all_eval_stats.html` + `.json` | BKH LLM grader pass rates | Tab 03 BKH Results |
| `evals/reports/va_staging/*.html` + `.json` | VA staging eval results | Tab 04 VA Staging Results |
| `evals/reports/sa/comparison.html` | SA ablation comparison (MRR by config) | Tab 05 Ablation Study |
| `nbks/mvp/llm-callibration.ipynb` | Cohen's d, RAGAS scores, prompt versions | Tab 02 Eval Methods |
| `nbks/sa/ablation_analysis.ipynb` | Ablation failure modes | Tab 05 Ablation Study |
| `evals/pipelines/utils/report_sa_comparison.py` | Config labels, cost estimates | Tab 05, Tab 07 |
| `evals/pipelines/utils/_html.py` | SVG bar primitives (reuse in output) | Tab 08 Tooling |
| `.claude/docs/*.md` | Tooling strategy, plans | Tab 07-10 |

## Pipeline → Doc → PPT/Excalidraw flow

```
uv run python -m evals.pipelines.run render <report-data.json>
uv run python -m evals.reports.utils.figures

# Outputs to share downstream:
# • eval_framework_tabs.html  → upload to Drive (this skill) / open locally
# • evals/reports/figures/*.svg → drag into PPT slides / import into Excalidraw
```

## Workflow

### 1. Audit what's changed

Before writing anything, check what's new:

```bash
# Find report files newer than the HTML doc
find evals/reports -name "*.json" -newer eval_framework_tabs.html 2>/dev/null
# Check notebook modification times
ls -lt nbks/mvp/llm-callibration.ipynb nbks/sa/ablation_analysis.ipynb
```

Ask the user which sections to refresh if it's ambiguous. If they say "everything," do a full regeneration.

### 2. Extract metrics from JSON reports

Prefer JSON sources over HTML scraping — they have clean structured data.

```python
import json
from pathlib import Path

# BKH eval stats (Layer 2 grader pass rates)
stats = json.loads(Path("evals/reports/bkh/eval_stats/all_eval_stats.json").read_text())
# Structure: {"stats": {"<label>": {"grader_results": {"<grader_name>": {"pass_rate": 0.72, "avg_score": 0.78}}}}}

# BKH suite (Layer 1 heuristic metrics)
suite = json.loads(Path("evals/reports/bkh/eval_suite/all_suite.json").read_text())
# Structure: {"metrics": [{"name": "...", "value": ..., "threshold": ..., "passed": bool}]}
```

See `references/json_schemas.md` for the full schema for each report type.

### 3. Extract from notebooks

For notebook data, read the `.ipynb` JSON and extract output cells:

```python
import json
nb = json.loads(Path("nbks/mvp/llm-callibration.ipynb").read_text())

# Cell outputs are in nb["cells"][N]["outputs"]
# Key cells (0-indexed):
# Cell 40: Prompt v2 vs v3 comparison (Answer Relevancy scores)
# Cell 49: VA staging dataset info (n tasks, n VA staging v2)
# Cell 51: RAGAS scores on VA staging (ctx_precision mean, faithfulness mean)
# Cell 55: Cohen's d "Final Showdown" — grader discrimination ranking
```

Extract `text` outputs from cells with `output_type == "stream"` or `data["text/plain"]` from `display_data` cells.

### 4. Refresh figures and embed into the HTML doc

```bash
# Step A — regenerate SVGs from live data
make figures                          # all 8 figures
make figures FIGS="mrr_comparison"   # one specific figure

# Step B — embed SVGs inline into eval_framework_tabs.html
make embed-figures

# Or run both in one command:
make report
```

The embed step replaces Chart.js `<canvas>` elements with inline `<svg>` content.
The HTML stays self-contained — no external file paths needed.

For narrative content (tables, stat cards, insight callouts), edit directly:
- **Tables**: find `<table class="dt">` by its `<h3>` heading, update `<td>` values
- **Stat cards**: update `<div class="n">` values
- **Callouts**: update `<div class="insight">` or `<div class="cue ...">` text

### 5. Upload to Google Drive

After updating the local file, upload to Drive to replace the canonical hosted version:

```
Drive file ID: 1US08ui4zOBR05XXem4tqvqNhk0PUNrtu
Drive folder: 1y4V-dz5uVS486VcbURUYAUb2nsTnVH6Q (Galactus shared folder)
Title: "VIR-193 — Eval Framework Source of Truth (Tabbed)"
```

Use `create_file` with `disableConversionToGoogleType: true` and `contentMimeType: "text/html"`.
Note the new file ID and tell the user to delete the old one (or note both exist in Drive).

### 6. Verify

After uploading, open the Drive file link and confirm:
- Tab 1 stat cards show updated numbers
- Charts render (Chart.js loads from cdnjs CDN)
- Tab navigation works across all 10 tabs
- No JavaScript errors in the browser console

---

## Tab structure (10 tabs)

| Tab | ID | Key data |
|-----|----|---------|
| 01 BKH Dataset | `bkh` | 69,198 turns, 1.7% rated, response type donut, language split |
| 02 Eval Methods | `methods` | Cohen's d bar, calibration P/R/F1, prompt v2→v3→v4 |
| 03 BKH Results | `bkh-results` | Grader pass rates vs threshold, failure priority matrix |
| 04 VA Staging | `va` | VA grader pass rates, BKH vs VA side-by-side |
| 05 Ablation Study | `ablation` | MRR by config, feature flag ΔMRR, stat power curve |
| 06 To Production | `production` | Observability tracks, confidence gates, hackathon plan |
| 07 Bedrock KB | `bedrock` | KB IDs, retrieval modes, field mapping, validation matrix |
| 08 Tooling | `tooling` | ADK vs LangGraph, LangSmith setup, hooks arch, SVG primitives |
| 09 Eval Ops | `ops` | Make commands, suite types, two-layer pipeline diagram |
| 10 Plans | `plans` | Golden dataset phases, semantic cache design, hackathon checklist |

---

## Key data values (current as of May 2026)

These are the verified values from the last full eval run. Use these as the baseline; update individual values as new data arrives.

### BKH Dataset (Tab 01)
- Total turns: 69,198 · Unique conversations: 30,557 · Unique users: 10,263
- Rated turns: 1.7% (276 liked / 869 disliked) · Dislike:like ratio: 3.1:1
- Response types: has_sources=74.2%, unknown=17.3%, escalation=5.0%, clarification=1.9%, interrupted=1.7%
- Failure taxonomy: unrated=79.6%, A_retrieval=15.1%, B_language=4.2%, E_grounding=0.6%, C_friction=0.2%, no_failure=0.3%
- Language: Danish=68%, Unknown=22%, English=10%, Dutch=1%, German=0.4%

### Eval Methods (Tab 02)
Cohen's d (grader discrimination, n=50 calibration):
- RAGAS ctx_precision: **+0.393** (best)
- Escalation v4: +0.283
- Completeness v4: +0.245
- Grounding v1: +0.089
- Answer Relevancy v4: −0.005 (marginal)
- DeepEval completeness: **−0.210** (anti-correlated — DO NOT USE for A/B)

Prompt evolution (Answer Relevancy):
- v2: liked=0.600, disliked=0.680
- v3: liked=0.885, disliked=0.670

### BKH Results (Tab 03, n=50)
- Answer Relevancy: 72% pass (avg 0.78, threshold 75%) — FAIL
- Completeness: 68% pass (avg 0.73, threshold 70%) — FAIL
- Escalation: 80% pass — PASS ✓
- Grounding: **0% pass** (avg 0.50, threshold 80%) — FAIL ⚠️
- DeepEval relevancy: 54%, completeness: 64%, escalation: 64%

### VA Staging (Tab 04, n=50 synthetic)
- Completeness: 90% ✓ · Escalation: 98% ✓
- RAGAS ctx_precision: 42% (mean=0.459) · RAGAS faithfulness: **18%** (mean=0.347) ⚠️
- Grounding: 52% · Answer Relevancy: 68%

### Ablation Study (Tab 05, n=44 tasks)
Top configs by MRR:
1. adk_flash_thinking1024: **0.656**
2. lg_multi_query: 0.594
3. adk_thinking1024: 0.583
4. adk_flash: 0.563
5. lg_crag: 0.547

Feature impact (ΔMRR vs baseline):
- Thinking (hc_adk): **+0.165** · Flash model: +0.145 · Multi-query: +0.076
- CRAG alone: +0.005 · LLM planner: −0.031 · CRAG+Thinking: **−0.063**

---

## Visualization primitives from evals/pipelines/utils/_html.py

The pipeline uses two SVG bar helpers. Replicate these in docs when embedding inline:

```python
# pct_bar_pass: green ≥0.8, amber ≥0.5, red <0.5
f'<svg width="100" height="10"><rect width="{int(rate*100)}" height="10" fill="{color}" rx="2"/>...'

# pct_bar_error: red >0.5, amber >0.2, blue ≤0.2
f'<svg width="120" height="12"><rect width="{int(rate*120)}" height="12" fill="{color}" rx="2"/>...'
```

For PPT/Excalidraw: export these as SVG screenshots from the HTML report, or regenerate using `make report` and copy from `evals/reports/**/*.html`.

---

## Adding a new eval run to the doc

When a new eval run completes:

1. `make report` → one command: HTML reports + 8 SVG figures + embed into doc
2. Optionally update any narrative tables/stat cards manually (see step 4 above)
3. Upload to Drive (see step 5)
4. Commit:
   ```bash
   git add eval_framework_tabs.html evals/reports/figures/*.svg
   git commit -m "docs: refresh eval metrics from <run_date> results"
   ```

## PPT export path

The SVG files in `evals/reports/figures/` are ready to drop into slides:
- **PowerPoint (via pptx skill)**: "add the eval figures to the deck" — the skill reads `evals/reports/figures/*.svg` and inserts them as slide images
- **Excalidraw**: File → Import SVG → select from `evals/reports/figures/`
- **Google Slides**: Insert → Image → Upload from computer

Figures are sized at ~9×4.5 inches / 150 DPI — suitable for full-width slides.

---

## References

- `references/json_schemas.md` — full schema for eval_stats.json, eval_suite.json, comparison.json
- `evals/pipelines/utils/report_sa_comparison.py` — config labels and cost estimates (source of truth for Tab 05)
- `evals/pipelines/utils/_html.py` — SVG bar helper functions
