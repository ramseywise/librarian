---
generated_by: src/librarian/tools/slides/flashcards.py
decks:
- data-engineering/07-architecture-and-governance/slides/deck.yaml
cards:
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
- front: How should you pseudonymise an identifier, and what does sharing a key across domains mean?
  back: Use a keyed hash with the key outside the lake, and treat sharing a key across domains as a deliberate decision to link people.
  lesson: data-engineering/07-architecture-and-governance/notes/02-access-control-pii-gdpr
- front: Why is removing names not anonymising?
  back: Removing names is not anonymising, since behaviour and demographics can single people out and be joined to public lists.
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
- front: How do you work out who a change to a column will hurt?
  back: Follow the chain to named owners, check the log for unregistered readers, and give a new unit a new column name.
  lesson: data-engineering/07-architecture-and-governance/notes/03b-data-contracts-who-a-change-reaches
- front: Where does governance actually exist?
  back: Decide ownership and enforcement before you need them, because governance only exists where a step can fail.
  lesson: data-engineering/07-architecture-and-governance/notes/01-data-architectures-mesh-fabric-mdw
- front: Where next
  back: Run the chapters' code, then bring real erasure and breach cases to a data protection officer instead of deciding alone.
  lesson: data-engineering/07-architecture-and-governance/notes/02-access-control-pii-gdpr
---
