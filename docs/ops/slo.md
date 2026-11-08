# SLOs, metrics and cost

What "working" means, how it is measured, and what fires when it is not. Status of each piece is
in `docs/status.md`; none of it has run on a real host yet.

## The objectives

| SLO | Target | SLI (what is counted) | Metric |
|---|---|---|---|
| Availability | 99.5% over 30 days | requests not answered with a 5xx, of all requests | `librarian_http_requests_total{status}` |
| Search latency | p95 under 500 ms | `/api/courses/search` and the `search_wiki` tool call (`/api/tools/search_wiki`) | `librarian_search_duration_seconds` |
| Chat first token | p95 under 4 s | request arrival to the first `token` event on `/api/chat/stream` | `librarian_chat_first_token_seconds` |

Notes that change how to read them:

- There is no `/api/search` route. Search is lesson search plus the `search_wiki` tool, so the
  search SLI is those two together; other `/api/tools/{name}` calls are not counted in it.
- 99.5% over 30 days is a budget of about 3.6 hours of full outage, or 0.5% of requests. 4xx is
  the caller's error and does not spend it. A planned upgrade that makes `/readyz` 503 does.
- Chat is measured to the first token, not to the last byte: an answer streams for as long as it
  takes. The per-route histogram records chat to the last byte, so its p95 is long by design.
- The bucket edges include 0.5 s and 4 s, so "fraction under the target" is exact, not
  interpolated. The alert rules compute it as a ratio of bucket counts.
- A stream that ends without any token is counted as `librarian_chat_streams_total{outcome="no_token"}`
  and is not in the first-token histogram. A provider outage therefore shows in the outcome
  counter, not as slow first tokens.

## `/metrics`

Prometheus text format. Off by default.

- **Turn it on:** set `LIBRARIAN_METRICS_TOKEN` (any long random string, `openssl rand -hex 32`)
  and restart. With it unset the route answers 404 and the middleware does nothing.
- **Protection:** the request needs `Authorization: Bearer <token>` (401 otherwise). Caddy also
  answers 404 for `/metrics` from outside, so only Prometheus on the compose network, which scrapes
  `librarian:8000` directly, reaches it. The route is outside the sign-in dependency on purpose: it
  has a credential of its own, so a scrape does not need a user.
- **Labels are bounded.** `route` is the matched path template (`/api/courses/lessons/{lesson_id:path}`),
  never the raw path; anything unmatched is `other`. No user, query or token ever becomes a label.
- **Gauges** are computed at scrape time from shared state, so any worker answers them correctly:
  `librarian_ready` (the same checks as `/readyz`), `librarian_release_info{release,content}`,
  `librarian_chat_spend_usd{window="today"|"30d"}`, `librarian_chat_spend_cap_usd{scope}`
  (0 means no cap), `librarian_state_disk_free_ratio` and `librarian_state_disk_free_bytes`.

### Several workers and replicas

`LIBRARIAN_API_WORKERS` (default 2) runs N uvicorn processes in one container. Counters and
histograms live in each process, so `librarian api` (the supervisor) switches the client to
multiprocess mode before it starts them: it empties a directory (default `<tmp>/librarian-prometheus`
inside the container; `PROMETHEUS_MULTIPROC_DIR` overrides it) and every worker writes there. A scrape of any
worker sums all of them. Consequences:

- The directory is emptied at every start, so counters reset on a restart. Prometheus handles that
  (`rate()` and `increase()` treat a drop as a reset).
- It is deliberately not under `var/`: replicas share that volume, and one replica's start would
  erase the others' counters. Each replica has its own directory and its own counters; Prometheus
  scrapes each replica (the example config uses DNS service discovery on `librarian`) and the
  queries `sum` across them.
- With one worker the default registry is exact and no directory is used.
- Dead workers' gauges are not an issue (there are no process-level gauges).

## Turning on Prometheus and Grafana

```sh
# .env on the host: LIBRARIAN_METRICS_TOKEN=..., GRAFANA_ADMIN_PASSWORD=...
# edit the probe target in deploy/prometheus/prometheus.yml to https://<domain>/readyz
COMPOSE_PROFILES=observability ./librarian start      # or: docker compose --profile observability up -d
```

- Prometheus: `127.0.0.1:9090` on the host (an SSH tunnel to reach it). It reads the token from
  `LIBRARIAN_METRICS_TOKEN`, writes it to a file inside its own container at start so the token
  is not in the config, and keeps 45 days (the 30-day availability panel needs more than 30).
- Grafana: `127.0.0.1:3000`, admin password from `GRAFANA_ADMIN_PASSWORD` (default `admin`:
  change it before the first login). The data source and the **Librarian SLOs** dashboard
  (`deploy/grafana/librarian.json`) are provisioned from files.
- Blackbox exporter probes `/readyz` over TLS through Caddy from the compose network, giving
  `probe_success` and `probe_ssl_earliest_cert_expiry`. This sees the proxy and certificate; it
  does not replace the external uptime monitor in `alerting.md`, which also sees the host and DNS.
