---
title: "Per-Column PII Verdicts: Keep, Remove, Move, Change"
tags: [infra, pattern]
summary: Take PII out of an app schema by classifying every column (Yes = names a person, Maybe = free text, ID = user uuid only, No) and giving each one of four verdicts — keep, remove, move to the system of record, or change its shape — with emails replaced by actor ids plus a staff-only view, and free text kept under a retention rule.
updated: 2026-10-30
sources:
  - data/raw/repos/nonprofit-success-ai/.claude--docs--supabase-schema-decisions.md
  - data/raw/repos/nonprofit-success-ai/CLAUDE.md
---

# Per-Column PII Verdicts: Keep, Remove, Move, Change

From a client partner-portal build (Postgres with row-level security, five agents). The
rule was **no PII in the app schema**: people and organisations live in the CRM, and app
tables hold only `crm_*_id` references. Getting there was done one column at a time,
using a single table.

## The classification

| PII class | Meaning |
|---|---|
| **Yes** | names a person (email, contact name, display name) |
| **Maybe** | free text that might contain a person (notes, descriptions, message bodies) |
| **ID** | a user uuid only |
| **No** | none |

## The four verdicts

- **Remove** when the value can be read from somewhere authoritative at request time. A
  user's email and display name come from the auth session. A `reviewed_by_email` or
  `created_by_email` column becomes the existing actor id, plus a **staff-only view that
  resolves ids to emails** for the few screens that need them.
- **Move** when the app needs the data briefly but it belongs elsewhere. A business's
  address moves to the CRM account record. Intake contact fields move to a staff-only
  contact table that is **purged after the CRM sync**.
- **Change** when the column's purpose survives but its content should not. A "point of
  contact" answer stores the role, not the name. Membership roles are narrowed to an
  enum.
- **Keep** everything classified No or ID, and the **Maybe** free text the agents need as
  input (mission, problem description, notes, drafts), with a retention rule attached.
  Audit and event `detail` columns are kept under a stricter rule: ids and enums only.

Telemetry tables (agent runs, tool calls, model budgets) are No by design: they store no
prompts or outputs. Auth's own user table stays as it is, because the auth provider
requires it.

## Enforcement around the schema

- The only door to the CRM is one server module. The intake's contact goes there, and the
  app row keeps the returned ids.
- The browser never writes the intake table. The public form posts to a server route
  (authenticated by an anonymous sign-in), and the route files the intake through one
  database function.
- Server logs come from a closed field set, and the logger is never passed an error
  object, prompt or row, because those can carry intake data.

## Left open

The decision record lists three items still to decide: the retention window, how
`projects` relates to engagements, and whether intake contacts should go straight to the
CRM and skip the app table entirely.

## See Also
- [[Data Clusters by Writer and Trust]] — extends (group by writer first; this splits by what a column can reveal)
- [[Server-Derived Autonomy Tier]] (same build's server-side enforcement stance)
