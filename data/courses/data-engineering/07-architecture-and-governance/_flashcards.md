---
generated_by: src/librarian/tools/slides/flashcards.py
decks:
- data-engineering/07-architecture-and-governance/slides/deck.yaml
cards:
- front: What are the six parts of this lecture, in order?
  back: The first two parts decide where data lives and who owns it, and the last four decide who may see it, keep it, remove it and be told when it changes.
  lesson: data-engineering/07-architecture-and-governance/readme
- front: Name four things this lecture teaches you to do.
  back: You will be able to place data, protect it, define it once and say who a change will break.
  lesson: data-engineering/07-architecture-and-governance/readme
- front: How do a modern data warehouse, a lakehouse and a data fabric differ?
  back: An MDW keeps a lake and a warehouse, a lakehouse drops the warehouse copy, and a fabric adds a governance layer on top.
  lesson: data-engineering/07-architecture-and-governance/notes/01-data-architectures-mesh-fabric-mdw
- front: What should you run before buying a cluster, and what does it not test?
  back: Run a representative query on one machine before buying a cluster, and remember that it tests volume and not concurrency.
  lesson: data-engineering/07-architecture-and-governance/notes/01-data-architectures-mesh-fabric-mdw
- front: How should you treat the size figures, and why is a mesh not a fourth option?
  back: The size figures are one practitioner's judgement, and a mesh is not a fourth option because it changes owners and not storage.
  lesson: data-engineering/07-architecture-and-governance/notes/01-data-architectures-mesh-fabric-mdw
- front: What do you ask first when choosing how to unify data, and why?
  back: Ask where each fact is written first, because what is derived can be rebuilt and a bug in it is cheap.
  lesson: data-engineering/07-architecture-and-governance/notes/01-data-architectures-mesh-fabric-mdw
- front: What does a mesh decentralise, and what stays central?
  back: A mesh decentralises ownership and products while keeping a central platform and a joint governance group.
  lesson: data-engineering/07-architecture-and-governance/notes/01b-data-mesh-topologies-and-scenarios
- front: What is the smallest self-serve platform that governs anything?
  back: One publish call that runs the mandatory checks and records dependencies is the smallest self-serve platform that governs anything.
  lesson: data-engineering/07-architecture-and-governance/notes/01b-data-mesh-topologies-and-scenarios
- front: When does a global standard actually take effect?
  back: A standard only takes effect when a step no domain can skip enforces it and routes each failure to a named owner.
  lesson: data-engineering/07-architecture-and-governance/notes/01b-data-mesh-topologies-and-scenarios
- front: How does the skeptic case say you should adopt a mesh?
  back: Take the mesh as principles to adopt selectively, starting with ownership on a shared platform, and decentralise technology last.
  lesson: data-engineering/07-architecture-and-governance/notes/01b-data-mesh-topologies-and-scenarios
- front: Which axes separate real mesh shapes, and what does each shape trade?
  back: Domain size and the way data moves separate six real mesh shapes, and each one trades agility against conformance.
  lesson: data-engineering/07-architecture-and-governance/notes/01b-data-mesh-topologies-and-scenarios
- front: Why start governance from a scanned inventory of personal data?
  back: You cannot protect a column you do not know is personal, so scan values as well as names and start from that inventory.
  lesson: data-engineering/07-architecture-and-governance/notes/02-access-control-pii-gdpr
- front: What do you use roles for, and what do you use attributes for?
  back: Use roles for coarse table grants and attributes for row and purpose rules, since most real systems need both.
  lesson: data-engineering/07-architecture-and-governance/notes/02-access-control-pii-gdpr
- front: What is the access boundary with an embedded engine, and how do you enforce it?
  back: With an embedded engine the boundary is what the process can touch, so publish masked copies and lock the connection.
  lesson: data-engineering/07-architecture-and-governance/notes/02-access-control-pii-gdpr
- front: What does Article 33 ask for, by when, and what can supply it?
  back: Article 33 asks for categories and approximate numbers within 72 hours of awareness, which only a log kept in advance can supply.
  lesson: data-engineering/07-architecture-and-governance/notes/02-access-control-pii-gdpr
- front: What are three gaps that survive good access control?
  back: Access control leaves gaps in free text, in copies outside production and in a log that was never kept, so include each in the inventory and the coverage check.
  lesson: data-engineering/07-architecture-and-governance/notes/02-access-control-pii-gdpr
- front: Why is removing names not anonymising?
  back: Removing names is not anonymising, since behaviour and demographics can single people out and be joined to public lists.
  lesson: data-engineering/07-architecture-and-governance/notes/02-access-control-pii-gdpr
