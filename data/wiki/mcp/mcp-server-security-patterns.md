---
title: MCP Server Security Patterns
tags: [mcp, infra, pattern]
summary: Security patterns for MCP servers — read-only invariant, sandbox isolation, secrets handling, and what to never expose over MCP.
updated: 2026-07-06
sources:
  - raw/sessions/2026-04-24T1048.md
  - raw/sessions/claude-2026-04-24-qq-do-i-need-to-push-playground-infrastr-108c3f61.md
---

# MCP Server Security Patterns

## The Read-Only Invariant

A knowledge-serving MCP server (e.g. a wiki, KB, or documentation server) **must never expose write tools**. The Librarian MCP server enforces this:

- All five tools (`search_wiki`, `read_page`, `list_domain`, `list_pages`, `get_domain_briefing`) are read-only
- No write, append, or delete tool is exposed
- The invariant is enforced at the tool-definition layer, not by a prompt instruction — a prompt instruction is soft (BY-4 in SANYI terms)

This is a [[SANYI Change-Contract System]] Buyi invariant: violating it has trust/security consequences and must never be made bypassable via config or env var.

## Sandbox vs Local Exposure

When running a MCP server locally (bound to `localhost`), secrets are only accessible to processes on the same machine. Pushing the server to a public-accessible environment (cloud, GitHub Codespaces, etc.) changes the attack surface:

| Context | Risk |
|---|---|
| `localhost` only | Low — only processes on the machine can reach it |
| Docker, no external port | Low — container-internal only |
| Cloud deployment, public port | High — treat as a public API; add auth |
| GitHub Codespaces / tunnel | High — URL is externally routable |

**Pattern:** keep MCP servers on `localhost` during development. Add authentication (API key header, OAuth) before any external exposure.

## Secrets in MCP Servers

Never embed secrets in the MCP server binary or config that gets checked in. Secrets the server needs:

- Load from `.env` (gitignored)
- Never log them (structured logging should never log auth headers or API keys)
- Never return them in tool responses — even in error messages

The Librarian MCP server reads only the `wiki/` directory (plain markdown) and requires no API keys. This is the preferred design: **make the MCP server stateless and secret-free by design**, pulling secrets only if absolutely necessary for a specific tool.

## What Not to Expose

Even in a read-only server, scope matters. If the wiki contains sensitive project pages (e.g. client names, internal architecture), those pages should live in `wiki/private/` (gitignored) and the server should optionally exclude that directory:

```python
# server.py — scoped WIKI_DIR excludes private by default
WIKI_DIR = Path("wiki")
PRIVATE_DIR = WIKI_DIR / "private"

pages = [p for p in WIKI_DIR.rglob("*.md")
         if not p.name.startswith("_")
         and not str(p).startswith(str(PRIVATE_DIR))]
```

Alternatively: run two MCP server instances — one public (excludes `wiki/private/`), one local-only (includes everything). Configure which clients get which.

## Sensitive Data Audit Pattern

Before making any repo or MCP server public, run a sensitivity audit:
1. Check for API keys, tokens, passwords in all files (not just `.env`)
2. Scan markdown files for company-specific names, client data, internal URLs
3. Verify `.gitignore` excludes all private directories
4. Check JSONL session files for conversation content (may contain sensitive context)

Typical sensitive finds in AI engineering repos:
- API keys hardcoded in test scripts
- Notion/Linear dumps in `raw/` containing internal project names
- Session JSONL files containing prompt conversations with client data

## See Also
- [[MCP Protocol]]
- [[SANYI Change-Contract System]]
- [[Input Guardrails Pipeline]]
- [[Agent Quality Review Checklist]] — alternative-to (review-time vs runtime enforcement)
