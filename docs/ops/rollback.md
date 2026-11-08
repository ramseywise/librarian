# Roll back

Two things roll back separately: the **image** (code and migrations) and the **content** (wiki, courses, search
index). Decide which one changed before the symptom started: `curl -sI https://<domain>/api/release` is auth'd, but any
API response carries `X-Librarian-Release`, and `cat .ops/image .ops/image.prev` names the image tags.

## Symptoms

- Errors, 5xx or a 503 `/readyz` right after `./librarian upgrade`: the image. If `upgrade` itself failed, it already
  rolled back (see `upgrade.md` step 4); check it did.
- Answers worse or pages missing after a content release, `/readyz` still 200: the content.

## Image

Checks:

```
cat .ops/image .ops/image.prev           # serving now / the one before
docker compose ps librarian              # which image is running
docker image ls | grep librarian         # the previous tag must still be on the host
./librarian status
```

Fix (rolls forward to the old tag; it takes a backup first, so a bad migration is still recoverable):

```
./librarian upgrade "$(cat .ops/image.prev)"
```

If `upgrade` refuses because the backup step fails (bucket down), you may skip it only when the broken release ran no
migration: `docker compose pull librarian && LIBRARIAN_IMAGE=$(cat .ops/image.prev) docker compose up -d --no-build librarian`,
then `printf '%s\n' "$(cat .ops/image.prev)" > .ops/image` by hand.

Verify: `curl -s https://<domain>/readyz` is 200 with `"status":"ready"`; `docker compose ps` shows the old tag; sign in.

Migrations are expand-only inside a release, so the old image runs on the new schema. If the bad release broke that
rule (a column was dropped or renamed), rolling the image back is not enough: `restore.md`, `--replace`, accepting the
loss of writes since the pre-upgrade backup.

## Content

Checks:

```
lb release list                          # * = current, P = pinned
docker compose exec librarian ls -l /app/var/content/current
```

Fix, naming the last good release from the list (the pin stops pulls following `latest`, so a later release does not
undo this):

```
lb release pin content-<good-sha>
curl -fsS -X POST https://<domain>/admin/reload -H "Authorization: Bearer $LIBRARIAN_API_TOKEN"   # swap now; or wait for the next poll
```

When the content is fixed and a new release is out: `lb release unpin`, then `/admin/reload` again.

Verify: `lb release list` marks the good one `*` and `P`; the `X-Librarian-Release` response header
(`curl -sI -H "Authorization: Bearer ..." https://<domain>/api/release`) shows its name; ask the chat one question that
the bad release got wrong; `/readyz` is 200.

If `pin` fails (name not in the bucket and not on disk): `stale-search.md`, last section.
