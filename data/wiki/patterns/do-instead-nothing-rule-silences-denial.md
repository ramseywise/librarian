---
title: Do-Instead-Nothing Rule Silences a Loud Denial
tags: [patterns, infra, pattern]
summary: "A Postgres `do instead nothing` rule added to 'harden' an append-only table converts a loud permission-denied error into a silent 0-row success, because rule rewriting runs before the permission check — and grep-the-SQL tests plus `has_table_privilege` probes stay green either way, so the guarantee must be verified behaviourally on a local database."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/reviews/2026-09-23-dis372-dis374-evidence-stage-data-platform.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-23-dis372-dis374-evidence-stage-data-platform.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-23-dis372-dis374-evidence-stage-data-platform.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-23-dis372-dis374-evidence-stage-data-platform.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-23-dis372-dis374-evidence-stage-data-platform.md
---

# Do-Instead-Nothing Rule Silences a Loud Denial

## The mechanism

An append-only table (a governance decision ledger, in the akira source) was protected two ways
at once: the UPDATE/DELETE grants were revoked, **and** `create rule ... do instead nothing`
rules were added for UPDATE and DELETE. The migration's comment justified the rules by claiming
that a revoked grant yields "a silent 0 rows with no error", which the rule would fix.

The claim is backwards. Postgres applies **rule rewriting before the executor's permission
check**. A `do instead nothing` rule discards the statement before the revoked grant is ever
consulted, so the client gets success with 0 rows and `{ error: null }`. A revoked grant on its
own raises a loud `permission denied` (SQLSTATE 42501). The rule is what *creates* the silence it
was written to prevent.

## Why nothing could catch it

- The unit test was `readFileSync` of the migration plus regex greps for the rule text. It would
  pass if the rule were a no-op or had the opposite effect. This is
  [[Tested Decision, Untested Expression]] applied to SQL: the text is tested, the behaviour is not.
- The operator probe was `has_table_privilege(..., 'UPDATE' | 'DELETE')`, which reads **grants,
  not rules**. It returns false whether or not a rule intercepts the write.
- The repo bans destructive mutate-and-rollback probes against production, so the one check that
  would show the behaviour was structurally unavailable there.

The failure scenario: a later migration grants UPDATE, or an admin tool calls `.update()`. The
write silently does nothing, the caller sees no error, and every available check stays green. A
rule *is* an interception, so "verify a constraint in a way that cannot be intercepted" applies
to it directly.

## The rule

1. **Pick one enforcement mechanism and know its failure signal.** Prefer the revoked grant: it
   is loud, and `has_table_privilege` genuinely verifies it. If rules are kept, state plainly in
   the migration that they trade the error for silence.
2. **Comments about database semantics are claims; check them.** The ordering of rewrite,
   permission check and trigger is not intuitive, and a wrong comment survives review because it
   sounds like hardening.
3. **Verify behaviourally on a local database** (a disposable `db-start` instance), where a
   destructive probe is legitimate: attempt the UPDATE/DELETE as the client role and assert the
   error code, not the absence of rows. Distinguish an error from zero rows as
   [[Make Each RLS Policy Individually Falsifiable]] does for WITH CHECK versus USING.

The finding came from the review adjudicator combining three candidates (the comment, the grep
test, the privilege probe) that no single per-dimension reporter had connected; see
[[Cross-Dimensional Review Adjudicator]].

## See Also
- [[Make Each RLS Policy Individually Falsifiable]] — extends (error versus zero-rows distinction, applied to rules)
- [[Silent Failure Catalogue]] — instance-of
- [[Tested Decision, Untested Expression]] — instance-of (SQL text tested, behaviour untested)
- [[Silence Reads as Clean]] — extends
- [[Cross-Dimensional Review Adjudicator]] — related (how the finding surfaced)
