---
title: '09 — Safety and Security: multiple choice and worked problems'
summary: Interview-style questions on this module, 18 multiple choice.
questions:
- id: h1
  prompt: 'Direct vs indirect prompt injection:'
  options:
  - Direct comes from the model's own output; indirect from the user
  - Direct comes from the user's input; indirect arrives via content the agent retrieves or reads
  - Direct targets the system prompt; indirect targets tools
  - Direct is deliberate; indirect is accidental
  answer: Direct comes from the user's input; indirect arrives via content the agent retrieves or reads
  explanation: In a direct injection the user types the attack. In an indirect one it is hidden in a web page, email,
    document or tool result that the agent reads, so the user may be the victim.
- id: h2
  prompt: 'The course''s framing of the core problem:'
  options:
  - Detection quality — better classifiers close the gap
  - 'Source → sink: "you contain it, you don''t detect it"'
  - Model alignment — a well-aligned model resists injection
  - Input sanitization — escaping untrusted content is sufficient
  answer: 'Source → sink: "you contain it, you don''t detect it"'
  explanation: This is the section's thesis. Injection is not a spam-filtering problem. Trace the untrusted
    *source* to the dangerous *sink* and cut the path — capability restriction, dual-LLM, human approval
    on the sink.
- id: h3
  prompt: The course frames prompt injection as a source-to-sink problem, where you contain it and do not detect it.
    Which answer to an interview question on injection is explicitly called wrong?
  options:
  - Any answer proposing capability restriction
  - Detection-only answers
  - Answers naming the dual-LLM pattern
  - Answers that mention human approval gates
  answer: Detection-only answers
  explanation: 'The course''s framing is that injection is contained, not detected, so an answer that only detects
    is the one called wrong. Trace the untrusted *source* to the dangerous *sink* and cut the path: capability restriction,
    dual-LLM, human approval on the sink.'
- id: h4
  prompt: 'In the dual-LLM pattern (Willison), the privileged LLM:'
  options:
  - Reads untrusted content and summarizes it for the quarantined LLM
  - Holds the tools and never reads untrusted content
  - Validates the quarantined LLM's outputs before execution
  - Runs with a stricter system prompt but the same inputs
  answer: Holds the tools and never reads untrusted content
  explanation: The privileged model sees only trusted input and is the one that plans and calls tools. Untrusted
    content goes to the quarantined model, and its output is passed around as a variable the privileged model never
    reads.
- id: h5
  prompt: 'The quarantined LLM:'
  options:
  - Has read-only tool access
  - Reads untrusted content but cannot act
  - Acts only after human approval
  - Runs a smaller model to limit damage
  answer: Reads untrusted content but cannot act
  explanation: The quarantined model is assumed to be compromised by whatever it reads, so it gets no tools. Injected
    text then cannot reach anything that can act.
- id: h6
  prompt: 'In the bank''s illustrative 9-step defence stack, input guardrails sit at position:'
  options:
  - 1st
  - 4th
  - 8th
  - 9th
  answer: 1st
  explanation: Input guardrails screen a request before anything else spends effort on it or is exposed to it, so
    they come first in the bank's stack.
- id: h7
  prompt: 'In the bank''s illustrative 9-step defence stack, output validation sits at:'
  options:
  - 2nd
  - 5th
  - 8th
  - 9th
  answer: 8th
  explanation: Output validation checks the response just before it leaves, after the model and the tools have run.
    Only the after-the-fact review follows it.
- id: h8
  prompt: 'In the bank''s illustrative 9-step defence stack, continuous trace grading sits at:'
  options:
  - 1st
  - 3rd
  - 6th
  - 9th
  answer: 9th
  explanation: Grading traces happens after the response has gone. It does not block anything; it catches what the
    earlier layers missed, so it comes last.
- id: h9
  prompt: 'Memory poisoning vs context poisoning:'
  options:
  - Memory poisoning affects the working context; context poisoning persists across sessions
  - Memory poisoning persists across sessions; context poisoning affects working memory within one
  - Both are within-session; they differ by attack vector
  - Both persist; they differ by which store is targeted
  answer: Memory poisoning persists across sessions; context poisoning affects working memory within one
  explanation: A poisoned memory entry is written to a store and loaded again in later sessions, so the attack outlives
    the conversation. Poisoned context lasts only as long as that context window.
