# Operations, content releases, CLI and environment

Moved from CLAUDE.md. Runbooks are in [ops/](ops/); what is deployed is in [status.md](status.md).

## Operations and content releases

- **Operations:** `./librarian start|stop|status|logs|backup|restore|upgrade|content push` is the one operator
  entrypoint (wraps compose and `librarian ops`, in `src/librarian/ops/`; runbooks in `docs/ops/`). The host pulls an
  image by tag (`LIBRARIAN_IMAGE`) and never builds. **Migrations are expand-only within a release:** add columns
  nullable (or with a server default), never drop or rename one in the same release that stops using it; the drop
  or rename ships one release later. That is what lets `./librarian upgrade` roll back to the previous image without
  down-migrations. `upgrade` first runs `librarian db check` (read-only; exit 1 on a pending migration or an unknown revision) on the serving image, and refuses without a backup younger than 15 minutes.
- **Content releases** (`src/librarian/release/`): a `content/*` tag runs `.github/workflows/content-release.yml`
  (checks, all eval-gate arms, then `librarian release build` inside the image, which refuses any `private/` path)
  and uploads `content-<sha>.tar.zst`, its `.sha256`, then `latest`. With `LIBRARIAN_RELEASE_URL` set the API
  serves `var/content/current`, pulls on start, every `LIBRARIAN_RELEASE_POLL_S` and on a signed `POST /admin/reload`,
  and names the release in `X-Librarian-Release`. Roll back with `librarian release pin <sha>` (the current release
  and two before it stay on disk); `unpin` follows `latest` again. A release index is built for one state dir
  (`/app/var`); a host with another one refuses it. Release and scraper fetches refuse loopback, private, link-local and multicast addresses, on every redirect hop; set `LIBRARIAN_RELEASE_ALLOW_PRIVATE_ADDRESSES=1` if the bucket endpoint is internal, and `LIBRARIAN_SCRAPE_ALLOW_PRIVATE_ADDRESSES=1` to scrape an internal host.

## CLI

- CLI: `librarian wiki stats|snapshot|check|gaps|log|ask|graph|rename|relink|lint|verify|index-add|see-also|sync-check|compact-signals|week`,
  `librarian ingest triage|lint-raw|overlap|precheck|closeout|mark|status|pending|notion|linear|pdf`, `librarian scrape sessions|docs|repos|feeds|arxiv|bookmarks`,
  `librarian courses check|review`, `librarian feedback export|prune`, `librarian users add|list|invite|invites|promote`, `librarian keys create|list|revoke`,
  `librarian db upgrade|check|import-attempts|import-drill-log`, `librarian ops backup|restore|upgrade|schedule|list|prune-logs`,
  `librarian release build|pull|pin|unpin|list`, `librarian mcp [--rebuild]`, `librarian api`. Each is a thin dispatcher to the
  module's `main(argv)`, and `python -m librarian.<module>` works too.

## Environment


```
ANTHROPIC_API_KEY=       # Required for MCP server and scripts
NOTION_API_KEY=          # Required for Notion ingestion
LINEAR_API_KEY=          # Required for Linear ingestion
DROPBOX_PDF_PATH=        # Path to local Dropbox PDF directory
LIBRARIAN_AGENT_LOG_RETENTION_DAYS=90  # logs/agent.jsonl lines older than this are dropped; 0 keeps all
```

Agent log retention (`LIBRARIAN_AGENT_LOG_RETENTION_DAYS`, default 90, added 2026-11-17, not yet committed): `logs/agent.jsonl`
holds each answer's query text and user id. Each API worker prunes it at start and then daily (a lock lets one do the work),
and `librarian ops prune-logs [--days N] [--dry-run]` does it on demand (on the compose host:
`docker compose exec librarian librarian ops prune-logs --dry-run`). It rewrites only that file, keeps any line it cannot
date, and never touches `data/raw/`, `data/wiki/` or the other logs. The compose `backup` service does not mount that volume,
so `ops schedule` does not prune it. The product metrics read this file, so a window longer than the retention shows less history.

`POST /admin/reload` signature (2026-11-17, not yet committed): the request format is unchanged
(`X-Librarian-Timestamp`, `X-Librarian-Signature` over `<timestamp>.<body>`), but each signature is accepted once. A repeat
gets 401 "Signature already used."; a retry needs a new timestamp. The used signatures are rows in `accounts.rate_limits`
(`release-sig:<hash>`), shared across workers, so no migration. If the database cannot be read the call answers 503.

Source from `.env` (gitignored). See `.env.example`.

## Not verified

- The `./librarian` verbs on a host. The script's `upgrade` control flow is tested against a fake `docker`; nothing
  else here has run on a real host (`docs/status.md`).
- The content-release path end to end. The workflow has never run: there is no bucket, no real upload and no webhook
  call against a live host. Pull, verify, swap and pin are tested locally in `tests/release/`.
- That "roll back to the previous image without down-migrations" works, which relies on every release following the
  expand-only rule; no test starts an old image on a migrated database.
- The ingest commands that need keys (`notion`, `linear`, `pdf`) against the real services: not run for this page.
