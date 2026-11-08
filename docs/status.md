# Status: what is built, and what has been checked

As of 2026-11-08, commit `0d071e20` plus the staged work described below. Plan:
`.claude/docs/plans/2026-11-07-multi-user-production.md`.

A passing suite is not "deployed", and a pushed commit is not "qualified". This page says how far
each capability has actually been checked, and what the check was.

## Levels

| Level | Meaning |
|---|---|
| `built` | The code exists. Tests may exist, but no CI run has covered this code (staged work, or no test at all). |
| `tested in CI` | A test file or workflow job exercises it, and that job passed on the latest commit on `main`. |
| `checked on a host` | Run on a real host with a real domain, with the date and host recorded. |
| `drilled` | Backups and restore only: a restore from a real backup object was run and timed. |
| `in progress` | Being built right now in another session. Not yet judged. |

Nothing is `checked on a host` or `drilled` yet: no host is recorded as live, and no restore has
been run. If a row claims either, it is wrong.

CI reference for `main` at `0d071e20` (run 42476834677): `ci / test` (the full `pytest tests/
--ignore=tests/e2e`), `ci / lint`, `architecture` (import-linter and pyright), `frontend` and
`docker` passed. **`e2e-container` failed** (the container refused to start without
`ANTHROPIC_API_KEY`, which the startup validation now requires), and it also failed on the
previous push. The staged `tests/e2e/run_container.sh` sets `LIBRARIAN_CHAT_ENABLED=false`; not yet run in CI. So anything whose only evidence is the container e2e is not `tested in CI`.

"Staged" means the files are in the index and not yet committed, so no CI run has seen them.

## Capabilities

