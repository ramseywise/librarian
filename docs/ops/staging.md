# Staging

A second copy of the stack on the same host, to run a new image against the e2e set before
production gets it. Nothing here has run on a host yet (`docs/status.md`).

## What is separate and what is shared

| | Staging | Shared with production |
|---|---|---|
| Compose project | `librarian-staging` | no |
| Volumes (Postgres, indexes, Caddy certificates) | `librarian-staging_*` | no |
| Env file | `.env.staging` | no |
| Host ports | 8081 (HTTP), 8444 (HTTPS), changeable | production keeps 80/443 |
| Image state | `.ops/staging/` | no |
| Content (`./data`, `./content`) | read-only bind mounts of the same directories | **yes** |
| Backups | none (leave `LIBRARIAN_BACKUP_URL` unset) | n/a |

Content is shared on purpose: staging tests the code against the content production serves. If
you want a content release tested first, point staging at it with its own `LIBRARIAN_RELEASE_URL`
and prefix in `.env.staging`.

Staging must not share secrets, the database, an OAuth client or the Anthropic key with
production. It gets a low spend cap (`.env.staging.example` sets 2 USD a day).

## One-time setup

```sh
cp .env.staging.example .env.staging        # gitignored
$EDITOR .env.staging                          # fresh secrets: openssl rand -hex 32
```

Reaching it: staging listens on 8081/8444 by default so it can sit beside production. Give it a
host name (`staging.<domain>`, `LIBRARIAN_DOMAIN` in `.env.staging`) and either forward that name
to port 8444 from whatever fronts the host, or move production elsewhere and set the ports to
80/443. A public name gets its own Let's Encrypt certificate from staging's Caddy, which needs
ports 80/443 to reach it, so on one host the simplest shape is a forwarded name. With
`LIBRARIAN_DOMAIN=localhost` Caddy uses its internal CA and the tests need `SSL_CERT_FILE` set to
its root, as `tests/e2e/run_compose.sh` does.

## Day to day

Every operator command takes `--stack staging` (or `LIBRARIAN_STACK=staging`):

```sh
./librarian --stack staging start      # uses LIBRARIAN_IMAGE from .env.staging; waits for /readyz
./librarian --stack staging status
./librarian --stack staging logs librarian
./librarian --stack staging stop
```

To move staging to a new tag, edit `LIBRARIAN_IMAGE` in `.env.staging`, then `docker compose -p
librarian-staging --env-file .env.staging pull librarian` and `./librarian --stack staging start`.
`./librarian --stack staging upgrade <tag>` also works, but it keeps production's gate (no
upgrade without a backup younger than 15 minutes), and staging has no bucket by design, so it
will refuse until you give staging one.

`./librarian --dry-run --stack staging start` prints the exact compose commands without running them.

## Promoting

1. CI builds `sha-<short>` on main (`ci.yml`, `docker` job).
2. Put it on staging: `./librarian --stack staging start` with `LIBRARIAN_IMAGE=ghcr.io/<owner>/librarian:sha-<short>` in `.env.staging`.
3. Run the **Promote** workflow (`.github/workflows/promote.yml`, Actions, Run workflow) with that tag.
   It runs `tests/e2e/test_container.py` against `STAGING_URL`, then, after the `production`
   environment approval if you configured one, copies the image to the `production` tag in GHCR
   (`docker buildx imagetools create`: a registry-side copy, not a rebuild).
4. On the host: `./librarian upgrade production`. This is the backed-up, readiness-checked, auto-rolled-back path in `upgrade.md`.

Repository settings the workflow needs: variable `STAGING_URL` (`https://staging.<domain>`, no
trailing slash), and in the `staging` environment the secret `STAGING_API_TOKEN` (staging's
`LIBRARIAN_API_TOKEN`).

### What the workflow cannot check

- It does not know which image staging runs. `/metrics` is closed at the proxy, and `/readyz`
  does not name the release, so step 2 is on you. (The release shows in `librarian_release_info`
  on staging's own Prometheus, if you run the observability profile there.)
- It does not deploy. The last step is deliberately yours, on the host.
- The e2e file tests the auth gate, probes and the bundled UI, not chat or search quality.
- `production` as a moving tag means "whatever was promoted last"; to go back, promote an older
  `sha-` tag again, or `./librarian upgrade <old sha tag>` on the host (the previous tag is in `.ops/image.prev`).

## Tear down

`docker compose -p librarian-staging --env-file .env.staging down -v` removes the staging
containers and volumes. The project name keeps this from touching production's volumes.
