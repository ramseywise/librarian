---
generated_by: src/librarian/tools/slides/flashcards.py
decks:
- programming/backend-and-system-design/slides/deck.yaml
cards:
- front: What are the four parts of this lecture, in order?
  back: The lecture moves from what one request promises, to the parts that serve it, to the sums that size them, to whole designs.
  lesson: programming/backend-and-system-design/readme
- front: Name four things this lecture teaches you to do with a backend design.
  back: You will be able to compute what a design needs and say what each box does when it is slow, down or running twice.
  lesson: programming/backend-and-system-design/readme
- front: What should a client do after a timeout?
  back: Retry only what is idempotent or carries a key. Otherwise read the state before acting.
  lesson: programming/backend-and-system-design/notes/01-api-design
- front: Why does a cursor beat an offset on a deep page?
  back: Offset cost grows with depth and repeats rows when new ones arrive. A keyset cursor does neither, but can't jump to page 50.
  lesson: programming/backend-and-system-design/notes/01-api-design
- front: What makes a JWT check strict?
  back: A JWT's header doesn't choose its own algorithm. Your configuration does, along with issuer, audience and required claims.
  lesson: programming/backend-and-system-design/notes/02-auth-sessions-jwt-oauth
- front: Is a logged-in user allowed this object?
  back: Check access on every object, not only every route, and deny by default. A valid token proves who is asking, not what they may touch.
  lesson: programming/backend-and-system-design/notes/02-auth-sessions-jwt-oauth
- front: How do you stop a hot key's expiry hitting the database?
  back: A TTL doesn't protect you when a popular key expires. Limit its fills to one at a time and jitter the expiry.
  lesson: programming/backend-and-system-design/notes/03-caching-and-queues
- front: How do a database write and a message stay together?
  back: Write the row and the outbox entry in one transaction, and make the consumer idempotent, because delivery is at-least-once.
  lesson: programming/backend-and-system-design/notes/03-caching-and-queues
- front: Which balancing policy keeps the tail down?
  back: Balance on live load, and prefer two random choices, because least loaded melts when its counts go stale. Hash only when a key must land in one place.
  lesson: programming/backend-and-system-design/notes/04-load-balancing-and-rate-limiting
- front: Why must a rate-limit check be one atomic step?
  back: Check and spend in one atomic statement at the store. Read-then-write admitted about seven times a limit of 100 with 8 threads.
  lesson: programming/backend-and-system-design/notes/04-load-balancing-and-rate-limiting
- front: How hot should you run a server pool?
  back: Run servers well below saturation, commonly 50 to 70%, since wait grows sharply near the limit. Larger pools can run hotter.
  lesson: programming/backend-and-system-design/notes/05-estimation-and-scaling
- front: How does a process stop without dropping requests?
  back: On SIGTERM fail readiness, wait for load balancers to notice, stop accepting, finish in-flight work, then exit before the grace period ends.
  lesson: programming/backend-and-system-design/notes/06-containers-cicd-and-deployment
- front: Which probe may check the database?
  back: Only readiness may reflect a dependency. A slow database failing liveness restarts the whole fleet, and a restart could never have fixed it.
  lesson: programming/backend-and-system-design/notes/06-containers-cicd-and-deployment
- front: How can a 10 second blip take a service down for good?
  back: Fix the sustaining effect, not the trigger. Retries need a budget, at one layer, with jittered backoff, and recovery means cutting load.
  lesson: programming/backend-and-system-design/notes/07-reliability-under-load
- front: Why can a server at full throughput be in total outage?
  back: 'Measure from the client, and bound the queue: limit below capacity × deadline. Overload needs a queue with a limit, not a longer one.'
  lesson: programming/backend-and-system-design/notes/07-reliability-under-load
- front: What order does a design discussion follow?
  back: Name the requirement that drives the design before you draw anything, then take each box away and say what users see.
  lesson: programming/backend-and-system-design/notes/08-design-walkthroughs-rate-limiter-notifications-scheduler
