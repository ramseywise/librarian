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

## Secrets as files (optional)

Every secret setting also reads `<NAME>_FILE`: the file's contents, trailing newline stripped. Covered:
`DATABASE_URL`, `LIBRARIAN_API_TOKEN`, `LIBRARIAN_SESSION_SECRET`, `GOOGLE_CLIENT_SECRET`, `GITHUB_CLIENT_SECRET`,
`RESEND_API_KEY`, `ANTHROPIC_API_KEY`, `LIBRARIAN_API_KEY`, `LIBRARIAN_RELEASE_WEBHOOK_SECRET`, `LIBRARIAN_METRICS_TOKEN`.
Setting both `NAME` and `NAME_FILE` is an error that names the variable (never the value), and so is an unreadable file.

**Not covered** (read outside the settings object): `AWS_*` (the `backup` service's bucket keys), `SENTRY_DSN`, `OTEL_*`,
and the `ANTHROPIC_API_KEY` that the presenter and cartographer tools read straight from the environment (the API and
chat agent do read `ANTHROPIC_API_KEY_FILE`). For Postgres use its own `POSTGRES_PASSWORD_FILE`. Keep those in `.env`.

Example, as `docker-compose.secrets.yml` next to the compose file (not committed; the files sit in `/srv/librarian/secrets/`,
mode 600, owned by root). `DATABASE_URL` is the full URL, so the database password appears once, in its own file:

```yaml
secrets:
  session_secret:   { file: ./secrets/session_secret }
  anthropic_key:    { file: ./secrets/anthropic_key }
  resend_key:       { file: ./secrets/resend_key }
  webhook_secret:   { file: ./secrets/webhook_secret }
  database_url:     { file: ./secrets/database_url }       # postgresql://librarian:<pw>@postgres:5432/librarian
  postgres_password: { file: ./secrets/postgres_password }

services:
  librarian:
    secrets: [session_secret, anthropic_key, resend_key, webhook_secret, database_url]
    environment:
      - DATABASE_URL=            # the base file sets it from POSTGRES_PASSWORD; clear it so only _FILE is set
      - LIBRARIAN_SESSION_SECRET_FILE=/run/secrets/session_secret
      - ANTHROPIC_API_KEY_FILE=/run/secrets/anthropic_key
      - RESEND_API_KEY_FILE=/run/secrets/resend_key
      - LIBRARIAN_RELEASE_WEBHOOK_SECRET_FILE=/run/secrets/webhook_secret
      - DATABASE_URL_FILE=/run/secrets/database_url
  backup:
    secrets: [database_url, resend_key]
    environment:
      - DATABASE_URL=
      - DATABASE_URL_FILE=/run/secrets/database_url
      - RESEND_API_KEY_FILE=/run/secrets/resend_key
  postgres:
    secrets: [postgres_password]
    environment:
      POSTGRES_PASSWORD: ""
      POSTGRES_PASSWORD_FILE: /run/secrets/postgres_password
```

Run with `docker compose -f docker-compose.yml -f docker-compose.secrets.yml up -d` (the `./librarian` script does not
add the second file). Remove the same names from `.env` or the "both set" error stops the API at start. An empty
`NAME=` is treated as unset, so clearing in `environment:` works. Check which form is in use without printing a value:
`docker compose exec librarian sh -c 'env | grep -c _FILE'`. Rotation of each secret: `rotate-secrets.md`.
