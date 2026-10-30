---
title: Provider-Agnostic Model Adapter
tags: [infra, llm, pattern]
summary: "Make model calls provider-portable by separating a canonical request/response contract from per-provider adapters, routing through a registry of logical model names with capability flags, and handling provider-specific parameters at the adapter boundary — drop only cosmetic params, never correctness-critical ones, and log every drop."
updated: 2026-10-30
sources:
  - data/raw/repos/sisyphus/interviewing--rounds--technical-questions--real-tech-question-bank.md
---

# Provider-Agnostic Model Adapter

The design answer to "make this model configuration work with any provider." The source is
an interview answer bank drafted from vendor docs (LiteLLM, LangChain), so treat it as
documented practice rather than a measured result.

## Structure

1. **Canonical contract.** One normalized request/response shape (messages, tools,
   max_tokens, temperature, stop sequences, response format; text/tool-calls, usage, errors
   back) used by every call site. Retries, logging and evals operate only on these types.
2. **Adapter per provider.** Translates the canonical request into the provider's call and
   the response back. Auth, base URLs and parameter-name differences live only here — the
   same contract-vs-implementation split used for tool design
   ([[Tool Design as Harness Surface]]).
3. **Registry of logical names.** Call sites ask for `"fast-writer"` or `"strong-reasoner"`,
   not a vendor model id, so a provider swap is a config change. LiteLLM and LangChain's
   `init_chat_model` implement this at library level.
4. **Config versioned apart from code**, so a model or prompt swap needs no deploy — but pin
   the exact model snapshot behind each logical name; a moving alias is an unrevertable
   deploy (see [[Frozen Version Stamps on Logged Results]]).

## Provider-specific parameters

Most providers reject unknown fields with a 400 rather than ignoring them (e.g. some
reasoning models refuse any non-default `temperature`; penalty params that exist on one API
do not exist on another). In order of preference:

- **Per-provider whitelist** — each adapter declares the canonical fields it accepts and
  maps or drops the rest.
- **Capability flags in the registry** (`supports_temperature`, `supports_streaming`, …) so
  callers branch deliberately instead of catching runtime errors.
- **A `drop_params`-style escape hatch** only for cosmetic parameters. Silently dropping
  something like `max_tokens` changes behaviour; that must fail.
- **Fail loud in dev, degrade in prod** — validate outgoing payloads against the target
  provider's schema in CI; in production prefer drop/clamp over failing the agent turn, but
  log every drop so behaviour drift is visible.

## Testing across many models

With N models from M providers, don't run the full suite on every model per PR: mock the
model for harness unit tests, smoke-test one cheap representative per provider family on
PRs, and run the full matrix nightly, on release candidates, or when the diff touches the
adapter/registry layer — the class of change where provider quirks surface.

## See Also
- [[Tool Design as Harness Surface]] — extends (same contract/implementation separation)
- [[Production Reliability Primitives]] — extends (cross-provider fallback needs a uniform interface)
- [[Frozen Version Stamps on Logged Results]] — prerequisite-for (pinning what a logical name resolves to)
- [[Agent Engineering Question Chains]] — instance-of (the interview question this answers)
