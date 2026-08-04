---
title: Task Decomposition Patterns
tags: [agents, llm, pattern]
summary: "Four axes for splitting work across agents — functional, spatial, temporal, and data-driven — distinguished by what each one assumes about independence, and the dependency structure that decides which axis a given task actually admits."
updated: 2026-08-04
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--03-harness--agents-design.md
---

# Task Decomposition Patterns

Before you can distribute work across agents you have to cut it somewhere, and there are
four distinct axes to cut along. The choice is usually made implicitly and usually made
wrong, because the intuitive axis — split by *what kind of work* — is only one of four and
is frequently the least parallel.

The load-bearing insight is that **each pattern is a bet about where the dependencies
aren't.** Decomposition doesn't remove coupling; it chooses which coupling to expose as a
handoff. Picking an axis along which the work is genuinely coupled produces agents that
block on each other and a system slower than the single agent it replaced.

## The four axes

| Pattern | Split by | Assumes | Fails when |
|---|---|---|---|
| **Functional** | Technical domain or expertise — *what kind of work* | Kinds of work are separable | One artifact needs several kinds of work interleaved |
| **Spatial** | File or directory structure | Files are independently processable | Files have complex cross-dependencies |
| **Temporal** | Sequential stages, later depending on earlier | Stages have a real ordering | Stages are actually concurrent (serializes for nothing) |
| **Data-driven** | Data partitions — chunks processed independently | Records don't interact | Results require cross-partition aggregation |

## Functional decomposition

Split by the kind of work: research, writing, review, code generation. This is the default
because it maps onto how human teams are organized, and it is the axis most likely to be
chosen without considering the others.

Its weakness is that it produces **maximum handoff traffic per unit of work**. A single
deliverable passes through every specialist, so the number of interface boundaries scales
with the number of specialties rather than with the volume of work. When throughput is the
goal rather than quality-per-item, functional decomposition is usually the wrong cut — it
parallelizes across *stages*, which only helps if multiple items are in flight.

## Spatial decomposition

Split by file or directory. Described in the source as *especially powerful when working
with large codebases with many files that could be processed independently* — a migration,
a lint sweep, a docstring pass.

The stated failure condition is precise: **if your files have complex dependencies on each
other, spatial decomposition breaks down.** A rename that crosses module boundaries is not
a spatial task no matter how many files it touches, because the agent working on file A
needs to know what the agent working on file B decided.

The practical test is whether an agent can complete its slice **without reading outside
it**. If it can't, the slice isn't a slice. This is the axis worktree isolation is built
for — see [[Multi-Agent Context]].

## Temporal decomposition

Break into sequential stages where later stages depend on earlier ones being complete.
This is decomposition that deliberately *does not* parallelize; its purpose is to bound
each agent's scope and make the intermediate state inspectable, not to run things at once.

Temporal decomposition is what a planner/executor split is, and its value is the gate
between stages rather than the split itself. A stage boundary is a natural place to put a
verification step, which is why long-horizon work tends toward this axis even when other
axes are available. See [[Plan and Execute Pattern]] and [[Long-Horizon Execution]].

## Data-driven decomposition

Split by data partition. The source calls this one *less common but really powerful* for
tasks over large datasets where chunks can be processed independently.

It is the axis with the cleanest parallelism — partitions are independent by construction
if the partitioning is correct — and the one with the sharpest hidden cost, which is the
**aggregation step**. Anything requiring a global view (deduplication, ranking, a total)
must happen after every partition returns, which reintroduces a barrier the per-partition
parallelism was supposed to avoid. Fan-out mechanics in [[Send API Fan-out]].

## Choosing

The axes are not exclusive, and real systems nest them — temporal at the top (plan, then
execute, then verify), spatial or data-driven inside the execute stage. What matters is
choosing deliberately rather than defaulting to functional because it reads like an org
chart.

The diagnostic question in each case is the same: **what would two agents on this axis
need to tell each other?** If the answer is "nothing," the axis is real. If the answer
involves ongoing coordination, you have found the coupling and should cut elsewhere — or
accept a protocol, which is what [[Protocol-Driven Multi-Agent Collaboration]] is for.

And before any of this: confirm the single-agent ceiling was actually reached. Premature
decomposition is one of the eight [[Agent Deployment Anti-Patterns]], and coordination
overhead routinely exceeds the parallelism gained.

## See Also
- [[Graph Engineering]] <!-- auto-linked -->
- [[Harness Engineering]] <!-- auto-linked -->
- [[Harness Orchestration]] <!-- auto-linked -->
- [[Protocol-Driven Multi-Agent Collaboration]] — depends-on (what coordinates the pieces once split)
- [[Multi-Agent Orchestration Patterns]] — complements (the topology, orthogonal to the cut)
- [[Multi-Agent Context]] — implements (spatial isolation via worktrees)
- [[Agent Deployment Anti-Patterns]] — prerequisite-for (verify the single-agent limit first)
- [[Send API Fan-out]] — instance-of (data-driven decomposition, mechanically)
- [[Plan and Execute Pattern]] — instance-of (temporal decomposition, mechanically)
