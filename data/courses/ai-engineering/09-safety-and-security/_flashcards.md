---
generated_by: src/librarian/tools/slides/flashcards.py
decks:
- ai-engineering/09-safety-and-security/slides/deck.yaml
cards:
- front: What are the six parts of this lecture, in order?
  back: The parts follow the notes, from what can go wrong, through the defences and the tests of them, to what to do when one is breached.
  lesson: ai-engineering/09-safety-and-security/readme
- front: Name four things this lecture teaches you to do with an agent's security.
  back: You will be able to map an agent's paths, enforce limits outside the model, test them honestly and respond when they fail.
  lesson: ai-engineering/09-safety-and-security/readme
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
- front: What gives layered defences real depth?
  back: Layers with different blind spots give real depth, and a stack of similar filters doesn't.
  lesson: ai-engineering/09-safety-and-security/notes/04-tool-and-execution-sandboxing
- front: What can a short policy function check before a tool runs, and where does identity come from?
  back: A short function can check tool choice, ownership and amount with identity taken from the session.
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
- front: Why is prompt injection unlike SQL injection?
  back: SQL has a protocol-level separation of code and data, so parameterised queries remove the bug class. A prompt is one token sequence, and roles are only trained conventions, so no equivalent guarantee exists.
  lesson: ai-engineering/09-safety-and-security/notes/01-threat-model
- front: What is the lethal trifecta?
  back: Access to private data, exposure to untrusted content and the ability to communicate externally. Together they let injected text steal data, and removing any one prevents that specific outcome.
  lesson: ai-engineering/09-safety-and-security/notes/01-threat-model
- front: What does the trifecta leave out?
  back: 'Integrity. An agent with untrusted input and a refund or delete tool can do damage with no private data or exit. Generalise to: can untrusted text cause any consequential action?'
  lesson: ai-engineering/09-safety-and-security/notes/01-threat-model
- front: How do you enforce access control in RAG?
  back: Filter by the authenticated caller inside the retriever, before the model sees results. The caller comes from the session and is never a model-supplied argument.
  lesson: ai-engineering/09-safety-and-security/notes/01-threat-model
- front: OWASP LLM Top 10 or MITRE ATLAS, which do you use?
  back: OWASP as an application checklist, ATLAS to describe the steps of an attack, often when working with a security team. NIST AI 100-2 gives the taxonomy behind both.
  lesson: ai-engineering/09-safety-and-security/notes/01-threat-model
- front: Are reasoning traces safe to log freely?
  back: No. Green et al. found they frequently contain sensitive user data, more so with larger reasoning budgets. Give them the same retention and access rules as the input.
  lesson: ai-engineering/09-safety-and-security/notes/01-threat-model
- front: What makes misuse hard to catch per request?
  back: Capability laundering splits a harmful task into harmless-looking subtasks, so no single response is harmful. Detection needs a view across requests.
  lesson: ai-engineering/09-safety-and-security/notes/01-threat-model
- front: How do you rank an agent's attack paths on a first pass?
  back: Enumerate source, sink and whether a human or a control sits between them, then rank by the severity of the sink.
  lesson: ai-engineering/09-safety-and-security/notes/01-threat-model
- front: Jailbreak or injection, what's the difference?
  back: A jailbreak overrides the model's safety training, usually by the user, and yields bad content. An injection overrides the application's instructions, usually through third-party data, and yields actions or leaks the user didn't ask for.
  lesson: ai-engineering/09-safety-and-security/notes/02-prompt-injection-and-jailbreaks
- front: Why isn't a classifier enough?
  back: It is heuristic, attackers can retry and adapt, and legitimate text looks similar. It lowers the rate but gives no boundary, and AgentDojo found a detector cut attacks to 8% while degrading utility.
  lesson: ai-engineering/09-safety-and-security/notes/02-prompt-injection-and-jailbreaks