- Alerts exist in `deploy/prometheus/alerts.yml` but go nowhere until an Alertmanager (or Grafana
  contact point) is configured. Without one they are visible in the Prometheus Alerts page only.
  `alerting.md` still covers the external probe, Sentry and the backup email.
- Check the rules after editing them: `docker run --rm --entrypoint promtool -v "$PWD/deploy/prometheus:/w:ro" prom/prometheus:v3.16.0 check rules /w/alerts.yml`.

## Alerts and what to do

All rules are in `deploy/prometheus/alerts.yml`. `page` means wake someone; `ticket` means look
tomorrow.

### Error rate

`LibrarianErrorBudgetFastBurn` (page: 5xx at 14.4x the budget over 5 m and 1 h),
`LibrarianErrorBudgetSlowBurn` (page: 6x over 6 h and 1 h), `LibrarianErrorBudgetSimmering`
(ticket: the 3-day ratio is over 0.5%). Two windows each, so a short blip does not page and a
slow leak is still caught.

1. In the dashboard, which route has the 5xx? `sum by (route) (rate(librarian_http_requests_total{status=~"5.."}[15m]))`.
2. `./librarian logs librarian` and Sentry for the traceback.
3. Was there an upgrade or content release just before? `./librarian upgrade <previous tag>`
   goes back (`upgrade.md`); a content release is pinned back with `librarian release pin`.
4. Database errors point at Postgres: `./librarian status`, then `restore.md` only if the data
   itself is damaged.

### Latency

`LibrarianSearchSlow`, `LibrarianChatFirstTokenSlow` (ticket). Search: a cold or rebuilding index
(`librarian_ready`), a very large corpus after a content release, or CPU starvation (`docker stats`).
Chat first token: check `outcome="no_token"` first (provider errors), then provider status; the
retrieval step before the model call is the part you control.

### Readiness

`LibrarianNotReady` (page), `LibrarianReadinessFlapping` (ticket), `LibrarianPublicProbeFailing`
(page). `curl https://<domain>/readyz` names the failing check (`database`, `index`, `content`).
The API is down for the proxy but fine inside means Caddy or DNS; read `./librarian logs caddy`.
Flapping is usually a restart loop (out of memory) or a database that drops connections.

### Certificate

`LibrarianCertExpiringSoon` (14 days) and `LibrarianCertExpiryCritical` (3 days). Caddy renews at
30 days left, so this means renewal has been failing: ports 80 and 443 must reach the host and
DNS must point at it. `./librarian logs caddy | grep -i acme`.

### Disk

`LibrarianStateDiskLow` (under 15% free) and `LibrarianStateDiskCritical` (under 5%). The gauge is
the disk holding `var/`, which is where indexes, logs and caches grow. Free space: `docker system prune`
for old images, old index builds in `var/index/` (keep `current`), `logs/`. Postgres has its own
volume on the same host usually; check `df -h` there too. The metric does not see a different disk.

### Spend

`LibrarianSpendNearGlobalCap` (ticket) fires at 80% of `LIBRARIAN_CHAT_DAILY_BUDGET_USD` for the
day. At 100% chat stops for everyone until 00:00 UTC. Who is spending: `GET /api/admin/spend`
(below). Raise the cap or lower a user's cap, or revoke a key (`librarian keys revoke`).

## Cost visibility

`GET /api/admin/spend` (admin only; a non-admin gets 403) returns:

- `users`: each user's id and display name (no email), today and last-30-days USD, ordered by
  30-day spend, highest first;
- `global`: today and 30-day USD against the configured caps and the fraction used;
- `models`: USD and answer count per model, with a `source` field (`logs/agent.jsonl`) saying where the split came from.

How accurate it is: the figures are the estimate the spend cap uses (token counts times the price
table in `src/librarian/pricing.py`), not the provider invoice. The `chat_usage` table has one row per
user and UTC day and no model column, so the model breakdown comes from `logs/agent.jsonl` and covers
only the answers that file still holds. Compare with the provider's console once a month.

### The price table must be reviewed

Prices live in `src/librarian/pricing.py` with a `PRICES_REVIEWED` date.

```sh
uv run librarian pricing check     # prints the table and the review date
```

It exits 1 when the date is more than 35 days old, or when the configured `ANTHROPIC_MODEL` is
missing from the table (a missing model means its cost is not counted and the cap does not trip).
To review: compare each row with the published prices, fix any difference, then set
`PRICES_REVIEWED` to today. Run the check from the monthly routine; it is not in CI, because a
check that goes red when nobody changed anything trains people to ignore CI.

## What none of this proves

Nothing here has run on a host. The rules pass `promtool check rules`; the Prometheus and
blackbox configs pass their checkers; the dashboard is valid JSON that has not been opened in
Grafana. The thresholds (14.4x, 6x, 15% disk, 80% spend) are the textbook values, not tuned on
this service's traffic; revisit them after a month of real data.
