# Initiative: RAG Pipeline — Requirements and Scope

**Source:** https://app.notion.com/p/31ef148b3ab78016a69ffe7a2a2b01cd
**Last edited:** 2026-06-17
**Project:** Help Centre
**Status:** In Review
**Type:** Shaping

## Purpose

Collect requirements and separate into scopes to enable faster delivery of first version.

---

## Requirements

### Knowledge Ingestion
- Support ingestion of Help Center knowledge content
- Support knowledge sources in multiple languages
- Support multiple markets (accounting rules differ by country)
- Support updating and adding additional knowledge sources in the future

### Knowledge Retrieval
- Allow Support agent to retrieve relevant knowledge for a given user question
- Retrieval must support filtering by: language, market, product area
- Responses must reference the originating knowledge source

### Support Escalation
- Indicate when human support is required (knowledge insufficient)
- Identify scenarios that should not be answered automatically: subscription termination, account-specific cases
- Forward conversation to Intercom with full context
- Support email-based support forwarding when required
- Log original user question + final agent response on escalation
- Escalated conversations available for review and continuous improvement

### Confidence / Safety Signals
- Provide a confidence signal for retrieved knowledge
- Support threshold-based decisions: answer / ask clarification / escalate
- Especially important initially to maintain user trust

### Interaction Requirements
- Support conversational clarification for ambiguous questions
- Communicate system activity when responses take longer (streaming / processing indicator)
- Validate effectiveness of clarification questions during testing

### Platform Compatibility
- Support web and mobile surfaces
- Retrieval capability operates independently of the interface
- Future: voice interface support

### Performance and Cost
- Target: **<2 seconds to first character** under normal conditions
- Support efficient retrieval at scale
- Allow monitoring of cost per request

### Observability
- Retrieval requests must be logged
- Possible to inspect which knowledge sources were retrieved per request

### Evaluation
- Support offline evaluation using test datasets
- Support tracking key quality metrics over time

### User Signal Collection
**Explicit:**
- Thumbs up/down on individual messages and session level
- Free-text comments on individual messages and sessions
- User contacts support without system suggesting it

**Implicit:**
- Number of turns before resolution or escalation

### Sessions and Memory
- Create new sessions and maintain session history

### Authentication
- Authentication + authorization handled securely
- Must reliably identify active organization when making API/DB calls
- Support access control on knowledge sources (users only receive knowledge relevant to their permissions and plan)

### Knowledge Sources
- Help Center articles
- Blog posts
- Intercom chat logs (expected to be high-value)
- Intercom macros (templates used by support agents for common questions)
- Public accounting guidance relevant to supported markets (e.g., Danish accounting guidance)

**Note:** Current dataset is primarily Danish. Multilingual strategy required as system expands.

---

## MVP Goal — #1 Iteration

Deliver a first production-ready knowledge retrieval system enabling users to get reliable answers to common product and accounting questions directly within the Help Center, reducing need to contact support.

MVP validates:
- Users can successfully resolve questions through conversational interaction
- Answers are grounded in trusted knowledge sources
- System avoids incorrect/misleading responses by escalating when necessary
- Basic observability provides sufficient insight to evaluate quality and identify gaps

**Scope:** Danish market only (DK/EN languages). Foundation for a reusable knowledge capability to later power Copilot.

### MVP Scope & Constraints
- Danish market only — languages (DK/EN) — source written in Danish
- System design must allow future support for multiple languages, markets, and product areas

### MVP Knowledge & Retrieval
- Minimum: Help Center articles + blog content
- Preferred: include Intercom content (if feasible)
- Responses must include reference to originating source (link/title)
- System must avoid answering when sufficient grounding not available

### MVP Support Escalation
- Escalation triggered when: system lacks sufficient info, or predefined unsupported scenarios
- Escalation paths: Contact support entry points (UI-level)
- Escalated cases must be loggable
- Support forwarding full context to Intercom

### MVP Confidence & Safety
- Basic safety mechanisms
- Decide whether to answer or not
- Prevent low-confidence responses

### MVP Observability & Evaluation (Minimal)
- Questions + retrieval requests logged with metadata
- Inspect retrieved knowledge sources per request
- Minimal evaluation setup for answer quality

### MVP Performance & Platform
- Target: <2 seconds to first token
- Support web surface
- Authentication handled securely
- Support session handling and history

### MVP Architecture (Important for future)
- Retrieval exposed via service/API layer (UI-independent)
- Designed as reusable service for: Help Center (MVP) → Copilot (future)

---

## Goal — Next Iterations

Evolve from basic retrieval into a continuously improving, reusable intelligence layer supporting both Help Center and Copilot.

Progressive expansion in: coverage (markets, languages, sources), answer quality (feedback loops, data refinement), advanced interactions (clarification, guidance, context-aware responses), context-dependent behavior.

### Interaction & Escalation
- Generate follow-up questions to clarify ambiguous input and guide users toward resolution

### Knowledge Expansion
- External accounting knowledge sources
- Expand to multiple markets (Germany, France primary focus, Netherlands)
- Multiple languages + English
- Product area segmentation

### Evaluation & Learning
- Expand evaluation tooling and datasets
- Use collected user signals for continuous improvement
- Enable systematic review of flagged sessions and low-confidence responses