- front: Explain the dual LLM pattern.
  back: A privileged model has tools and sees only trusted text. A quarantined model reads untrusted text and has no tools. The privileged one passes its output around as opaque variables, so the text can't steer it.
  lesson: ai-engineering/09-safety-and-security/notes/02-prompt-injection-and-jailbreaks
- front: What does CaMeL add to it?
  back: Capabilities on each value, recording sources and allowed readers, enforced by an interpreter at tool calls. So untrusted text can't choose a recipient or flow data somewhere it isn't allowed. It solved 77% of AgentDojo tasks with provable security against 84% undefended.
  lesson: ai-engineering/09-safety-and-security/notes/02-prompt-injection-and-jailbreaks
- front: What does plan-then-execute leave open?
  back: Arguments. The tools are fixed, but untrusted text can change the values passed to them unless those flows are also constrained.
  lesson: ai-engineering/09-safety-and-security/notes/02-prompt-injection-and-jailbreaks
- front: How would you report a defence's effectiveness?
  back: Attack success and utility together, tested with attacks adapted to that defence, stating what scope any guarantee covers.
  lesson: ai-engineering/09-safety-and-security/notes/02-prompt-injection-and-jailbreaks
- front: Does instruction hierarchy training solve injection?
  back: It helps a lot and doesn't give a guarantee. Use it, keep tool output in its own role, and still design for the model being fooled.
  lesson: ai-engineering/09-safety-and-security/notes/02-prompt-injection-and-jailbreaks
- front: Why is accuracy wrong for a guard?
  back: Harm is rare, so flagging nothing scores high. Use recall, FPR, and precision at your deployment's base rate.
  lesson: ai-engineering/09-safety-and-security/notes/03-guardrail-models
- front: Why does a good guard feel bad in production?
  back: Recall and FPR don't change with base rate, but precision does. At a low base rate, most flags are false alarms.
  lesson: ai-engineering/09-safety-and-security/notes/03-guardrail-models
- front: How does Llama Guard adapt to a new policy?
  back: The taxonomy is part of the input, so you can change it with zero- or few-shot prompting. Then re-measure, as the performance isn't inherited.
  lesson: ai-engineering/09-safety-and-security/notes/03-guardrail-models
- front: What can Granite Guardian check that a toxicity filter can't?
  back: RAG risks such as groundedness, context relevance and answer relevance, as well as jailbreak and harm classes.
  lesson: ai-engineering/09-safety-and-security/notes/03-guardrail-models
- front: How do you reduce the latency of guarding?
  back: Run input checks in parallel, cascade from a small model to a large one on uncertain cases, and buffer streamed output.
  lesson: ai-engineering/09-safety-and-security/notes/03-guardrail-models
- front: How do you measure bias without demographic data?
  back: 'Counterfactual pairs: same prompt, names swapped, repeated samples, compare an outcome. First-Person Fairness used this at scale.'
  lesson: ai-engineering/09-safety-and-security/notes/03-guardrail-models
- front: What three kinds of refusal should be separated?
  back: 'Per Wen et al.: the query isn''t answerable, the model isn''t confident, or the answer conflicts with values. Each needs a different fix.'
  lesson: ai-engineering/09-safety-and-security/notes/03-guardrail-models
- front: What is excessive agency?
  back: 'OWASP LLM06: an agent with more tools, permissions or autonomy than its task needs. The fix is least agency, per task and per user.'
  lesson: ai-engineering/09-safety-and-security/notes/04-tool-and-execution-sandboxing
- front: Where does a refund limit belong?
  back: In the tool layer, in plain code, since a prompt rule can be argued around. The model's output is a proposal.
  lesson: ai-engineering/09-safety-and-security/notes/04-tool-and-execution-sandboxing
- front: What's a confused deputy here?
  back: A privileged tool acting on another party's behalf because it trusted a model-supplied identity. Bind identity from the session and use per-user credentials.
  lesson: ai-engineering/09-safety-and-security/notes/04-tool-and-execution-sandboxing
