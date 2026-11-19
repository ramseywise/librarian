---
title: LangGraph Platform Data Model and Double-Texting
tags: [frameworks, langgraph, concept]
summary: "The hosted LangGraph runtime's objects (assistant, thread, run, cron job, stateless run), the strategies for a second message arriving mid-run, and the book's deployment and security checklist."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-learning-langchain-ch09-deployment.md
  - data/raw/papers/2026-11-08-learning-langchain-ch08-patterns-to-make-the-most-of-llms.md
---

# LangGraph Platform Data Model and Double-Texting

The book's ch. 9 (*Learning LangChain*) deploys a template retrieval agent with Supabase (pgvector) as the vector store, LangSmith for tracing and LangGraph Platform as the backend API. This page keeps the parts that name mechanisms: the platform's objects and its answers to double texting.

## Objects

| Object | What the book says it is |
|---|---|
| Assistant | A configured instance of a compiled graph, which hides the cognitive architecture behind it and carries its own configuration and metadata |
| Thread | The state built up across a group of runs; its state at a given moment is a checkpoint |
| Run | One invocation of an assistant, which may be tied to a thread |
| Cron job | Triggers a graph on a schedule the user sets; each firing makes a fresh thread from the assistant and input |
| Stateless run | Makes a thread from the input, executes without checkpointing, then removes the thread; if the worker dies midway, a background stateless run begins again from the start |

The platform API streams in five modes: `values`, `messages`, `updates`, `events` and `debug`. [[LangGraph Advanced Patterns]] tabulates three, and ch. 8 of the book names `updates`, `values` and `debug` for `stream_mode`.

## Double texting

Double texting means a user sends another message while the graph is still working on the previous one. The book gives strategy lists in two chapters:

- Ch. 8 (concepts): refuse, run the new input independently, queue it, interrupt the current run, or fork and merge. The book expects fork-and-merge to be best when state can be merged (CRDTs are the example) or when the user settles conflicts; otherwise they pick from the other four. If partial state survives an interrupt, leftover tool-call messages without results must be cleared, or the run can get stuck.
- Ch. 9 (the platform API): reject, enqueue, interrupt, rollback.

The two lists differ. Ch. 8 says only some of its strategies are in LangGraph Platform, and the extraction does not say how the ch. 9 names line up with the ch. 8 ones.

## Deployment steps and checklist

- Start the app locally with `langgraph dev` (the CLI wants Python 3.11 or higher) and exercise it with cURL and the SDK before deploying.
- Place `langgraph.json` in or above the directory holding the compiled graphs; it names `dependencies`, `graphs` and `env`.
- In the deployment form, flag secrets such as `OPENAI_API_KEY` as secret.
- The example `documents` table has 1536-dimension vectors to fit OpenAI embeddings and needs changing for another embedding model. Its `match_documents` function ranks by cosine similarity with a metadata filter and a cap on matches.
- Put human-in-the-loop checkpoints where logic calls tools or reaches certain documents.
- Security: grant least-privilege credentials, and treat the agent as able to do anything its permissions allow, so stack defences (read-only credentials plus a sandbox). Restrict file access to one directory and database credentials to the tables in use. Against abuse and runaway cost, the book suggests verified accounts, rate limits in middleware, and guardrails against prompt injection built from scoped permissions and strict prompts.

## Limits

- The chapter is a tutorial for one vendor stack (LangGraph Platform, LangSmith Plus, Supabase), so UI steps and pricing tiers age fast, and the code listings are partly cut off in the extraction.
- The platform is said to handle up to 500 requests per second in a Production deployment, with highly available storage and automatic backups (self-reported by the vendor); no benchmark or hardware is given.
- No measurements, cost or latency figures; monitoring gets a few sentences, and testing and evaluation are deferred to ch. 10 (see [[LangSmith Platform]]). The security advice is generic and untested against prompt injection.
- The double-texting strategy lists in ch. 8 and ch. 9 differ, as noted above.

## See Also
- [[LangGraph Advanced Patterns]] — prerequisite-for
- [[LangChain Fundamentals — create_agent, Tools, Structured Output]] — prerequisite-for
- [[LangSmith Platform]] — related (tracing and evaluation used with the deployment)
- [[HITL and Interrupt Patterns]] — related
