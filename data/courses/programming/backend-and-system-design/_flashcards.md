---
imported_hash: c43dd778669503e6
decks:
- learn-ai-engineering/programming/backend-and-system-design/slides/deck.yaml
cards:
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
---
