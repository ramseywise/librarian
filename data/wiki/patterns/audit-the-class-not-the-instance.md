---
title: Audit the Class, Not the Instance
tags: [patterns, infra, pattern]
summary: "When a bug has a nameable shape (wrong client for the authorization model), sweep every surface behind the same boundary before fixing — an issue naming one silently-empty admin queue turned up a second page with the identical query and a write path whose failure was masked only because the broken read gave it nothing to act on; fix the read alone and the write starts returning 500s."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-03-dis122-admin-review-queue.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-03-dis122-admin-review-queue.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-03-dis122-admin-review-queue.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-03-dis122-admin-review-queue.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-03-dis122-admin-review-queue.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-03-dis122-admin-review-queue.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-03-dis122-admin-review-queue.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-03-dis122-admin-review-queue.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-03-dis122-admin-review-queue.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-03-dis122-admin-review-queue.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-03-dis122-admin-review-queue.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-03-dis122-admin-review-queue.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-03-dis122-admin-review-queue.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-03-dis122-admin-review-queue.md
---

# Audit the Class, Not the Instance

From a Supabase-backed Next.js app (repo akira) where which client factory a file
imports *is* its authorization model (see [[Written-but-Inert RLS Policies]]).

## The named bug

An admin review queue read `events where needs_review = true` through the **anon**
client. The only select policy for anon required `needs_review = false`. The
intersection is empty by construction — not flaky, not data-dependent — and RLS
filtering a row out is a successful zero-row response, so the `if (error)` branch never
fired. ~100 events awaited review; the tab said "everything looks good".

## The audit

The fix plan re-ran the audit against current `main` instead of trusting the issue body,
and drew the audit boundary by **the access gate**, not the directory: the HTTP Basic-auth
proxy gated both the `(admin)` route group and `/api/admin/*`, so an API route behind it
is exactly as much "the admin surface" as a page. Grepping every client construction in
both found:

| Surface | Client | Status |
|---|---|---|
| Dashboard tab read (the issue's subject) | anon | silently empty |
| Dashboard tab write | admin | already correct |
| **Second, separately linked review page's API GET** | anon | **silently empty — not in the issue or the research** |
| **That page's "mark reviewed" POST** | anon | **would fail visibly — masked** |
| Five other admin surfaces | admin | correct |

The write was the instructive one. `events` had no UPDATE policy for any role but service
role, so the anon update affects zero rows and `.select().single()` errors (a visible
500). It had never been reported because the GET on the same page returned nothing, so
there was never a row to click. **A silent defect upstream was hiding a loud one
downstream.** Fixing only the named read would have converted a quiet bug into a new
production error on the first click.

## Why the client swap is safe

Switching three call sites to the service-role client bypasses RLS — acceptable only
because every one sits behind the proxy's auth gate before any database call runs. The
swap does not widen *who* can see the data; it lets an already-authorized admin see what
the UI already implies they can act on. The argument rests on the gate, so the plan
named it explicitly and left it untouched.

## Tests that tested the bug

The two existing unit test files mocked `createServerClient` — the anon factory. They
passed against the buggy code and would have failed *for the wrong reason* against the
fix. They were updated to mock the client now used, and a real integration test was
added against a local database harness: seed a `needs_review = true` row, call the fixed
GET handler, assert it comes back. Then proven by reverting the fix — the test failed
(the anon server factory needs a request scope a plain test call does not have) — and
restored. A mock cannot tell "calls the right function" from "the right function returns
the right rows under the actual policy". Review noted the POST still lacked a
real-database test: the same gap that let the original bug ship past mocks.

## Scope discipline

The two broken reads were the literal same query in two files — the duplication that let
the bug exist twice. Extracting a shared helper was named as the real fix for the
duplication and **deferred**: folding a structural refactor of two separately-tested
files into a client-swap bugfix enlarges review. Likewise, a sibling review noted the
defence against the *next* anon-read-on-a-no-policy-table is convention and review, not
code; a lint rule is the follow-up.

## See Also
- [[Written-but-Inert RLS Policies]] — extends (the queue bug, here audited as a class)
- [[Mocked-Away Body Hides the Defect]] — related (unit mocks of the wrong client passed against the bug)
- [[Red-Then-Green Proof for Fix-Stage Tests]] — related (regression test proven by reverting the fix)
- [[Silence Reads as Clean]] — instance-of (zero rows read as "queue empty")
- [[The Untested Copy Wins]] — related (the duplicated query)
