---
title: "Data Mesh Topologies by Domain Granularity and Distribution"
tags: [data-engineering, architecture-and-governance, comparison]
summary: "Strengholt describes six data mesh topologies that differ in domain granularity and in whether data moves peer to peer or through a central distribution layer, with the costs he sees in each."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-strengholt-data-mesh-topologies.md
---
# Data Mesh Topologies by Domain Granularity and Distribution

Strengholt asks which mesh architectures companies adopt and what drives each choice. He describes six scenarios, separated by domain granularity and by peer-to-peer versus centrally governed distribution. All of it is his observation of customer architecture sessions at Microsoft: opinion, with no measurement.

| Scenario | Shape | What he reports |
|---|---|---|
| 1. Fully federated, fine-grained | Domains publish to each other directly | Described as Dehghani's purest form; hard to achieve because all domains must conform and infrastructure is duplicated. Costs: capability duplication, heavy network use, cross-domain lookups |
| 2. Fully governed | A central distribution layer sits in front of the domains | Fixes data gravity and conformance; slows time to market and adds coupling. Chosen mostly by financial institutions and governments |
| 3. Hybrid federated | Data-product creation is centralised, sometimes owned by a platform team | Consumers are more autonomous |
| 4. Value-chain mesh | Closely working domains are grouped and treated as a single larger domain | Central standards apply only where one chain meets another |
| 5. Coarse-grained aligned | Domains hold tens or hundreds of applications | Capabilities such as data quality and master data management tend to be duplicated |
| 6. Coarse-grained governed | Scenario 5 plus a central distribution platform or marketplace | Fails without a strong central mandate |

## Practices he gives

- Before a coarse-grained mesh (scenario 5), decompose the domains properly, settle who owns each application and its data, and guide data-product creation firmly. In coarse-grained meshes, take in only unique data, straight from where it originates.
- In scenario 2 he describes a multiple-workspaces-shared-lake design: domains build data products in their own workspaces, and distribution to other domains goes through a central storage layer with a container per domain.
- His term *architectural quantum* means that many different small data-product architectures may be instantiated for serving and pulling data across domains.
- His conclusion is that no topology is right or wrong, and that mesh is best treated as a framework: implement what works.

## Limits

- The account is anecdotal, drawn from the author's customer conversations at Microsoft, with no counts, sample or measurement.
- The saved page carries no publication date.
- The author expects, and does not show, that scenario 2 is difficult across multiple clouds.
- The author's employer (Microsoft) and his book *Data Management at Scale*, recommended at the end, are context to weigh.

## See Also
- [[Data Mesh as an Ownership Model and Federated Governance]] — prerequisite-for
- [[Warehouse, Fabric and Lakehouse: Sizing the Physical Architecture]] — related