- front: What stops a paused worker overwriting its successor?
  back: A lease lets someone else take over, and a fencing token stops the old owner's late write. It protects only the systems that compare it.
  lesson: programming/backend-and-system-design/notes/08-design-walkthroughs-rate-limiter-notifications-scheduler
- front: When should a feed do its fan-out work?
  back: Choose the hybrid threshold to bound the worst burst, not to minimise a total. Timelines hold IDs, and page by keyset cursor.
  lesson: programming/backend-and-system-design/notes/09-design-walkthroughs-kv-store-and-feed
- front: How does a log-structured store survive a crash?
  back: Log with fsync before acknowledging, and replay the log since the last flush. A torn last record was never acknowledged, so losing it is correct.
  lesson: programming/backend-and-system-design/notes/09-design-walkthroughs-kv-store-and-feed
- front: What does a model gateway do differently?
  back: Limit tokens rather than requests, and fall back only before the first token. A hypothetical mix had its costliest request at 67x the median.
  lesson: programming/backend-and-system-design/notes/10-ai-system-reference-architecture
- front: Why checkpoint a long agent run?
  back: Save state after each step, because restart cost grows exponentially with run length. The backend tools carry over, and a resumed tool call needs an idempotency key.
  lesson: programming/backend-and-system-design/notes/10-ai-system-reference-architecture
- front: Which HTTP methods are idempotent?
  back: The safe ones (GET, HEAD, OPTIONS, TRACE), plus PUT and DELETE. POST and PATCH are not by default.
  lesson: programming/backend-and-system-design/notes/01-api-design
- front: How do you make POST safe to retry?
  back: Client-generated idempotency key, stored with the saved response in the same transaction as the work; a repeat replays it, and a different body with the same key is an error.
  lesson: programming/backend-and-system-design/notes/01-api-design
- front: What stops lost updates over HTTP?
  back: ETag on read, `If-Match` on write, 412 when it no longer matches.
  lesson: programming/backend-and-system-design/notes/01-api-design
- front: Offset or keyset?
  back: 'Keyset for deep or changing lists: constant cost and no duplicates. Offset for small, stable lists that need numbered pages.'
  lesson: programming/backend-and-system-design/notes/01-api-design
- front: What is the N+1 problem, and the fix?
  back: One query for a list plus one per item. Batch the per-item keys in one query, for example with a DataLoader.
  lesson: programming/backend-and-system-design/notes/01-api-design
- front: How do you stop an expensive GraphQL query?
  back: Trusted documents for first-party clients; otherwise depth, breadth and cost limits, plus pagination on every list.
  lesson: programming/backend-and-system-design/notes/01-api-design
- front: REST or gRPC between services?
  back: gRPC if you own both ends and want typed contracts, deadlines and streaming; REST when clients are many or unknown.
  lesson: programming/backend-and-system-design/notes/01-api-design
- front: What is deadline propagation?
  back: One absolute deadline for the whole call tree; each hop passes on what remains so nobody works for a caller that has gone.
  lesson: programming/backend-and-system-design/notes/01-api-design
- front: 401 or 403?
  back: 401 means not authenticated; 403 means authenticated and refused. See chapter 2.
  lesson: programming/backend-and-system-design/notes/01-api-design
- front: What is REST?
  back: A style where the API is resources named by URLs, acted on with the standard HTTP methods through representations such as JSON, with every request self-contained. Statelessness lets any replica answer and caches sit in between.
  lesson: programming/backend-and-system-design/notes/01-api-design
- front: Authentication or authorisation?
  back: Who you are, against what you may do. Different code, different failures, 401 against 403.
  lesson: programming/backend-and-system-design/notes/02-auth-sessions-jwt-oauth
- front: Session or JWT?
  back: Session when revocation and simplicity matter and one backend owns the store. JWT when many services verify without calling home; keep it short-lived.
  lesson: programming/backend-and-system-design/notes/02-auth-sessions-jwt-oauth
