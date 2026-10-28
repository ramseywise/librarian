---
title: The Free Decision Is the Long-Lead Item
tags: [patterns, pattern]
summary: "On a critical path where a zero-cost decision gates fast mechanical steps, which in turn gate a calendar clock that more engineering cannot speed up, the decision is the long-lead item. Make it at once, not in the cycle where its downstream work is scheduled. Every day it slips is added directly to the launch date."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-08-31-g6-domain-dns.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-08-31-g6-domain-dns.md
  - data/raw/repos/akira/.claude--docs--plans--2026-08-31-g6-domain-dns.md
  - data/raw/claude-docs/playground/docs/plans/2026-08-31-g6-domain-dns.md
  - data/raw/repos/playground/.claude--docs--plans--2026-08-31-g6-domain-dns.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-08-31-g6-domain-dns.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-08-31-g6-domain-dns.md
---

# The Free Decision Is the Long-Lead Item

The usual way to find the long-lead item is to look for the slowest work. Sometimes the
slowest *thing* on a path is not work at all. It is a clock that starts only after a
chain of fast steps. Then the item with the real lead time is whatever starts that
chain, and that is often a decision that costs nothing to make.

## The shape (from akira's domain-and-DNS issue)

```
apex-path decision      — $0, no dependencies, unbounded until someone makes it
  → point domain at host        — < 1 h, plus 0–48 h DNS propagation
    → SPF/DKIM/DMARC on a send subdomain — < 1 h once the domain is live
      → wire transactional SMTP; first real email is sent
        → sender-reputation warm-up starts HERE, not at provisioning
          → ~2–3 weeks of calendar time (an unverified planning placeholder)
            → external beta can send branded email
```

Every engineering step takes less than a day. The multi-week part is warm-up, and its
clock starts at **first real send**, not when the records are provisioned. So it cannot
start early, and nobody can speed it up. A slip in the decision is **added** to the
warm-up tail, because each link depends strictly on the one before.

The roadmap had placed this issue in a later beta cycle, after other beta work, which
treated it as if it depended on that work. Its only real dependency was the decision.
The plan's recommendation: make the call in the next decision session along with the
other beta-cycle calls, and run the mechanical steps right after it in the same ticket.

The plan also kept an important limit: internal alpha did not need any of this. A
recorded decision let alpha run on the host's own subdomain, and nothing in the tree
required a custom domain to boot (the site-URL settings fell back to the request host
instead of erroring). So the critical-path claim is scoped to *external* beta, which is
where it holds.

## Some decisions expire

The URL-shape decision behind this domain carried a note that it *"has an expiry, which
is why it is taken before the code needs it"*. Deep links were going to be printed on
physical QR placards in partner venues. A printed placard cannot be re-issued, so the URL
shape **freezes at the first partner print**. A decision like that has to be made
before the first irreversible use, which may be much earlier than the first code that
needs it.

## Check that the option can actually be had

The recorded URL decision named an apex domain. When someone finally checked it, the
domain belonged to an unrelated company: a ten-year registration, transfer-locked, with
live MX records serving that company's email. *"A domain with live MX records and a
ten-year registration is not a backorder candidate; it is a broker negotiation with an
unbounded price and timeline."* The decision had chosen an option that could not be
obtained. The plan written three days *before* that decision still said `ready` and
told an operator to buy a different apex (see [[Readiness Is Pinned to a Tree State]]).
The fix was a decision boundary, "buy nothing yet," with an NS-lookup table of
alternatives. No delegated nameservers counts as strong evidence that a domain is free,
but it is not a registrar quote. Later it turned out a suitable domain was already
owned. An open question the plan had raised itself ("is there already a domain?") was
answered in an issue comment that the next rewrite missed.

## Rules

- Price the critical path by what each step **depends on**, not by where the roadmap
  places it.
- When a calendar clock starts at an event (first send, first print, first index), work
  backwards from that event. Provisioning doesn't count as the start.
- Make decisions that have no dependencies and cost nothing as early as possible, and
  keep them out of the engineering lane. An agent should not make them. It should lay out
  the options and the cost of each day of delay.
- Before recording a decision that names a specific resource (a domain, a handle, a
  vendor tier), check that the resource can be obtained.
- Mark estimates with no committed source as `UNVERIFIED` right on the path diagram, so
  a placeholder doesn't harden into a date.

## See Also
- [[Paid Tiers Start at the Beta, Not the Alpha]] — related (an unset spend cap silently stopped three weeks of scheduled jobs)
- [[Deferred Decision Status]] — extends (a deferral needs a trigger; a long-lead decision needs a deadline)
- [[Readiness Is Pinned to a Tree State]] — alternative-to (the same plan's other failure: a READY that predated its decision)
- [[Plan Epistemic State Axis]] — prerequisite-for (keeping measured, inferred, and unverified claims apart on the path)
- [[Transactional Email Sender Setup]] — prerequisite-for (the DNS, template, and verification checklist behind the chain)
