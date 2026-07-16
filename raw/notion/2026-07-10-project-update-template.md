# Project Update Template (+ AI Chapter Project Updates)

**Source:** https://app.notion.com/p/381f148b3ab780c297b3f2f2ace69806
**Last edited:** 2026-07-10

Template used for weekly/biweekly AI chapter project updates (Help Center, Virtual Assistant, MCP). Sections: Progress since last update, Results & Learnings (Capability Owner), Delivery (Trio, with Target date / Status 🟢🟡🔴 / Cause / Impact / Action if at risk), Next 2 weeks, Risks & blockers.

## Help Center Agent — summary Thu 9 Jul

**Progress:** tested search/reranking adjustments; validated that reranking significantly improves answer quality, but the Stockholm Bedrock region lacks the AI models needed to support it natively; identified data gaps — broken/mismapped links between old product-a articles and client-a Intercom articles.

**Finding → so what:** source reranking is critical, but Bedrock KB reranking is unavailable in Stockholm (no model support) → need to evaluate moving to Frankfurt region for reranking + more capable embedding models; also need to clean up article URL mappings.

**Delivery:** 🔴 Blocked — no golden evalset or evaluator tooling yet, so baseline performance can't be measured and no data-driven improvements can be made.

**Next 2 weeks:** experiment with RAG reranking + early stopping; explore Frankfurt region migration for Bedrock KB reranking; fix product-a→client-a URL mapping data quality; build baseline golden evalset and evaluators.

**Risks:** missing golden evalset/evaluators (core team to prioritize this cycle); Stockholm region model limitations blocking local RAG optimization (resolution: evaluate Frankfurt); poor user redirection from bad URL mapping (dedicated cleanup task).

## Virtual Assistant Agent — summary Thu 9 Jul (posted)

**Progress:** mapped VA foundations — analyzed business domains/use cases to define technical architecture and prep for estimation; began building a separate, stable service platform, deployed initial "Hello World" test version.

**Delivery:** Target end Q3. 🟢 On track.

**Next 2 weeks:** analyze business domains/boundaries/use cases; define technical architecture for agents/skills to enable estimation; deploy basic "Hello World" version; establish standalone service/platform foundation.

**Risks:** none active this cycle.

## External MCP Server — summary Thu 9 Jul (posted)

client-a is building a publicly hosted MCP server letting external AI clients (primarily Claude) read/act on client-a accounting data via natural language — invoicing, contacts, products, bank reconciliation — directly from Claude without switching to the product UI. MVP scoped to Denmark with API key auth.

**Progress:** read docs and started a tool naming/description convention; **pivoted MVP target market to France** — the new Zervent invoicing API covers ~95% of French invoice operations, so scope moved from Denmark to France, with a demo target at a French accounting conference in September; mapped all 70 planned tools against the new API (Zervent for France vs. existing product-a API) and updated the PRD; completed OAuth2 feasibility assessment with the IAM team; aligned with the banking team on language choice and long-term MCP architecture; published a formal RFC on Python vs. TypeScript for the MCP server runtime, coordinated with banking.

**Finding → so what:** Zervent API covers ~95% of French invoice operations and is accessible via the existing product-a API key — no new auth system needed for France. France becomes the right first market, with the September conference as a concrete demo target; Denmark/Netherlands launch follows once the Zervent routing layer is in place.

**Delivery:** 🟡 At risk — no solution yet for the OAuth2 dependency, which risks the Sept 14 France conference date. Finding a solution with the IAM team.

**Next 2 weeks:** standardize tool names/descriptions to meet Anthropic connector listing requirements; verify Claude prompts users for confirmation before data-modifying actions (tested locally in Claude Desktop); build a routing layer that detects French-market users and routes to Zervent vs. product-a; deploy the server to a staging environment for internal integration testing.

**Risks:** no ready OAuth2 solution (full implementation = months) — IAM + Sebastian syncing to determine whether the Advisor gateway is a viable shortcut or the public release timeline needs re-baselining; write tools not yet cleared for production — security review needed (Dmytro + stakeholders) before enabling data-modifying tools publicly.