- front: How do you revoke a JWT?
  back: You can't directly. Short expiry plus refresh, or a `jti` denylist until expiry, which brings back a lookup.
  lesson: programming/backend-and-system-design/notes/02-auth-sessions-jwt-oauth
- front: 'What is the `alg: none` attack?'
  back: The token declares itself unsigned and a naive verifier agrees. Verifiers must fix allowed algorithms themselves.
  lesson: programming/backend-and-system-design/notes/02-auth-sessions-jwt-oauth
- front: What is key confusion?
  back: An RS256 public key gets used as an HS256 secret because the token chose the algorithm. Tie each key to one algorithm.
  lesson: programming/backend-and-system-design/notes/02-auth-sessions-jwt-oauth
- front: What must a resource server check on a JWT?
  back: Signature, algorithm, `iss`, `aud`, `exp`, `typ`, then scope and object-level access.
  lesson: programming/backend-and-system-design/notes/02-auth-sessions-jwt-oauth
- front: What does PKCE protect?
  back: 'A stolen authorization code: redeeming it needs a verifier that was never sent through the browser.'
  lesson: programming/backend-and-system-design/notes/02-auth-sessions-jwt-oauth
- front: Why rotate refresh tokens?
  back: A replayed old token reveals theft, so the server revokes the family.
  lesson: programming/backend-and-system-design/notes/02-auth-sessions-jwt-oauth
- front: ID token or access token?
  back: ID token tells the client who logged in; access token authorises API calls.
  lesson: programming/backend-and-system-design/notes/02-auth-sessions-jwt-oauth
- front: How do you store passwords?
  back: Argon2id or scrypt with a unique salt, at settings under a second per hash, and upgrade on next login.
  lesson: programming/backend-and-system-design/notes/02-auth-sessions-jwt-oauth
- front: What is BOLA?
  back: Authenticated users reach objects they don't own because the endpoint trusts the id. Scope queries to the principal.
  lesson: programming/backend-and-system-design/notes/02-auth-sessions-jwt-oauth
- front: What stops CSRF?
  back: A synchronizer token or Fetch Metadata, with `SameSite` as extra depth. It doesn't apply to tokens sent in headers.
  lesson: programming/backend-and-system-design/notes/02-auth-sessions-jwt-oauth
- front: Describe look-aside caching.
  back: Read cache; on a miss read the database and fill; on a write update the database and delete the key.
  lesson: programming/backend-and-system-design/notes/03-caching-and-queues
- front: Why delete and not update on write?
  back: Deletes are idempotent and can't leave an older value after a newer one.
  lesson: programming/backend-and-system-design/notes/03-caching-and-queues
- front: What is a cache stampede and the fix?
  back: Many misses for one hot key at once. Single flight within a process, leases across a fleet, jitter on TTLs.
  lesson: programming/backend-and-system-design/notes/03-caching-and-queues
- front: How can a stale value get in after a delete?
  back: A reader's fill arrives after a writer's delete. Leases reject the late fill.
  lesson: programming/backend-and-system-design/notes/03-caching-and-queues
- front: What's the danger in a 90% hit ratio?
  back: The database sees a tenth of the load, so losing the cache means 10x.
  lesson: programming/backend-and-system-design/notes/03-caching-and-queues
- front: At-least-once or exactly-once?
  back: Delivery is at-least-once. Exactly-once effect comes from an idempotent consumer.
  lesson: programming/backend-and-system-design/notes/03-caching-and-queues
- front: What is a visibility timeout?
  back: A received message is hidden, and reappears unless deleted within the window.
  lesson: programming/backend-and-system-design/notes/03-caching-and-queues
- front: When use a dead-letter queue?
  back: After a fixed number of failed receives, so a poison message stops blocking and someone is alerted.
  lesson: programming/backend-and-system-design/notes/03-caching-and-queues
- front: Kafka or a work queue?
  back: Log for events with replay and many readers; queue for jobs with competing workers.
  lesson: programming/backend-and-system-design/notes/03-caching-and-queues
- front: How do you keep order in Kafka?
  back: Key by entity so that entity's events share a partition.
  lesson: programming/backend-and-system-design/notes/03-caching-and-queues
