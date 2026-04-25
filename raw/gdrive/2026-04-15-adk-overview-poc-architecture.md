# ADK Overview & POC Architecture

**Source:** Google Drive (shared by Dan, shine.co)
**File ID:** 1iRq0dDS6ZuPbSa520PYkF0ss0giPCqanqz90t664Js0
**Created:** 2026-04-15 | **Modified:** 2026-04-23
**Type:** Google Slides presentation (13 slides)

---

## Slide 1: Title

ADK Overview & POC Architecture

---

## Slide 2: Runtime Event Loop

*(Visual diagram — ADK's runtime event loop architecture)*

---

## Slide 3: Callback

*(ADK callback mechanism)*

---

## Slide 4: Plugin

*(ADK plugin system)*

---

## Slide 5: Features

*(ADK feature overview)*

---

## Slide 6: ADK — Strengths and Trade-offs

*(Detailed strengths and trade-offs)*

---

## Slide 7: ADK — Strategic Upside and Key Trade-offs (C-level)

*(Executive summary of ADK positioning)*

---

## Slide 8: Goals for the POC

**Fast**
- Minimize LLM calls to reduce latency and cost
- Optimized for prefix caching to improve performance at scale

**Scalable**
- Scalable across domains to manage tool, instructions, and context complexity
- Scalable across teams to enable clear ownership and coordination

---

## Slide 9: Architecture Ideas (Four Patterns Evaluated)

### Manager / Experts as Tools
**Pros:** Clear boundaries, multi-model flexibility, framework agnostic A2A
**Cons:** More LLM calls, higher latency

### Manager / Experts
**Pros:** Strong domain separation, multi-model flexibility
**Cons:** Coordination overhead, more complex handoffs

### Router / Experts / Orchestrator
**Pros:** Strong domain separation, efficient routing, multi-model flexibility
**Cons:** Coordination complexity, harder to govern

### Agent with Skills & Compaction ← (selected/recommended: "C")
**Pros:** Domain separation, minimal coordination, lean context via dynamic tools
**Cons:** Less explicit orchestration, softer domain boundaries, limited per-domain model specialization

*Patterns labelled M/M/R/C — "C" (Agent with Skills & Compaction) appears to be the recommended POC architecture*

---

## Slide 10: POC Architecture (v1 — Static HTML client)

```
Tools        Transport    Data     Client
FastMCP  →   FastAPI   →  DB       Python
                          RAG      JavaScript
                          Static   Test App
                          HTML
Agent: FastAPI
Domain: [domain layer]
```

---

## Slide 11: (Visual diagram — not captured in text extraction)

---

## Slide 12: POC Architecture (v2 — React/Vite client with A2UI)

```
Tools        Transport    Data     Client
FastMCP  →   FastAPI   →  DB       TypeScript
             FastAPI      RAG      React/Vite
             a2ui          
Agent: FastAPI
Domain: [domain layer]
```

*Note: v2 introduces A2UI (agent-to-UI) pattern with FastAPI as the a2ui transport layer*

---

## Slide 13: DEMO

*(Live demo segment)*
