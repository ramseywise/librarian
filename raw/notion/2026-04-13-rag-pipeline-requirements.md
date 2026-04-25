# Initiative: RAG Pipeline — Requirements and Scope

**Source:** Notion (work)  
**Date:** 2026-04-13  
**URL:** https://www.notion.so/31ef148b3ab78016a69ffe7a2a2b01cd

---

## Purpose

Collect requirements and separate into scopes to enable faster delivery of a first version of a knowledge retrieval system for Shine.

---

## Requirements

### Knowledge Ingestion
- Must support Help Center knowledge content ingestion
- Must support multiple languages and multiple markets (accounting rules differ by country)
- Must support updating and adding additional knowledge sources in the future

### Knowledge Retrieval
- Support agent must be able to retrieve relevant knowledge for a given user question
- Retrieval must support filtering by: language, market, product area
- Responses must reference the originating knowledge source

### Support Escalation
- Must indicate when human support is required (insufficient knowledge)
- Must identify unsupported scenarios: subscription termination, account-specific cases
- Must forward conversation to Intercom with full context
- Must support email-based support requests
- Escalated conversations must log the original user question + final agent response
- Escalated conversations should feed back into knowledge base improvement

### Confidence / Safety Signals
- Must provide a confidence signal for retrieved knowledge
- Must support threshold-based decisions: answer / ask clarification / escalate
- Critical initially to maintain user trust

### Interaction Requirements
- Must support conversational clarification for ambiguous questions
- Must communicate system activity during processing (loading indicators)
- Clarification effectiveness should be validated during testing

### Platform Compatibility
- Must support web and mobile surfaces
- Retrieval capability must operate independently of interface
- Should support voice interface

### Performance and Cost
- Response time target: <2 seconds to first character under normal operating conditions
- Must support efficient retrieval at scale
- Must allow monitoring of cost per request

### Observability
- Retrieval requests must be logged
- Must be possible to inspect which knowledge sources were retrieved per request

### Evaluation
- Must support offline evaluation using test datasets
- Must support tracking key quality metrics over time

### Sessions and Memory
- Must support creating new sessions and maintaining session history

### Authentication
- Authentication and authorization must be handled securely
- Must reliably identify active organization for API/DB calls
- Must support access control on knowledge sources
- Users must only receive knowledge relevant to their permissions and plan

### Knowledge Sources
- Help Center articles
- Blog posts
- Intercom chat logs (expected high signal)
- Intercom macros (templates used by support agents)
- Public accounting guidance (e.g., Danish accounting guidance)

**Note:** Dataset is primarily Danish initially. Translation and multilingual strategy required for expansion.

---

## MVP Scope (Iteration 1)

**Goal:** Deliver a first production-ready knowledge retrieval system enabling users to get reliable answers to common product and accounting questions within the Help Center, reducing support contacts.

**Validates:**
- Users can successfully resolve questions through conversational interaction
- Answers are grounded in trusted knowledge sources
- System avoids incorrect/misleading responses by escalating when necessary
- Basic observability provides sufficient insight to evaluate quality and identify gaps

**Scope Constraints:**
- Danish market only (DK/EN languages), source written in Danish
- System design must allow future multi-language, multi-market, multi-product-area support

**Knowledge Sources for MVP:**
- Minimum: Help Center articles + blog content
- Preferred: include Intercom content if feasible

**Escalation:**
- Trigger when: system lacks sufficient info OR request falls into predefined unsupported scenarios
- Log all escalated cases for later analysis
- Forward full context to Intercom

**Confidence & Safety:**
- Basic safety mechanisms: decide whether to answer or not, prevent low-confidence responses

**Observability:**
- Log questions + retrieval requests with metadata
- Inspect retrieved knowledge sources per request
- Minimal evaluation setup for answer quality assessment

**Performance:**
- Target: <2 seconds to first token
- Support web surface
- Authentication must be handled securely
- Session handling and history

**Architecture (important for future):**
- Retrieval must be exposed via service/API layer (UI-independent)
- Designed as reusable service for: Help Center (MVP) → Copilot (future)

**UI Scope (ownership to be clarified):**
- Simple chat interface
- Articles overview
- Contact support options

---

## Next Iterations Goal

Evolve the knowledge system from basic retrieval to a continuously improving, reusable intelligence layer supporting both Help Center and Copilot.

**Expansion areas:**
- Multiple markets (Germany, France, Netherlands)
- Multiple languages (markets + English)
- Product area segmentation
- External accounting knowledge sources
- Feedback collection mechanisms
- Proper evaluation tooling
- Continuous improvement loops
