# core/ — ETL pipeline

Standalone scripts that populate `raw/` from external sources, plus the `researcher/`
sub-package that processes PDFs into Obsidian notes. Wiki compilation (data/raw/ → data/wiki/)
happens via Claude Code skills, not here.

## Pipeline overview

```
source (Notion / Linear / web / PDFs / repos / sessions / ...)
    └── core/<scraper>.py
            └── data/raw/<subdir>/YYYY-MM-DD-<slug>.md   (immutable once written)
                    └── [wiki compilation via Claude skills]
                                └── data/wiki/<domain>/<page>.md
```

`core/manifest.py` tracks what has been ingested (SHA-256 hash dedup). Run
`core/lint_raw.py` before ingesting to enforce the filename convention.
`core/relinker.py` runs after compilation to discover missing semantic links.

## Entry points

| Script | Ingests | Target dir | Key deps |
|--------|---------|------------|----------|
| `ingest_notion.py` | Notion pages (API) | `raw/notion/` | `notion-client` |
| `ingest_linear.py` | Linear issues (API) | `raw/linear/` | `linear-sdk` |
| `ingest_pdf.py` | PDFs from Dropbox | `raw/pdfs/` | `pypdf2` |
| `scrape_bookmarks.py` | Web URLs from `raw/web/bookmarks.txt` | `raw/web/` | `trafilatura` |
| `scrape_repos.py` | Local git repos listed in `raw/repos/repos.txt` | `raw/repos/` | none |
| `scrape_claude_docs.py` | `.claude/` folders + `docs/` from all workspace projects | `raw/claude-docs/` | none |
| `scrape_sessions.py` | Claude Code and Codex session JSONL | `raw/sessions/` | none |
| `seed_from_playground.py` | playground repo `.claude/docs/` | `raw/playground-docs/` | none |

### Invocation

```bash
uv run python core/<script>.py [args]
```

Most scrapers accept `--dry-run`. Check `--help` for script-specific flags.

## core/researcher/ sub-package

Self-contained PDF → Gemini → Obsidian pipeline. Reads PDFs, chunks them, sends to
Gemini for structured extraction, and writes Obsidian-flavored markdown to the configured
vault. Does **not** write to `raw/` — output goes directly to Obsidian.

```bash
uv run python -m core.researcher [--pdf path/to/file.pdf] [--batch]
```

Settings are loaded from `.env` via `core/researcher/_settings.py`.

## Supporting modules

| Module | Purpose |
|--------|---------|
| `manifest.py` | SHA-256 hash dedup registry (`raw/manifest.jsonl`). Use `ManifestSession` for batch ingest to avoid O(N²) file reads. |
| `lint_raw.py` | Pre-ingest filename linter — enforces `YYYY-MM-DD-lowercase-slug.md` convention |
| `relinker.py` | Post-ingest semantic relinking pass — discovers missing wiki links via embeddings. Bridges core/ and app/ (imports `app.backend.embeddings`). |

## Constraints

- `raw/` is **immutable input** — scrapers append, never modify or delete existing files.
- Manifest format (JSON lines, one entry per file) is a contract — the `path` and `hash`
  keys are relied upon by wiki compilation skills.
- Wiki compilation stays in Claude Code skills; `core/` is ETL only.
