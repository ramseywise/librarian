---
title: Empty-String Env Override Defeats Nullish Coalescing
tags: [patterns, infra, pattern]
summary: "Clearing an env var for one run with `VAR= cmd` makes it present-but-empty, which a truthy check treats as unset but `process.env.VAR ?? fallback` does not. A documented escape hatch for bypassing an experiment override silently produced `no_api_key` and an empty model name, so env fallbacks should use `||` or an explicit empty check, and one-off bypasses should delete the key."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-06-dis196-stale-needs-review.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-06-dis196-stale-needs-review.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-06-dis196-stale-needs-review.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-06-dis196-stale-needs-review.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-06-dis196-stale-needs-review.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-06-dis196-stale-needs-review.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-06-dis196-stale-needs-review.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-14-pr269-unreviewed.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-14-pr269-unreviewed.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-14-pr269-unreviewed.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-14-pr269-unreviewed.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-14-pr269-unreviewed.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-14-pr269-unreviewed.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-14-pr269-unreviewed.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-14-dis196-stale-needs-review.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-14-dis196-stale-needs-review.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-14-dis196-stale-needs-review.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-14-dis196-stale-needs-review.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-14-dis196-stale-needs-review.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-14-dis196-stale-needs-review.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-14-dis196-stale-needs-review.md
---

# Empty-String Env Override Defeats Nullish Coalescing

Found during a data-remediation run in akira. Enrichment had an experiment-scoped override
(`ENRICHMENT_API_KEY` / `ENRICHMENT_BASE_URL` / `ENRICHMENT_MODEL`) that pointed model calls
at a local cheaper-model endpoint. It was set in `.env.local`. The remediation had to run
on the production model path instead, so the plan documented the obvious escape hatch:

```
ENRICHMENT_API_KEY= ENRICHMENT_BASE_URL= ENRICHMENT_MODEL= npx tsx script.ts
```

dotenv's default `override: false` leaves any variable already in `process.env` alone,
**even an empty one**. So the shell-level empty string does win over the file. That part
was correct. A second, unrelated workstream's plan assumed the same escape hatch worked.

## Why it still failed

An empty string is *present but falsy*. Two kinds of check treat it differently:

| Check | `VAR=''` behaves as |
|---|---|
| `if (env.VAR)` | unset, so the fallback is used |
| `env.VAR ?? fallback` | **set**, and the empty string is used |

`??` substitutes only for `null` / `undefined`. Two production call sites used it:

1. `Boolean(env.ENRICHMENT_API_KEY ?? env.OPENAI_API_KEY)` evaluated to `Boolean('')`,
   which is false. Every row returned `no_api_key` immediately, with no network attempt.
2. `model: env.ENRICHMENT_MODEL ?? DEFAULT_MODEL` resolved to `model: ""`. That would
   have broken the call on its own even if the first bug were fixed.

The credential resolver's own key/URL branch used a truthy `if`, so it fell through
correctly. The result was one function honouring the bypass and two others ignoring it,
inside the same request.

## The earlier failure looked different

The first attempt days before had failed with "cannot connect", because the override's
local endpoint was unreachable. That run was diagnosed as an environment leak, and the
empty-string bypass was written up as the fix. The second run then failed with a
**different** error (`no_api_key`). It was root-caused with a standalone probe that
printed the resolved `{apiKey: SET/unset, baseURL, model}` before any paid call was spent,
not by retrying.

## Rules

- **For env fallbacks, use `||` or an explicit `=== undefined || === ''` check**, not `??`.
  In env-var semantics, empty almost always means "unset".
- **Be consistent within one resolution path.** A mix of truthy and nullish checks over the
  same variables gives a bypass that half works.
- **To bypass an override in-process, `delete process.env.X`** after dotenv loads, rather
  than setting it to `''`. Then set any required value (the model name) explicitly instead
  of relying on a fallback.
- **Probe the resolved configuration before spending.** Print what the resolver returns,
  with secrets reduced to SET/unset, before the first real model call.
- **A documented escape hatch is a claim.** Two plans cited this one, and neither had run
  it end to end.

## Recurrence in review

A later unreviewed-fixes audit in the same repo listed the fix for this defect ("empty
`ENRICHMENT_*` vars treated as set") among the changes no reviewer had seen. The run that
first hit it worked around the bug with a scratch script rather than the documented
command, so the defect stayed in the code until it was fixed separately. A workaround that
works keeps the bug alive.

## See Also
- [[Settings Field Names Are a Shared Env Namespace]] — related (another silent env-binding collision)
- [[Silent Failure Catalogue]] — instance-of (a default-filled absence that reads as configured)
- [[Sanitize Never Fails, Validate Never Mutates]] — related (the remediation run where this surfaced)
