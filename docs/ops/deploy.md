# Deploy

Needs a Linux host with Docker (Compose v2) and ports 80 and 443 reachable.

1. `git clone <repo> /srv/librarian && cd /srv/librarian`
2. `cp .env.example .env` and set: `LIBRARIAN_DOMAIN`, `LIBRARIAN_PUBLIC_URL`, `POSTGRES_PASSWORD` (URL-safe),
   `LIBRARIAN_SESSION_SECRET`, `ANTHROPIC_API_KEY`, a login method (Google, GitHub, or `RESEND_API_KEY` +
   `EMAIL_FROM`), `LIBRARIAN_OWNER_EMAIL`, and `LIBRARIAN_IMAGE=ghcr.io/<owner>/librarian:sha-<short>`.
   For backups also set `LIBRARIAN_BACKUP_URL`, `LIBRARIAN_BACKUP_ENDPOINT_URL`, `LIBRARIAN_BACKUP_AGE_RECIPIENT` and
   the `AWS_*` keys (see `restore.md`).
3. `./librarian start` (pulls, never builds; waits for `/readyz`; adds the nightly `backup` service when a bucket is set).
4. DNS: an A/AAAA record for `LIBRARIAN_DOMAIN` to the host. Caddy gets the certificate on the first request.
5. Content: from your laptop, `DEPLOY_HOST=user@host DEPLOY_PATH=/srv/librarian ./librarian content push`.

Locally the same verbs work with `./librarian --local start` (builds, API on http://127.0.0.1:8000, no TLS).
`./librarian --dry-run <command>` prints what it would run. Upgrades: `upgrade.md`. Restore: `restore.md`.