- front: What is the dual-write problem?
  back: Database and broker can't commit together. Use an outbox with an idempotent consumer.
  lesson: programming/backend-and-system-design/notes/03-caching-and-queues
- front: Layer 4 or layer 7?
  back: Layer 4 forwards fast with no view of HTTP. Layer 7 routes by content, retries and terminates TLS, at more cost.
  lesson: programming/backend-and-system-design/notes/04-load-balancing-and-rate-limiting
- front: Which balancing policy by default?
  back: P2C or least requests. Round robin only for uniform requests and servers.
  lesson: programming/backend-and-system-design/notes/04-load-balancing-and-rate-limiting
- front: Why two random choices?
  back: Exponential improvement over one choice, a constant factor from three, and it resists herding on stale data.
  lesson: programming/backend-and-system-design/notes/04-load-balancing-and-rate-limiting
- front: What is a lame duck?
  back: A task that keeps serving and tells clients to stop sending, before a clean exit.
  lesson: programming/backend-and-system-design/notes/04-load-balancing-and-rate-limiting
- front: What does consistent hashing buy?
  back: About 1/N of keys move when a node joins, against nearly all with mod N.
  lesson: programming/backend-and-system-design/notes/04-load-balancing-and-rate-limiting
- front: Why virtual nodes?
  back: One point per node gives uneven arcs; many points even out load and allow weighting.
  lesson: programming/backend-and-system-design/notes/04-load-balancing-and-rate-limiting
- front: Token bucket or sliding window?
  back: Bucket when you want a chosen burst; sliding counter for a plain per-minute quota.
  lesson: programming/backend-and-system-design/notes/04-load-balancing-and-rate-limiting
- front: What's wrong with fixed windows?
  back: Twice the limit can pass in a moment across the boundary.
  lesson: programming/backend-and-system-design/notes/04-load-balancing-and-rate-limiting
- front: How do you rate limit across servers?
  back: A shared counter with an atomic operation, or async counters with cached decisions if the round trip costs too much.
  lesson: programming/backend-and-system-design/notes/04-load-balancing-and-rate-limiting
- front: 'Limiter store down: open or closed?'
  back: Usually open with a coarse local limit; closed for high-risk paths such as login.
  lesson: programming/backend-and-system-design/notes/04-load-balancing-and-rate-limiting
- front: What status do you return?
  back: 429 with `Retry-After`.
  lesson: programming/backend-and-system-design/notes/04-load-balancing-and-rate-limiting
- front: How do you start an estimate?
  back: State the assumptions, then users to average rate, a peak factor, sizes, retention, copies. Use it to make a decision.
  lesson: programming/backend-and-system-design/notes/05-estimation-and-scaling
- front: Peak or average?
  back: Peak, plus the failure of your largest unit.
  lesson: programming/backend-and-system-design/notes/05-estimation-and-scaling
- front: Why not run at 95% utilisation?
  back: Waiting grows like 1/(1 − ρ). In the 16-worker example, the wait at 95% is about ten times that at 80%.
  lesson: programming/backend-and-system-design/notes/05-estimation-and-scaling
- front: How do you turn QPS into machines?
  back: QPS × CPU per request, divided by a target utilisation, then rounded up for failure.
  lesson: programming/backend-and-system-design/notes/05-estimation-and-scaling
- front: Little's law?
  back: In-flight = arrival rate × latency.
  lesson: programming/backend-and-system-design/notes/05-estimation-and-scaling
- front: Why do bigger pools tolerate higher utilisation?
  back: 'One shared queue absorbs bursts: statistical multiplexing.'
  lesson: programming/backend-and-system-design/notes/05-estimation-and-scaling
- front: What is 99.99% in minutes?
  back: 52.56 per year, 4.32 per 30 days.
  lesson: programming/backend-and-system-design/notes/05-estimation-and-scaling
- front: What do twenty 99.9% dependencies give?
  back: About 98%, since required dependencies multiply.
  lesson: programming/backend-and-system-design/notes/05-estimation-and-scaling
