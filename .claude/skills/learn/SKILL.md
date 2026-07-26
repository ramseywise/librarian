---
name: learn
description: "Process queued arXiv papers and surface relevant ones for current work. Runs /ingest on raw/web/ scoped to arxiv files, then queries the wiki for what's new and surfaces top 3 papers. Optional topic filter: /learn RL alignment. Run from the librarian repo."
---

You are a research curator processing the arXiv paper queue and surfacing relevant papers
for the current learning agenda.

This skill is the human gate for the automated arXiv fetch pipeline:
- The cron job (`ARXIV_FETCH_ENABLED=true uv run cartographer --cron`) drops papers into `raw/web/`
- `/learn` processes that queue and surfaces what's worth reading

**This skill runs from the librarian repo.** If invoked from another repo, ask the user to
switch to `~/workspace/librarian` first.

---

## Step 1 — Parse arguments

Parse `$ARGUMENTS`:
- **No argument** → process all queued arXiv papers
- **Topic keywords** (e.g., `RL alignment` or `RLHF DPO`) → filter surfaced papers to those topics

Store any keywords as `TOPIC_FILTER`.

---

## Step 2 — Check the queue

Use Bash to count pending arXiv files in `raw/web/`:

```bash
ls raw/web/*-arxiv-*.md 2>/dev/null | wc -l
```

If count is 0:
- Report: "No arXiv papers queued. Run `ARXIV_FETCH_ENABLED=true uv run cartographer --cron` to fetch."
- Stop here.

If count > 0, report: "Found N queued arXiv papers. Processing..."

---

## Step 3 — Ingest queued papers

Run the ingest skill scoped to `raw/web/` for arxiv files only.

Use Bash to identify the arxiv files pending ingest (not yet in manifest):

```bash
uv run python -c "
from core.manifest import REPO_ROOT, MANIFEST_PATH
import json, re
from pathlib import Path

manifest_paths = set()
if MANIFEST_PATH.exists():
    for line in MANIFEST_PATH.read_text().splitlines():
        if line.strip():
            entry = json.loads(line)
            manifest_paths.add(entry['path'])

web_dir = REPO_ROOT / 'raw' / 'web'
pending = [f for f in sorted(web_dir.glob('*-arxiv-*.md'))
           if str(f.relative_to(REPO_ROOT)) not in manifest_paths]
for f in pending:
    print(f.relative_to(REPO_ROOT))
"
```

For each pending file, invoke the `/ingest` skill with that path (or call it once with
`raw/web/` — the ingest skill handles targeted compile mode).

Invoke: `/ingest raw/web/`

This will compile new arXiv markdown files into wiki pages. Wait for ingest to complete.

---

## Step 4 — Surface top papers

After ingest, query the wiki to find what was just added. Read the newly compiled wiki
pages for the ingested papers.

For each ingested paper, extract:
- Title
- arXiv ID and URL
- Published date
- Abstract (first 2-3 sentences)
- Categories

**Apply topic filter** (if `TOPIC_FILTER` was set): only include papers where the title
or abstract mentions any of the filter keywords (case-insensitive).

**Rank by relevance** to the current learning agenda:
- Priority topics: reinforcement learning, RLHF, DPO, GRPO, alignment, constitutional AI,
  reward modeling, language models, RAG, agentic systems
- Secondary: fine-tuning, instruction tuning, evaluation, safety

Select **top 3** papers (or all if fewer than 3 remain after filtering).

---

## Step 5 — Output

Print a clean summary:

```
## arXiv Learning Queue — YYYY-MM-DD

Processed N papers → M passed topic filter

### Top picks

**1. [Title](url)**
arXiv XXXX.XXXXX | Published: YYYY-MM-DD | Categories: cs.CL, cs.AI
> [2-3 sentence abstract excerpt]

**2. [Title](url)**
...

**3. [Title](url)**
...

---
To add to a pillar reading list, copy the arXiv URL and link it from the relevant
05-RL/ or pillar README. No automated LAE writes — the human decides what enters
the curriculum.
```

If `TOPIC_FILTER` was set and 0 papers matched: report that and show up to 3 unfiltered
picks instead with a note that the filter returned nothing.

---

## Notes

- Papers stay in `raw/web/` after ingest — the manifest tracks what's been compiled.
- Re-running `/learn` on an already-ingested batch is safe — ingest skips unchanged files.
- To fetch fresh papers before running `/learn`: `ARXIV_FETCH_ENABLED=true uv run cartographer --cron`
- To fetch without the full cron: `uv run python -m core.scrape_arxiv`
