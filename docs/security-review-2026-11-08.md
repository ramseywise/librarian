# Security review, 2026-11-08

Scope: `src/librarian/api/` (routes, auth, CSRF, rate limits, middleware), `src/librarian/agent/` (chat loop, tools),
and the session/account code they depend on (`src/librarian/accounts/`). Method: read every route and its dependency,
trace each credential from cookie or header to a user, read each outbound HTTP and filesystem call, then fix the small,
certain issues with tests. This is a code review by the author's tooling, not a penetration test, and nobody else has
read it. Not reviewed: the frontend bundle beyond its Markdown renderers, the Caddyfile beyond what is noted, the
Docker image's OS packages, `src/librarian/tools/` (presenter, cartographer, slides: offline tools), and any host
configuration.

Severity: High = exploitable by an unprivileged outsider or breaks tenant isolation; Medium = needs a signed-in user or
a precondition, real impact; Low = hardening, limited impact; Info = a fact to keep in mind.

## Findings

| ID | Severity | Location | Finding | Status |
|---|---|---|---|---|
| S1 | Medium | `agent/loop.py` `_public_page_exists` (was an `rglob(f"{page_id}.md")`) | The chat highlight step took a page id the model chose through `read_page` and globbed for it. A glob character in the id matched other files, and the check did not exclude `private/`, so the model (steered by injected page text) could confirm a private page's existence through a highlight event. | Fixed: a plain-stem regex and an explicit private exclusion. Tests: `test_highlight_never_confirms_a_private_page_or_takes_a_glob`. |
| S2 | Medium | `accounts/sessions.py`, `api/routers/auth.py` | Sessions had an absolute lifetime only: no idle timeout. Login kept any session cookie the browser sent, so a session id planted before sign-in (fixation) stayed valid and a stolen cookie lived 30 days regardless of use. | Fixed: idle timeout `LIBRARIAN_SESSION_IDLE_DAYS` (default 7, 0 = off; absolute `LIBRARIAN_SESSION_DAYS` is never extended); login revokes the presented session and issues a new id; stale rows are swept when a session is created. Migration 0008 adds nullable `sessions.last_used_at`. Tests in `tests/api/test_auth.py`. |
| S3 | Medium | `accounts/users.py`, `accounts/invites.py`, `accounts/keys.py` | No way to lock out a user: removing a user's sessions and keys left them able to sign in again (still invited or a user), and a role change did not end their sessions, so a demoted admin kept admin rights until the cookie expired. | Fixed: `users disable|enable` (CLI and `POST /api/admin/users/{email}/disable|enable`, audited) sets `disabled_at`, kills sessions, revokes keys and blocks every sign-in path and key; the owner cannot be disabled; any role change ends that user's sessions. Migration 0008 adds nullable `users.disabled_at`. Tests in `tests/api/test_auth.py`. |
| S4 | Medium (mitigated) | `agent/loop.py`, wiki and web-captured pages as tool results | Indirect prompt injection: page text returned by `search_wiki`/`read_page` enters the model's context. Hostile text in a captured source could try to steer the answer. Impact is bounded: every agent tool is `read_only=True`, none can fetch a URL or write, the CSP `img-src 'self' data: blob:` blocks image-based exfiltration, and private pages are excluded from tool results. | Partly fixed: the system prompt now states that tool-returned text is source material, never instructions (`test_the_system_prompt_treats_page_text_as_data`). Not solvable by prompt alone; a model can still be talked into a misleading answer. Open: S1-style exclusions must be kept if a tool is added. |
| S5 | Low | `api/routers/graph.py` (`/api/graph`, `POST /api/layout/umap`, `/api/edges/semantic`), `api/routers/tools.py` | Authenticated routes that do real compute (UMAP layout, graph build, tool calls) have no rate limit. Only `/auth/*`, chat and feedback are limited. A signed-in user (or a leaked key) can load the host. | Not fixed. Needs a decision on limits per route and a shared limiter; the table-backed `rate_limits` exists for it. Open. |
| S6 | Low | `api/security.py` `ChatLimiter` | The per-minute burst limit is per process, so with N workers a user gets N times the burst. The daily spend cap is shared (database) and unaffected. | Accepted, documented in code. Revisit if burst abuse shows in the spend metrics. |
| S7 | Low | `api/security.py` `AuthLimiter` | The shared (database) auth limiter fails open if the database is down, falling back to the per-process one. | Accepted: failing closed would make a database blip a sign-in outage. Documented. |
| S8 | Low | `api/routers/release.py` `/admin/reload` | Public path with an HMAC check inside the route. A captured signed request can be replayed within the 300 s skew (the action is an idempotent pull, so impact is a redundant pull), and bad signatures are not throttled beyond the app-wide limits. | Not fixed. Add `auth_limiter` or a nonce if the endpoint is ever non-idempotent. Open. |
| S9 | Low | `docker-compose.yml` `LIBRARIAN_FORWARDED_ALLOW_IPS=*` | uvicorn trusts `X-Forwarded-For` from any peer. Safe only because port 8000 is `expose`d, not published, and Caddy is the sole ingress. Publishing the port would let a client forge its address and slip past the auth limiter. | Accepted. Do not publish 8000; `deploy.md` and the compose comment say so. |
| S10 | Low | `agent/` logging, `logs/agent.jsonl` | The agent log stores the user's query text and user id (personal data, not secrets) in a local file. Completion text is gated by `LIBRARIAN_TRACE_CONTENT` (off). No tokens, cookies or keys are logged: `RequestLogMiddleware` records method, path, status and user id only. | Accepted. Retention of that file is not defined; set a rotation policy before inviting people who did not consent to logging. Open. |
| S11 | Info | `api/prom.py`, `docker/Caddyfile` | `/metrics` is outside the app-wide auth. It requires `LIBRARIAN_METRICS_TOKEN` (404 when unset) and Caddy answers 404 for the path from outside. | Checked. Two locks present. |
| S12 | Info | `config.py` | Secret settings may now come from `<NAME>_FILE`. `AWS_*`, `SENTRY_DSN`, `OTEL_*` and the presenter/cartographer tools' direct `ANTHROPIC_API_KEY` read are outside the settings object and have no file form. | Documented in `docs/ops/deploy.md`. |
| S13 | Info | image config | `LIBRARIAN_PUBLIC=true` is set in the Dockerfile, so `private/` trees are never read or served by the deployed container (the compose tmpfs masks are the second lock). A local run leaves it off (single-user laptop); a multi-user host that runs the code outside the image must set it. | Checked. |

