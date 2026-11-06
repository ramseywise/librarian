---
name: learn
description: "Process the queued reading list — arXiv papers and RSS/blog posts — and surface relevant items for current work. Runs /ingest on data/raw/web/ scoped to fetched files, then queries the wiki for what's new and surfaces the top 3. Optional topic filter: /learn RL alignment. Run from the librarian repo. Use when working through fetched arXiv and feed items, or asking what is new and worth reading. Do NOT use for compiling a specific source (/ingest), questions about what the wiki already knows (/query), or adding items to a course reading list, which the human decides."
---

You are a research curator processing the reading queue and surfacing relevant items
for the current learning agenda.

## Core rule

Ingest what is queued, surface at most 3 items worth reading, and leave every decision about the curriculum to the human.

## Workflow

This skill is the human gate for the automated fetch pipelines, which write two kinds of
queue file into `data/raw/web/`:
- `*-arxiv-*.md` — papers, from `ARXIV_FETCH_ENABLED=true uv run cartographer --cron`
- `*-feed-*.md` — RSS/blog posts, from `FEED_FETCH_ENABLED=true uv run cartographer --cron`

`/learn` processes both and surfaces what's worth reading.

**This skill runs from the librarian repo.** If invoked from another repo, ask the user to
switch to `~/workspace/librarian` first.

---

### Step 1 — Parse arguments

Parse `$ARGUMENTS`:
- **No argument** → process everything queued
- **Topic keywords** (e.g., `RL alignment` or `RLHF DPO`) → filter surfaced items to those topics

Store any keywords as `TOPIC_FILTER`.

---

### Step 2 — Check the queue

Use Bash to count pending queue files in `data/raw/web/`:

```bash
find data/raw/web -maxdepth 1 \( -name '*-arxiv-*.md' -o -name '*-feed-*.md' \) 2>/dev/null | wc -l
```

If count is 0:
- Report: "Nothing queued. Run `ARXIV_FETCH_ENABLED=true FEED_FETCH_ENABLED=true uv run cartographer --cron` to fetch."
- Stop here.

If count > 0, report: "Found N queued items. Processing..."

---

### Step 3 — Ingest queued papers

Run the ingest skill scoped to `data/raw/web/` for fetched queue files only.

Use Bash to identify the queue files pending ingest (not yet in manifest):

```bash
uv run python -c "
from librarian.ingest.manifest import REPO_ROOT, MANIFEST_PATH
import json, re
from pathlib import Path

manifest_paths = set()
if MANIFEST_PATH.exists():
    for line in MANIFEST_PATH.read_text().splitlines():
        if line.strip():
            entry = json.loads(line)
            manifest_paths.add(entry['path'])

web_dir = REPO_ROOT / 'data' / 'raw' / 'web'
queued = sorted(set(web_dir.glob('*-arxiv-*.md')) | set(web_dir.glob('*-feed-*.md')))
pending = [f for f in queued
           if str(f.relative_to(REPO_ROOT)) not in manifest_paths]
for f in pending:
    print(f.relative_to(REPO_ROOT))
"
```

For each pending file, invoke the `/ingest` skill with that path (or call it once with
`data/raw/web/` — the ingest skill handles targeted compile mode).

Invoke: `/ingest data/raw/web/`

This will compile new arXiv markdown files into wiki pages. Wait for ingest to complete. Its report, log line and reviewer verdict
belong to that run: `/learn` does not repeat them.

---

### Step 4 — Surface top items

After ingest, query the wiki to find what was just added. Read the newly compiled wiki
pages for the ingested items.

For each ingested item, extract:
- Title
- URL, plus the arXiv ID for papers or the source name for feed posts
- Published date
- Abstract or summary (first 2-3 sentences)
- Categories

**Apply topic filter** (if `TOPIC_FILTER` was set): only include items where the title
or abstract/summary mentions any of the filter keywords (case-insensitive).

**Rank by relevance** to the current learning agenda:
- Priority topics: reinforcement learning, RLHF, DPO, GRPO, alignment, constitutional AI,
  reward modeling, language models, RAG, agentic systems
- Secondary: fine-tuning, instruction tuning, evaluation, safety

Break ties by source confidence (frontmatter `confidence:`): `high` > `medium` > `low`.
Tier 2 feed posts are `low` — they are gap-detectors, so surface them for what they point
at rather than citing them as the record.

Select **top 3** items (or all if fewer than 3 remain after filtering). Prefer a mix over
three items from the same feed — a high-volume blog should not crowd out the rest.

---

### Step 5 — Output

Print a clean summary, in the template under Output format.

---

### Notes

- Queue files stay in `data/raw/web/` after ingest — the manifest tracks what's been compiled.
- Re-running `/learn` on an already-ingested batch is safe — ingest skips unchanged files.
- To fetch fresh items before running `/learn`:
  `ARXIV_FETCH_ENABLED=true FEED_FETCH_ENABLED=true uv run cartographer --cron`
- To fetch without the full cron: `uv run librarian scrape arxiv` or
  `uv run librarian scrape feeds` (add `--list-feeds` to see the source table,
  `--dry-run` to preview).
- Feed volume varies a lot by source — the fetcher's default window is 7 days, so a
  wider `--since-days` can queue a large batch in one go.

## Output format

```
## Learning Queue — YYYY-MM-DD

Processed N items (P papers, F posts) → M passed topic filter

### Top picks

**1. [Title](url)**
arXiv XXXX.XXXXX | Published: YYYY-MM-DD | Categories: cs.CL, cs.AI
> [2-3 sentence abstract excerpt]

**2. [Title](url)**
Addy Osmani (tier 1) | Published: YYYY-MM-DD
> [2-3 sentence summary excerpt]

**3. [Title](url)**
...

---
To add to a pillar reading list, copy the URL and link it from the relevant
05-RL/ or pillar README. No automated LAE writes — the human decides what enters
the curriculum.
```

Use the `arXiv <id> | … | Categories: …` line for papers and the
`<source name> (tier N) | …` line for feed posts.

If `TOPIC_FILTER` was set and 0 items matched: report that and show up to 3 unfiltered
picks instead with a note that the filter returned nothing.

## Calibration

3 picks, or all if fewer than 3 remain after filtering. A longer list is the failure this skill exists to prevent: it hands the triage back to the human. Too narrow is the opposite failure: three items from one high-volume feed, or an empty result that hides everything because a keyword missed, which is why a filter matching 0 items still shows up to 3 unfiltered picks.

Keep the excerpt to 2-3 sentences of the abstract or summary. Tier 2 feed posts are `low` confidence: a pick that cites one as the record has overclaimed. Never write to the curriculum, however good the pick looks.