- front: Replica or shard?
  back: Replica for read volume, shard for write volume or data size. Shard last.
  lesson: programming/backend-and-system-design/notes/05-estimation-and-scaling
- front: What limits sharding?
  back: Hot keys and cross-shard work. A key with fraction *f* caps the cluster at node capacity / *f*.
  lesson: programming/backend-and-system-design/notes/05-estimation-and-scaling
- front: What does Amdahl's law say?
  back: Speedup is capped at 1 / (serial fraction).
  lesson: programming/backend-and-system-design/notes/05-estimation-and-scaling
- front: Container versus VM?
  back: A container is an isolated process sharing the host kernel, using namespaces and cgroups. A VM has its own kernel.
  lesson: programming/backend-and-system-design/notes/06-containers-cicd-and-deployment
- front: How do you keep images small and safe?
  back: Multi-stage builds, slim base pinned by digest, non-root user, `.dockerignore`, no secrets in layers.
  lesson: programming/backend-and-system-design/notes/06-containers-cicd-and-deployment
- front: What does shell-form `CMD` break?
  back: The shell is PID 1 and may not forward SIGTERM, so the process gets SIGKILL at the deadline.
  lesson: programming/backend-and-system-design/notes/06-containers-cicd-and-deployment
- front: Graceful shutdown sequence?
  back: On SIGTERM, fail readiness, wait for load balancers to notice, stop accepting, finish in-flight work, exit before the grace period ends.
  lesson: programming/backend-and-system-design/notes/06-containers-cicd-and-deployment
- front: Liveness versus readiness?
  back: Liveness failure restarts, and is for unrecoverable states. Readiness failure removes from traffic, and is for temporary ones. Don't put dependencies in liveness.
  lesson: programming/backend-and-system-design/notes/06-containers-cicd-and-deployment
- front: '`maxSurge` versus `maxUnavailable`?'
  back: Extra pods allowed, rounded up; missing pods allowed, rounded down. Both default to 25%.
  lesson: programming/backend-and-system-design/notes/06-containers-cicd-and-deployment
- front: Canary versus blue-green?
  back: Canary sends a small share to the new version and evaluates it. Blue-green swaps all traffic between two full environments, with instant rollback.
  lesson: programming/backend-and-system-design/notes/06-containers-cicd-and-deployment
- front: How big a canary?
  back: Big enough to get evidence in the time you'll wait. A model shows that errors at detection are nearly constant below 1%, then grow with share.
  lesson: programming/backend-and-system-design/notes/06-containers-cicd-and-deployment
- front: How do you rename a column with no downtime?
  back: Expand (add new, write both), migrate (backfill, read new), contract (drop old). Each step is a separate deploy.
  lesson: programming/backend-and-system-design/notes/06-containers-cicd-and-deployment
- front: What does a CPU limit do versus a memory limit?
  back: CPU limit throttles, showing as latency. Memory limit kills.
  lesson: programming/backend-and-system-design/notes/06-containers-cicd-and-deployment
- front: HPA formula?
  back: '`ceil(current × metric / target)`, with a 10% tolerance and rate limits on scale-up.'
  lesson: programming/backend-and-system-design/notes/06-containers-cicd-and-deployment
- front: Why does autoscaling miss spikes?
  back: Saturated CPU hides true demand, and each step must wait for pods to start.
  lesson: programming/backend-and-system-design/notes/06-containers-cicd-and-deployment
- front: Why focus on p99?
  back: 'Fan-out multiplies tail events: with 1% slow and 100 calls, 63% of requests wait for a slow one.'
  lesson: programming/backend-and-system-design/notes/07-reliability-under-load
- front: What's a hedged request?
  back: A second copy sent after a delay, near p95, taking the first answer. Idempotent operations only. About 5% extra load.
  lesson: programming/backend-and-system-design/notes/07-reliability-under-load
