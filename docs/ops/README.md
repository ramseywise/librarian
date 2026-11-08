# Operations runbooks

Every page here has the same shape: symptoms, checks (exact commands), fix, verify. Commands run on the host in the
repo directory (`/srv/librarian`). `lb` below means `docker compose exec librarian librarian`, the CLI inside the
running image (add `-f` flags or `--stack` yourself on a second stack).

| Situation | Page |
|---|---|
| A new release is bad: roll the image or the content back | [rollback.md](rollback.md) |
| A secret leaked or is due for rotation | [rotate-secrets.md](rotate-secrets.md) |
| Someone must lose access now | [revoke-user.md](revoke-user.md) |
| Search shows old or wrong results | [stale-search.md](stale-search.md) |
| `/readyz` answers 503 | [readiness-stuck.md](readiness-stuck.md) |
| Practise all of the above | [game-day.md](game-day.md) |

Set-up and recovery pages that these link to rather than repeat:

- [deploy.md](deploy.md): first deploy, secrets as files.
- [upgrade.md](upgrade.md): `./librarian upgrade`, its backup gate and automatic rollback.
- [restore.md](restore.md): backups, restore, the drill table.
- [alerting.md](alerting.md): the four alerts that page the owner.

First look at any incident: `curl -s https://<domain>/readyz`, `./librarian status`,
`docker compose logs --tail 100 librarian`. The security review is [../security-review-2026-11-08.md](../security-review-2026-11-08.md).