- front: How should you pseudonymise an identifier, and what does sharing a key across domains mean?
  back: Use a keyed hash with the key outside the lake, and treat sharing a key across domains as a deliberate decision to link people.
  lesson: data-engineering/07-architecture-and-governance/notes/02-access-control-pii-gdpr
- front: Why is k-anonymity alone not enough?
  back: k-anonymity stops singling out but not inference, so check each group for several sensitive values and treat the result as personal data until the DPO argues it down.
  lesson: data-engineering/07-architecture-and-governance/notes/02-access-control-pii-gdpr
- front: Why must the path from erasure request to verified deletion be scheduled in advance?
  back: The right to erasure has a one-month clock, so the path from request to verified deletion has to be scheduled in advance.
  lesson: data-engineering/07-architecture-and-governance/notes/02-access-control-pii-gdpr
- front: What is erasure across copies, and what window must it fit?
  back: Erasure is a set of mechanisms over every copy, and it has to fit inside Article 12's one-month response window.
  lesson: data-engineering/07-architecture-and-governance/notes/02-access-control-pii-gdpr
- front: What does an automated check show that a deletion ticket does not?
  back: Automate a check across every store, because the ticket reports what was deleted and only the check shows what remains.
  lesson: data-engineering/07-architecture-and-governance/notes/02-access-control-pii-gdpr
- front: How do you keep processing records so that a gap surfaces before a regulator finds it?
  back: Keep processing records as data with a required-fields test, so a gap fails a check and does not wait for a regulator.
  lesson: data-engineering/07-architecture-and-governance/notes/02-access-control-pii-gdpr
- front: How does a semantic layer stop a fan-out, a mean of ratios and a summed balance?
  back: A semantic layer holds metrics and join keys as data and compiles each request at its grain, so nobody rewrites the join or the division.
  lesson: data-engineering/07-architecture-and-governance/notes/03-catalog-semantic-layer-and-contracts
- front: What are four ways a catalog or metric layer looks finished and is not?
  back: A catalog measured by coverage, a certification that never expires, a tier read as trust and metric logic left in BI tools all look finished while people still disagree.
  lesson: data-engineering/07-architecture-and-governance/notes/03-catalog-semantic-layer-and-contracts
- front: How do you work out who a change to a column will hurt?
  back: Follow the chain to named owners, check the log for unregistered readers, and give a new unit a new column name.
  lesson: data-engineering/07-architecture-and-governance/notes/03b-data-contracts-who-a-change-reaches
- front: Where does governance actually exist?
  back: Decide ownership and enforcement before you need them, because governance only exists where a step can fail.
  lesson: data-engineering/07-architecture-and-governance/notes/01-data-architectures-mesh-fabric-mdw
- front: What do you do with real erasure and breach cases?
  back: Run the chapters' code, then bring real erasure and breach cases to a data protection officer instead of deciding alone.
  lesson: data-engineering/07-architecture-and-governance/notes/02-access-control-pii-gdpr
- front: What separates an MDW from a lakehouse?
  back: An MDW copies at least some data from the lake into a relational warehouse. A lakehouse copies none and serves from the lake through a table format.
  lesson: data-engineering/07-architecture-and-governance/notes/01-data-architectures-mesh-fabric-mdw
- front: Federation or unbundling?
  back: Federation unifies reads, with one interface over many stores (virtualization). Unbundling unifies writes, with a log and derived views keeping stores in step (ELT, CDC).
  lesson: data-engineering/07-architecture-and-governance/notes/01-data-architectures-mesh-fabric-mdw
- front: What makes an MDW a data fabric?
  back: 'Added features: access policies, catalog, MDM, virtualization, real time, APIs, services, products. Serra''s personal line is three or more, and he admits it is fuzzy.'
  lesson: data-engineering/07-architecture-and-governance/notes/01-data-architectures-mesh-fabric-mdw
- front: When is one node enough?
  back: Serra's example is under 1 TB; measure a representative query first. Volume alone rarely justifies MPP at that size, though concurrency can.
  lesson: data-engineering/07-architecture-and-governance/notes/01-data-architectures-mesh-fabric-mdw
- front: Is a data mesh an architecture?
  back: Mainly an ownership and organisational model. Each domain still runs an MDW, fabric or lakehouse.
  lesson: data-engineering/07-architecture-and-governance/notes/01b-data-mesh-topologies-and-scenarios
