# Search returns stale results

Search reads the index file. In release mode both the content tree and the index come from the same release through
two symlinks, so "stale" is one of: the wrong release is current, the symlinks disagree, a worker still holds the old
index, or the index was never rebuilt from changed content.

## Symptoms

A page you just published is not found, an old answer persists, a retired page still ranks, or two requests return
different content.

## Checks

```
lb release list                                     # which release is current / pinned
curl -sI -H "Authorization: Bearer $LIBRARIAN_API_TOKEN" https://<domain>/api/release | grep -i x-librarian-release
docker compose exec librarian ls -l /app/var/content/current /app/var/index/current
docker compose exec librarian cat /app/var/content/pin 2>/dev/null     # a pin freezes the content
curl -s https://<domain>/readyz
```

Read it as: `content/current` points at `releases/<name>`; `index/current` should be the index inside that same
release. Repeat the header check several times: different names across calls mean workers disagree (one has not
reloaded). The release you expect not being listed means the pull failed: `docker compose logs --tail 200 librarian | grep -i release`.

## Fix

1. Pinned by mistake: `lb release unpin`.
2. Pull and swap now, every worker: `curl -fsS -X POST https://<domain>/admin/reload -H "Authorization: Bearer $LIBRARIAN_API_TOKEN"`
   (an admin session or key works too; the CI webhook uses a signed request). A 502 `Release not installed` names why
   (checksum, bucket unreachable, private path in the archive): fix that, repeat.
3. Release mode off (no `LIBRARIAN_RELEASE_URL`): content is `./data`. Rebuild the index from it:
   `docker compose run --rm indexer`, then the `/admin/reload` call above.
4. The release itself is stale or wrong: build and push a new one (`content-release` workflow), or `rollback.md` to pin an older one.
5. Still stale: `docker compose restart librarian`. State is in the volume and the database, so a restart loses nothing.

## Verify

Query a phrase that exists only in the new content; `X-Librarian-Release` shows the expected name on five requests in
a row; `/readyz` is 200 with `"index":"ready"`.
