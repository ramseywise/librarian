---
title: A Check That Answers a Proxy Question
tags: [llm, infra, pattern]
summary: "A capability precheck answered 'is there a well-formed agent file at this path?' while its caller needed 'will a dispatch naming this agent resolve in this session?' — the two coincide only when the session root equals the repo root — so it reported resolved and the dispatch then failed; when the real question cannot be probed, make the check emit the scope it actually answered (absolute root, cwd) so the caller can see the gap."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/galactus/docs/plans/2026-08-20-resolve-capability-registry.md
  - data/raw/repos/galactus/.claude--docs--plans--2026-08-20-resolve-capability-registry.md
  - data/raw/claude-docs/galactus/docs/plans/2026-08-16-segmentation-parity.md
  - data/raw/repos/galactus/.claude--docs--plans--2026-08-16-segmentation-parity.md
---

# A Check That Answers a Proxy Question

From a review harness (galactus) whose skills dispatch a repo-local subagent (a fog advisor)
after a `resolve-capability` precheck.

## The incident

The precheck reported `resolved: true` when three things held. The agent file existed at
`repo_root / agent_path`, it had valid YAML front matter, and its `name:` matched the
filename stem. A plan's epistemic pass then ran the check, got exit 0, and dispatched. The
dispatch failed with "Agent type not found". The session was rooted at the parent workspace
directory. The host loads `.claude/agents/` from the **session root**, so it never saw the
repo-local agent. The check resolved the path against the cwd, which was the repo, so it
passed.

The function's own docstring named this exact failure. The guard existed to catch it and
reproduced it instead. The plan was recorded with an UNTESTED epistemic status rather than
quietly running a substitute agent ("a substituted dispatch is a failed dispatch").

## The shape of the bug

| The check answered | The caller needed |
|---|---|
| Is there a well-formed file here? | Will a dispatch naming this agent resolve in *this* session? |

These are the same question only when session root equals repo root. Working from a parent
directory was the normal pattern, not an edge case. The CLI defaulted `--repo-root` to `.`,
and the skills called it without the flag, so they relied on the cwd being the repo root.

## Why the obvious fixes were rejected

- **Probe the registry directly.** The agent registry is session state held by the host
  process. A `uv run` subprocess has no API to it, and nothing about it is written to disk.
  That route was closed.
- **Try a test dispatch.** It has side effects and cost, so it is unsuitable as a
  precondition.
- **Document the constraint.** It was already documented, in the docstring, and was still
  violated. The repo's rule is that *a rule you rely on belongs in a hook, not in prose*.

## The chosen fix: make the answer's scope visible

The resolution logic was left alone, because it answers the file question correctly. What
changed is that the payload now reports **what it was answered against**:

- `repo_root_abs`, the resolved absolute path that was checked, on success and failure
  alike.
- `cwd`, so a mismatch between the two shows up as the signal.
- The skills pass `--repo-root` explicitly and treat a `repo_root_abs` that is not the
  expected checkout as an invalid resolution.

A negative smoke test checks the other side: run from `/tmp`, the check exits 1, and the
payload confirms that `/tmp` was what got checked.

General rule: when a check can only answer a proxy for the real question, it must say
which question it answered. A bare `true` lets the caller read the proxy as the real thing.

## See Also
- [[A Check Must Say Why It Could Not Check]] — extends (the failure-side twin: say why you could not check, and here also what you checked)
- [[Rationale-Blind Worst-Case Review]] — prerequisite-for (the advisor this precheck guards)
- [[Vendored Hooks Resolve to the Global Copy]] — extends (another session-root vs repo-root resolution trap)
- [[Capability vs Phase Skills]] — extends
