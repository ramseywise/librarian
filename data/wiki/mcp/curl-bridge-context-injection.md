---
title: Curl-Bridge Context Injection
tags: [mcp, infra, pattern]
summary: A reverse proxy can give any shell-capable agent access to a memory service without MCP, plugins or hooks — inject text telling the model to curl allowlisted read-only bridge endpoints with its existing Bash tool, and overwrite identity fields server-side so the model cannot forge them.
updated: 2026-10-16
sources:
  - data/raw/claude-docs/guacamayo/docs/research/2026-08-20_tencentdb-memory_parity.md
---

# Curl-Bridge Context Injection

The architecturally interesting piece of a reference team-memory system, surfaced in
guacamayo's parity review against librarian.

## Mechanism

- The agent's model base URL is pointed at a **reverse proxy**; tenancy rides in the URL
  path (`/<client>/<spaceId>`).
- The proxy does **not** inject tool definitions. It injects *prompt text instructing the
  model to `curl` the proxy's own bridge endpoints* using the Bash tool the agent already
  has.
- The bridge is a **read-only allowlist** of endpoints.
- **Identity is overwritten server-side** (`team_id`, `user_id`, `agent_id`) on every bridge
  call, so whatever the model puts in the request, it cannot impersonate another tenant.

Because the only capability required is "can run a shell command", it works with **any
shell-capable agent** and needs no MCP server, no plugin, and no hook installation.
Framework-specific plugins exist but are optional adapters that bypass the proxy and lose
the team layer (session init, skill bridge, knowledge injection, ACL-checked borrowing).

## When to use it, and when not

- **Use** when you must serve heterogeneous agent runtimes you do not control, or a runtime
  with no tool-registration surface.
- **Don't** when the client has native integration points. The review's verdict for
  Claude Code: take the *pattern* as a known option but don't adopt the proxy — Claude Code
  has hooks, skills and MCP natively.
- The security property rests entirely on the proxy: the model-authored curl is untrusted
  input, so the allowlist and the identity overwrite are the controls, not the prompt.

## Related finding from the same review

The opposite failure was found at home: librarian's MCP server was **documented** in
guacamayo's CLAUDE.md, README and AGENTS.md and invoked by two skills, yet **configured
nowhere** (no `mcpServers` block, no `.mcp.json`). The skills' fallback silently degraded
to the human narrating context. "Do not assume this is only a config paste" — call sites
and tool-permission allowlists also need checking once the server resolves.

## See Also
- [[MCP Server Security Patterns]] — alternative-to (tool-registration surface with its own auth controls)
- [[Silence Reads as Clean]] — extends (documented-but-unconfigured MCP that degrades silently)
- [[Tool Design as Context Engineering]] — extends
