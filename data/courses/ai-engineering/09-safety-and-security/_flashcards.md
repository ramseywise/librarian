---
generated_by: tools/slides/flashcards.py
decks:
- ai-engineering/09-safety-and-security/slides/deck.yaml
cards:
- front: Which combination of capabilities can make an agent leak?
  back: An agent with untrusted input, private data and external communication can be made to leak.
  lesson: ai-engineering/09-safety-and-security/notes/01-threat-model
- front: Why can a build check the lethal trifecta automatically?
  back: The trifecta is a property of the tool list, so a build can check it automatically.
  lesson: ai-engineering/09-safety-and-security/notes/01-threat-model
- front: Besides injection, which paths should a threat model list?
  back: List paths for privacy, supply chain, misuse and accidental harm, as well as for injection.
  lesson: ai-engineering/09-safety-and-security/notes/01-threat-model
- front: Who owns jailbreaks and who owns prompt injection?
  back: Jailbreaks are mostly a model problem, and injection is mostly a system design problem.
  lesson: ai-engineering/09-safety-and-security/notes/02-prompt-injection-and-jailbreaks
- front: Why must an injection detector trade missed attacks against false alarms?
  back: Injected and legitimate text overlap, so detectors trade missed attacks against false alarms.
  lesson: ai-engineering/09-safety-and-security/notes/02-prompt-injection-and-jailbreaks
- front: What does the Dual LLM pattern separate, and what does that limit?
  back: Separating the model that reads untrusted text from the one with tools limits what a fooled model can do.
  lesson: ai-engineering/09-safety-and-security/notes/02-prompt-injection-and-jailbreaks
- front: What must you measure alongside a provenance policy that stops an attack?
  back: A provenance policy can stop the attack outright, at a utility cost you should measure.
  lesson: ai-engineering/09-safety-and-security/notes/02-prompt-injection-and-jailbreaks
- front: What do input rails protect, and what do output rails protect?
  back: Input rails protect what the model sees, and output rails protect what users see.
  lesson: ai-engineering/09-safety-and-security/notes/03-guardrail-models
- front: What happens to a guardrail's recall and precision as harmful traffic gets rarer?
  back: Recall holds as harmful traffic gets rarer, while precision collapses and nearly every flag is false.
  lesson: ai-engineering/09-safety-and-security/notes/03-guardrail-models
- front: What does a guardrail cascade buy you?
  back: A cascade gets near-large-model accuracy at far lower average latency.
  lesson: ai-engineering/09-safety-and-security/notes/03-guardrail-models
- front: What should you track that never shows up in a single reply?
  back: Track false refusals and paired fairness gaps, because neither one shows up in a single reply.
  lesson: ai-engineering/09-safety-and-security/notes/03-guardrail-models
- front: What can a short policy function check before a tool runs, and where does identity come from?
  back: A short function can check tool choice, ownership and amount with identity taken from the session.
  lesson: ai-engineering/09-safety-and-security/notes/04-tool-and-execution-sandboxing
- front: What gives layered defences real depth?
  back: Layers with different blind spots give real depth, and a stack of similar filters doesn't.
  lesson: ai-engineering/09-safety-and-security/notes/04-tool-and-execution-sandboxing
- front: What do process limits stop, and what needs a stronger boundary?
  back: Process limits stop runaway work, and only a stronger boundary stops reads outside the directory.
  lesson: ai-engineering/09-safety-and-security/notes/04-tool-and-execution-sandboxing
- front: How do you close the way out and notice a changed tool definition?
  back: Filter network and rendered links, and hash the tool definitions you reviewed so changes stand out.
  lesson: ai-engineering/09-safety-and-security/notes/04-tool-and-execution-sandboxing
- front: What should happen to each confirmed red-team finding?
  back: Automated adversaries scale testing, and each confirmed finding should become a permanent test.
  lesson: ai-engineering/09-safety-and-security/notes/05-red-teaming-tools
- front: Why point red-team tools at the whole application and not a bare model?
  back: Point these tools at the whole application, since a bare model scan can't see your tools or data.
  lesson: ai-engineering/09-safety-and-security/notes/05-red-teaming-tools
- front: What true attack rate can zero successes in twenty tries still allow?
  back: Zero successes in twenty tries still allows a true attack rate of about 16%.
  lesson: ai-engineering/09-safety-and-security/notes/05-red-teaming-tools
- front: When does a security test count as passed?
  back: Count a security test as passed only with harm in the baseline and a recorded denial when guarded.
  lesson: ai-engineering/09-safety-and-security/notes/05-red-teaming-tools
- front: What does each of campaigns and suites contribute?
  back: Campaigns find what suites don't know about, and suites keep those findings fixed.
  lesson: ai-engineering/09-safety-and-security/notes/05-red-teaming-tools
- front: How does AI incident response differ from standard incident response?
  back: Standard incident response applies, with non-determinism, sensitive evidence and persistent bad inputs added.
  lesson: ai-engineering/09-safety-and-security/notes/06-incident-response
- front: Why build narrow, tested kill switches?
  back: Narrow, tested kill switches let you act quickly, while keeping most of the product running.
  lesson: ai-engineering/09-safety-and-security/notes/06-incident-response
- front: What makes finding everyone affected a simple query?
  back: With retrieved document IDs in your traces, finding everyone affected becomes a simple query.
  lesson: ai-engineering/09-safety-and-security/notes/06-incident-response
- front: After removing a bad input, what else must you clear and evaluate?
  back: Clear everything derived from a bad input, and evaluate retrained models on agentic tasks.
  lesson: ai-engineering/09-safety-and-security/notes/06-incident-response
- front: When is an AI incident finished?
  back: An incident is finished once a regression test, threat-model update and detection rule exist.
  lesson: ai-engineering/09-safety-and-security/notes/06-incident-response
- front: What decides whether Harbour is high-risk under the EU AI Act, and where should that check live?
  back: High-risk status comes in through the roadmap, so put an Annex III check in feature review, where stopping it is cheap.
  lesson: ai-engineering/09-safety-and-security/notes/07-compliance-and-regulation
- front: Why can an older summary of the EU AI Act give you the wrong compliance date?
  back: Annex III duties now start on 2 December 2027 while transparency already applies, so check the amendment and date your notes.
  lesson: ai-engineering/09-safety-and-security/notes/07-compliance-and-regulation
- front: Why doesn't a vendor's paperwork or setting answer a customer's compliance questionnaire?
  back: The answers depend on what your system does with data, so keep a register of every place it goes and have a person own it.
  lesson: ai-engineering/09-safety-and-security/notes/07-compliance-and-regulation
- front: If you assume the model will be fooled, what do you limit and test?
  back: Assume the model will be fooled, limit what a fooled model can do, and test that the limit holds.
  lesson: ai-engineering/09-safety-and-security/notes/01-threat-model
- front: What's the first step in securing your agent?
  back: Start by drawing your own system and listing its paths from untrusted text to a way out.
  lesson: ai-engineering/09-safety-and-security/notes/01-threat-model
---