- front: What's a metastable failure?
  back: A trigger pushes the system into a bad state, and a sustaining effect such as retries keeps it there after the trigger has gone.
  lesson: programming/backend-and-system-design/notes/07-reliability-under-load
- front: How do you recover from a retry storm?
  back: Cut the load below the recovery point, disable or budget retries, then ramp up.
  lesson: programming/backend-and-system-design/notes/07-reliability-under-load
- front: How should retries work?
  back: One layer, exponential backoff with jitter, a budget, only retryable errors, idempotency keys.
  lesson: programming/backend-and-system-design/notes/07-reliability-under-load
- front: Circuit breaker downside?
  back: Modal behaviour that's hard to test, and it can add to recovery time. A local retry token bucket is a common alternative.
  lesson: programming/backend-and-system-design/notes/07-reliability-under-load
- front: How do deadlines work across services?
  back: Pass the remaining time on, subtract a margin, refuse work you can't finish, and propagate cancellation.
  lesson: programming/backend-and-system-design/notes/07-reliability-under-load
- front: Throughput versus goodput?
  back: Work done versus useful work received in time. Under overload the two can differ by almost everything.
  lesson: programming/backend-and-system-design/notes/07-reliability-under-load
- front: FIFO or LIFO under overload?
  back: Bounded FIFO if the queue is short; LIFO when it's long, because the newest requests are the ones that can still succeed.
  lesson: programming/backend-and-system-design/notes/07-reliability-under-load
- front: How do you compute a fleet p99?
  back: Sum histogram buckets across hosts, then estimate. Never average per-host quantiles.
  lesson: programming/backend-and-system-design/notes/07-reliability-under-load
- front: Head or tail sampling?
  back: Head is cheap, but it's decided in advance. Tail keeps slow and failed traces, but it costs buffering.
  lesson: programming/backend-and-system-design/notes/07-reliability-under-load
- front: Four golden signals?
  back: Latency, traffic, errors, saturation.
  lesson: programming/backend-and-system-design/notes/07-reliability-under-load
- front: What's an error budget?
  back: 1 − SLO. It's a shared number for deciding whether to release or to stabilise.
  lesson: programming/backend-and-system-design/notes/07-reliability-under-load
- front: RPO versus RTO?
  back: RPO is how much data you can lose, measured in time. RTO is how long you can be down.
  lesson: programming/backend-and-system-design/notes/07-reliability-under-load
- front: What does losing a region require?
  back: Capacity of 1/(N−1) extra, replication with known lag, a decision mechanism with fencing, and drills.
  lesson: programming/backend-and-system-design/notes/07-reliability-under-load
- front: Where does the rate limiter sit?
  back: At the gateway, with counters in a nearby store, or local counters synced periodically.
  lesson: programming/backend-and-system-design/notes/08-design-walkthroughs-rate-limiter-notifications-scheduler
- front: How do you make it correct under concurrency?
  back: Check-and-spend as one atomic operation at the store.
  lesson: programming/backend-and-system-design/notes/08-design-walkthroughs-rate-limiter-notifications-scheduler
- front: Limiter store down?
  back: Usually a coarse local limit. Fail open or closed depends on what the limit protects.
  lesson: programming/backend-and-system-design/notes/08-design-walkthroughs-rate-limiter-notifications-scheduler
- front: What status code?
  back: 429, with `Retry-After`.
  lesson: programming/backend-and-system-design/notes/08-design-walkthroughs-rate-limiter-notifications-scheduler
- front: Rate limiting across regions?
  back: Give each region a share of the limit. A global synchronous counter costs too much latency.
  lesson: programming/backend-and-system-design/notes/08-design-walkthroughs-rate-limiter-notifications-scheduler
- front: Why separate notification queues?
  back: A campaign would delay urgent messages by its whole length.
  lesson: programming/backend-and-system-design/notes/08-design-walkthroughs-rate-limiter-notifications-scheduler
- front: How do you avoid duplicate notifications?
  back: A dedupe key with a unique constraint, committed with the queue write, plus an outbox with idempotent consumers.
  lesson: programming/backend-and-system-design/notes/08-design-walkthroughs-rate-limiter-notifications-scheduler
