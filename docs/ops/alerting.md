# Minimum alerting

Four things page the owner, and everything else waits for the full phase 5 SLO work. All of it is
configured outside the repo, so this page is a checklist. Tick each box once on the real host, then
record the date in `docs/status.md` (Alerting row).

Replace `<domain>` with `LIBRARIAN_DOMAIN`. The alert address is the owner's own mailbox, which is
kept out of this repo.

## What the app gives you

- `GET /healthz` returns 200 while the process answers. Use it for "is the container up".
- `GET /readyz` returns 200 with `{"status": "ready"}` once an index is loaded, and **503** with
  `{"status": "not_ready", ...}` while it is building, missing or broken. Neither route needs a
  token. Use `/readyz` for the uptime probe: it is the one that notices a missing index.
- Caddy gets the certificate from Let's Encrypt and renews it by itself. The probe on expiry is a
  second pair of eyes, for when renewal fails (port 80 blocked, DNS moved).

## 1. Uptime probe and certificate expiry

Pick one external service (Better Stack, UptimeRobot, Healthchecks.io or Cloudflare Health
Checks all do this). It must run from outside the host and outside the compose network, or it
will not notice the host or Caddy being down.

- [ ] Create an HTTPS monitor on `https://<domain>/readyz`.
  - Method GET, expect status 200, check every 1 to 5 minutes, timeout 10 s.
  - Optional body check: contains `"status":"ready"`.
  - Alert after 2 consecutive failures, to avoid paging on one restart. A planned upgrade can
    take up to the container start period (300 s on cold index builds), so pause the monitor
    for an upgrade or accept one alert.
- [ ] Turn on certificate expiry on the same monitor (or add an SSL monitor on `<domain>:443`).
  Alert at 21 days and again at 7 days before expiry. Caddy renews at about 30 days, so a
  21-day alert means renewal has failed for at least a week.
- [ ] Send alerts to the owner's email, plus one push channel (phone app or SMS) so that a mail
  outage and a host outage are not the same outage.
- [ ] Test it: stop the stack (`docker compose stop librarian`), confirm the alert arrives, start
  it again, confirm the recovery notice.

A monitor config can live in the repo only for a service that reads one from a file. None of the
above services is chosen yet, so nothing is committed. If Cloudflare Health Checks or Better
Stack's Terraform provider is picked, add the file under `docs/ops/` in that change.

## 2. Sentry alert rules

Sentry is already wired in the app: it starts when `SENTRY_DSN` is set, names the environment from
`SENTRY_ENVIRONMENT`, and tags every event with `LIBRARIAN_RELEASE`. Credential headers and
cookies are scrubbed before sending (`tests/api/test_observability.py`).

- [ ] Create a Sentry project (platform Python/FastAPI) and put its DSN in the host's `.env` as
  `SENTRY_DSN`. Set `SENTRY_ENVIRONMENT=production`. Restart the stack.
- [ ] Send a test event and see it in Sentry. Without this the rules below are untested.
- [ ] Alert rule "new issue": Alerts, Create Alert, Issues. Condition: a new issue is created.
  Filter: environment equals `production`. Action: email the owner. Frequency: once per issue.
- [ ] Alert rule "error-rate spike": Alerts, Create Alert, Issues (or Metric alert on event
  count). Condition: more than 10 events in 5 minutes (tune it after a week of real traffic) in
  `production`. Action: email the owner. This also catches a known issue that suddenly gets loud.
- [ ] Regression alert: the same "new issue" rule with "issue changes state from resolved to
  unresolved", so a fixed bug that returns is not silent.
- [ ] Check the monthly event quota and turn on the spike protection setting, so one loop cannot
  use the free tier in an hour.

## 3. Failed backup email

The nightly backup job (`librarian ops backup`, built by the D1 work) exits non-zero on failure and
sends an email through Resend. This is the only alert whose code lives in the repo. Its absence is
the failure mode, so also add a dead-man check.

- [ ] In the host's `.env`, set `RESEND_API_KEY` and `EMAIL_FROM` (already used for sign-in
  links, so the sending domain with SPF and DKIM is verified once). Use the exact variable names
  that the D1 backup job reads for the alert recipient (check `.env.example` once it lands).
- [ ] Force a failure once (for example point the bucket variable at a name that does not exist),
  run the job by hand, and see the email arrive. Restore the setting.
- [ ] Dead-man check: add a Healthchecks.io-style "ping on success" check for the nightly job,
  with a grace period of 26 hours. A job that never starts (cron gone, host rebooted without the
  timer) sends no failure email; this check alerts on the missing success.
- [ ] Confirm the bucket lifecycle rule keeps 30 days and that the newest object is under 26 hours
  old (a manual look at the bucket is enough for the first week).

## 4. When an alert fires

1. Open `https://<domain>/healthz` and `/readyz` from your own machine.
2. `./librarian status` and `./librarian logs` on the host once D4 lands; until then
   `docker compose ps` and `docker compose logs --tail 100 librarian`.
3. `/readyz` 503 with `"index": "missing"` means the indexer did not run: `docker compose run
   --rm indexer`.
4. A bad release: roll the image back with `./librarian upgrade <previous-sha>` (D2) and pin the
   previous content release (`librarian release pin <sha>`, phase 4).

## Not in this page

SLO dashboards, Prometheus metrics, disk and spend-cap alerts and a game-day belong to the full
phase 5.1 in `.claude/docs/plans/2026-11-07-multi-user-production.md`.