- id: h10
  prompt: 'Denial-of-wallet describes:'
  options:
  - Exhausting a rate limit to deny service
  - Driving up an attacker-controlled volume of expensive model calls to inflate cost
  - Stealing API keys to bill a victim
  - Blocking payment flows in an agentic commerce system
  answer: Driving up an attacker-controlled volume of expensive model calls to inflate cost
  explanation: An attacker triggers a large number of expensive model calls. The service stays up and the bill grows.
    Budgets, rate limits and caps on loop iterations are the defences.
- id: h11
  prompt: 'The three boundaries the course says to establish before shipping any agent:'
  options:
  - Model, data, and network
  - Who can trigger it, where it can act, what it did
  - Input, output, and audit
  - Identity, authorization, and encryption
  answer: Who can trigger it, where it can act, what it did
  explanation: Who can trigger it is authentication and authorisation of callers, where it can act is scoped permissions
    and sandboxing, and what it did is the audit record.
- id: h12
  prompt: 'The course names three boundaries to establish before shipping any agent: who can trigger it, where it
    can act, and what it did. Which requirement does "what it did" map to?'
  options:
  - Rate limiting
  - Audit logging / traceability
  - Least-privilege scopes
  - Authentication
  answer: Audit logging / traceability
  explanation: You can only investigate or undo what was recorded. Rate limiting, scopes and authentication answer
    the other two questions.
- id: h13
  prompt: 'The degradation ladder, in order:'
  options:
  - Human → retry → fallback model → simpler baseline
  - Retry → fallback model → simpler baseline → human
  - Fallback model → retry → human → simpler baseline
  - Simpler baseline → retry → fallback model → human
  answer: Retry → fallback model → simpler baseline → human
  explanation: The ladder runs from cheapest and least disruptive to most. A retry handles a transient error, a
    fallback model a provider outage, a simpler baseline gives a degraded answer, and a person comes last because
    that is slowest and costliest.
- id: h14
  prompt: 'Best-of-N jailbreaking (Hughes et al.) reported attack success rates of:'
  options:
  - 45% on GPT-4o, 38% on Claude 3.5 Sonnet
  - 89% on GPT-4o, 78% on Claude 3.5 Sonnet
  - 99% on both
  - 60% on GPT-4o, 20% on Claude 3.5 Sonnet
  answer: 89% on GPT-4o, 78% on Claude 3.5 Sonnet
  explanation: Cite the numbers. 89%/78% is the argument that no prompt-level filter is a boundary; it
    is a speed bump in front of one.
- id: h15
  prompt: Best-of-N jailbreaking (Hughes et al.) reported attack success rates of 89% on GPT-4o and 78% on Claude
    3.5 Sonnet. What does that result imply for guardrail strategy?
  options:
  - Better prompt-level filters can close the gap
  - Prompt-level defenses are probabilistic — architectural containment must carry the load
  - Only frontier models are safe against BoN
  - Sampling temperature should be set to 0
  answer: Prompt-level defenses are probabilistic — architectural containment must carry the load
  explanation: Best-of-N jailbreaking reached 89% on GPT-4o and 78% on Claude 3.5 Sonnet (Hughes et al.) by resampling
    variations of a prompt. A filter that falls to trying again is a speed bump, not a boundary, so containment
    in the architecture has to carry the load.
- id: h16
  prompt: '"Typoglycemia" as an attack refers to:'
  options:
  - Injecting invisible Unicode characters
  - Scrambling word interiors so filters miss the string but the model still reads it
  - Overwhelming the tokenizer with rare tokens
  - Homoglyph substitution in domain names
  answer: Scrambling word interiors so filters miss the string but the model still reads it
  explanation: A model, like a person, can read "ignroe prevoius insturctions", but a filter looking for the exact
    phrase does not match it.
- id: h17
  prompt: 'The three guardrail placements:'
  options:
  - Ingest, index, retrieve
  - Input, output, action
  - Client, gateway, model
  - Pre-flight, in-flight, post-flight
  answer: Input, output, action
  explanation: Input guardrails screen what comes in, output guardrails check what goes back, and action guardrails
    check a tool call before it runs.
- id: h18
  prompt: 'The PII detection ladder, and its hard case:'
  options:
  - LLM → NER → regex → hybrid; hard case is structured identifiers
  - Regex → NER → LLM → hybrid; hard case is contextual PII
  - Hybrid → regex → NER → LLM; hard case is multilingual text
  - NER → regex → hybrid → LLM; hard case is nested JSON
  answer: Regex → NER → LLM → hybrid; hard case is contextual PII
  explanation: Contextual PII ("the patient in room 4 who came in Tuesday") defeats regex and mostly defeats
    NER. Naming it is the senior signal.
---