- front: What's a TTL for here?
  back: A message that's late can be worse than none. RFC 8030 requires one on every push.
  lesson: programming/backend-and-system-design/notes/08-design-walkthroughs-rate-limiter-notifications-scheduler
- front: What happens with dead device tokens?
  back: Remove them when the provider rejects them.
  lesson: programming/backend-and-system-design/notes/08-design-walkthroughs-rate-limiter-notifications-scheduler
- front: Exactly-once delivery?
  back: Not achievable through a best-effort provider. At-least-once, with deduplication where you control the code.
  lesson: programming/backend-and-system-design/notes/08-design-walkthroughs-rate-limiter-notifications-scheduler
- front: What stops two schedulers firing a job twice?
  back: A leader, plus a unique `(job, due)` key.
  lesson: programming/backend-and-system-design/notes/08-design-walkthroughs-rate-limiter-notifications-scheduler
- front: Lease versus fencing token?
  back: A lease lets someone else take over. A token stops the old owner's late write.
  lesson: programming/backend-and-system-design/notes/08-design-walkthroughs-rate-limiter-notifications-scheduler
- front: Skip or double-run?
  back: It depends on the job. Default to skip, since a double launch may not be reversible.
  lesson: programming/backend-and-system-design/notes/08-design-walkthroughs-rate-limiter-notifications-scheduler
- front: What's the midnight problem?
  back: Humans pick round times. Hash jobs into a window instead.
  lesson: programming/backend-and-system-design/notes/08-design-walkthroughs-rate-limiter-notifications-scheduler
- front: What's a poison job?
  back: One that crashes its worker each time. Limit attempts, and move it to a failed state.
  lesson: programming/backend-and-system-design/notes/08-design-walkthroughs-rate-limiter-notifications-scheduler
- front: Parts of an LSM store?
  back: Write-ahead log, memtable, immutable sorted tables, compaction, usually bloom filters.
  lesson: programming/backend-and-system-design/notes/09-design-walkthroughs-kv-store-and-feed
- front: LSM versus B-tree?
  back: LSM has cheap writes, and reads pay for it, as does compaction. A B-tree updates in place, and reads are steadier.
  lesson: programming/backend-and-system-design/notes/09-design-walkthroughs-kv-store-and-feed
- front: How does a crash recover?
  back: Replay the log since the last flush into a new memtable. A torn last record was never acknowledged.
  lesson: programming/backend-and-system-design/notes/09-design-walkthroughs-kv-store-and-feed
- front: How does a delete work?
  back: With a tombstone, removed at a major compaction.
  lesson: programming/backend-and-system-design/notes/09-design-walkthroughs-kv-store-and-feed
- front: What does R + W > N give you?
  back: Overlapping reads and writes, without the failure cases covered.
  lesson: programming/backend-and-system-design/notes/09-design-walkthroughs-kv-store-and-feed
- front: R and W for N = 3?
  back: Commonly 2 and 2. They overlap and each tolerates one down node.
  lesson: programming/backend-and-system-design/notes/09-design-walkthroughs-kv-store-and-feed
- front: Why does a quorum help latency?
  back: It waits for the fastest k, so it avoids the slowest replica.
  lesson: programming/backend-and-system-design/notes/09-design-walkthroughs-kv-store-and-feed
- front: Sloppy quorum and hinted handoff?
  back: Write to a stand-in when an owner is down, and pass it back later. Availability up, overlap guarantee gone.
  lesson: programming/backend-and-system-design/notes/09-design-walkthroughs-kv-store-and-feed
- front: Vector clock versus last write wins?
  back: Vector clocks detect concurrent writes so that they can be merged. Last write wins picks one by clock, losing the other.
  lesson: programming/backend-and-system-design/notes/09-design-walkthroughs-kv-store-and-feed
- front: Fan-out on write or read?
  back: Write for fast reads, except for very large accounts. Read to avoid write bursts, at a read cost. Hybrid does each where it's cheap.
  lesson: programming/backend-and-system-design/notes/09-design-walkthroughs-kv-store-and-feed
