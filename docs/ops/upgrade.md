# Upgrade

```
./librarian upgrade sha-<short>          # a bare tag reuses the repository of the image now serving
./librarian upgrade ghcr.io/<owner>/librarian:sha-<short>
```

What it does, in order:

1. Runs `librarian ops upgrade <image>` in the `backup` service on the **current** image. It reuses a backup younger
   than `LIBRARIAN_BACKUP_MAX_AGE_MIN` (15) or takes one now. No backup, no upgrade (exit 3), nothing changed.
2. `docker compose pull librarian`, then `up -d --no-build` (the `indexer` job runs first, then `librarian`,
   which runs `librarian db upgrade` at start).
3. Waits up to `LIBRARIAN_READY_TIMEOUT` (300 s, the image's health start period) for `/readyz`.
4. On failure, brings the previous image back and waits again. The backup from step 1 stays in the bucket.
   On success the tag is recorded in `.ops/image` (the one before it in `.ops/image.prev`).

Why rollback is safe: migrations are **expand-only within a release** (CLAUDE.md). The previous image runs against the
upgraded schema because the new release only added nullable columns and tables. A drop or rename ships one release
after the code stopped using the column. There are no down-migrations.

If a release did break that rule, rolling back the image is not enough: `./librarian restore latest --replace
--identity <key>` returns the data to the pre-upgrade backup (writes since then are lost).

Content (wiki, courses) is separate: `./librarian content push`. Previous images stay on the host; do not prune the
last two (`docker image ls`).
