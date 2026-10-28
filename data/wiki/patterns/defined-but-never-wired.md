---
title: Defined but Never Wired
tags: [patterns, llm, pattern]
summary: "When output violates a contract, or retrieval misses what it should find, first check that the contract or capability actually reaches the call site. In one pass, librarian found a full system prompt defined but never passed to the API and a full-text-search extension installed but never queried. Both symptoms had been blamed on the model or the ranker."
updated: 2026-10-17
sources:
  - data/raw/repos/librarian/.claude--docs--plans--2026-07-31-LIB-61-insights-section-contract.md
  - data/raw/repos/librarian/.claude--docs--plans--2026-08-04-staff-review-fixes.md
  - data/raw/repos/nonprofit-success-ai/.claude--docs--research--2026-08-18_dssg-second-brain_codemap-review.md
---

# Defined but Never Wired

The symptom gets blamed on the most expensive, least controllable component, usually the
model. The cause is a missing wire one layer up. The artifact that should fix the problem
already exists in the module, reads as correct, and is never handed to the thing that
needs it.

## Instances (librarian, 2026-07/08)

| Where | What existed | What the call actually used | How it was blamed |
|---|---|---|---|
| Insights report generator | `_SYSTEM_PROMPT`, ~50 lines including the nine pinned section IDs | `call_claude()` passed a hardcoded one-line stub, "You are an expert data analyst…" | The issue assumed the model sometimes ignores the section contract. The output had **zero** section IDs because the contract never reached the model |
| MCP wiki search | DuckDB `fts` extension INSTALLed and LOADed at index build | Search SQL was whole-phrase `lower(content) LIKE '%q%'` | Poor recall. A multi-word query matched only an exact substring, and the "hybrid" rerank only reordered the LIKE survivors |
| Same search's rerank | A blend weight labelled `fts_score` | `1.0 - (i / len(rows))`, which is list position, not relevance | The blend looked principled but did not encode any relevance |
| Path-guard pre-commit hook | `no-hardcoded-paths` | Scoped `files: ^src/`, a directory that does not exist | The hook never fired, and a hardcoded home path shipped right past it |
| guacamayo review driver (2026-08 code review) | `DriverConfig.findings_path` override field, threaded to the single call site as `config.findings_path or _FINDINGS_JSONL_PATH` | The CLI's option block never sets the field, so every real run writes to the hardcoded constant, a path inside the original checkout | Looked like configurable plumbing. The only test that exercised the path monkeypatched the *module constant*, which bypasses the field. The test passing proved nothing about the override |

## The check

Before designing a retry loop, a validator, or a better model for a contract violation,
trace the contract from definition to call:

1. **Find the definition** (prompt constant, extension, index, schema).
2. **Find the call** that should consume it, and read the literal argument. Do not trust
   the variable's name.
3. **Grep for readers of the definition.** A module-level constant with no reader is the
   fingerprint.

In the report-generator case, wiring the prompt was step 1 of the fix. The retry
validator, which checks all nine IDs and retries once with a corrective message naming the
missing ones, became the safety net. It was no longer the fix. The plan also logged a
`section_ids_missing` event so that a week of real drop rates could decide whether the
next step should be a deterministic template with LLM prose in slots.

## Why it hides

- The definition reads as authoritative, so reviewers check its *content* and never its
  *use*.
- The downstream behaviour is partly right. A model given a weak stub still writes a
  plausible report, and LIKE still finds some pages. So the gap looks like a quality
  problem, not a wiring problem.
- An "installed and loaded" log line or a `fts_score` variable name tells the reader the
  capability is in use.

## Tests that patch around the plumbing

When a test overrides a module constant (`monkeypatch.setattr("mod._PATH", tmp)`) instead of
passing the config field the code offers for that override, the test is green and the
field is still unwired. Prefer driving overrides through the public config path. A grep
for the field name that finds only its declaration and its one consumer, with no
producer, is the signature of this pattern.

## See Also
- [[Write-Only Fields and the Reader Map]] — extends (the input-side twin, a value produced and never consumed)
- [[Confidence That Is Not a Probability]] — instance-of (a "score" that is really list position)
- [[Config Reference Rot]] — extends (a guard scoped to a path that no longer exists)
- [[Fallback Mistaken for the Design]] — extends (the degraded path is the only one that ever ran)
- [[Assembled, Not Generated Replies]] — alternative-to (the deterministic-template endpoint a validated contract can graduate to)
- [[Fixture Eval Blind to the Swapped Component]] — extends (an eval that never exercises the live retrieval path cannot see the gap)
- [[Cross-Sweep Finding Fingerprint]] — related (the same review of the guacamayo driver found the digest's missing repo namespace)
