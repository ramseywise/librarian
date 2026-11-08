# Rotate secrets

Do one secret at a time, verify, then the next. Where the secret lives: `.env` on the host, or a file if you use
`<NAME>_FILE` (`deploy.md`). After editing either, `docker compose up -d librarian` (a plain restart does not re-read
`.env`). Anything that leaked is rotated first and investigated second.

| Secret | Where | What breaks while it changes | Order |
|---|---|---|---|
| `LIBRARIAN_SESSION_SECRET` | host | It signs only the 10-minute OAuth state cookie. Logins in flight fail (user retries); signed-in sessions are unaffected (they are random tokens in the database). | Change, restart. |
| `LIBRARIAN_RELEASE_WEBHOOK_SECRET` | host **and** the repo's Actions secret `LIBRARIAN_RELEASE_WEBHOOK_SECRET` | Until both match, the release workflow's reload call gets 401; hosts still pick releases up at the next poll. | New value in GitHub first (the workflow is idle between releases), then host, restart. |
| `LIBRARIAN_API_TOKEN` | host, and any script using it | Everything that sends the old bearer token gets 401. | Change, restart, update callers. |
| API keys (`lk_...`, per user) | database | Only that key's MCP client. | `lb keys create <email> --name <what>`, give it out, `lb keys revoke <old-id>`. List with `lb keys list <email>`. |
| `GOOGLE_CLIENT_SECRET` / `GITHUB_CLIENT_SECRET` | host, and the provider's console | Google/GitHub sign-in fails between provider change and restart. Email links and signed-in sessions keep working. | Add the new secret at the provider (Google allows two), host, restart, delete the old one. GitHub shows one at a time: expect a short gap. |
| `RESEND_API_KEY` | host | Sign-in emails and the failed-backup email stop. | Create new key in Resend, host, restart, delete old key. |
| `ANTHROPIC_API_KEY` | host | Chat and the presenter/cartographer tools fail. | New key in the console, host, restart, delete old key. |
| `LIBRARIAN_METRICS_TOKEN` | host and Prometheus config | Scrapes get 404/401. | Change both, restart both. |
| `POSTGRES_PASSWORD` | host, and inside Postgres | The API cannot connect until both agree. | `docker compose exec postgres psql -U librarian -c "ALTER USER librarian PASSWORD '<new>'"`, set `.env`, `docker compose up -d librarian backup`. URL-safe characters only. |
| Backup age key | password manager; the **public** half in `LIBRARIAN_BACKUP_AGE_RECIPIENT` | Old backups need the old private key; new ones use the new. | `age-keygen -o new.key`, put the new `age1...` in `.env`, restart `backup`, run `./librarian backup`. Keep the old private key until the old backups age out (30 days). |
| Bucket keys `AWS_*` | host (the `backup` service), and the CI release secrets | Backups fail; the failed-backup email fires. | New token in the bucket's console, host, `docker compose up -d backup`, `./librarian backup`, then revoke the old token. CI uses separate `RELEASE_AWS_*` secrets. |
| `SENTRY_DSN` | host | Error events stop. | Rarely needed; rotate the key in Sentry, host, restart. |

## Verify

- `curl -s https://<domain>/readyz` is 200 after the restart.
- Exercise the one thing the secret protects: sign in (session, OAuth, Resend), send one chat message (Anthropic), push
  a no-op content release or `curl` the signed reload (webhook), `./librarian backup` (age, bucket), `curl -H "Authorization: Bearer <token>"` (API token).
- `lb users list` still shows the users: the database was not touched.
- A leaked **user session** is not a secret rotation: use `revoke-user.md`.
- Never paste a secret into a ticket, chat or the shell history (`read -rs` or write the file with an editor).
