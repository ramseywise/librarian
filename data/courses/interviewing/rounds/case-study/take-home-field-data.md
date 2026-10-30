---
imported_hash: 9002e5edbae0e656
title: 'Take-home assignments: field data and practice prompts'
summary: What AI-engineering take-homes actually ask for, how they're graded, and a pool of real prompts to practice on.
order: 14
kind: reading
section: Case study
source: sisyphus/interviewing/rounds/case-study/take-home-field-data.md
---

# Take-home assignments: field data and practice prompts

What AI-engineering take-homes actually ask for, how they're graded, and a pool of real
prompts to practice on. This complements the take-home and work-trial sections in the
[README](readme.md) and [study-guide.md](study-guide.md). For timed practice, run one of these
prompts through `env-drill env2` (AI-allowed, production feature) or as a 2–4 h self-set build.

Source: [alexeygrigorev/ai-engineering-field-guide](https://github.com/alexeygrigorev/ai-engineering-field-guide)
`interview/questions/06-home-assignments.md` and `webinars/04-take-home-assignments.md`,
imported 2026-10-29. That analysis covered 1,765 JDs and 100+ GitHub repos of submissions
(Q4 2025–Q2 2026). Per-item source links were stripped; see upstream.

## Prevalence and format

- **17 of 51** companies with a disclosed process include a take-home; another **5** use paid work trials.
- Asked for: **RAG (40%+)**, agents and tool-calling (30%+), conversational (20%+), document processing (15%), LLM-as-judge eval (10%+).
- Deadline of 2–7 days for **2–4 h of real work**. "Not code golf": they grade decisions and clarity.
- Followed by a **45–90 min defense round**, which often matters more than the code.
- AI tools: only one company explicitly allows them, none ban them, and most say nothing.

## How they are graded

Many assignments include explicit evaluation criteria. Patterns across repos:

- Functional correctness - does the system work end-to-end, handle edge cases, produce correct outputs
- Code quality and architecture - modular design, clean code, extensibility, proper error handling
- Evaluation methodology - whether candidates build eval harnesses, define metrics, measure quality systematically
- Production readiness - scalability considerations, caching, monitoring, cost optimization, security (PII handling, input sanitization, rate limiting)
- Performance targets - response time (e.g., <2s p95 latency, ~0.5s per response), throughput (100+ req/s), cache hit rates (>40%), cost reduction (>30%)
- Testing - unit tests (sometimes mandatory), test coverage targets (e.g., 80%), edge case handling
- Documentation - README quality, design decision explanations, trade-off analysis
- Weighted rubrics - some assignments provide explicit scoring: e.g., 30% functionality, 30% challenge completion, 25% context engineering, 15% code quality
- Quantitative metrics - ARI/NMI for clustering, RAGAS metrics for RAG (faithfulness, answer relevancy, context precision), confidence scores for extraction

## What stands out

The best submissions share these traits:

- Ask clarifying questions before starting. Double your time estimate.
- Start with evaluation - build an eval harness before writing the main logic. YC startups report this as the top signal: "Red flag if candidate doesn't start with evals"
- Document design decisions and trade-offs - why you chose this approach over alternatives
- Include a Loom/video walkthrough of your submission
- Make it configurable - one engineer built a PDF summarizer CLI with a config file for different models and chunking strategies, got two competing offers within 72 hours
- Test edge cases - even if testing isn't explicitly required, include basic tests
- Show production awareness - error handling, monitoring hooks, cost estimates
- Connect technical metrics to business outcomes
- Prepare for the defence round - practice explaining your architecture decisions, trade-offs, and what you'd do differently with more time

Common mistakes:

- Not asking clarifying questions before starting
- Putting too little effort in - "most engineers put way too little effort into take-homes"
- Rushing without documenting design decisions and trade-offs
- Over-engineering beyond what was asked without justification
- Ignoring evaluation and testing of AI outputs - this is the single biggest differentiator
- Not preparing for the walkthrough/defence round - the follow-up interview is often more important than the code itself

**The single biggest differentiator:** submissions that skip evaluating and testing the AI
outputs are the ones that don't get offers. Build the eval harness first.

## Practice prompts

Each prompt is a real assignment as candidates reported it. Pick one, set a 3 h timer, and
deliver a repo with a README covering design decisions, the eval harness and results, what
you'd do with more time, and cost/latency estimates. Then rehearse the defense with
`interview-drill` against [questions.md](questions.md).

### RAG and Document Q&A

The most common assignment type (40%+ of GitHub submissions).

- Build a RAG chatbot that ingests PDFs/documents, creates embeddings in a vector DB, and answers questions with citations. Must respond "I don't have that information" when answer is unavailable. Answers must come strictly from retrieved context (10+ candidate submissions across 5+ companies).
- Build a policy document RAG assistant with mandatory source citations for every answer. Return safe fallbacks for out-of-scope questions. Comes with a 7-question evaluation set across 3 categories (answerable, partially answerable, unanswerable).
- Build a document Q&A system with citation tracking that handles multi-hop questions (questions requiring information from multiple documents or sections to answer).
- Build a live chat agent grounded in FAQ knowledge base. Model must answer only from known FAQ data.
- Design a customer support chatbot using RAG with open-source models. Requirements: 100+ concurrent users, <2 second latency, grounded in company docs, analytics tracking.
- Build a CLI tool for summarizing long PDFs with configurable models and chunking strategies.
- Refactor an existing messy RAG application into a clean architecture. Preserve all external behaviors (exact API endpoints), eliminate global mutable state, ensure testability without requiring running services (5+ candidate submissions for one company).
- Build an agentic RAG system for government documents. 100% open-source required (Ollama + CrewAI + pgvector). Must integrate with OpenWebUI. Evaluated using RAGAS metrics (faithfulness, answer relevancy, context precision, context recall).

### Agents and Tool-Calling

Second most common (30%+).

- Build an assistant agent handling database queries, document search, and bash commands. Bash commands require explicit user approval.
- Build an AI agent that transforms Monday.com project management data into conversational business insights using dual-LLM architecture.
- Build an AI agent demonstrating natural interaction, agentic behavior, and clear reasoning steps.
- Build a customer support agent.
- Build an autonomous agent using an open-source LLM with observability/eval layer.
- Build an agent that reads customer CSV data and generates personalized email campaigns with evaluation metrics.
- Build a code review agent that analyzes Python files and provides actionable feedback.
- Build a Singapore public transport query agent that fetches live data from 7 LTA APIs about buses, trains, traffic, and station conditions.
- Build a sales insights agent that answers questions about subscription/revenue data. Must detect and refuse PII requests (emails, phone numbers, credit card tokens). No raw rows passed to the LLM - aggregates only. Evaluated on 3 dimensions: accuracy, safety/refusal correctness, reasoning quality.
- Build an evaluation tool for LLM hallucination detection.

### Multi-Agent Systems

- Build a multi-agent content generation system: 5 core agents (research, writing, editing, SEO, publishing). Takes product JSON input, generates FAQ document, product page, and comparison page. All outputs must follow strict JSON formats. LangChain + Groq.
- Implement a minimal workflow engine with graph-based nodes, state management, branching/looping, and tool-based logic. Max 50 steps. Built-in infinite-cycle protection required. Unit tests mandatory (6+ candidate submissions).
- Build a 5-agent CBT therapy system: agents autonomously design, critique, and refine therapy exercises. Human-in-the-loop approval required before finalization.
- Build a 4-stage bedtime story pipeline: Spec Builder, Storyteller, LLM Judge, Rewriter. Must use gpt-3.5-turbo. Up to 2 revision cycles. LLM judge evaluates stories against the spec.

### Document Extraction and Processing

- Build a marksheet extraction API: parse complex table layouts and handwriting from academic marksheets into structured JSON.
- Build a physician notetaker: transform physician-patient conversations into structured clinical documentation..
- Build a legal document analysis tool for contracts: extract key information, identify risks (auto-renewal traps, liability, IP ownership, non-competes), generate structured summaries.
- Build a CBT assistant combining RAG with safety mechanisms. Crisis detection mandatory. PII redaction and pseudonymization required. No secrets in logs. Educational only, not clinical advice.
- Take a blood test report as PDF, understand medical issues, generate suggestions by fetching content from online blog articles with source links.
- Build a question deduplication and clustering pipeline: exact dedup, semantic dedup, LLM-based cluster discovery, classification. Output evaluated with ARI, NMI, homogeneity, completeness metrics.
- Build a data pipeline that processes 1,000 messy products from 4 vendors, normalizes them into a unified schema, fetches supplementary data via rate-limited async API calls (vendor-specific token-bucket rate limits), enriches products through AI-powered duplicate detection. Must support both CLI and API access.
- Build a transaction-to-user matching system: identify users whose names appear in transaction descriptions, find similar transactions via text matching, propose improvements (semantic embeddings, database integration). Spring Boot + Java.
- Build real-time earnings call transcription and insight streaming: streaming audio-to-text via Whisper, real-time extraction of financial signals (revenue, guidance, risks, outlook), SSE output.

### Full-Stack AI Applications

- Build a Telegram bot for investment coaching with safety filtering. Educational content only - no personalized financial advice.
- Build a multi-agent D&D dungeon simulation: Game Master agent + Player agents. Must address at least 3 of 6 challenges (long campaigns, secrets, rulings, self-aware dungeon, living world, ambiguity). LangGraph required.
- Build a memory extraction and personality transformation system: extract structured long-term memory from chat history as JSON, transform responses based on personas (calm mentor, witty friend, therapist). Open-source LLMs only, no proprietary APIs.
- Build an AI judge for a Rock-Paper-Scissors variant: classify player inputs as VALID/INVALID/UNCLEAR, handle typos and edge cases, tool-based state management workflow (2 submissions).
- Build a web app that converts markdown to slide deck presentations by splitting content into logical sections based on a target slide count. Document size limited to 150K tokens, single API call. Next.js + OpenAI.
- Build an LLM processing pipeline with intelligent routing, multi-level caching (exact + semantic), provider health monitoring with failover, and distributed tracing. Targets: 100+ req/s, p95 latency under 2s, >40% cache hit rate.
- Build an NPC system for a job simulation platform: three AI co-workers with distinct personalities, a "Director Agent" that detects conversation loops via semantic similarity (0.85 threshold), RAG-based knowledge retrieval. FastAPI + Claude API + FAISS.
- Build an LLM-based rating prediction and prompt evaluation system with user and admin dashboards. Node.js + MongoDB + Google Generative AI.
- Build an AI-first CRM module: React/Redux frontend, FastAPI backend, LangGraph with 5+ tools. Deliverable: GitHub repo + 10-15 minute demo video.

### Legal Document AI

Legal document processing emerged as a distinct category in 2026, with a repeating pattern: ingest messy legal documents, retrieve grounded evidence, generate cited drafts, and learn from operator edits.

- Build a legal document AI workflow with a three-tier extraction cascade and an improvement-from-edits loop. The system must ingest, extract, ground, and iteratively improve based on operator corrections.
- Pearson Specter Litt: Take-home requiring ingestion of messy legal documents, grounded retrieval, cited draft generation, and learning from operator edits. Delivered as a scrum sprint plan.

### RAG and Document Q&A (2026)

- Quorium: Build a RAG Q&A chatbot for an AI Engineer Trainee role. Standard RAG pipeline with document ingestion and question answering.
- ITJ: RAG-based document QA system as a take-home challenge.
- NTT DATA: RAG system over sustainability reports.
- NeoStats: Chatbot assignment for an AI Engineer case study.
- Trinamix: Supply chain RAG chatbot over a 2,000-PO supplier register and governance policy. Built with Flowise, Pinecone, and GPT.
- GoTyme Bank: Full-stack document extraction system combining OCR and LLM, with a React frontend.

### Agents and Multi-Agent Systems (2026)

- Go Fig AI: Build an inbox-triage agent skill with a human-in-the-loop approval gate. 2-hour cap.
- Yuno: Multi-agent orchestration platform with Ollama, Streamlit, and Telegram.
- RefundPilot: Containerized internal support workspace that evaluates e-commerce refund requests, applies refund policy, resists prompt-injection attempts, and records structured decision logs.
- AgentCollect: Full-Stack AI Engineer (AI-Native) hiring challenge.
- Neon Health: AI Agent with OpenAI integration.
- Future Research: LangGraph multi-agent fitness coach with hub routing to sub-agents (coach, workout-generator, workout-logger) via Claude structured output.
- KarthikTools: Full-stack web app where a backend agent executes predefined tools with a clear execution trace.

### LLM Applications and Infrastructure

- GenAI Labs: Production-ready LLM-driven SQL analytics pipeline with token counting, SQL validation, observability, and benchmarking. Multiple submissions.
- VantageScore: GenAI-powered credit risk scoring with ML ensemble, explainability, and LLM enrichment.
- AEGIS: AEO content scoring, LLM query fan-out, and embedding-based semantic gap analysis.
- SHL: GenAI assessment recommendation system.
- Camplight: LLM interview task.
- VijaySaravanaPandi: NL-to-app "compiler" — turns a natural-language app description into a working application via structured, validated intermediate representations (not just prompt to code).
- Jpower3145: Local LLM pre-interview task.
- Cerebras: AI Engineer Model Quality and Performance hiring challenge (perf UI, eval pruning).
- nickusevich: Novelty detection for football news using hybrid retrieval (pgvector + tsvector + RRF), LLM reranking, and LLM-based publish/skip/review decisions.

### Embeddable and Conversational AI

- EloquentAI: Build an embeddable AI agent chat widget.
- Fleetio: Hybrid deterministic + LLM weekly fleet digest.
- Zap: AI-powered client onboarding automation.
- Adobe (FDE): GenAI-powered creative automation pipeline for social ad campaigns.

### Official Company Challenges

Official repos published by companies as part of their hiring process:

- [ML6 (laine)](https://github.com/ml6team/laine-engineer-coding-challenge) - Coding challenge for evaluating AI Engineer candidates
- [Jaseci Labs](https://github.com/jaseci-labs/take-home-ai-engineer) - Take-home for AI Software Engineer candidates
- [Jitera](https://github.com/Jitera-Interviews/genai-takehome) - Take-home task for GenAI roles
- [AuxoAI](https://github.com/AuxoAI-Hiring/ai-engineer-assignment) - AI Engineering Take-Home
- [Coginis Research](https://github.com/CoginisResearch/ai-engineer-challenge) - AI Product Engineer Hiring Challenge
- [Future Research](https://github.com/future-research/candidate-assessment) - AI Engineer take-home assessment + exercise dataset
- [Go Fig AI](https://github.com/go-fig-ai/take-home-inbox-triage) - Inbox-triage agent with human-in-the-loop
- [Cerebras](https://github.com/danielkim-cerebras/ai-model-quality-challenge) - Model Quality and Performance challenge
- [AI:AT](https://github.com/AIAT-AIandBusinessgrowth/standort-agent-challenge-public) - Multi-criteria location evaluation agent
- [Bloom (radialreview)](https://github.com/radialreview/bloom-coffee-ai) - Pre-built coffee ordering app candidates extend with an AI order taker