## HC Agent — summary Fri 19 Jun

**Progress:** built first retrieval-validation smoke test; finalized and tested PII-masking/privacy pipeline; extracted ground-truth test data from past conversations and resolved website URL mapping issues; Help Center Assistant Agent fully built and ready for benchmarking; integrated DataDog + Langfuse for monitoring/error tracking/prompt debugging/cost tracking; built Terraform infra to auto-crawl and process help center docs; ran an Intercom escalation experiment (chat summary handoff to Intercom).

**Finding → so what:** ingested articles contained boilerplate website noise — added a temporary AI-agent filter, but the long-term fix is cleaning data earlier, at upload time. Regex alone failed to mask Danish names; combining a language gateway with SpaCy NLP + local database lists solved it — now have an accurate Danish PII-protection strategy.

**Delivery finding:** ~10% of Help Center requests mention a URL, another ~10% leave an email address — strong signals a user wants human assistance rather than an automated answer; useful for designing human-escalation triggers.

**Delivery status:** 🟡 At risk — target date TBD pending eval-set alignment; dependency on evaluation data/tooling delays official benchmark testing and launch prep. Action: align on human validation for QA pairs, define eval sets and grading criteria.

**Next 2 weeks:** clean up knowledge base data sources; host alignment session for human-validated QA pairs; optimize search/RAG retrieval; run benchmark testing across 6 metrics (routing, query quality, recall, correctness, hallucination defense, speed) once test sets unblock; define real-time Langfuse monitoring metrics + grading criteria/automation for golden eval sets; fix Terraform to separate staging/prod, add Intercom as a data source, remove legacy sources.

**Risks:** Help Center agent can't be evaluated yet — golden dataset exists and is ready, but graders and evaluation tooling are missing. Resolution: align cross-functionally this week to assign graders and set up tooling.

## Virtual Assistant — project update Fri 19 Jun

**Progress:** held client interviews on the VA MVP; rectified staging against production (Terraform, Bedrock resources); started migrating the VA PoC from TypeScript ADK to Python LangGraph — team chose to build Router, HC subgraph, and Receptionist Agent together in one step rather than the phased approach in the VA LangGraph Roadmap.

**Delivery:** 🟢 On track.

**Next 2 weeks:** more client interviews; continue LangGraph "Hello World" setup (Golden Path baseline — deployable Python LangGraph env with CI/CD, Langfuse tracing, DataDog observability).

## External MCP server — update Fri 23 Jun

First official project update now that the initiative has a dedicated space. MVP: publicly hosted MCP server for client-a accounting data, scoped to Denmark, API key auth (see PRD).

**Progress:** MCP server PoC built covering a subset of the target tool set — validated end-to-end, not yet deployed, foundation for continued work (not a throwaway); PRD review/refinement and estimation in progress.

**Auth note:** MVP uses API key auth via a custom connector in Claude, not a native connector — native connectors require OAuth, in dialog with IAM. Until then, users connect via a custom MCP connector + API key.

**Delivery:** target Aug 17, 2026. 🟢 On track.

**Next 2 weeks:** finalize scope/estimation (tool list still being scoped); start deployment work; talk to banking about legal/compliance.

## Older entry — VA project update, Fri 19 Jun

**Progress:** client interviews on VA MVP; staging/prod alignment (Terraform, Bedrock); finalized two ground-truth datasets from Intercom conversations (URL grounding/retrieval scores; escalation/out-of-scope detection) + exploratory data analysis on OOS/escalation signals; Langfuse integration done; Intercom escalation experiment done; HC UI components done (shared with VA).

**Delivery:** 🟢 On track.

**Next 2 weeks:** finalize Langfuse experiments SDK integration; more client interviews; move Intercom escalation experiment to staging; VA/HCA evaluation using new datasets with LLM graders, documented results, article coverage/corpus quality recommendations.

**Risks:** evaluation is crucial for tuning RAG config; implementing the HC UI components (part of product-a-web repo) into the VA MVP can take a long time.
