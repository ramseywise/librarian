# librarian — the Python package

The library behind the `librarian` CLI: ETL that populates `data/raw/` from external sources,
helpers for the wiki (triage, telemetry, relinking, renaming), the course catalog and the
settings every other part of the repo reads its paths from. Wiki compilation (data/raw/ →
data/wiki/) happens via Claude Code skills, not here.

```
src/librarian/
  config.py      Settings and get_settings(): repo root, every path, model names
  log_config.py  structlog setup with secret redaction
  cli.py         `librarian <group> <verb>`: thin dispatchers to each module's main(argv)
  wiki/          parser, health, telemetry, graph, rename, relinker, common
  retrieval/     embeddings (needs the `api` extra)
  courses/       catalog, curriculum, leitner, glossary, importer
  ingest/        scrapers, ingest gate, manifest, sensitive scans, raw lint
```

Import direction: `apps/` and `tools/` import `librarian`; `librarian` never imports them.

## Settings

`librarian.config.get_settings()` finds the repo root from `$LIBRARIAN_ROOT`, else the nearest
`pyproject.toml` above the package (a checkout or editable install), else above the working
directory. An installed wheel run outside a checkout must set `LIBRARIAN_ROOT`. The existing
variable names (`WIKI_DIR`, `COURSES_DIR`, `WIKI_DB_PATH`, `SISYPHUS_DIR`,
`LIBRARIAN_EMBEDDING_MODEL`, ...) still override the defaults. Modules assign their path
constants from it at import, so tests keep monkeypatching the module-level names.

## Pipeline overview

```
source (Notion / Linear / web / PDFs / repos / sessions / ...)
    └── librarian scrape|ingest <verb>
            └── data/raw/<subdir>/YYYY-MM-DD-<slug>.md   (immutable once written)
                    └── [wiki compilation via Claude skills]
                                └── data/wiki/<domain>/<page>.md
```

`ingest/manifest.py` tracks what has been ingested (SHA-256 hash dedup). Run
`librarian ingest lint-raw` before ingesting to enforce the filename convention.
`librarian wiki relink` runs after compilation to discover missing semantic links.
`librarian ingest triage` triages each raw file before compiling it: unchanged or duplicate,
and whether to compile, strip or route to private, using the scans in `ingest/sensitive.py`.
`librarian wiki stats|snapshot|check|gaps` compute the health numbers and run the private-leak check.

## Commands

| Command | Ingests | Target dir | Key deps |
|---------|---------|------------|----------|
| `librarian ingest notion` | Notion pages (API) | `data/raw/notion/` | `httpx`, `pydantic-settings` (`NOTION_API_KEY`) |
| `librarian ingest linear` | Linear issues (GraphQL API) | `data/raw/linear/` | `httpx`, `pydantic-settings` (`LINEAR_API_KEY`) |
| `librarian ingest pdf` | PDFs from Dropbox (`DROPBOX_PDF_PATH`) | `data/raw/pdfs/` | `pdfplumber` |
| `librarian scrape bookmarks` | Web URLs from `data/raw/web/bookmarks.txt` or `--url` | `data/raw/web/` | `httpx`, `beautifulsoup4` |
| `librarian scrape arxiv` | Recent arXiv papers, keyword-filtered | `data/raw/web/` | `httpx` |
| `librarian scrape feeds` | Recent RSS/Atom posts from the tracked blogs | `data/raw/web/` | `httpx`, `beautifulsoup4` |
| `librarian scrape repos` | Local git repos listed in `data/raw/repos/repos.txt` | `data/raw/repos/` | none |
| `librarian scrape docs` | `.claude/` folders and `docs/` from all workspace projects | `data/raw/claude-docs/` | none |
| `librarian scrape sessions` | Claude Code and Codex session JSONL | `data/raw/sessions/` | none |
| `librarian courses import` | Coursework from `learn-ai-engineering` (`make import-courses`) | `data/courses/` | `pyyaml` |

Most scrapers accept `--dry-run`. Check `--help` for script-specific flags. Every verb also runs as
`python -m librarian.<package>.<module>`.

The session tooling that used to live beside these (`cron`, `enrich`, `migrate`) now belongs to
`tools/cartographer/`; run it with `uv run cartographer --cron`.

## Modules

| Module | Purpose |
|--------|---------|
| `ingest/base.py` | `ScraperBase` ABC and `REPO_ROOT`: shared CLI flags, logging and manifest handling for the scrapers. |
| `ingest/manifest.py` | SHA-256 hash dedup registry (`data/raw/manifest.jsonl`). Use `ManifestSession` for batch ingest to avoid O(N²) file reads. |
| `ingest/lint_raw.py` | Pre-ingest filename linter. Enforces `YYYY-MM-DD-lowercase-slug.md`. |
| `ingest/ingest_gate.py` | Pre-ingest triage: unchanged, duplicate, changed or new, and whether to compile, strip or route to `private/`. Uses `sensitive.py` and `manifest.py`. |
| `ingest/sensitive.py` | Pattern scans for secrets, contact details and listed terms. Reports categories and lines, never values. |
| `wiki/relinker.py` | Post-ingest semantic relinking pass. Suggest-only; imports `retrieval.embeddings` (needs the `api` extra). |
| `wiki/common.py` | Shared wikilink regexes, `slugify`, alias lookup and canonical link types. |
| `wiki/telemetry.py` | Wiki health numbers, operation log, private-leak check and gaps list. Writes to `data/telemetry/`. |
| `wiki/graph.py` | Hubs, bridges and consensus clusters of the link graph (`make wiki-graph`). Needs `networkx` and `scikit-learn` (the `api` extra). |
| `wiki/rename.py` | Renames a wiki page and rewrites every inbound link. Dry run by default. |
| `wiki/parser.py`, `wiki/health.py` | The graph payload the API serves, and the latest telemetry row. |

## Constraints

- `data/raw/` is **immutable input** — scrapers append, never modify or delete existing files.
- Manifest format (JSON lines, one entry per file) is a contract — the `path` and `hash`
  keys are relied upon by wiki compilation skills.
- Wiki compilation stays in Claude Code skills; this package is ETL and read-side logic only.
- `courses` imports `ingest`, never the reverse. The git-ignore helpers both sides need live in
  `ingest/gitignore.py` (they used to sit in `courses/importer.py`, which made `ingest.scrape_repos`
  import `courses`). `import-linter` enforces the sub-package layering; see `pyproject.toml`.