- front: What goes in a timeline cache?
  back: IDs, not bodies. It can be rebuilt.
  lesson: programming/backend-and-system-design/notes/09-design-walkthroughs-kv-store-and-feed
- front: How do you page a feed?
  back: A keyset cursor, not an offset.
  lesson: programming/backend-and-system-design/notes/09-design-walkthroughs-kv-store-and-feed
- front: Why the threshold in the hybrid?
  back: To bound the worst burst, not to minimise the total.
  lesson: programming/backend-and-system-design/notes/09-design-walkthroughs-kv-store-and-feed
- front: What's different about LLM requests?
  back: Cost varies by orders of magnitude and isn't known up front, responses take seconds and hold a connection, and failed work may still be billed.
  lesson: programming/backend-and-system-design/notes/10-ai-system-reference-architecture
- front: Why not rate-limit requests only?
  back: Requests don't measure work or spend. Limit tokens too, per tenant.
  lesson: programming/backend-and-system-design/notes/10-ai-system-reference-architecture
- front: How do you enforce a token budget when cost is unknown?
  back: Reserve prompt tokens plus `max_tokens` before the call, and settle to actual usage after it.
  lesson: programming/backend-and-system-design/notes/10-ai-system-reference-architecture
- front: What does a reservation cost you?
  back: Near the limit, it refuses some requests that would have fitted.
  lesson: programming/backend-and-system-design/notes/10-ai-system-reference-architecture
- front: When is provider fallback safe?
  back: Before the first token reaches the client. After that, end with an explicit error.
  lesson: programming/backend-and-system-design/notes/10-ai-system-reference-architecture
- front: What happens when a client disconnects?
  back: Cancel upstream, settle for what was produced, and stop paying.
  lesson: programming/backend-and-system-design/notes/10-ai-system-reference-architecture
- front: Why is round robin weak here?
  back: Requests differ greatly in size, and replicas differ in which prefixes they have cached. Route by load and cache affinity.
  lesson: programming/backend-and-system-design/notes/10-ai-system-reference-architecture
- front: What should an LLM fleet autoscale on?
  back: Queue depth and first-token latency against the SLO, not GPU utilisation. Keep warm headroom, since a cold start takes minutes.
  lesson: programming/backend-and-system-design/notes/10-ai-system-reference-architecture
- front: SSE or WebSocket for tokens?
  back: SSE is plain HTTP, one way, with resumption built in, and it's enough for a reply. WebSocket fits when the client also sends during the stream.
  lesson: programming/backend-and-system-design/notes/10-ai-system-reference-architecture
- front: What's the risk of a semantic cache?
  back: A similar question isn't the same question, so a hit can be confidently wrong, and across tenants it's a leak.
  lesson: programming/backend-and-system-design/notes/10-ai-system-reference-architecture
- front: Why checkpoint an agent?
  back: Restart cost grows exponentially with steps. Per-step checkpoints keep it near linear.
  lesson: programming/backend-and-system-design/notes/10-ai-system-reference-architecture
- front: Then what's needed on a resumed tool call?
  back: An idempotency key, since the step may run twice.
  lesson: programming/backend-and-system-design/notes/10-ai-system-reference-architecture
- front: How do you stop a prompt injection reaching a tool?
  back: A deterministic policy between proposal and execution, the user's own identity on the call, and an allow-listed exit.
  lesson: programming/backend-and-system-design/notes/10-ai-system-reference-architecture
- front: How do you ship a new model version?
  back: A regression gate against a baseline, a canary, and the model id recorded on every trace.
  lesson: programming/backend-and-system-design/notes/10-ai-system-reference-architecture
- front: Why route every model call through one gateway?
  back: A gateway is one service every model call passes through, so authentication, counting, limits, provider choice and logging live in a single place rather than in each caller.
  lesson: programming/backend-and-system-design/notes/10-ai-system-reference-architecture
---
