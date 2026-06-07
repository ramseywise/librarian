# AI Engineering Chapter Meeting #2 — Notes

**Source:** Google Drive (Google Meet Notes by Gemini, shared by Sebastian Rose)
**File ID:** 1jKU7UywHboRPihFNbuWBnfgbvI4HvqKxS3brf1Cezlk
**Date:** 2026-05-28
**Attendees:** Danni Gregersen, Sebastian Rose, Abhimanyu Aryan, Anders Dehn, Axel Simond, Cedric Deniau, Clara Quintans, Clément Gilardy, Dan Steenbjerg Rasmussen, Daniel Tadros, Dmytro Yarmak, Felix Schweickard, Hong-Thai Nguyen, Ingo Schindler, Jakob Henning Jensen, Jeremy Simon, Jonas Maia, Jonathan Coneggo, Manuel PEIXOTO, Marco Enrique Zimmermann, Marcos OLIVEIRA, Nicklas Munksgaard Larsen, Ramsey Wise, Silviu Lupu, Yan Zhang, Alex Makssoud, Vincent Salinos, Marc Roulet, Andres Arias, Olivier Chatelin, Raphael BACCONNIER, Teresa Chambel, David Gold

---

## Summary

Meeting reviewed agent framework adoption and KPI tracking strategies with finalized Langfuse legal and security status.

**Agent Framework Selection Strategies**
Teams analyzed internal framework transitions, noting shifts toward LangGraph and custom pipelines. A new selector tool was introduced to guide future technical framework decisions.

**KPI Tree Alignment Progress**
Leadership emphasized standardizing customer interaction metrics across teams. Various departments reported on their current status regarding automated resolution tracking and transaction matching success rates.

**Langfuse Legal and Security**
Legal approval for Langfuse is complete, enabling mandatory Single Sign-On and data governance implementation. Future meetings will focus on Model Context Protocol server integration.

---

## Decisions

**ALIGNED**
- **Langfuse SSO integration requirement** — The team aligned that Single Sign-On (SSO) is a mandatory requirement for the Langfuse implementation to satisfy security and compliance policies.

---

## Next Steps

- [Sebastian Rose] Create KPI Register: Create a register to centralize and share Key Performance Indicator trees from all teams.
- [Clara Quintans] Research Langfuse Access: Research methods to switch to two-factor authentication or single sign-on for Langfuse access.
- [Clara Quintans] Prepare MCP Discussion: Coordinate with team members to share experience regarding MCP server usage for the next meeting.
- [Hong-Thai Nguyen] Define Agentic Metrics: Consult with expert Product Managers to define business metrics for evaluating agentic performance.

---

## Key Discussion Points

### Agent Framework Survey

**Current team usage:**
- **Danni Gregersen (Banking/ADK team)**: Consistently using Google ADK throughout the project period. No experimentation with other frameworks.
- **Hong-Thai Nguyen (Advisor Production)**: Moved away from AutoGen (AG2) entirely. Building direct custom pipelines with well-defined workflow instead — "AG2 is slower and brings no additional benefit." Team defines exactly what agents need to do, links them by workflow.
- **Axel Simond (Virtual Assistant)**: Transitioning toward LangGraph for the next iteration of the virtual assistant. Previously used AutoGen/AG1.

**AI Agent Framework Selector Tool (Alex Makssoud):**
- Excel-based tool comparing AG2, LangChain, CrewAI, and Pyante across dimensions: multi-agent orchestration, RAG, role-based agents, reliability.
- Decision-support mechanism for conversations, not a strict benchmark or automated decision engine.
- Shared with chapter for teams to use and adapt. Can easily add more frameworks.
- Built originally for a US company discussion on framework selection.

### KPI Trees

**Virtual Assistant team (Sebastian Rose):**
- Primary KPI: percentage of customers with regular AI interaction (goal completion rate > X%).
- Goal completion = no escalation to customer support, or successful completion of an agentic action (create invoice, write email, etc.).
- Completion meaning varies by intent/context.

**Advisor Production team (Hong-Thai Nguyen):**
- Metrics: cost, token consumption, volume of interactions resolved through automated validation without human intervention (no-touch rate).
- Not yet formally defined; needs PM input on business metrics.

**Banking team (Clara Quintans / Jonas Maia):**
- No formal KPI tree yet. Have eval metrics for synthetic datasets but not product-level KPIs.
- In progress; will align once defined.

**Matching service team (Andres Arias):**
- Metric: percentage of correctly matched transactions to invoices.
- Tracking auto-reconciliation accuracy. ~90% success rate with current models.
- Tracking if auto-reconciled matches are later reverted by users.

**Plan:** Sebastian Rose to create a centralized KPI registry to share and align KPI trees across all teams.

### Langfuse Legal & Security Update (Clara Quintans)

- Legal review is complete.
- Contract being finalized to align with Shine's requirements (needed before production data use).
- Governance framework in development: PII reduction required before sending data to Langfuse (external SaaS hosting).
- SSO is mandatory once pro contract is signed (security team requirement).
- Onboarding process for new teams to production not yet defined.
- Development/testing use is fine in the meantime.
- Advisor Production team (Hong-Thai) has already connected Langfuse to Advisor Production staging for observability.

### MCP Server — Next Chapter Topic

- Next meeting will focus on Model Context Protocol (MCP) server.
- Daniel Tadros: team has an MCP server currently on staging.
- Clara Quintans: team member participated in hackathon MCP server group; will coordinate to share insights.
- Sebastian Rose's VA team also has MCP discussions and plans to present.
- Agreed: deferred to next session as it's a large topic requiring dedicated preparation.
