# Backups and restore

## What is backed up

The database (Postgres on a host, SQLite when run without compose): accounts, sessions, attempts, progress, chat
spend, audit. Not backed up: `var/index/` and the DuckDB index (`librarian index build` rebuilds them) and the wiki
(it is in git). Each backup is `librarian-<UTC time>-<release>.dump.age` plus `.manifest.json` (release, Alembic
revision, row count per table, sha256 of the dump). The dump is encrypted with `age` to a public key: the host never
holds the private key. The manifest is plain JSON (counts and checksums, no row data).

## Set up (once)

1. `age-keygen -o librarian-backup.key`. Print the public key (`age1...`) into `LIBRARIAN_BACKUP_AGE_RECIPIENT`.
   Keep the private key in a password manager plus one offline copy. Without it a backup is unreadable.
2. A bucket (Cloudflare R2: endpoint `https://<account>.r2.cloudflarestorage.com`, region `auto`) with a lifecycle
   rule that expires objects after 30 days, and an API token scoped to that bucket.
3. In `.env`: `LIBRARIAN_BACKUP_URL=s3://<bucket>/librarian`, `LIBRARIAN_BACKUP_ENDPOINT_URL`,
   `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_DEFAULT_REGION=auto`, and `RESEND_API_KEY` + `EMAIL_FROM` +
   `LIBRARIAN_OWNER_EMAIL` so a failed run emails you.
4. `./librarian start` (adds the nightly `backup` service, 03:30 UTC) and `./librarian backup` once to check.

## Restore

```
./librarian restore latest --identity ~/librarian-backup.key           # or a named object from `ops list`
./librarian restore latest --identity ~/librarian-backup.key --replace # the database has data
```

The wrapper stops the API (nothing writes), then `librarian ops restore` runs the fences: it refuses a database that
has data unless `--replace`; checks the dump against the manifest's sha256; loads it into a NEW database; requires that
copy's Alembic revision and every table's row count to equal the manifest; only then swaps it in. The old database is
kept beside it (`<name>_pre_restore_<time>` in Postgres, `*.pre-restore-*` for SQLite) and never dropped. Then the
wrapper starts the API and waits for `/readyz`. If a fence rejects the restore the API stays stopped on purpose; read
the error, then `./librarian start` once you know the live database was not replaced. A backup newer than the code
(unknown Alembic revision) is refused: restore with the release that took it.

## Drill

Run on a scratch compose project, never on the live one, from the most recent nightly object:

```
COMPOSE_PROJECT_NAME=librarian-drill LIBRARIAN_DOMAIN=localhost LIBRARIAN_HTTP_PORT=8080 LIBRARIAN_HTTPS_PORT=8443 \
  ./librarian restore latest --identity ~/librarian-backup.key
```

Record each drill below. Check after it: sign-in works, `users` and `attempts` counts match the manifest.

| Date | Operator | Object restored | Backup size | Restore time (to /readyz) | Result | Notes |
|---|---|---|---|---|---|---|
| not yet drilled | | | | | | |