- front: Are rlimits and a clean env enough for model-written code?
  back: They stop runaway resources and environment leaks, and they don't confine files or network. Use a container with no network, or a microVM for untrusted code.
  lesson: ai-engineering/09-safety-and-security/notes/04-tool-and-execution-sandboxing
- front: How can a chat reply leak data without any tool?
  back: A rendered Markdown image or link carrying data in its URL. The browser's request is the exfiltration. Allow-list at the renderer.
  lesson: ai-engineering/09-safety-and-security/notes/04-tool-and-execution-sandboxing
- front: How would you secure an MCP server you installed?
  back: Pin a hash of each tool definition, fail closed on change, scope its credentials, restrict its network, and review new versions like code.
  lesson: ai-engineering/09-safety-and-security/notes/04-tool-and-execution-sandboxing
- front: Why treat an agent's skill library as supply chain?
  back: Agents can self-poison by imitating bad skills, as EvoMal measured, and removing the originals doesn't fully clear it. Gate and attribute writes.
  lesson: ai-engineering/09-safety-and-security/notes/04-tool-and-execution-sandboxing
- front: How should a tool hold credentials?
  back: Give each call a short-lived token scoped to the customer in the session, so a policy bypass still meets a database that says no. The tool layer injects it, because anything the model can read an injection can try to print.
  lesson: ai-engineering/09-safety-and-security/notes/04-tool-and-execution-sandboxing
- front: What was Perez et al.'s contribution?
  back: Using one model to red-team another at scale, with a classifier as judge, which uncovered tens of thousands of offensive replies without hand-writing test cases.
  lesson: ai-engineering/09-safety-and-security/notes/05-red-teaming-tools
- front: How does MART differ?
  back: It's iterative. An adversary writes attacks, the target is safety-tuned, and the adversary has to find new ones. It reported violation rates down by up to 84.7% after four rounds.
  lesson: ai-engineering/09-safety-and-security/notes/05-red-teaming-tools
- front: garak, PyRIT or promptfoo?
  back: garak for a broad scanner sweep, PyRIT to script custom campaigns, promptfoo for app-specific attacks and CI next to evals. They overlap, so choose by the question.
  lesson: ai-engineering/09-safety-and-security/notes/05-red-teaming-tools
- front: You got 0 successes in 20 tries. What can you claim?
  back: At 95%, the true rate may still be about 16%. Report the bound and do more runs, or show that the control holds by construction.
  lesson: ai-engineering/09-safety-and-security/notes/05-red-teaming-tools
- front: How can a safety test pass while measuring nothing?
  back: The model didn't try, or the harness missed it. So require a baseline run where harm occurs, and evidence of denial in the guarded run. Otherwise report inconclusive.
  lesson: ai-engineering/09-safety-and-security/notes/05-red-teaming-tools
- front: Static suite or adaptive attack?
  back: Both. The suite prevents regressions cheaply, on every change. Adaptive campaigns find what the suite doesn't know about, and each finding joins the suite.
  lesson: ai-engineering/09-safety-and-security/notes/05-red-teaming-tools
- front: What do you check when reading an attack success rate?
  back: The target, the judge and its errors, attempts allowed, behaviours tested, whether the attack was adapted to the defence, and the utility cost.
  lesson: ai-engineering/09-safety-and-security/notes/05-red-teaming-tools
- front: What's different about LLM incident response?
  back: Runs may not reproduce, there's often no error, the evidence is sensitive, and bad input can persist in stores and affect later users.
  lesson: ai-engineering/09-safety-and-security/notes/06-incident-response
- front: What must be logged to investigate?
  back: Model and prompt versions, retrieved document IDs and versions, tool calls and results, policy decisions, session and customer, with redaction, access control and retention.
  lesson: ai-engineering/09-safety-and-security/notes/06-incident-response
- front: What do you do first?
  back: Preserve evidence and use the narrowest switch that stops the harm, such as one tool. Then scope it.
  lesson: ai-engineering/09-safety-and-security/notes/06-incident-response