- front: Name the four principles.
  back: Domain ownership, data as a product, self-serve platform, federated computational governance.
  lesson: data-engineering/07-architecture-and-governance/notes/01b-data-mesh-topologies-and-scenarios
- front: Why can't domain tests catch `CA` against `California`?
  back: Each table is valid by its own rules. The failure is between products, so it takes a global rule run by the platform, plus a shared mapping.
  lesson: data-engineering/07-architecture-and-governance/notes/01b-data-mesh-topologies-and-scenarios
- front: What's the minimum to call something a mesh?
  back: There is no agreed minimum. Serra argues principle 2 must hold in addition to 1, since federation alone satisfies only 1.
  lesson: data-engineering/07-architecture-and-governance/notes/01b-data-mesh-topologies-and-scenarios
- front: Which mesh shape would you start with?
  back: 'Shared platform, domains owning data: Serra''s Type 1, which is close to Strengholt''s topology 2 (our mapping; Strengholt says there''s no right or wrong). Decentralise technology last.'
  lesson: data-engineering/07-architecture-and-governance/notes/01b-data-mesh-topologies-and-scenarios
- front: A strong case against mesh?
  back: 'Serra''s: warehouses fail from people and process, not scale, and few meshes reach production. Gartner, as he quotes it, expected it to fold into fabric, though he doesn''t.'
  lesson: data-engineering/07-architecture-and-governance/notes/01b-data-mesh-topologies-and-scenarios
- front: Fabric or mesh?
  back: Not a choice between rivals. A mesh can use a fabric inside each domain, and a fabric's catalog and policies help enforce principle 4.
  lesson: data-engineering/07-architecture-and-governance/notes/01b-data-mesh-topologies-and-scenarios
- front: RBAC or ABAC?
  back: RBAC for coarse, auditable grants. ABAC adds subject, object, environment attributes and purpose, for row and purpose rules without a role explosion. Most systems use both.
  lesson: data-engineering/07-architecture-and-governance/notes/02-access-control-pii-gdpr
- front: Why isn't a DuckDB view a security control?
  back: 'The connection can read the base table, and DuckDB has no roles or `GRANT`. Restrict the process instead: separate files, allowed directories, locked configuration, OS permissions.'
  lesson: data-engineering/07-architecture-and-governance/notes/02-access-control-pii-gdpr
- front: 'Pseudonymised or anonymised: what''s the difference?'
  back: Pseudonymised data can be re-attributed with separately held information and remains personal data (Recital 26). Anonymous data can't reasonably be and falls out of scope.
  lesson: data-engineering/07-architecture-and-governance/notes/02-access-control-pii-gdpr
- front: Why is a hashed phone number weak?
  back: The input space is small, so an attacker enumerates it. A shared salt doesn't change that. Use an HMAC with a key held in a KMS, or a vault token.
  lesson: data-engineering/07-architecture-and-governance/notes/02-access-control-pii-gdpr
- front: Name the three anonymisation tests.
  back: Singling out, linkability and inference (WP29 Opinion 05/2014).
  lesson: data-engineering/07-architecture-and-governance/notes/02-access-control-pii-gdpr
- front: What does k-anonymity miss?
  back: A group sharing one sensitive value reveals it. That is the inference test, and l-diversity addresses it. It also depends on having found every quasi-identifier.
  lesson: data-engineering/07-architecture-and-governance/notes/02-access-control-pii-gdpr
- front: How do you delete one person from a Parquet lake?
  back: 'Find the files with that person, rewrite them, then handle every downstream copy. In a table format: delete, then vacuum after the retention window.'
  lesson: data-engineering/07-architecture-and-governance/notes/02-access-control-pii-gdpr
- front: How do you handle backups for erasure?
  back: An erasure ledger replayed on every restore, a retention limit on backups, or crypto-shredding. Agree the design with the DPO, since none of the sources behind this chapter settles the legal standing of key destruction.
  lesson: data-engineering/07-architecture-and-governance/notes/02-access-control-pii-gdpr
- front: When does the 72-hour clock start?
  back: When the controller has reasonable certainty that personal data was compromised (EDPB Guidelines 9/2022). A short investigation may come first and should start promptly.
  lesson: data-engineering/07-architecture-and-governance/notes/02-access-control-pii-gdpr
- front: Is erasure absolute?
  back: No. Article 17(3) excludes legal obligation, some archiving and research, and legal claims. Tax records can stay while a marketing profile goes.
  lesson: data-engineering/07-architecture-and-governance/notes/02-access-control-pii-gdpr
