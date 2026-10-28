---
title: A Secret Scanner Must Never Echo Its Match
tags: [infra, pattern]
summary: "A gate that scans a client bundle for a leaked privileged key must report only file:line and a kind label, never the matched text. A violation message that prints the token into CI logs leaks it a second time. A 'self-defeat' regression test pins this. Detect by decoding the JWT role claim rather than its shape, so the deliberately public anon key cannot false-positive. Scan only the client output tree, behind a scan floor."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-03-dis36-production-smoke.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-03-dis36-production-smoke.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-03-dis36-production-smoke.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-03-dis36-production-smoke.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-03-dis36-production-smoke.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-03-dis36-production-smoke.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-03-dis36-production-smoke.md
---

# A Secret Scanner Must Never Echo Its Match

From planning a production-smoke checklist for a Next.js + Supabase product (repo akira).
The one check that needed no deployment was "no service-role key in any client bundle".
It was designed as a `make gate` script that runs right after `build`.

## Design decisions

- **Report location, never content.** The detector returns `{ line, kind }` and nothing
  else. A violation reads like `file:line — service-role JWT (role claim) found in a CLIENT
  bundle`. A scanner that prints its match copies the secret into every CI log that
  records the failure, which is worse than having no check. The plan named the
  **self-defeat regression test** its single highest-value test. That test builds a
  fixture with a real-shaped service-role JWT, captures stderr and asserts the token
  substring never appears. "Must not be dropped under time pressure."
- **Decode the claim, don't match the shape.** Every legacy Supabase API key is an HS256
  JWT, and the anon key is *meant* to ship in the bundle. A plain `eyJ…` regex
  false-positives on every build. Instead, the script finds JWT-shaped candidates, decodes
  the payload and flags only `role === 'service_role'`. That cannot fire on the anon key.
- **Defence in depth on names.** A literal grep for the env var names
  (`SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_SECRET_KEY`) catches a misconfigured alias.
  The known blind spot is written down instead of guessed at: a newer non-JWT secret
  format under a third name. No literal prefix was encoded because none existed in the
  tree to verify against.
- **Scan the right tree.** Scan only `.next/static` (the client output, 55 files),
  never `.next/server`, which reads the key legitimately (1,009 files).
- **Floor and ordering.** A `MIN_FILES` floor fails the check when the scan collapses
  (see [[Scan-Floor Guard Against Silent No-Op Checks]]). If the gate is reordered so the
  scan runs before `build`, it fails loudly with "run make build first" instead of
  passing on an empty directory. The floor is measured once, not maintained, and catches
  total collapse rather than partial loss. That was accepted, because a counter that must
  be bumped on every build change is one people route around.
- **Testable shape.** Export the detection predicate, return `{ exitCode }` instead of
  calling `process.exit`, and guard side effects behind an entry-point check, following
  the repo's existing gate scripts.

## Split the issue at the deployment boundary

The issue priced all five smoke checks as one small task, but no deployment existed. The
plan shipped the deployment-independent quarter, recorded what was already true (CI gates
`main`), and kept the rest as a dated, non-fabricated checklist that becomes the spec for
a later `smoke-prod` target. Building HTTP probes against an origin that had never
existed would have been dead code nobody could demonstrate. Other points from the split:

- An open question that is out of scope *by construction of what the plan builds* does
  not hold the plan below READY. A precondition that blocks one of its own steps does.
- Don't average a size across halves when one half cannot be estimated yet. Say so.
- A presence check for a secret on the live origin must be presence-only, never the
  value, and needs a route without side effects (voting on a real poll writes data).

The plan was later superseded before it was executed. The design reasoning above is what
carried forward.

## See Also
- [[Scan-Floor Guard Against Silent No-Op Checks]] — extends (the same walk/detect/floor gate shape, applied to secrets)
- [[Written-but-Inert RLS Policies]] — related (the import-graph gate keeping the admin client out of client components)
- [[Agent Credential Ceiling]] — related (keep privileged credentials out of reach rather than detect them later)
- [[Silent Failure Catalogue]] — related
