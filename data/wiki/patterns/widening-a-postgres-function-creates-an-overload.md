---
title: Widening a Postgres Function Creates an Overload
tags: [infra, pattern]
summary: "`create or replace function` with extra trailing defaulted parameters does not widen the existing function: Postgres identifies a function by name plus full argument-type list, so it creates a second overload alongside the old one; drop the old signature explicitly first and confirm the generated types show one Args shape."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-24-dis384-measurement-loop.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-24-dis384-measurement-loop.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-24-dis384-measurement-loop.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-24-dis384-measurement-loop.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-24-dis384-measurement-loop.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-24-dis384-measurement-loop.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-24-dis384-measurement-loop.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-24-dis384-measurement-loop.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-24-dis384-measurement-loop.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-24-dis384-measurement-loop.md
---

# Widening a Postgres Function Creates an Overload

## The gotcha

An akira migration needed to pass serving context into a poll-creation RPC, so it added two
trailing parameters with defaults (`p_result_set_id uuid default null`,
`p_served_positions jsonb default '{}'`) and used `create or replace function`. The plan
assumed this widened the function in place, since old callers could still omit the new
arguments.

It did not. **Postgres identifies a function by its name plus its full parameter-type
list.** A different list is a different function. `create or replace` created a second,
overloaded function and left the old four-argument one in place. The symptom showed up in
the generated client types: `supabase gen types` emitted **two** members in the RPC's `Args`
union.

## Why it matters

- Callers that pass only the old arguments can resolve to either overload, or fail as
  ambiguous, depending on how the arguments are typed.
- Grants and revokes issued against the new signature do not apply to the old one, so the
  old one keeps whatever exposure it had.
- The old body, without the new behaviour, stays callable indefinitely.

## The fix

```sql
drop function if exists public.create_poll_with_options(text, timestamptz, text, uuid[]);
create or replace function public.create_poll_with_options(..., p_result_set_id uuid default null, ...)
```

Then re-issue grants and revokes against the new signature. Regenerate the types and
confirm there is exactly **one** `Args` shape. The migration header records why the drop is
there, so the next person widening an RPC's parameter list does not rediscover it.

## See Also
- [[Migration Done Means Pushed and Probed]] — related (generated types as the probe that caught it)
- [[Written-but-Inert RLS Policies]] — related (another migration that reads correct and is not)
