# Readiness stuck

`GET /readyz` is public and returns 503 until all its checks pass. Liveness (`/healthz`) can be 200 meanwhile. The
body names the failing check:

```
curl -s https://<domain>/readyz     # {"status":"not_ready","index":"<state>","checks":{"index":..,"content":..,"embeddings":..}}
```

## Symptoms

The uptime probe on `/readyz` fires; `./librarian start` or `upgrade` times out waiting; chat and search return 503
with `Retry-After: 5`.

## Checks and fixes, per check

**`index` false** (`"index"` is `missing`, `building` or `error`): the search index file is absent or unreadable.
The API never builds it in production (`LIBRARIAN_INDEX_AUTOBUILD=0`); the `indexer` job does.

```
docker compose ps -a indexer && docker compose logs --tail 100 indexer
docker compose run --rm indexer                          # build it (first build is slow; minutes)
docker compose exec librarian ls -l /app/var/index/ /app/var/index/current
```
Then `curl -fsS -X POST https://<domain>/admin/reload -H "Authorization: Bearer $LIBRARIAN_API_TOKEN"`. In release
mode a release without an index also lands here: pull a release that has one (`stale-search.md`). `building` that
never ends: the indexer is stuck or out of disk (`df -h`, `docker system df`).

**`content` false** (only present when `LIBRARIAN_RELEASE_URL` is set): no release is installed, so there is nothing
to serve. Typical on a fresh host or after the bucket URL changed.

```
lb release list                                          # empty?
docker compose logs --tail 100 librarian | grep -i release
lb release pull                                          # uses LIBRARIAN_RELEASE_URL; prints the result
```
Fix the URL/bucket if it fails (public read, `latest` object exists), or push the first release with the
`content-release` workflow. For a host without a bucket, unset `LIBRARIAN_RELEASE_URL` and `./librarian content push`.

**`embeddings` false**: the embedding model is not loaded and was expected. (A model that failed to load is reported
as `degraded: embeddings_unavailable` and stays ready, with text-only search; this check is for one still loading or
missing.)

```
docker compose logs --tail 100 librarian | grep -i -E "embed|model"
docker compose exec librarian df -h /app/var /root 2>/dev/null
```
Wait out a cold start (the image's start period is 300 s); if it persists, the model files are missing from the image
or the volume is full: free space, then `docker compose up -d --force-recreate librarian`.

**All checks never run** (no JSON, connection refused, 502 from Caddy): the API is not up. `docker compose ps`,
`docker compose logs --tail 200 librarian` — a database that is down (`postgres` unhealthy), a failed migration
(`librarian db upgrade` error), or a bad setting (`SecretFileError: set X or X_FILE, not both`) stops it at start. After an
upgrade, roll back first (`rollback.md`), read logs second.

## Verify

`curl -s https://<domain>/readyz` is 200 with every check true; `./librarian status` says ready; one search and one
chat message succeed.
