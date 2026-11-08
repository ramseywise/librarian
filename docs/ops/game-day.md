# Game day

Four failures, practised once on the **staging** stack (`./librarian --stack staging ...`, `staging.md`) before anyone
needs them on the real one. **None of this has been run yet.** The results tables are empty on purpose; a row is
filled when a person ran the scenario and watched the alert arrive, and `docs/status.md` moves only then.

Before starting: a fresh backup (`./librarian --stack staging backup`), the alert channels open (email, phone, Sentry,
Prometheus at `:9090/alerts`), and a second person or a timer noting times. Stop a scenario that goes beyond its
"abort" line and use the linked runbook. Alert names are in `deploy/prometheus/alerts.yml`; the uptime probe, Sentry
and backup-email alerts are in `alerting.md`. `lb` = `docker compose -p librarian-staging exec librarian librarian`.

Each scenario records: time injected (T0), time the alert fired, time recovered, and what was surprising.

## 1. Kill Postgres

Inject: `docker compose -p librarian-staging stop postgres`.

Expected: `/readyz` and sign-in fail; the API cannot reach accounts. Alerts: `LibrarianNotReady` (and
`LibrarianPublicProbeFailing` if readiness covers it from outside), the uptime probe on `/readyz`, and a burst of 5xx
feeding the `LibrarianErrorBudgetFastBurn` rule; Sentry "new issue" for the database errors. Within a minute, not at
the end of the hour.

Runbook: `readiness-stuck.md` ("All checks never run"), then `docker compose logs postgres`. Fix:
`docker compose -p librarian-staging start postgres`; the API reconnects without a restart (confirm; if not, restart it
and record that it needed one). Data check: `lb users list` shows the same users.

Verify recovery: `/readyz` 200, sign-in works, a chat message succeeds, alerts resolve. Abort and restore (`restore.md`)
only if Postgres will not start with its volume intact; do not delete the volume in a drill.

| Date | Operator | T0 | Alert fired (which, when) | Recovered | Needed a restart of the API? | Surprises |
|---|---|---|---|---|---|---|
| not yet run | | | | | | |

## 2. Kill a worker

Inject: the API runs N uvicorn workers in one container. List processes without `ps`:
`docker compose -p librarian-staging exec librarian sh -c 'for p in /proc/[0-9]*; do echo "${p#/proc/} $(tr "\0" " " < $p/cmdline)"; done'`,
then `docker compose -p librarian-staging exec librarian kill -9 <pid of one worker, not the parent>`.

Expected: the master restarts the worker; at most a few failed requests (in-flight ones on that worker), no sustained
alert. The point is to see that nothing is lost and that no page fires for a self-healing event. If load is on, a short
`LibrarianReadinessFlapping` or a small blip in the 5xx ratio is acceptable; `LibrarianNotReady` for more than a minute
is not.

Runbook: none needed if it self-heals; if the container goes down instead of restarting the worker, `readiness-stuck.md`.
In-memory state lost with the worker: the burst limiter and the chat-spend counters of that worker (the database holds
the daily spend), so also check `curl .../api/me` still reports the right "spent today".

Verify recovery: worker count back to N (same listing), `/readyz` 200, a chat message streams to the end.

| Date | Operator | T0 | Alert fired (or none) | Worker back after | Failed requests seen | Surprises |
|---|---|---|---|---|---|---|
| not yet run | | | | | | |

## 3. Push a bad content release

Inject, on staging only: build a release that is wrong in a way the checks may not catch (for example with a key page
deleted) and publish it the normal way, or `lb release pin` to a deliberately old release. Do not use a release whose
archive fails its checksum: that case is rejected at install and is a different test (the swap must not happen; verify it
by trying once).

Expected: the swap succeeds (the package is valid), so `/readyz` stays 200 and no host alert fires. What notices is the
product signal: `lb metrics check-release` (grounding and down-rating fall; `alerting.md` section 5) and a person.
Record honestly whether anything alerted; this scenario exists partly to show the gap.

Runbook: `rollback.md`, content section: `lb release list`, `lb release pin <last good>`, signed or admin
`POST /admin/reload`.

Verify recovery: `X-Librarian-Release` header shows the good name on repeated requests; the query that the bad release
got wrong is right again; `lb release list` shows `P` on the good one. Then `lb release unpin`.

| Date | Operator | T0 | Alert / signal that noticed it | Time to notice | Time to roll back | Surprises |
|---|---|---|---|---|---|---|
| not yet run | | | | | | |

## 4. Revoke the admin key

Inject: the admin's API key is "leaked". `lb keys list <admin email>`, then `lb keys revoke <key id>`.

Expected: any client using that key (MCP in remote mode, scripts) gets 401 on the next request; no host alert (this is
a deliberate act, not a failure). Evidence is the audit log: `key_revoke` with the actor. A 401 spike from the old
client may show in the error rate but is 4xx, not 5xx, so not in the availability burn alerts.

Runbook: `revoke-user.md` (the admin is a user: `lb users disable` is wrong for the owner, who cannot be disabled; for
the owner revoke keys and rotate `LIBRARIAN_API_TOKEN`, `rotate-secrets.md`). Also test the break-glass path: with the
key gone and the browser logged out, the operator still administers through the CLI inside the container (`lb users list`)
and the bootstrap token, and signs in by Google, GitHub or email link as the owner.

Verify recovery: the old key gets 401 (`curl -s -o /dev/null -w '%{http_code}' -H "Authorization: Bearer <old>" https://<staging domain>/api/me`);
a new key works; `GET /api/admin/audit` shows `key_revoke` and `key_create`.

| Date | Operator | T0 | Old key refused after | Break-glass path worked? | Audit showed it? | Surprises |
|---|---|---|---|---|---|---|
| not yet run | | | | | | |

## After the day

Fix every surprise in the runbook it belongs to, and note the change in the results row. Then change the
`docs/status.md` row from "built" to "drilled" with the date and the staging host, and name the scenarios not run.
