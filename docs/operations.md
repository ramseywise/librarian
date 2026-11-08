# Operations, content releases, CLI and environment

Moved from CLAUDE.md. Runbooks are in [ops/](ops/); what is deployed is in [status.md](status.md).

## Operations and content releases

- **Operations:** `./librarian start|stop|status|logs|backup|restore|upgrade|content push` is the one operator
  entrypoint (wraps compose and `librarian ops`, in `src/librarian/ops/`; runbooks in `docs/ops/`). The host pulls an
  image by tag (`LIBRARIAN_IMAGE`) and never builds. **Migrations are expand-only within a release:** add columns
  nullable (or with a server default), never drop or rename one in the same release that stops using it; the drop
  or rename ships one release later. That is what lets `./librarian upgrade` roll back to the previous image without
  down-migrations. `upgrade` refuses without a backup younger than 15 minutes.
- **Content releases** (`src/librarian/release/`): a `content/*` tag runs `.github/workflows/content-release.yml`
  (checks, all eval-gate arms, then `librarian release build` inside the image, which refuses any `private/` path)
  and uploads `content-<sha>.tar.zst`, its `.sha256`, then `latest`. With `LIBRARIAN_RELEASE_URL` set the API
  serves `var/content/current`, pulls on start, every `LIBRARIAN_RELEASE_POLL_S` and on a signed `POST /admin/reload`,
  and names the release in `X-Librarian-Release`. Roll back with `librarian release pin <sha>` (the current release
  and two before it stay on disk); `unpin` follows `latest` again. A release index is built for one state dir
  (`/app/var`); a host with another one refuses it.

## CLI

- CLI: `librarian wiki stats|snapshot|check|gaps|log|ask|graph|rename|relink|lint|verify|index-add|sync-check|compact-signals|week`,
  `librarian ingest triage|lint-raw|overlap|closeout|mark|status|pending|notion|linear|pdf`, `librarian scrape sessions|docs|repos|feeds|arxiv|bookmarks`,
  `librarian courses check|review`, `librarian feedback export|prune`, `librarian users add|list|invite|invites|promote`, `librarian keys create|list|revoke`,
  `librarian db upgrade|import-attempts|import-drill-log`, `librarian ops backup|restore|upgrade|schedule|list`,
  `librarian release build|pull|pin|unpin|list`, `librarian mcp [--rebuild]`, `librarian api`. Each is a thin dispatcher to the
  module's `main(argv)`, and `python -m librarian.<module>` works too.

## Environment


```
ANTHROPIC_API_KEY=       # Required for MCP server and scripts
NOTION_API_KEY=          # Required for Notion ingestion
LINEAR_API_KEY=          # Required for Linear ingestion
DROPBOX_PDF_PATH=        # Path to local Dropbox PDF directory
```

Source from `.env` (gitignored). See `.env.example`.
