# Backlog

Work to do later. Written 2026-11-19, after the refactor of 2026-11-17. Each item says what it is, why it is not done, and what finishes it.
Nothing here has been checked on a host; see `docs/status.md` for what has.

## 1. Before committing the refactor

The working tree holds the refactor uncommitted, on `main`. Branch first.

- [ ] Pin migration `0009_intake.py` in `tests/db/migrations.sha256`.
- [ ] Run `terraform init` once in `infra/` and `infra/bootstrap/`, and commit both `.terraform.lock.hcl` files.
- [ ] Browser pass, which no test covers: error notices, the error boundary, nav drawer, atlas, wiki map, glossary tooltip.
- [ ] `tests/api/test_course_search.py::test_acceptance_wiki_scoped_results_match_a_wiki_only_index` failed once in a full run on 2026-11-17 and passed alone and in the next full run. Find the test it depends on, or show it is unrelated to the refactor.
- [ ] `SANYI.md` and one plan file still name the deleted `src/librarian/mcp/codemap_tools.py`. `SANYI.md` is hand-maintained, so this edit is yours.
- [ ] Decide: keep or revert the exact version pins in `app/package.json` (added beyond the brief).

## 2. First deployment to a host

`infra/` validates under Terraform 1.10.5 and has never been planned or applied. `infra/README.md` lists everything unverified.

- [ ] Measure memory and disk: run the full Compose stack locally and read `docker stats`. `t3.large` and 40 GiB are guesses.
- [ ] Look up the cost of the chosen instance in the chosen region.
- [ ] Decide Terraform or OpenTofu. Only Terraform was run.
- [ ] Decide how the first content load reaches a host with no SSH. Recommended: the content-release path (`src/librarian/release/`, `content-release.yml`). The alternative is sshd tunnelled through SSM, which adds a key.
- [ ] Bootstrap the state bucket, then `plan` and read it (13 resources to add, or 12 without DNS), then `apply`.
- [ ] Confirm the amd64 image builds in CI. Only arm64 was built locally.
- [ ] Follow `docs/ops/deploy.md` on the host, then record the result in `docs/status.md` with the date and host.
- [ ] Run and time one restore drill (`docs/ops/restore.md`), and record it.
- [ ] Confirm Caddy obtains a certificate through the Elastic IP.

## 3. Security and operations follow-ups

- [ ] Throttle bad signatures on the release endpoint (review item S8). Replay protection is done; throttling is not.
- [ ] Decide whether 90 days is the right agent-log retention (`LIBRARIAN_AGENT_LOG_RETENTION_DAYS`).
- [ ] Decide whether the seven codemap tools should proxy in remote MCP mode. They are local-only today.
- [ ] Fix the one known pyright error at `src/librarian/agent/loop.py:530`.
- [ ] Add a route-enumeration test over `app.routes` that fails on a route with no auth dependency and no public-list entry. kiez has the equivalent; librarian does not.

## 4. Frontend follow-ups

- [ ] Parse the two remaining unchecked `JSON.parse(...) as` casts with a schema: `useDrillTimer.ts:53`, `useCourseProgress.ts:70`.
- [ ] Review the 12 inline eslint-disable comments added with the accessibility lint; fix or justify each.
- [ ] The axe test covers four components in jsdom with colour contrast off. Add a rendered check on the main routes if a browser test suite is added.
- [ ] Manual accessibility pass: keyboard-only walk and a screen reader on the main flow. Not done.
- [ ] `WikiGraph.tsx` (919 lines) and `Atlas.tsx` (846 lines) were split only where the move was pure. A further split changes behaviour and needs a decision.

## 5. Experiments and housekeeping

- [ ] LB11: an endorsed / deprecated mark on wiki pages as a retrieval signal. Needs you to say which pages count as endorsed, and must clear all six `make eval-gate` arms before adoption.
- [ ] LO5: `~/workspace/cartographer` is a drifted, uncommitted copy of `tools/cartographer`. Decide which survives.
- [ ] LO6: per-slot ports for parallel worktrees. Only if worktrees collide on ports.

## 6. Open from the 2026-11-19 design review

What the review proposed and was not done. Done items are in `docs/status.md` and frame 12 of `docs/librarian.excalidraw`; the target is `docs/librarian-to-be.excalidraw`.

- [ ] P3: run `make eval-grounding` once (billed, about $0.71, $6.86 ceiling) for the first baseline of the 0.5 support threshold, which was never tuned.
- [ ] P2 abstain floor. Top scores of answered and unanswerable questions overlap, so any fixed floor refuses good answers or passes bad ones. Waits for enough P13 golden cases to pick it from; must clear all six `make eval-gate` arms.
- [ ] P7 answer sampler. Nothing to sample until a host has traffic: waits for section 2.
- [ ] P11 tool contract: write down once what chat, MCP and the HTTP tools each promise (inputs, errors, limits). Needs a decision; no outside caller yet.
- [ ] P8 Alertmanager and a scheduled restore drill. Alert rules go nowhere until one is configured; part of section 2.

Closed without change: P4 shared burst window (daily caps are already shared in Postgres).
