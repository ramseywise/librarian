---
title: API Design Fundamentals
tags: [infra, reference]
summary: "The API layer at system-design grain — entities become plural-noun REST resources, path/query/body by role, REST outside and gRPC inside, GraphQL only when clients need different shapes (and its N+1 trap), cursor over offset pagination for live feeds, identity from the auth token never the body, plus idempotency keys, versioning, and rate limits."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/interviewing--guides--9-system-design--02-api-design.md
  - data/raw/repos/sisyphus/interviewing--guides--9-system-design--02-api-design.md
---

# API Design Fundamentals

Scoped to what a design round needs (about five minutes of a 45-minute round), not
production API design from scratch. Source is a cleaned video-transcript overview, medium
confidence.

## Entities → resources → endpoints

The core entities you identified become REST resources: plural nouns, no verbs (`GET /orders/123`,
not `GET /fetchOrder`) — the HTTP method is the verb. In practice GET and POST carry most
designs, PATCH occasionally; don't spend time on PUT vs PATCH.

**Where inputs go:** resource id → path; filter, sort, page → query; the object being created
→ JSON body. Responses are a status class (2xx/4xx/5xx) plus a named return type ("returns
`List<Event>`") — don't enumerate fields.

## REST, GraphQL, gRPC

| | REST | GraphQL | gRPC |
|---|---|---|---|
| Where | client-facing | client-facing | service-to-service |
| Shape | resource-based, JSON | query-based, JSON | function-based, Protobuf |
| Pick when | the default | many clients need different fields of the same graph | internal calls needing small payloads, typed contracts, codegen |

GraphQL removes over- and under-fetching but brings the **N+1 query problem** (100 users → 1 +
100 queries for their posts); batch loading (DataLoader) is the fix to name. Don't reach for it
on CRUD, booking, or delivery systems.

## Pagination

Offset (`?page=2&limit=20`) is simple and fine for static admin lists, but concurrent inserts
cause duplicates and skipped rows. **Cursor pagination** (`?cursor=…`, last-seen item) is stable
under continuous inserts — the answer for feeds.

## Authentication

Never accept user identity in the request body — any client can spoof it. Send a bearer token
(JWT or session) in the `Authorization` header and derive the user id server-side. JWT is
stateless and self-contained; a session token needs a lookup but is easier to revoke.

## Production details worth a sentence

- **Idempotency keys** on retried mutations (payments) so a client timeout doesn't double-charge.
- **Versioning** (`/v1/…`) for public APIs.
- **Rate limiting** (token bucket, leaky bucket).
- **Structured error objects** (code + message), not bare status codes.

## See Also
- [[Backend Scaling Fundamentals]] — related (the substrate behind the endpoints)
- [[System Design Interview Study Guide]] — prerequisite-for (step 3 of the round)
- [[RAG API Design Patterns]] — extends (the same layer for a retrieval service)
