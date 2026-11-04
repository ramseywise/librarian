---
title: "Unreliable Networks, Clocks and Process Pauses"
tags: [foundations, concept]
summary: "A timeout means 'unknown', not 'failed'; clock skew of a few milliseconds makes last-write-wins drop acknowledged writes and inverts cause and effect; processes can pause unnoticed; checksums catch corruption that still parses."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--01-storage-and-compute-foundations--notes--06-when-distributed-systems-fail.md
---

# Unreliable Networks, Clocks and Process Pauses

Across machines the determinism of a single computer is gone: some parts work, some do not, and no part knows which (**partial failure**). A single machine prefers to crash rather than return a wrong answer. Rerunning a failed batch job from the start turns a partial failure into a total one, a fine bargain for batch and not for a large service. Treat each simulation below as a calculation of a consequence, not a measurement of a system.

## A timeout is "I do not know"
A lost request, a crashed server and a lost or slow reply all look identical to the client. With moderate fault rates (2% lost request, 2% lost reply, 2% slow, 1% crash), 6,794 of 100,000 calls timed out and the write HAD been applied in 57% of those. If only replies are lost, 100% of timeouts hide a success. A TCP acknowledgement means only that the kernel got the bytes; certainty needs a positive application reply. The response is to retry plus deduplicate (see [[Idempotent Retries and Request IDs]]).

**Choosing a timeout** has no right answer. Short ones declare slow nodes dead, duplicating work and shifting load onto stressed nodes (a cascade); long ones delay action. Real networks have no upper bound on delay (queues in switches, OS, hypervisor, congestion control); variable delay is the price of cheap shared capacity. Measure the round-trip distribution. For a 5 ms median with 1-in-1,000 spikes, false "dead" verdicts per 10,000 checks were 840.1 at 10 ms, 15.3 at 25 ms, 7.6 at 100 ms, 2.9 at 500 ms and 0.1 at 2000 ms: past the body of the distribution you pay 20 times more waiting for a halving of false alarms. Adaptive phi accrual detectors adjust to observed variability. One study counted about 12 network faults per month in a medium datacenter, half disconnecting one machine and half a rack.

## Clocks
A **time-of-day clock** is roughly comparable across machines but can jump, including backwards, when NTP corrects it. A **monotonic clock** only moves forward and suits durations (use it for timeouts) but is meaningless on another machine. 200 ppm of drift is 17.3 s per day. The best NTP over the public internet is around 35 ms, and a paused VM's clock can stop. A wrong clock causes silent data loss, not an alert, so monitor offsets.

**Last-write-wins loses acknowledged writes under skew.** Two nodes taking writes to one key every 10 ms on average:

| Skew | Writes silently dropped |
|---|---|
| 0 ms | 0.00% |
| 1 ms | 2.48% |
| 3 ms | 7.05% |
| 10 ms | 19.61% |
| 35 ms | 41.25% |
| 1000 ms | 50.01% |

What matters is skew relative to the gap between writes, so frequently updated keys are at risk and light tests miss it (about 39% lost at 1 ms gaps with 3 ms skew; under 0.1% at 1000 ms gaps).

**Cause and effect invert.** When a payment event follows a drop-off by 5-50 ms and the payment clock is 20 ms behind, 33.41% of payments are stamped before the drop-off (11.02% at 10 ms, 66.85% at 35 ms, 100.00% at 80 ms), giving negative durations in the warehouse. Order within one source by a sequence number or log offset and treat cross-service timestamps as approximate: a timestamp is really a range. One globally distributed database makes that range explicit and waits out the uncertainty (about 7 ms) before committing.

## Process pauses
A thread can stop for a long while and resume without knowing: stop-the-world GC, VM suspension, CPU steal, slow I/O, swapping, `SIGSTOP`. A process stopped for 0.8 s showed a worst heartbeat gap of 0.804 s against 0.010 s undisturbed. The check-lease-then-act pattern is unsafe because the pause can fall between the lines, and checking more often does not close the window. A long GC can silence a Spark executor enough to be declared lost.

## Corruption, lying and system models
**Byzantine** faults (arbitrary or malicious messages) need more than two thirds of nodes correct and are rarely worth it inside one datacenter. Weak lying does matter: use application-level checksums, input sanity checks and several NTP servers. In 20,000 single-bit flips a length check caught 0 and crc32 caught 20,000; without a checksum a flipped bit turned fare 1200 into 9200 and still parsed.

A **system model** states design assumptions: network synchronous, partially synchronous or asynchronous; nodes crash-stop, crash-recovery or Byzantine (partial synchrony with crash-recovery is the useful pairing). **Safety** (nothing bad ever happens; violation has a moment) must hold always; **liveness** (something good eventually happens; eventual consistency is one) may wait for recovery. A **limping node** (a network card at 1 Kb/s that still answers heartbeats) passes heartbeat checks, so alert on latency and throughput too. If you can avoid distribution, do.

## See Also
- [[Fencing Tokens and Zombie Writers]] — extends
- [[Idempotent Retries and Request IDs]] — related
- [[Latency Percentiles, Tail Amplification and Coordinated Omission]] — related (the same long tail decides a node's fate)
- [[Quorums, Version Vectors and Last-Write-Wins]] — related
