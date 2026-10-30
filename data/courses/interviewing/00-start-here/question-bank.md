---
imported_hash: 8a8b4c578fecd7c1
title: Field question bank
summary: About 560 AI-engineering interview questions as reported by candidates, grouped by topic.
order: 2
kind: reading
source: sisyphus/interviewing/question-bank.md
---

# Field question bank

About 560 AI-engineering interview questions as reported by candidates, grouped by topic.
These are questions only, with no answers. Use them for cold recall: pick a section, answer
out loud, then check yourself against the matching round or guide.

| Section | Rehearse with |
|---|---|
| Technical | [technical-questions/theory-bank.md](../rounds/technical-questions/theory-bank.md), [guides/](guides/) |
| System design | [system-design-round/interviewer-personas.md](../rounds/system-design-round/interviewer-personas.md) (mock), [walkthroughs/](rounds/system-design-round/walkthroughs/) |
| Coding | [coding-challenge/questions.md](../rounds/coding-challenge/questions.md), [drills/coding/](../drills/coding/) |
| Behavioral | [behavioral/probe-bank.md](../rounds/behavioral/probe-bank.md), [project-deep-dive/probe-bank.md](../rounds/project-deep-dive/probe-bank.md) |

Source: [alexeygrigorev/ai-engineering-field-guide](https://github.com/alexeygrigorev/ai-engineering-field-guide)
`interview/questions/questions.md`, imported 2026-10-29. Per-question source footnotes
(Reddit, Glassdoor, blogs) were stripped; see upstream for attribution.

## Technical Questions

### LLM Fundamentals

- How do LLMs work?
- How do transformers work?
- What is tokenization and how does it affect LLM performance?
- What is the difference between pre-training and fine-tuning?
- Explain context windows and their limitations.
- What are scaling laws and why do they matter?
- What is temperature and top-p sampling? How do they affect outputs?
- Explain few-shot learning and chain-of-thought prompting.
- What is KV cache? How does it help in LLM inference?
- Can you describe the difference between GenAI and traditional programming in the context of solving a real-world problem?
- How do you ensure the outputs from large language models are consistent and accurate, especially when dealing with complex multi-step workflows?
- What's an RAG model? Explain the complete process.
- What are embeddings?
- How does chunking happen?
- What is the difference between discriminative and generative models?
- What is graph RAG? How does it differ from standard RAG?
- What is reflection in the context of LLM agents?
- Explain KL divergence.
- What is the difference between symbolic and connectionist AI?
- Describe the types of text summarization techniques and when you'd use each.
- How do you do memory management and context management with LLMs?
- What is the self-attention mechanism? How does it differ from multi-head attention?
- What is grouped query attention and how does it differ from standard multi-head attention?
- What are the differences between BPE, WordPiece, and character-level tokenization? What are the trade-offs?
- Explain the difference between encoder-only, decoder-only, and encoder-decoder Transformer architectures. When would you use each?
- Why are decoder-only models dominant even for non-generation tasks?
- What is positional encoding and why is it needed in Transformers?
- What are the key MMLU, BigBench, and HumanEval benchmarks? What does each measure and what are its limitations?
- What is the difference between RLHF and DPO? When would you prefer one over the other?
- What is Mixture of Experts (MoE)? How does it improve efficiency?
- How do LLMs actually generate text? Explain the autoregressive decoding process.
- What are decoding strategies like beam search, top-k, and top-p? When do you use each?
- What is FlashAttention and how does it work?
- Why is LLM inference memory-bounded?
- How do stop sequences work in LLMs?
- What is the context window and what happens when you exceed it? How do you handle long documents?
- What risks arise from applying a general-purpose tokenizer to specialized domains like legal or medical text?

### RAG Systems

- Design a RAG system for a customer support chatbot. How do you evaluate it? (reported across multiple companies)
- How would you design an LLM-powered enterprise search system?
- Design a generative AI document-processing pipeline for unstructured data (emails, PDFs, images) to automate workflows like claims processing.
- How would you use GPT-4 to generate accurate answers based on proprietary documents?
- Design a generative QA assistant for your company's knowledge base.
- You're making a system that processes huge PDF reports. How would you handle the problem of not keeping an entire report's context when splitting a document for a chatbot?
- How would you efficiently generate and store embeddings for products and queries in a chatbot application?
- How would you handle the problem of a model hallucinating when no information is found in the given context?
- What retrieval-augmented generation (RAG) projects have you worked on?
- Design a question-answering system over internal documentation.
- How do you ensure the quality of data that an LLM interacts with?
- Compare sparse vs. dense retrieval. When would you use each?
- What are common RAG failure points and how do you debug them?
- How do you protect sensitive/confidential data in a RAG pipeline?
- What vector databases have you used? Which ones and why?
- You have a financial report where page 1 says "all amounts in thousands." How do you handle document-wide context when chunking page by page?
- What is hybrid search? When would you combine vector search with keyword search (BM25)?
- What is re-ranking and why is it needed on top of vector retrieval? Explain cross-encoder vs. bi-encoder.
- How do you scale a RAG system to 10M+ articles? Discuss sharding, caching, and retrieval optimization.
- Your RAG system returns relevant documents but users still can't find the answer. How do you transform it from a search engine into an answer engine?
- How do you evaluate a RAG pipeline? What metrics would you use? (NDCG, MRR, precision@k, recall)
- How do you handle citations and source attribution in a RAG system?
- How does Approximate Nearest Neighbor (ANN) search work? Explain HNSW indexing.
- Where do embeddings fail? Discuss negation, temporal reasoning, and precision requirements.
- What is semantic caching and how can it reduce cost and latency in a RAG system?
- Design a RAG system that maintains context across multi-turn conversations.
- What are the key tradeoffs when designing a RAG system (latency vs accuracy, chunk size vs context, cost vs quality)?
- How do you optimize RAG latency in production?

### Agents and Tool Use

- What is an AI agent and what is its role in a broader system?
- What's the difference between an agent and a simple LLM chain? (reported across multiple companies)
- What makes an AI system truly agentic and what does not qualify?
- When is an agentic architecture the wrong solution?
- How do you define and enforce agent autonomy boundaries?
- What are the essential components of an agent beyond an LLM?
- How do you prevent agents from over-reasoning or over-planning?
- Walk through a production-ready agent architecture.
- What logic belongs in the orchestrator vs the LLM?
- How do you design a safe and debuggable agent loop?
- How do you implement termination conditions in long-running agents?
- How do agents decompose high-level goals into executable steps?
- Chain-of-thought vs tree-of-thought vs graph planning - when would you use each?
- How do you detect and stop infinite planning loops?
- How do you handle partial observability or missing information?
- How do agents decide a task is "done"?
- What planning failures are hardest to detect in production?
- How do agents decide which tool to use?
- How do you design tool schemas that reduce hallucinated actions?
- How do you sandbox tool execution safely?
- How do you handle tool failures, retries, and idempotency?
- What are the biggest security risks with tool-using agents?
- How do you control cost explosions from tool calls?
- Stateless vs stateful agents - tradeoffs and use cases?
- How do you version and roll back agent behavior?
- Describe how you would architect an AI agent system, including the agent loop, tool interfaces, memory design, orchestration technologies, and safety considerations.
- Design an agent analyzing customer support tickets, drafting responses, and escalating complex issues.
- Create a system where agents collaborate on research reports with citations.
- Build an agent reviewing code and suggesting improvements.
- How do you explain agentic systems to non-technical stakeholders?
- What types of memory do agentic systems need? Describe working, episodic, semantic, and procedural memory.
- How do you design long-term memory without polluting it?
- How do you implement human-in-the-loop (HIL) patterns and decide when to trigger human review?
- How do you monitor and observe autonomous agent behavior in production?
- How do you architect agents for regulated or compliance-heavy domains (e.g., financial, healthcare)?
- When do you use orchestration vs choreography patterns for multi-agent systems?
- How do you filter PII in agent pipelines before data reaches the LLM?
- How do you evaluate agent performance? What metrics matter (tool selection quality, action advancement, context adherence)?

### Fine-tuning and Training

- When would you fine-tune vs use prompt engineering? (reported across multiple companies)
- What is PEFT/LoRA and when would you use it?
- What is QLoRA and how does it differ from LoRA? When would you choose one over the other?
- What is RLHF and why is it important?
- Fine-tune or use prompt-engineered RAG?
- How would you design a model that can solve math problems? Walk through data collection, supervised fine-tuning, post-training, and evaluation.
- How would you design a scalable and efficient system for training a large language model, considering both computational and data constraints?
- Explain the RLHF pipeline: supervised fine-tuning, reward model training, and PPO. How does DPO simplify this?
- What is instruction tuning and how does it differ from pre-training?
- What is speculative decoding and how does it speed up inference?
- How do you convert implicit user behavior (edits, acceptance, rejection) into training signals for model improvement?
- Explain quantization. What are the trade-offs between model size, speed, and accuracy?

### Evaluation and Metrics

- What metrics do you consider when benchmarking and evaluating LLM performance?
- How do you evaluate a chatbot? (candidates wish they prepared for this)
- How do you detect and mitigate hallucinations in production? (reported across multiple companies)
- How would you prevent factual errors in a summarization system?
- How would you reduce hallucinations in a medical chatbot?
- What happens when the LLM is confidently wrong? How do you debug a RAG chatbot giving confident but wrong answers? (candidates wish they prepared for this)
- Explain SHAP, LIME, and model interpretability.
- How do you detect and mitigate hallucinations?
- Explain evaluation metrics: perplexity, ROUGE, BLEU. What are the pitfalls of n-gram-based metrics?
- What are your testing strategies for non-deterministic outputs?
- How do you measure accuracy in generative systems where traditional metrics don't apply?
- What operational/business metrics matter for AI systems beyond accuracy? (win rate, deflection rate, p95 latency)
- How would you evaluate and monitor a model in production, not just offline?
- How have you addressed bias/fairness in your models? Can you provide an example of a trade-off you've faced?
- What is time to first token and why does it matter for user experience?
- How do you measure hallucination rate in production?
- What is "vibes-based" evaluation vs. a formal eval framework? How do you build proper evals?
- How do you build a golden dataset for evaluation? How do you use it for regression testing?
- How does the system get better over time? Describe feedback and reinforcement loops.
- How do you decide success metrics for an ML model?
- How would you implement A/B testing for different prompt variations?
- How would you test a new model before full deployment? Describe A/B testing, canary, interleaved, and shadow testing strategies.
- Two models have identical accuracy but different confidence levels. Which do you choose? Explain model calibration.
- A production chatbot's accuracy dropped from 95% to 80% in six weeks. How do you diagnose the root cause before retraining?

### ML Fundamentals

- How do you approach data pre-processing and feature engineering?
- Explain SQL versus NoSQL databases for AI workloads.
- What steps would you take to diagnose performance bugs in a model?
- Should you optimize for latency or throughput? (for a personal assistant with one request)
- Should you use data parallelism for a single-request personal assistant? Why or why not?
- Explain how Transformers work. Why are they foundational? (reported across multiple companies)
- How would you handle real-time versus batch processing for data updates? When is one preferred over the other?
- How do you ingest and process different types of data (structured, unstructured, event data)?
- Explain the bias-variance tradeoff in simple terms.
- Why are neural networks usually not the first choice for tabular data?
- How do you handle imbalanced datasets in real projects?
- Explain the difference between RNN and LSTM.
- Debug a model that runs but doesn't learn. Identify broadcasting errors and dimension mismatches.
- Statistics questions: probability, distributions, regression, Bayesian analysis, hypothesis testing.
- Explain supervised vs. unsupervised learning. When would you use each?
- What is regularization? Compare L1, L2, and dropout.
- What is feature scaling and when is it necessary? Compare normalization vs standardization.
- Implement cosine similarity in NumPy.

### Python and Software Engineering

- How do you handle race conditions in your code?
- What is the Global Interpreter Lock (GIL) in Python?
- What is something unique about Python when it comes to concurrency?
- What are some problems you can run into when using asynchronous programming in Python?
- What is Docker?
- Why do we use Selenium?
- Have you heard about Redis?
- Explain the JavaScript event loop.
- How do you call models via API/SDK? How do you handle retries, timeouts, and logging?
- Which AI development platforms or tools do you regularly use, and why?
- Explain memory leaks and garbage collection in Python.
- What is the difference between class methods and static methods?
- Explain super() and Method Resolution Order in multiple inheritance.
- How do you debug Python code in production? "In production, there will be no VS Code."
- How do you use asyncio for concurrent I/O in Python? When would you use threading vs. multiprocessing instead?
- How do you optimize SQL queries? Explain the order of execution in SQL.
- What are Git branching strategies for deployment? How do you perform a rebase? How do you handle merge conflicts?
- Have you worked with real-time communication technologies like WebRTC?

### Infrastructure and MLOps

- How would you design a large-scale AI model deployment system?
- How would you design a distributed training system for deep learning?
- How would you design a scalable data pipeline for ML applications?
- How would you design a GenAI system to handle traffic spikes without overwhelming the model provider?
- How would you monitor production AI systems?
- What are major scaling challenges for LLM-powered applications?

### Cost and Latency Optimization

- Your app gets 1M queries/day - how do you optimize cost? (reported across multiple companies)
- How do you reduce token costs at scale? (candidates wish they prepared for this)
- How would you think about cost and capacity planning for an LLM-powered application at scale?
- How would you make GPT-based API calls cost-efficient under heavy load?
- How would you reduce token costs?
- Explain quantization and model distillation for inference optimization.
- Describe the latency/cost/relevancy tradeoff triangle in GenAI systems. How do you manage all three?
- How do you reduce latency in GenAI applications?
- Cost vs. quality trade-offs: when is a small open-source model "good enough" vs. GPT-4-class?
- By trimming prompts and caching embeddings, how would you reduce API spend? Walk through a before-and-after cost breakdown.
- Explain multi-layer caching strategies: retrieval cache, prompt cache, and response cache.
- What is model tiering? When do you route to a small distilled model vs. a large LLM?
- What is prompt compression and how does it reduce cost?
- Latency vs. throughput optimization for LLM serving - what are the trade-offs?
- How would you benchmark each LLM call in a multi-step pipeline to identify latency bottlenecks?
- Estimate the budget for a RAG pipeline at enterprise scale (e.g., 300,000 legal contracts).
- What's the real bottleneck in LLM serving throughput? How does PagedAttention address it?

### Safety and Guardrails

- When and how would you implement LLM guardrails?
- How would you design a language model that minimizes harmful outputs while still being useful and expressive?
- How would you build a system that detects whether content violates policy or contains offensive material?
- How do you protect against prompt injection and jailbreaking?
- What steps would you take to handle exceptions in a GenAI application?
- Explain Constitutional AI and alignment considerations.
- How do you handle data privacy and PII in prompts and logs?
- How do you address bias in training data and generated content?
- How do you red-team an LLM system?
- Your application generates code that gets executed. How do you prevent malicious code generation and execution?

## System Design Questions

### AI System Design

- Design ChatGPT.
- Design our Claude chat service.
- Design a small language learning model that could run on a phone while making sure it's polite.
- Here's a junior developer's design for an inference batching system. Can you review it and explain what you'd change or improve?
- Design the OpenAI Playground - specifically the feature that lets developers simulate full conversations and threads.
- Design a real-time chatbot API (low-latency handling, session management, concurrency, safety filters).
- Design a Document Q&A Assistant.
- Design a Hallucination-Free Banking Chatbot.
- Design a Hospital Voice Assistant (handle noise, privacy, latency, domain vocabulary).
- Design a Feedback Loop for Writing Tools.
- Design a Legal Contract Generation system with compliance requirements.
- Design an AI Search system scaling to 10M+ articles.
- Design a Resume Classifier for Team Routing.
- Design an AI-powered Candidate Sourcing System with 750M profiles, semantic search, and <500ms latency.
- Scale an AI chat feature to 1M daily users - discuss trade-offs. (reported across multiple companies)
- Design for 1M users (scale beyond prototype). (candidates wish they prepared for this)
- Design a system to process 10k user uploads per month (bank payslips, IDs, references). How would you extract data, detect inconsistencies, reject invalid files, and handle LLM provider downtime?
- Design a system that lets doctors automatically send billing info to insurers based on patient notes.
- Design a conversational recommender system that suggests products based on user preferences, combining chat, retrieval, and database layers.
- Design a fast autocomplete system using LLMs.
- Design an AI-powered legal assistant.
- Build a generative resume builder with memory.
- Create an internal Slack bot answering HR questions.
- Design a GitHub Copilot-style JavaScript development tool.
- Design an AI co-pilot like GitHub Copilot (real-time streaming completions).
- Design a Midjourney/Stable Diffusion image generation service (queueing, GPU scheduling).
- Design a Perplexity.ai / real-time LLM-powered search engine.
- Design a Ghibli Image Generator (text prompt ingestion, model selection, GPU inference, cost throttling, safety filters).
- Design a Dynamic Questionnaire Engine for an Insurance Platform (JSON-driven, frontend decision tree without backend calls).
- Design a user profile system addressing storage, multi-device tracking, and preference flexibility. Optimize for 100 million users with batch migration.
- Design a distributed search system capable of handling a billion documents and a million QPS, while also managing LLM inference for over 10,000 requests per second.
- Design hybrid search combining traditional text retrieval with semantic similarity - top-k similar documents from a corpus of over 10M documents with a response time under 50ms.
- Design a workflow to remove all dead links for hundreds of client websites assuming you have API access to overwrite their HTML.
- How would you design the UX for an AI assistant that is often slow?
- How would you surface model limitations or errors to users without breaking trust?
- Design a scalable image-generation pipeline for millions of users.
- How would you scale a generative content platform for millions of users?
- Design an In-Memory Database with SET, GET, BEGIN, ROLLBACK, COMMIT, and nested transaction support.
- Design an AI recommendation system.
- Design a fraud detection system.
- Design a chatbot architecture end-to-end (LLM + backend + data flow).
- Design a distributed job queue for 100k+ GPU training jobs with preemption and checkpointing.
- Design a temperature prediction system handling inconsistent global datasets (hybrid ML-LLM).
- Design an end-to-end RAG service: data ingestion, indexing, retrieval, generation, evals, tracing, guardrails.
- Design a rate-limiter and code the core part.
- Scaling AI systems to millions of users: latency and cost trade-offs, batching, caching, streaming, failure modes.
- Design ChatGPT's cross-conversation memory feature.
- Design a multi-step agentic workflow (meeting scheduling, code review, email campaigns).
- Design a content/policy violation detection system.
- Design a unified query engine across dispersed data sources like email, calendar, documents, and chat.
- How would you implement an AI application from start to finish, from kickoff meeting through deployment? (IBM)
- How would you design a scalable and reliable automation workflow? What considerations for error handling, monitoring, and debugging?
- How would you handle real-time versus batch processing for data updates? When is one preferred over the other?
- How do you ingest and process different types of data (structured, unstructured, event data)?

### Traditional System Design

- Design GitHub Actions.
- Design Slack.
- Design Online Chess.
- Design a Payment System.
- Design a Webhook Callback System.
- Design TinyURL (Bitly).
- Design Instagram / TikTok feed.
- Design Twitter / X (timeline, posting, followers, trending topics).
- Design YouTube / Netflix video streaming platform.
- Design Uber (ride-sharing backend: matching, ETA, pricing surges).
- Design WhatsApp / Messenger (1:1 + group chat at global scale).
- Design a distributed key-value store (like DynamoDB / Cassandra).
- Design Google Docs collaborative editing (real-time, eventually consistent).
- Design Yelp / Google Maps nearby search.
- Design a rate limiter (global, per-user, distributed).
- Design Discord (voice + text chat, millions concurrent in voice channels).
- Design Stripe payment processing system (high consistency, PCI compliance).
- Design a distributed job scheduler (like AWS Batch at planetary scale).
- Design a notification system that can send 1B notifications/day with <1% loss.
- Design a strongly-consistent distributed database (Spanner / CockroachDB-like).
- Design a high-frequency trading exchange matching engine.
- Our p99 latency went from 50ms to 2s overnight - how would you debug and fix?
- Design a global WebSocket service (10M+ concurrent connections).
- Design a global feature flag / config service (multi-region, zero-downtime rollouts).

### System Troubleshooting

- A system's 95th percentile latency spiked from 100ms to 2000ms. Identify bottlenecks rapidly.
- How would you handle a 10x traffic spike during a product launch?
- What happens if your primary data center goes offline for six hours?

## Coding Problems

### LeetCode / Algorithm Style

- Word Search on Grid using Trie + DFS (LeetCode Medium).
- LRU Cache with O(1) time complexity using HashMap + Doubly Linked List.
- Prime numbers between 0 and 100.
- Check whether two strings are anagrams of each other.
- Serialize Binary Tree (space-optimized, discussion-based with compression techniques and backward compatibility).
- LeetCode 2408: Design SQL.
- LeetCode 981: Time Based Key-Value Store.
- Unix cd command with symbolic link resolution.
- Reverse a linked list with constraints (AI-assisted coding round - candidate must prompt LLM effectively).
- Find the Excel column name from its column number (e.g., column 702 = "AAA").
- Construct a tree from a list where index = node value and value = parent node (LC Medium).
- CodeSignal GCA: 4 questions in 70 min - two medium-hard, one graph, one greedy with bit ops.
- Union Find problem + AI question (use DistilBERT to categorize CSV text with sentiments, must pass 5 test cases checking embeddings length, output structure).
- Write code for a banking application using HashMap/TreeMap. Design a task executor - store and pause tasks.
- A gRPC service is timing out. Add an async boundary, handle failure modes (retries, dead letter queues, idempotency), scale with multi-threading or message queues.
- Discuss serialization approaches, compression techniques, streaming formats, backward compatibility, and corruption recovery - no code written, pure discussion. (Microsoft senior)

### OpenAI-Specific Coding

- KV Store Serialize/Deserialize.
- In-Memory Database: Implement SQL-Like Operations.
- Versioned key-value store implementation (Time Travel Hash variant).
- Credits management system - track credit state across issued and used credits with different expiration rules and usage requirements, with increasing complexity.
- Refactoring round: 100-120 lines of intentionally convoluted, deeply nested code. Refactor for long-term maintainability while keeping existing tests green and extending to new ones.

### Anthropic-Specific Coding

- 4-level progressive coding assessment: Level 1 (SET/GET/DELETE), Level 2 (SCAN/SCAN_BY_PREFIX), Level 3 (timestamped operations + TTL), Level 4 (file compression/decompression with storage management).

### ML / AI Coding

- 1-NN (simplest KNN case) and feedforward neural network implementation.
- Transformer bug-fixing exercise with position embedding and KV cache issues.
- PyTorch code completion with complexity analysis.
- Implement Multi-Head Attention from memory.
- Implement a full Transformer layer from memory.
- Implement LoRA adapter from scratch.
- Implement efficient LLM API batch processing.
- Debug code handling embeddings.
- Write scripts preparing text for fine-tuning.
- Build a gRPC service for financial report generation (async conversion, thread management, error handling, batch processing).
- Implement neural networks, LSTMs, and RNNs from scratch using NumPy or PyTorch.
- Implement cached attention and grouped query attention variants.
- Implement beam search, top-k, and top-p decoding strategies from scratch.
- Implement autoregressive generation with top-p sampling.
- Implement logistic regression with SGD, L2 regularization, and early stopping in NumPy.
- Implement stratified K-fold splitting.

### Practical / Data Processing

- Speed coding: given a complicated JSON file, extract a specific part following some pattern, then feed that to an AI model and get the summary. 30-minute time limit, browser/ChatGPT allowed.
- Design a concurrent web crawler handling robots.txt, rate limiting, and circular references while maintaining data integrity and freshness.

## Behavioral Questions

### Project Deep Dives

- Walk me through an AI project you built end-to-end. (very common in 2026)
- Tell me about a project you're most proud of, and what role you played?
- What is your most challenging work in GenAI?
- Describe a time you reduced hallucinations/cost in production. (very common in 2026)
- Describe a time you had to optimize an existing process or workflow for efficiency or scalability.
- Describe a challenging prompt engineering problem that you solved.
- Is there an actual eval framework, or is it vibes-based?
- Present a "proud" project to a panel: design decisions, trade-offs, what broke, and what you'd change.
- Tell me about your past projects. (Apple, Discord, Anduril)
- Tell me about a recent/favorite project and some of the difficulties you had. (Meta)
- Tell me about a technical challenge that you have overcome.
- Tell me about the greatest accomplishment of your career. (Meta)
- What level of prompts have you written? What kind of projects did you work on?

### Conflict and Collaboration

- Give a specific example of conflict with another person, how resolution took form, and the rationale behind the choices you made.
- How do you collaborate with non-technical stakeholders?
- How do you manage workload in a distributed team?
- Conflict handling.
- Describe a time you disagreed with a team member about how to approach a problem. How did you handle it?
- Tell me about a time you struggled to work with one of your colleagues. (Meta)
- Tell me about a time you handled a difficult stakeholder.
- Tell me about a time you had to explain a complex technical concept to someone without a technical background.
- Tell me about a time you convinced someone to change their mind.
- What types of team members do you find difficult to work with? (Visa)
- Describe communication to resolve ambiguity. (Anthropic)
- Describe a time you had trouble communicating with stakeholders and how you overcame it. (OpenAI)

### Leadership and Ownership

- Have you mentored teammates remotely?
- Describe a time you drove technical decisions at scale and guided teams through complex challenges.
- Describe a time you mentored engineers who went on to senior roles.
- Tell me about a time you showed leadership. (OpenAI EM)
- Tell me about a time you led an initiative or took ownership of a challenging task.
- Tell me about a time you took the initiative to solve a problem.
- Tell me about a time when you made short-term sacrifices for long-term gains.
- How do you prioritize tasks?
- How do you lead under risk and uncertainty? (Anthropic)
- As a manager, how do you handle trade-offs? (OpenAI EM)
- How do you manage your team's career growth? (OpenAI EM)
- Tell me about a time when you worked on a project with a tight deadline.
- Explain management style, execution strategy, and culture choices. (Anthropic)

### Technical Decision-Making

- Which model provider do you prefer for creative writing tasks?
- How do you compare AI coding assistants like Cursor, Windsurf, or Claude Code?
- What recent AI paper or development caught your attention?
- What side projects have you built with AI?
- Why a particular storage solution over alternatives?
- How did you decide which model to use for inference?
- What frameworks are you familiar with? What have you built before?
- Which models have you worked with? Which cloud providers are you familiar with?
- Tell me about a time when you solved a complex problem and how you went about it.
- Tell me about a time when a technical misjudgment led to a project delay. What did you learn? (Anthropic)
- What would you do if, midway through a project, you realized it was actually unfeasible? (Anthropic)
- Describe a time you had to quickly learn a new technology or methodology to complete a project.
- How would you handle real-time versus batch processing for data updates? When is one preferred over the other?

### Failure and Learning

- Most challenging project.
- What would you do differently?
- Tell me about a time when you received negative feedback and how you handled it.
- What's a mistake you made, and what did you learn from it?
- Describe a project that didn't go as planned. What did you learn? (Anthropic)
- Describe a project where your AI solution failed and how you addressed it. (Google DeepMind)
- Why do you think we should NOT hire you? (Google, Visa)
- Tell me about a time when you had to think outside the box to complete a task.

### AI-Specific Behavioral

- How do you stay updated with fast-changing AI tech? (very common in 2026)
- How do you collaborate with non-technical stakeholders on AI features? (very common in 2026)
- Can you give an example of a time when you addressed ethical concerns in an ML project?
- Tell me about a time you made a safety-first decision in a project. (Anthropic)
- Tell me about a time you identified a major risk in an AI system — what did you do? (Mistral)
- Describe a time you reduced cost or latency in a production AI system.
- How do you manage ambiguity in ML projects where requirements and data evolve over time?
- How do you use AI coding agents in your work?
- Did you apply GenAI techniques to solve a problem not usually solved with GenAI?
- Do you fact-check AI outputs or just trust them? How do you validate AI-generated content?

### Culture and Motivation

- Why OpenAI? / Why Microsoft? / Why this company?
- Why change now?
- Tell me about yourself.
- Walk me through your resume. (OpenAI)
- Describe career decisions and culture fit. (Anthropic)
- How do you handle AI-safety conflicts with project goals? (Anthropic)
- Why do you want to pursue research? (for research roles)

### AI-Conducted Interview Follow-ups

These are follow-up probes from AI agents conducting interviews (emerging trend at Eightfold.ai):

- How would you handle edge cases?
- What alternative approaches did you consider?
- Time and space complexity analysis.
- Why did you choose this specific data structure?

## Project Deep Dive

Project deep dive (also called "technical project presentation") is an interview round where you present a past project and get grilled on technical decisions. Unlike behavioral questions that ask about situations, this is a structured presentation format testing ownership, architectural judgment, and depth of understanding.

### Opening Questions

- Walk me through your most technically challenging project. (OpenAI - 45-min presentation to a peer engineer)
- Walk me through a project you owned end-to-end. What were the key technical decisions? (Anthropic - 25-min presentation + 15-20 min discussion)
- Tell me about a project you're most proud of, and what role you played. (OpenAI)
- Tell me about a recent/favorite project and some of the difficulties you had. (Meta)

### Follow-up Probes

These are the probing questions interviewers ask during project deep dives to test depth of understanding:

- Why did you choose that particular storage/model/architecture over alternatives?
- Is there an actual eval framework here, or is it vibes-based? (OpenAI)
- What alternative approaches did you consider, and why did you reject them?
- How would you handle different requirements or scale constraints?
- What would you do differently if you started this project over?
- What was the most challenging technical decision and how did you make it?
- Did the solution actually work? How do you know? What metrics did you track?
- What were the trade-offs you made, and are you still comfortable with them?
- How did you communicate technical decisions to stakeholders?
- What would you explore next if you had more time?
- How do you monitor the model post-deployment for drift or degradation?
- What trade-offs did you make between retrieval speed vs. context length, fine-tuning vs. prompt engineering, GPU cost vs. latency?

## Take-Home Assignments

See also: [take-home-field-data.md](../rounds/case-study/take-home-field-data.md) for the take-home analysis and practice prompts.

### RAG / Chatbot Systems

- Blood test report AI: Create a project that takes a blood test report in PDF format, understands medical issues, and provides suggestions by fetching them from online blog articles. Submit in a few hours.
- Customer support RAG chatbot: Design a production-ready chatbot using open-source tools. Requirements: 100+ concurrent users, <2 second latency, grounded in company docs, cost-effective, analytics tracking. Score: 9/10.
- Document Q&A system: Build a document Q&A system with citation tracking for multi-hop questions.
- Build a RAG chatbot that ingests PDFs/documents, creates embeddings in a vector DB, and answers questions with citations (10+ candidate submissions across 5+ companies).
- Refactor a messy RAG codebase into a modular, production-ready service with FastAPI and LangGraph (5+ candidate submissions for one company).
- Build a policy document RAG assistant with mandatory source citations for every answer. Includes a 7-question evaluation set.

### Agent Systems

- Build an AI agent demonstrating natural interaction, agentic behavior, clear reasoning steps, and strong technical decision-making. 3-day window. Company: Eightfold.ai.
- Customer email campaign agent: Build an agent reading customer CSV data and generating personalized email campaigns with evaluation metrics.
- Code review agent: Implement a code review agent for Python files with actionable feedback.
- Conversational Calendar Booking Agent: LangGraph/LangChain orchestration, Streamlit chat interface, FastAPI backend, Google Calendar integration via Service Accounts, function calling for booking logic.
- Create a customer support agent relevant to the company's product within 1.5 hours. Red flag if candidate doesn't start with evals.
- Build a simple autonomous agent using an open-source LLM with a task-specific goal and an observability/eval layer.
- Build an assistant agent handling database queries, document search, and bash commands. Explicit evaluation criteria: tool selection accuracy, response grounding, error handling.
- Build a production-ready AI agent that transforms project management data into conversational business insights using dual-LLM architecture (primary + fallback).
- Build an agentic RAG system evaluated using RAGAS metrics (faithfulness, answer relevancy, context precision).
- Build a chatbot-driven TikTok Ad Campaign Creation Agent.

### Multi-Agent Systems

- Build a multi-agent content generation system: 5 core agents (research, writing, editing, SEO, publishing) orchestrated through a pipeline.
- Implement a minimal workflow engine with graph-based nodes, state management, branching/looping, and tool-based logic. Max 50 steps. Unit tests mandatory (6+ candidate submissions).
- Build a 5-agent CBT therapy system with crisis detection, safety filtering, and PII redaction.

### LLM-as-Judge / Evaluation

- Build an evaluation tool for LLM hallucination detection.
- Build a 4-stage bedtime story pipeline: Spec Builder, Storyteller, LLM Judge, Rewriter. Must use gpt-3.5-turbo. Up to 2 revision cycles (4+ candidate submissions).
- Build a sales insights agent with PII safety: 3-dimension evaluation (accuracy, safety, reasoning).
- Build a live chat agent grounded in FAQ knowledge base (2 candidate submissions with different tech stacks).

### Document Extraction and Processing

- Build a marksheet extraction API: parse complex table layouts and handwriting. Confidence scoring required. FastAPI + Docker + Gemini 1.5 Flash.
- Build a physician notetaker: medical transcription NLP system with NER and SOAP notes (3+ candidate submissions).
- Refactor a messy codebase into a modular, production-ready service (5+ candidate submissions for one company).
- Build an AI-powered legal document analysis tool for contracts.

### Voice AI and Conversational Systems

- Build real-time concall transcription and insight streaming for Indian accents.
- Build a Singapore public transport query agent with voice interface.
- Build a Telegram bot for investment coaching with safety filtering. 3 days / 6-8 hours.
- Build a live chat support agent with OpenAI, session persistence, and conversation history (2 candidate submissions).
- Build conversational agents with game-based evaluation (2 submissions).

### Full-Stack AI Applications

- AI-First CRM: HCP Module: React/Redux frontend, FastAPI backend, LangGraph with 5+ tools (summarization, entity extraction). Models: gemma2-9b-it or llama-3.3-70b via Groq API. Deliverable: GitHub repo + 10-15 minute demo video. Expected time: ~60 hours.
- Login page with validations: Create a login page accepting email and password with basic validations. Estimated 2-3 hours within 2-3 day window.
- Build a production-ready mental health MVP with safety, privacy, PII redaction, and evaluation.
- Build a production-grade distributed LLM processing pipeline with smart routing for 100K+ daily requests.
- Build an intelligent NPC system for a job simulation platform.
- Build an LLM-based rating prediction system with prompt evaluation and dashboards.
- Build a markdown-to-slides generator with cost and time metrics tracking.
- Build a deduplication and clustering pipeline with ARI/NMI evaluation metrics.
- Build a transaction matching system.
- Build a D&D dungeon simulation with context engineering. Evaluation rubric: 30% functionality, 30% challenge completion, 25% context engineering, 15% code quality. ~4 hours.
- Build a memory and personality engine using open-source LLMs only.

### Company Product Integration

- Roboflow: build a project using their CV platform and present to CTO.

### Performance / Optimization

- Anthropic performance take-home: Code optimization for speed. 4-hour limit. Python workload simulating TPU-like operations. Tests low-level optimization skills. Now open-sourced for practice.

### OpenAI-Specific

- 48-hour technical project: Take-home assignment delivered day after recruiter call, 48-hour completion window. Practical coding, not puzzle-based.

### Red Flags (Unreasonable Assignments)

Reported by candidates:

- 72-hour "Round 1" demanding full RAG + agents + UI.
- Build an LLM agent to ingest years of financial reports with stock price analysis and chart generation using only freemium APIs. Candidate withdrew, calling it "an unpaid mini-consulting project."
- 45 minutes for 3 complex tasks.

## Round notes

Questions from the field guide's per-round files that aren't listed above, followed by that
round's guidance on what interviewers evaluate and the most common mistakes.

### Theory

Additional questions:

- What's RAG? Explain the complete process.
- Text vs Vector search. When would you use each?
- You're making a system for huge PDF reports. How would you process them?
- What makes an AI system agentic?
- When agent is the wrong solution?
- How do you ensure the output from LLMs is consistent and accurate?
- What metrics do you consider when evaluating LLM performance?
- When would you fine-tune vs use prompt engineering vs RAG?

#### How to Prepare

Focus on practice over theory. Interviewers care more about how you build, evaluate, and operate AI systems than about transformer internals. The most common questions test RAG systems, agents, and production concerns.

- RAG systems - build a working pipeline end-to-end
- Agents - understand the full architecture: planning, tool use, memory, termination. Key questions: when NOT to use agents
- Testing and evaluation - be able to describe how you build golden datasets

Common mistakes:

- Describing how to build systems but not how to evaluate or monitor them
- Not being able to explain trade-offs - just knowing what something is without knowing when to use it
- Ignoring cost, latency, and failure modes - interviewers want production thinking, not prototype thinking

### Project deep dive

Additional questions:

- What business problem were you solving? Why was it a priority?
- Who was the customer? Who benefited from this work?
- What was your actual role in building this?
- Why did you choose that particular approach over alternatives?
- Why did you pick that particular tech stack for data processing?
- What went wrong? What was harder than expected?
- How did you debug production issues?
- What was the outcome? How did stakeholders react?
- How did you handle data quality and preprocessing challenges?

#### What Interviewers Evaluate

- Technical leadership - Did you drive decisions, or just execute someone else's plan?
- Decision-making insight - Can you explain the reasoning behind architectural choices, not just describe them?
- Communication clarity - Can you explain complex systems to a peer without losing them?
- Impact orientation - Do you think about resource allocation and business outcomes, not just technical elegance?
- Honest self-assessment - Can you discuss limitations and what you'd do differently? Engineers who acknowledge gaps still get hired.
- Depth of understanding - Can you go multiple levels deep when probed? Interviewers want to see you understood the implementation, not just the design doc.

Key signal: the best candidates frame around impact ("reduced response time by 40%"), not technology names ("used LangChain and Pinecone").

For hiring managers, this is one of the most reliable ways to assess seniority. How someone talks about their work reveals:

- Did they drive decisions or execute tasks given to them?
- Did they identify problems proactively or wait to be told?
- Did they influence others or work in isolation?

There is nothing wrong with executing well - but the level of ownership and initiative visible in the narrative determines fit for the seniority level the company is hiring for.

#### How to Prepare

Project selection - Choose a project that demonstrates ownership. Recent and greenfield is better.

Structure your narrative around a natural progression:

1. Business problem - What problem were you solving and why did it matter? Who was the customer? What would happen if you didn't solve it?
2. Solution approach - How did you solve it at a high level? What architecture did you choose?
3. Key decisions - What specific technical decisions did you make? Why these decisions and not alternatives? What did you consider and reject?
4. Problems encountered - What went wrong? What was harder than expected? How did you debug and fix it?
5. Outcome - Did it work? How do you know? What metrics prove it?

The "why" behind every decision is the most important part. Saying "we used Postgres" is not interesting. Saying "we chose Postgres over DynamoDB because we needed complex joins for our reporting layer, and the write volume was low enough that a relational database wouldn't bottleneck us" shows engineering judgment.

Common mistakes:

- Monologuing without pausing for questions
- Focusing on technology names instead of decisions and trade-offs
- Not being able to go deeper when probed on implementation details
- Choosing a project where you weren't the primary decision-maker

### AI system design

#### Expectations

AI system design is primarily a senior-level round. Mid-level candidates may get system design questions but interviewers don't expect depth - a reasonable high-level architecture is sufficient.

At senior and staff levels, interviewers expect:

- Reasoning across uncertainty - keeping the system predictable despite unpredictable outputs
- Trade-off fluency - retrieval speed vs context length, fine-tuning vs prompting, GPU cost vs latency
- Communication clarity - narrating how information flows through the system

#### AI System Design vs System Design

The fundamental shift: when models like GPT-4 and Claude became accessible via APIs, the hard part stopped being model training and started being system orchestration.

- Traditional ML focuses on training pipelines
- AI/LLM system design focuses on orchestrating pre-trained models

Key differences:

- Data focus - training data and feature engineering vs context engineering, chunking, retrieval quality
- Output type - structured (scores, classifications) vs open-ended text, code, images
- Determinism - generally deterministic vs non-deterministic by default
- Evaluation - precision/recall/F1/AUC on held-out sets vs LLM-as-judge, human evaluation, task-specific evals
- Cost model - training compute (periodic) + serving vs per-token inference cost (continuous) + retrieval
- Failure modes - data drift, training-serving skew vs hallucination, prompt injection, context overflow, cost blowup
- Iteration speed - slow (retrain model) vs fast (change prompt, adjust retrieval)

#### ML system design

ML system design interviews focus on full training pipelines (feature stores, model lifecycle, offline evaluation):

- Design a recommendation system
- Design a fraud detection system
- Design a spam classifier
- Design a search ranking system
- Design an ad click prediction system

"GenAI interviews still care about standard distributed-systems basics, but they'll push harder on evaluation, guardrails, and context/tooling design."

#### Traditional system design

General system design questions commonly asked at OpenAI L5 and other AI companies (for *software engineers*):

- Design a distributed key-value store (like DynamoDB / Cassandra).
- Design a rate limiter (global, per-user, distributed).
- Design GitHub Actions.
- Design Online Chess.
- Design Instagram / TikTok / X (timeline, posting, followers).
- Design YouTube / Netflix video streaming platform.
- Design Uber (ride-sharing backend: matching, ETA, pricing surges).
- Design WhatsApp / Messenger (1:1 + group chat at global scale).
- Design Google Docs collaborative editing (real-time, eventually consistent).

#### How to Prepare

#### Structure your answer

Follow a five-step progression:

1. Problem framing (5-10 min) - clarify users, constraints, quality expectations, guardrails
2. High-level architecture (10-15 min) - core components and data paths from prompt to response
3. Deep dive (20-30 min) - RAG design, tool use, memory, evaluation, safety
4. Trade-offs (10-15 min) - what breaks, how you detect it, graceful degradation
5. Conclusion - summarize, list risks, outline next iteration

Most questions map to four repeatable patterns:

- RAG - system orchestration and grounding accuracy (the most common pattern)
- Feedback and reinforcement - implicit/explicit signals, active learning loops
- Hallucination mitigation - retrieval-grounded pipelines, confidence estimation, source transparency
- Scalability and cost optimization - multi-layer caching, model tiering, prompt compression

#### What companies build

Real production AI systems from engineering blogs - these inform the kinds of systems you'd be asked to design:

- Doctolib - agentic AI for customer support: specialized agents in a directed graph, ~17K daily messages
- Uber - GenAI Gateway: unified LLM platform, PII redactor, 60+ use cases
- Airbnb - LLM-powered conversational AI with Chain of Thought reasoning and guardrails
- Perplexity - 200M daily queries, RAG on Vespa.ai, fine-tuned Sonar models
- Slack - stateless RAG, LLMs in escrow VPC for data privacy
- LinkedIn - AI agent platform, strict data layer siloing
- Anthropic - multi-agent research: Opus orchestrator + Sonnet subagents, ~15x more tokens than chat
- DoorDash - AI-driven evaluation flywheel for LLM chatbots, hierarchical RAG

#### Common mistakes

- Jumping to a solution without clarifying requirements, constraints, and success criteria
- Treating the LLM as a source of truth instead of grounding with retrieval, tools, or citations
- Designing only the happy path without failure modes, monitoring, or evaluation
- Over-indexing on tool names - "I'd use LangChain" instead of explaining why you'd chain retrieval and generation
- Ignoring cost and latency - token budgets, model tiering, caching strategies
- Ignoring safety - prompt injection, data leakage, unsafe tool execution
- Putting control flow in prompts instead of the orchestrator (agentic designs)
- Choosing agents because they're exciting, not because the problem requires autonomy

### Behavioral

Additional questions:

- How do you stay up-to-date with the latest developments in AI?
- What side projects have you built with AI? What frameworks and models have you worked with?
- Why [company]?
- Why do you want to work here?
- Why [this startup]? with evidence of due diligence

#### How to Prepare

Find the values of the company you're interviewing for. For each value, prepare 2-3 scenarios from your experience where you can tell a story demonstrating that value using the STAR format (Situation, Task, Action, Result).

If the company doesn't have publicly shared values, use [Amazon's Leadership Principles](https://www.amazon.jobs/content/en/our-workplace/leadership-principles) as a starting point - many companies have something similar.

#### Common mistakes

- Giving generic STAR answers without concrete specifics - numbers, outcomes, what actually happened
- Reusing the same story across multiple rounds instead of preparing distinct examples
- Talking about technology names instead of impact and trade-offs
- Bluffing when you don't know something instead of being honest and curious
