---
imported_hash: 34c5bde073dc784e
title: SECURITY.md
summary: This file defines the security and safety rules that agents must not guess at.
order: 38
kind: reading
section: Templates / Openai repo template / Docs
source: learn-ai-engineering/ai-engineering/03-harness-engineering/templates/openai-repo-template/docs/SECURITY.md
---

# SECURITY.md

This file defines the security and safety rules that agents must not guess at.

## Secrets And Credentials

- Never hard-code secrets in source or docs.
- Document approved secret-loading paths here.
- Redact tokens, API keys, and personal data from logs and screenshots.

## Untrusted Input

- Treat external content as untrusted until validated.
- Record allowed fetch or execution boundaries here.
- If prompt injection or command injection risk exists, document the guardrail.

## External Actions

- List which actions require explicit approval.
- Record any production or destructive commands that agents must not run by default.
- Prefer sandbox-safe workflows for debugging and verification.

## Dependency And Review Rules

- New dependencies need justification in the active plan.
- Security-sensitive changes require explicit verification steps.
- Repeated security review comments should become checks, not tribal knowledge.
