---
title: Scaling Axes and Customer-Triggered Cost Cliffs
tags: [infra, concept]
summary: A small product's bill scales on three independent axes — users, catalogue, team velocity — and the first lines to break are team-velocity ones (CI minutes); the four-figure jumps are cliffs triggered by a single customer's compliance demand, not by traffic.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/research/2026-09-03-operating-cost-model.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-03-operating-cost-model.md
  - data/raw/claude-docs/akira/docs/research/2026-09-03-scaling-infra-strategy.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-03-scaling-infra-strategy.md
  - data/raw/claude-docs/akira/docs/research/2026-09-07-aws-credits-bedrock.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-07-aws-credits-bedrock.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-03-operating-cost-model.md
  - data/raw/claude-docs/playground/docs/research/2026-09-03-operating-cost-model.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-03-scaling-infra-strategy.md
  - data/raw/claude-docs/playground/docs/research/2026-09-03-scaling-infra-strategy.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-07-aws-credits-bedrock.md
  - data/raw/claude-docs/playground/docs/research/2026-09-07-aws-credits-bedrock.md
  - data/raw/claude-docs/diskoe/docs/research/applications-priority.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-03-dis125-ci-path-filter.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-03-dis125-ci-path-filter.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-03-dis125-ci-path-filter.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-03-dis125-ci-path-filter.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-03-dis125-ci-path-filter.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-03-dis125-ci-path-filter.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-03-dis125-ci-path-filter.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-03-dis125-ci-path-filter.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-03-dis125-ci-path-filter.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-03-dis125-ci-path-filter.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-03-dis125-ci-path-filter.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-03-dis125-ci-path-filter.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-03-dis125-ci-path-filter.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-03-dis125-ci-path-filter.md
---

# Scaling Axes and Customer-Triggered Cost Cliffs

An operating-cost model for a Next.js + managed-Postgres + serverless-host product (akira)
at pilot scale, with the lessons that generalise.

## Three axes, not one

| Axis | Driven by | First line to break |
|---|---|---|
| Users | sessions, bandwidth, function invocations | nothing until ~250k sessions/month |
| Catalogue | rows, storage, inference | model spend (see [[Two AI Cost Economies: Durable Once, Contextual On Demand]]) |
| Team velocity | commits, builds, CI jobs | **CI minutes — already over the plan ceiling at pilot** |

The surprise was the third axis. 58% of commits in a 30-day window touched only docs and
agent-config directories, yet every one ran the full pipeline. A CI path filter cut
minutes ~55% and still did not clear the ceiling once a third triggered job was added; a
faster push rate or one more heavy job breaks it again. With agentic workflows generating
many small doc-only commits, **team velocity is a billing axis** and "don't run the
pipeline on commits that cannot change the build" is the first optimisation, ahead of
anything on the user axis. Apply the same filter to the host's ignored-build step.

## Cliffs, not slopes

The four-figure-per-year jumps are not reached by growth. They are triggered by a
*customer*: an enterprise security review demanding SOC 2 / ISO 27001 forces the database
vendor's team tier (a ~24× jump from the pro tier) regardless of row count; a partner
demanding SAML SSO forces a deploy-platform add-on. Nothing about scale forces either — a
single procurement questionnaire does, and the compliance posture it implies costs far
more than the tier. Model these as discrete events with an owner, not as a slope.

## Credits and what they cannot buy

Cloud credits pay only for that cloud's own services. They pay for nothing on a
third-party host or managed database, which is where most of a small product's bill lives.
Structural consequence: credits are worth most against the biggest line (the database),
which is the one least movable (auth, RLS, and the ORM path are load-bearing across every
migration), and worth least against the line that could move cheapest (hosting). At this
bill size credits should not drive architecture; revisit near ~$500/month or when a raise
unlocks a larger tier. The only line credits touch without a rewrite is inference.

Shortlisting credit programmes (2026-08) added four rules. **Match credits to the spend
shape**: an evaluation phase on hosted APIs needs token and embeddings budget plus
observability, not GPUs, which ruled out whole programme families. **Benefit clocks start
on activation**, so programmes gated on incorporation lose nothing by waiting. **Never
incorporate early for credits**: a few thousand dollars doesn't outweigh closing
pre-incorporation grant routes. **Pick the comparison provider by lock-in**: an
OpenAI-compatible host drops in behind an existing base-URL seam, while a credit line
tied to one vendor's SDK is a sandbox, not a stack candidate. A starter tier applied for
now can usually be topped up later when a referral unlocks the larger tier.

## One security finding that is also a cost finding

Image optimisation configured with `hostname: '**'` turns the optimiser route into an open
proxy: anyone can point it at arbitrary remote URLs and burn the bandwidth budget. Narrow
`remotePatterns` to the publisher hostnames actually present in the catalogue.

## See Also
- [[Paid Tiers Start at the Beta, Not the Alpha]] — instance-of (CI minutes broke first; the database upgrade bought posture, not capacity)
- [[Two AI Cost Economies: Durable Once, Contextual On Demand]] — complements
- [[Deployment Topology Ladder]] — extends (cost axes as the reason to stay on a low rung)
- [[Complexity Floor]] — related (team-hours bound the reachable rung; CI minutes bound the commit rate)
- [[Rate-Limit Keying: Identity Over IP]] — related (the other open-endpoint exposure found in the same pass)
- [[Skip Steps, Not Jobs, Behind a Path Filter]] — extends (how the path filter was built and why it did not clear the ceiling)