## Checked and found sound

- **Authorization.** All routes sit behind the app-level `current_user` dependency except the explicit public set
  (`/healthz`, `/readyz`, `/api/auth/config`, `/api/legal/third-party`, `/admin/reload`, `/auth/*`, `/metrics`) and the
  static UI mount. Admin routes use `Admin`; member data routes filter by `user.id`; feedback delete is owner-scoped; key
  revoke checks the key is the caller's.
- **CSRF.** Cookie-authenticated writes need the double-submit `x-csrf-token`; logout and the email-link POST check
  themselves (token, `same_origin`); cookie WebSockets require a same-origin `Origin`. Bearer credentials are exempt
  because a browser does not attach them on its own.
- **Open redirect.** `safe_next` allows only a single leading `/` path (`//` and `/\` refused); Starlette percent-quotes
  control characters in the `Location` header.
- **Account enumeration.** `POST /auth/email` answers 202 for any address; link tokens are single-use, issued per hour
  with a cap, and spent by a POST confirmation page so mail scanners' GETs cost nothing.
- **Path traversal.** Course assets and sources, slide ids, and `read_page` resolve the path and compare it with the root
  (segment regex, `private` rejected). No bypass found.
- **SSRF / injection.** Outbound HTTP goes only to fixed OAuth and Resend endpoints and operator-set `release_url`
  and remote URLs; no user-supplied URL is fetched. Database access is SQLAlchemy Core with bound parameters; the one
  `text()` is the advisory lock. Markdown from the wiki/courses is sanitised (`rehype-sanitize`) after `rehype-raw`.
- **Secrets in the repo and logs.** Credential headers and cookies are scrubbed before Sentry; the secret-file errors
  name the variable and never the value (tested).

## Not covered

- No dynamic testing (no fuzzing, no scanner run against a deployed host), no dependency vulnerability scan (the SBOM job
  produces the inventory, nobody scans it yet), no review of the React app beyond its Markdown components, no review of
  Caddy's TLS settings, container capabilities, host hardening, Postgres roles, or the bucket and CI permission model.
- S5, S8 and S10 are open. The review has one author; a second reader would find different things.
