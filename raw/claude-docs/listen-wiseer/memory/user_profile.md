---
name: user_profile
description: Developer profile — stack, preferences, and communication style
type: user
---

- AI engineer on a large cross-functional team (BE/FE/ML/AI engineers + product trio — PM, designer, data analyst)
- Primary presentation audience: this mixed technical/product team
- Software engineer building AI-powered applications in Python
- Comfortable with async Python, LLM orchestration (LangGraph), and modern ML tooling
- Prefers concise, direct explanations — skip basics unless asked
- Uses uv, ruff, pytest, Pydantic v2 as defaults
- ML stack: PyTorch, HuggingFace/transformers, Polars, numpy, scikit-learn
- LLM: Claude API (anthropic SDK) + langchain-anthropic when LangFuse tracing is required
- Follows phased workflow: research → plan → execute → review (with human gates)
- All pipeline phases run directly in the main conversation context (not subagents)
- Workspace setup: global config in `~/.claude/`, project config in `{project}/.claude/`
- Hooks handle formatting (ruff) and test gates (pytest before commit) — do not run these manually
- Wants memory kept minimal: user profile + project decisions + genuinely non-obvious lessons only