- front: How do you find the blast radius?
  back: Start from the bad input, find each session that touched it, list what those sessions did, and state gaps in the logs as unknown.
  lesson: ai-engineering/09-safety-and-security/notes/06-incident-response
- front: Why isn't deleting a poisoned skill enough?
  back: Derived copies remain. EvoMal reported rates as high as 68% after removal. Follow lineage or rebuild from a known-good snapshot.
  lesson: ai-engineering/09-safety-and-security/notes/06-incident-response
- front: Can a monitor replace controls?
  back: No. SHADE-Arena's best monitor reached an AUC of 0.87, and monitors see only what's shown to them. It's a detection layer next to hard controls.
  lesson: ai-engineering/09-safety-and-security/notes/06-incident-response
- front: How would you monitor misuse that's invisible per conversation?
  back: Look jointly across a user's requests, and across users in aggregate. Clio describes doing this while limiting human access to raw conversations.
  lesson: ai-engineering/09-safety-and-security/notes/06-incident-response
- front: What should an incident leave behind?
  back: A regression case, an updated threat model and a detection rule.
  lesson: ai-engineering/09-safety-and-security/notes/06-incident-response
- front: Provider or deployer?
  back: A provider develops or commissions a system and puts it out under its own name. A deployer uses it under its authority. Building on a model API for your own use commonly makes you both.
  lesson: ai-engineering/09-safety-and-security/notes/07-compliance-and-regulation
- front: When can a deployer become a provider?
  back: 'Article 25(1): rebranding, substantial modification, or changing the intended purpose so a system becomes high-risk.'
  lesson: ai-engineering/09-safety-and-security/notes/07-compliance-and-regulation
- front: What makes a system high-risk?
  back: A safety component in a regulated product, or a listed Annex III use, such as credit scoring, hiring or managing workers. The use decides, not the model.
  lesson: ai-engineering/09-safety-and-security/notes/07-compliance-and-regulation
- front: When do high-risk duties apply?
  back: 'As amended by Regulation 2026/1744: 2 December 2027 for Annex III, 2 August 2028 for Annex I. The original dates were a year or more earlier.'
  lesson: ai-engineering/09-safety-and-security/notes/07-compliance-and-regulation
- front: What applies to a plain support bot today?
  back: Tell people it's an AI unless that's obvious, consider output marking, and apply the prohibitions and other law, such as GDPR.
  lesson: ai-engineering/09-safety-and-security/notes/07-compliance-and-regulation
- front: What's a SOC 2 report?
  back: A CPA's report on a service organisation's controls against the Trust Services Criteria. Read the scope, categories, period and exceptions. It's no statement about model quality.
  lesson: ai-engineering/09-safety-and-security/notes/07-compliance-and-regulation
- front: When does HIPAA apply to an AI vendor?
  back: When it creates, receives, maintains or transmits PHI on behalf of a covered entity, directly or as a subcontractor. A written contract has to come first.
  lesson: ai-engineering/09-safety-and-security/notes/07-compliance-and-regulation
- front: Does de-identifying solve HIPAA?
  back: If it meets §164.514, yes. Free text makes the safe harbor hard, as 18 identifier types must go and you must have no actual knowledge of re-identification.
  lesson: ai-engineering/09-safety-and-security/notes/07-compliance-and-regulation
- front: What does data residency miss?
  back: Logs, support access, sub-processors and your own stores. For EU data, ask about the transfer mechanism, not just the region.
  lesson: ai-engineering/09-safety-and-security/notes/07-compliance-and-regulation
- front: Is ZDR the same across vendors?
  back: No. It's by arrangement, it has exceptions such as flagged content or required abuse logs, and it can exclude features and models. Your own traces aren't touched.
  lesson: ai-engineering/09-safety-and-security/notes/07-compliance-and-regulation
- front: How do you avoid compliance theatre?
  back: 'Tie each duty to something the system already produces: traces, evals, approval records and rollout gates.'
  lesson: ai-engineering/09-safety-and-security/notes/07-compliance-and-regulation
---