- front: What do you need ready for a breach?
  back: Access logs with user, purpose, query and row count, an inventory, and a playbook. Article 33(3) asks for categories and approximate numbers.
  lesson: data-engineering/07-architecture-and-governance/notes/02-access-control-pii-gdpr
- front: 'Technical or business metadata: what''s the difference?'
  back: Technical can be read from systems (types, runs, lineage). Business comes from people (meaning, owner, trust). Only the first can be crawled.
  lesson: data-engineering/07-architecture-and-governance/notes/03-catalog-semantic-layer-and-contracts
- front: Push or pull ingestion?
  back: 'Pull crawls on a schedule and needs no producer changes, at the cost of lag. Push is immediate and sees only what emits. Run both: pull catches what nobody announced, and deletions.'
  lesson: data-engineering/07-architecture-and-governance/notes/03-catalog-semantic-layer-and-contracts
- front: Tier or certification?
  back: Tier is importance. Certification is a named reviewer's dated quality claim. A table can be tier 1 and uncertified.
  lesson: data-engineering/07-architecture-and-governance/notes/03-catalog-semantic-layer-and-contracts
- front: How do you measure a catalog?
  back: Not coverage alone. Descriptions older than the column's last change, share of warehouse reads on certified tables, tier 1 tables with no reads.
  lesson: data-engineering/07-architecture-and-governance/notes/03-catalog-semantic-layer-and-contracts
- front: What does a semantic layer do?
  back: It holds metrics and join keys as data, and compiles each request to SQL at the grain asked for, so nobody rewrites the join or the division.
  lesson: data-engineering/07-architecture-and-governance/notes/03-catalog-semantic-layer-and-contracts
- front: Why not average a daily ratio?
  back: 'It weights a quiet day like a busy one. Recompute from numerator and denominator at the grain requested. Here: 16.2% against a true 6.7%.'
  lesson: data-engineering/07-architecture-and-governance/notes/03-catalog-semantic-layer-and-contracts
- front: How does MetricFlow avoid fan-out?
  back: From entity types. Joining to a primary or unique key is a left join; foreign to foreign is refused. Cube instead aggregates each fact separately and joins on shared dimensions.
  lesson: data-engineering/07-architecture-and-governance/notes/03-catalog-semantic-layer-and-contracts
- front: How do you model a balance?
  back: 'As semi-additive: `non_additive_dimension` over the date, taking the last row per rider per period, then summing across riders.'
  lesson: data-engineering/07-architecture-and-governance/notes/03-catalog-semantic-layer-and-contracts
- front: A semantic layer or a mart per metric?
  back: A mart fixes a grain at build. A layer keeps the parts and computes at request, reading a modelled table. A few metrics in one tool may not need one.
  lesson: data-engineering/07-architecture-and-governance/notes/03-catalog-semantic-layer-and-contracts
- front: Does a semantic layer improve text-to-SQL?
  back: 'Vendor evidence says inside what''s modelled, yes: dbt''s 11-question test on the normalised schema had 62.5 vs 100 on Sonnet 4.6, and 70.0 vs 0 outside coverage; with 3 extra models, 90.0 vs 98.2. No independent replication that I found.'
  lesson: data-engineering/07-architecture-and-governance/notes/03-catalog-semantic-layer-and-contracts
- front: Data contract or dbt model contract?
  back: A data contract is a cross-team promise including meaning and owner. A dbt model contract is a build check on a model's columns and types.
  lesson: data-engineering/07-architecture-and-governance/notes/03b-data-contracts-who-a-change-reaches
- front: How do you know who a contract's consumers are?
  back: Registration, lineage and the query log, compared with each other. ODCS v3.2.0 has no field for it, on my search of it.
  lesson: data-engineering/07-architecture-and-governance/notes/03b-data-contracts-who-a-change-reaches
- front: Who owns what in a fare change?
  back: The contract owner decides when the column changes. The metric owner decides what revenue means and moves the one line.
  lesson: data-engineering/07-architecture-and-governance/notes/03b-data-contracts-who-a-change-reaches
- front: 'Rename or unit change: which is worse?'
  back: The unit change under the same name. Everything passes and the number is wrong. Give a new unit a new name.
  lesson: data-engineering/07-architecture-and-governance/notes/03b-data-contracts-who-a-change-reaches
- front: Do contracts reduce incidents?
  back: I found no controlled measurement in what I read. Don't quote a percentage without a named source and method.
  lesson: data-engineering/07-architecture-and-governance/notes/03b-data-contracts-who-a-change-reaches
---
