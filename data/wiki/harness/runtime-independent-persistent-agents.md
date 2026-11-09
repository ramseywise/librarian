---
title: Runtime-Independent Persistent Agents (RIPA)
tags: [harness, agents, concept]
summary: "RIPA defines a persistent agent as an identity, memory and executable-body triple that outlives the model, harness and server running it, and moves between them through a six-phase fenced migration; evidence is a handful of case studies on one agent lineage (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-zhao-2026-runtime-independent-persistent-agents.md
---

# Runtime-Independent Persistent Agents (RIPA)

The paper argues that "agent = model + harness" answers only what generates behaviour right now, and not what must stay continuous over time. Its alternative is a state triple: **identity** (the identity record), **memory** (durable private recall and the workflow state needed for continuity) and **body** (everything versioned: code, prompts, tools, policies, tests, and the contracts with providers). Model, harness and host are a swappable layer underneath, and chats, APIs and email are swappable surfaces on top. Queue state and task identity live in the persistent substrate, not in a harness transcript, and a transcript counts as raw evidence rather than memory. After a move the new harness session is fresh, and context is rebuilt from the durable records.

## Continuity as lineage

Continuity is defined as unbroken lineage rather than identical bytes. A migration that only changes the runtime leaves the identity version and body revision untouched, and memory can grow but not rewrite its past. Copying state does not copy authority: if one directory lands on two servers, both claim one ID, so a single continuation needs a lease, a fencing epoch or a declared multi-embodiment policy. Seven lifecycle operations are named. Restart and resume come first, then migrate, evolve and identity update, and finally replicate and a fork that descends from the original. Resume and restart keep continuity, migrate swaps the runtime, evolve changes the body, and the last two change who holds authority or identity.

## Migration protocol

Six phases: quiesce and fence, checkpoint, validate, bind, rehydrate, verify and resume, governed by six invariants (I1 to I6). The source stays fenced after the target activates, even if it reconnects. The authors describe this as a single governed promotion point and say it is not distributed consensus. Before any external effect, the intent is written down together with an epoch number for fencing and a key that makes retries safe; where a provider offers neither a way to reconcile nor idempotent delivery, the system refuses to proceed. Providers declare a kind (chat, runtime, VCS, review or service), a contract version and capabilities, and a swap that drops a capability must fail closed rather than pick another provider.

## Evidence

All of it is self-reported and comes from one evolving agent lineage.

- An existing agent with populated long-term memory was moved from a laptop to a desktop and back, then had its coding harness and model swapped, then its chat channel. The identity and memory hashes, the body revision and 22 earlier task IDs came through unchanged, and the checkpoints verified 76 and 77 portable files. Model and harness changed together in that case.
- A two-stage synthetic task paused after stage one, wrote out nine portable files and then continued under the original task ID; both stages totalled 28, grand total 56, and the exported source refused to restart.
- In a supervised study across two runtimes, 5 of 5 round trips and 5 of 5 same-runtime controls passed on the first attempt, with simple integer arithmetic as the task. Seven migrating source roots and seven return-export roots rejected post-export execution.
- A planned interruption killed the first worker before it replied; a replacement worker holding a new nonce finished the task a single time, and the earlier nonce was refused.
- Implementation tests: 963 passing in each of two snapshots, with no failures or skips.

## Limits

- The authors say the results do not show that behaviour stays equivalent, that any task can move, that external effects happen exactly once in general, or that it runs unattended reliably. Statistical reliability, operator effort, cost and model quality are not estimated.
- One body lineage, tool-free simple tasks, non-independent sessions, unattested backend models and withheld private data. The authors own both the system and the benchmark used, with no external replication.
- Not crash-atomic: a hard kill bypasses rollback, and no recovery from every half-written state is demonstrated. The guard against a second owner works locally only; remote services are not consulted, and it offers no defence against a detached copy holding its own credentials. Cursor translation between chat channels is not demonstrated; multi-embodiment and merging divergent memory are open.
- The extraction notes that the paper is about identity and migration and does not cover the tool-use loop.

## See Also
- [[Harness Anatomy]] — prerequisite-for
- [[Fencing Tokens and Zombie Writers]] — prerequisite-for (fencing epoch idea)
- [[Memory Architecture]] — related (what persists across runs)
- [[Idempotent Retries and Request IDs]] — related (idempotency keys for external effects)