| Capability | Level | Evidence | Not covered |
|---|---|---|---|
| Auth: Google and GitHub sign-in | `built` | Staged. `tests/api/test_auth.py` against faked providers (state, PKCE, verified email, `next` redirect). | No CI run; no real provider round trip. |
| Auth: email magic link (Resend) | `built` | Staged. `tests/api/test_auth.py` (single use, expiry, per-address cap, no mail for an uninvited address); `accounts/mailer.py`. | No CI run; no real Resend delivery, domain, SPF or DKIM. |
| Sessions and CSRF | `built` | Staged. `tests/api/test_auth.py` (cookie write needs the CSRF header, logout, expiry, websocket origin). | No CI run. |
| Invites | `built` | Staged. `tests/api/test_auth.py` (admin invite, CLI invite, duplicate refused, uninvited refused). | No CI run. |
| API keys | `tested in CI` | `tests/api/test_accounts.py` (key is its user, revoked key is 401, read-only key cannot write); committed. | Bootstrap `LIBRARIAN_API_TOKEN` is not yet retired. |
| Audit log | `built` | Staged. `accounts/audit_log.py`; asserted in `tests/api/test_auth.py`. | No CI run. |
| Postgres | `built` | `tests/db/test_postgres.py` runs only when `LIBRARIAN_TEST_DATABASE_URL` is set, and no workflow in this repo sets it. Compose stack with Postgres: `tests/e2e/run_compose.sh` (`make e2e-compose`), not in CI. | The suite that CI runs uses SQLite. |
| Alembic | `tested in CI` | `tests/db/test_db.py::test_migrations_upgrade_from_empty_and_are_idempotent`; seven revisions, 0001 to 0007 (0005 and 0006 are staged; 0007 `feedback` is unstaged). | Postgres upgrade path is not in CI. |
| N workers | `tested in CI` | `tests/api/test_workers.py` starts `librarian api --workers 2` and checks shared attempts and spend; committed in `d650248a`. | On SQLite, not Postgres; the multi-replica compose run is not in CI. |
| Indexer job | `tested in CI` | `tests/api/test_index_artifact.py` (deterministic build, atomic `current`, read-only handle, reload). | The compose `indexer` service is exercised only by `make e2e-compose`. |
| Per-user courses state | `built` | Attempts and progress per user: `tests/api/test_attempts.py`, `test_progress.py` (committed). Two-users test `tests/api/test_two_users.py` (staged). | The two-users test has not run in CI. |
| Remote MCP | `built` | Staged. `tests/api/test_mcp_remote.py`; `mcp/remote.py`. | No CI run; no real MCP client. |
| Hybrid retrieval (F10) | `built` | Measured 2026-11-08 on a tracked-files-only checkout: opt-in `LIBRARIAN_EXPERIMENT=hybrid-union` (BM25 top `limit*3` plus cosine top `limit*3` over all pages, then the usual blend). Identical hit/MRR to the default on sem 0.993/0.903, uniform 0.957/0.820, course 0.964/0.860, graph 0.993/0.903, multihop 0.983/0.950; nofts 0.800/0.599 against 0.700/0.553. `tests/api/test_hybrid_union.py`. | Off by default and not adopted: no gain on any arm with embeddings, and it adds a full-table cosine scan per query. Not run on a host. |
| Content releases | `built` | Staged. `src/librarian/release/` (build, pull, verify, swap, pin, prune); signed `POST /admin/reload`, `GET /api/release`, `X-Librarian-Release` and the UI's refetch on change; `.github/workflows/content-release.yml`. Tests: `tests/release/test_release.py` (private paths refused at build and at unpack, checksum mismatch, serve-root mismatch, pin and rollback, keep two previous, signature valid/wrong/stale/other body), `app/src/utils/__tests__/api.test.ts`, `useWikiData.test.tsx`. | No CI run. The workflow has never run: no bucket, no real S3/R2 upload, no webhook against a live host. Slides are not packaged. |
| Image releases (GHCR) | `built` | Staged. `ci.yml` `docker` job pushes `sha-<short>` and `main` to GHCR on main only; actions pinned to SHAs; `scripts/check_versions.py` (`tests/core/test_check_versions.py`). | No push has happened yet. |
| Backups | `built` | Staged. `librarian ops backup` (`src/librarian/ops/`), compose `backup` service; `tests/ops/`. | Nothing in a bucket; age and the aws CLI only in the image, never run against real storage. |
| Restore drill | `built` | Staged. `librarian ops restore`, `docs/ops/restore.md`; `tests/ops/`. | Never run. This row cannot reach `drilled` until a restore from a real object is timed. |
| Upgrade | `built` | Staged. `librarian ops upgrade` (refuses without a backup younger than 15 min), `./librarian`, `docs/ops/upgrade.md`; expand-only migration rule in CLAUDE.md; `tests/ops/`. | Never run on a host. |
| Rate limits (per process) | `tested in CI` | `tests/api/test_api_security.py` (chat 429), `tests/api/test_auth.py` (auth routes limited; staged), spend caps in `tests/api/test_accounts.py` (committed). | `AuthLimiter` is in memory per process, so with N workers the limit multiplies. |
| Rate limits (across workers) | `built` | Staged. `accounts/rate_limits.py`, migration 0006, `tests/db/test_rate_limits.py`; fails open behind the per-process guard. | Postgres path not in CI. |
| Alerting | `built` | The checklist in `docs/ops/alerting.md`. Sentry is wired in code and tested (`tests/api/test_observability.py`). | Nothing is configured outside the repo: no probe, no Sentry alert rules, no failed-backup email. |
| ZAP baseline | `built` | Reported by the owner: 0 FAIL and 5 accepted WARN. | No report file or workflow in the repo, so it cannot be re-read or re-run from here. Not run against a host. |
| Eval compare and product metrics (4b) | `built` | `librarian eval compare`, `librarian metrics product` and `check-release` (`src/librarian/metrics/`); `tests/metrics/test_reports.py` against a temp log and database. Run-books in `docs/ops/alerting.md` item 5. | Never run against real traffic: no `release`, user or cost field has been read from a real `logs/agent.jsonl`, and no variant has reached n = 30. No scheduler runs `check-release` yet. |
| Chat-answer eval (4b) | `built` | `evals/run_chat_eval.py`, `evals/golden_chat.json` (40 questions), `make eval-chat` and `make eval-chat-dry`; `tests/evals/test_chat_eval.py` with a fake client. WARN-only. | Never run with the real model or judge, so no baseline and no measured cost (the dry-run figure is an estimate from token budgets). `golden_chat.json` is unreviewed (`"reviewed": false`): questions, expected pages and rubric lines were written by a model. |
| Reader feedback (4b) | `built` | `src/librarian/feedback/`, `api/routers/feedback.py`, migration `0007_feedback.py`; `POST/GET/DELETE /api/feedback`, `GET /api/admin/feedback/summary`; `librarian feedback export` (anonymised, sensitive-term gated, refuses overwrite) and `prune` (scheduled, 180 days). `tests/api/test_feedback.py`, `tests/core/test_feedback_export.py`. | Postgres not run in CI. The export has never run on real data; no feedback has been collected. Notes are matched against a term list and simple patterns, not read by a person. |
| Experiments (4b) | `built` | `src/librarian/experiments.py`, `LIBRARIAN_EXPERIMENTS`; sticky sha256 assignment, admin-only `X-Librarian-Variant` override, variant on agent.jsonl, feedback rows and spans; `ranking=hybrid-union` switches the hybrid path per request. `tests/api/test_feedback.py`. | Assignment only: no experiment has run, and no result has been read. |
| Eval gate | `built` | Staged: six arms (`sem`, `nofts`, `uniform`, `course`, `graph`, `multihop`), 150 entries per set with 10 negatives (report-only), floors re-measured on a tracked-files-only checkout (`evals/baselines/live-*-2026-11-08T12-4*.json`); runs nightly, on PRs touching retrieval or evals, and before every content release. The previous four-arm gate is `tested in CI` (last nightly passed 2026-11-08). | The new floors have not run in CI; run-to-run noise not measured. New questions have had no human review. |
| Private-tree guards | `tested in CI` | `tests/api/test_public_mode.py`, `test_private_exclusion.py`, `test_agent_private_exclusion.py`, `tests/core/test_course_private.py`, `test_deploy_content.py`, leak checks in `test_wiki_telemetry.py`. Pre-commit hook `private-not-tracked` (`wiki check --tracked-only`). | The pre-commit hook is local, not a CI job. The release builder refuses private paths at build and at unpack (`tests/release/`, staged). |

## How to update this page

1. Change a row's level only when you can name the evidence: a test file, a workflow job and a
   green run, or for the top two levels, the date and host.
2. Staged or unpushed work stays `built` until a CI run has covered it.
3. When a host goes live, add a `Host` line here and move rows to `checked on a host` one at a
   time, with the date and the command or URL checked.
4. Record the restore drill (date, object, timings) in `docs/ops/restore.md`, then set the
   Restore drill row to `drilled`.
