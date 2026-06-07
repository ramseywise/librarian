# AI Engineering Chapter Meeting #1 — Notes

**Source:** Google Drive (Google Meet Notes by Gemini, shared by Sebastian Rose)
**File ID:** 1QCT4pDCh4fR9W3nFRgelMqRuXm4V4_9BWKYD-jXMq1I
**Date:** 2026-05-15
**Attendees:** Manuel PEIXOTO, Nicklas Munksgaard Larsen, Dmytro Yarmak, Felix Schweickard, Ingo Schindler, Daniel Tadros, Sebastian Rose, Teresa Chambel, Hong-Thai Nguyen, Dan Steenbjerg Rasmussen, Marco Enrique Zimmermann, Ramsey Wise, Marcos OLIVEIRA, Silviu Lupu, Jonas Maia, Abhimanyu Aryan, Yan Zhang, Danni Gregersen, Anders Dehn, Cedric Deniau, Clara Quintans, Axel Simond, Raphael BACCONNIER, Jonathan Coneggo, Jakob Henning Jensen, Clément Gilardy, Jeremy Simon

---

## Summary

The team reviewed Langfuse functionality for LLM observability and decided to pilot the platform for evaluation.

**Langfuse features and evaluation**
Participants explored Langfuse capabilities including prompt management, tracing, and metric tracking. They emphasized the need for transparent auditing and self-hosted deployments to meet compliance requirements.

**Agentic project observability needs**
Discussions focused on modeling complex agentic workflows and the importance of golden datasets for performance evaluation. The team concluded that deterministic metrics suit their current project needs better than LLM-based judges.

**Adopting Langfuse for testing**
The team decided to move forward with testing Langfuse for observability, marking the transition away from other evaluation tools. Future meetings will shift to a bi-weekly 1 hour schedule.

---

## Decisions

**NEEDS FURTHER DISCUSSION**
- **Tool selection for Shai project pending** — The team identifies a need for further evaluation and collaborative testing of available observability and evaluation tools to determine the best fit for the Shai project.

**ALIGNED**
- **SaaS hosting chosen for Langfuse testing** — The team determines that the SaaS version of Langfuse will be used for the current testing phase to avoid additional infrastructure management overhead.
- **LangFuse adoption for observability** — The virtual assistant and SHI teams will adopt LangFuse for observability and discontinue the use of Patronus AI.
- **Utilization of deterministic evaluation metrics** — The team will prioritize the use of deterministic evaluation metrics over LLM-as-a-judge for the current project phase.

---

## Next Steps

- [Danni Gregersen, Teresa Chambel] Send Slides: Distribute the meeting presentation slides to all participants.
- [Danni Gregersen, Teresa Chambel] Setup Langfuse Environment: Create an experimental environment in Langfuse to allow the team to evaluate the tool against their specific agentic project requirements.
- [Danni Gregersen] Setup Langfuse project: Initialize a workspace in the platform for the team. Grant access to facilitate testing of observability features.
- [Sebastian Rose] Reschedule team meeting: Shift the recurring session to a 1 hour time block on Thursday afternoons. Ensure the Friday slot is cleared for all participants.
- [Hong-Thai Nguyen, Manuel PEIXOTO] Evaluate Langfuse capabilities: Test the platform for benchmarking features while continuing to develop internal deterministic metrics.

---

## Key Discussion Points

### Langfuse Presentation (Danni Gregersen + Teresa Chambel)

- **Observability motivation**: Moving from "black box" to "glass box" LLM systems — complete transparency into inputs, outputs, and multi-agent steps. Auditability is a compliance requirement for AI inspections.
- **Datadog comparison**: Datadog has LLM observability but is not purpose-built for LLMs. Langfuse is purpose-built with SaaS and self-hosted deployment options.
- **Langfuse features**: Tracing (tool calls, guardrails, execution time, cost), prompt management (non-engineers can update prompts without code changes), experiment tracking (custom metrics like F1 score, latency), custom dashboards.
- **Cost model**: Unlimited users, charged per usage not per seat — scales across engineering and domain-expert teams.
- **Prompt management approach**: Banking team took a "Langfuse-first" approach — prompts managed in platform, CI checks alignment with repo fallbacks. Enables fast iteration without code changes.
- **Experiment traceability**: Platform tracks results and metrics but does not support uploading/running custom Python code — experiments must run in team's own code, results pushed to Langfuse.
- **Multi-agent modeling**: Langfuse can trace inter-agent communication via OpenTelemetry. Non-LLM deterministic steps can be tracked via the SDK.
- **SaaS vs self-hosting**: SaaS avoids infrastructure overhead; self-hosting preferred for PII/compliance. Security review currently underway.
- **Compliance pattern**: Use token-based references (IDs) to files in golden datasets rather than copying raw documents, to support data deletion compliance.

### Advisor Production Team — Agentic CPA Project (Hong-Thai Nguyen + Manuel PEIXOTO)

- **Project**: Automates invoice document processing using multiple agents + deterministic code. Input = invoice documents; output = posting entries. Agents can call other agents; deterministic code paths for specific steps.
- **Prior tool**: Patronus AI (self-hosted on-premise inside SHI). Moving away from it as it doesn't fit current SHI context.
- **Evaluation requirements**:
  - Deterministic/static metrics only (NOT LLM-as-a-judge) — hard output requirements for accounting fields
  - Evaluation must run on every PR (CI integration)
  - Public/accessible metrics so everyone sees when quality changes
  - Golden datasets built by domain experts (e.g., accountants), not just engineers
  - Evaluation conditions should be close to production (same context, models, data)
  - Measure: accuracy, correctness, no-regression, latency
- **Golden dataset tooling**: In-house tool allowing domain experts to annotate invoices and correct agent output. Expensive to build manually; partial automation via historical data possible.
- **Langfuse evaluation fit**: Open to trying Langfuse for observability. In-house evaluation solution being built for specific metric needs. LLM-as-a-judge considered overkill for hard-output accounting requirements.
- **Framework decision**: Moving away from frameworks (AutoGen/AG2); now building direct custom pipelines with well-defined workflow — "it's faster and brings nothing from AG2."

### Meeting Cadence
- Moving to bi-weekly, 1-hour sessions on Thursday afternoons (from 90-minute format).
- Next topic: Agentic frameworks and protocols.
