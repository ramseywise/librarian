## Review: rag_core_infra_improvements
Date: 2026-04-11

### Automated checks
- Tests: PASSED (305 / 0 / 0 — 1 pre-existing env gap: boto3 missing, unrelated)

### Plan fidelity

| Step | Plan | Implemented | Tests | Status |
|------|------|-------------|-------|--------|
| 1. Restructure: move 6 dirs under rag_core | git mv eval_harness, generation, ingestion, reranker, retrieval, schemas → rag_core/ | Done; stale index required `git rm --cached` on phantom paths first | 305 pass | Match |
| 1. Rewrite imports | 66 files: `agents.librarian.{mod}` → `agents.librarian.rag_core.{mod}` | Done via single-pass sed | 305 pass | Match |
| 2. setup.sh | check uv, copy .env, uv sync, mkdir data dirs | Done; executable | N/A | Match |
| 2. Makefile | setup, typecheck, eval-unit/regression/capability | Done; capability gated | N/A | Match |
| 3. OTel: otel.py | setup_otel(), idempotent, soft-fail, OTLP + Phoenix paths | Done | N/A | Match |
| 3. OTel: config.py | 4 otel_* fields on LibrarySettings | Done | N/A | Match |
| 3. OTel: factory.py | call setup_otel() at create_librarian() entry | Done | N/A | Match |
| 3. OTel: .env.example | OTEL_* vars documented | Done | N/A | Match |
| 3. OTel: pyproject.toml | otel extra with 5 packages | Done | N/A | Match |
| 4. docker-compose health checks | frontend healthcheck + start_period: 60s on api | Done | N/A | Match |
| 4. Jaeger service | profiles: [tracing], OTLP gRPC port, healthcheck | Done | N/A | Match |
| 5. mypy config | [tool.mypy] + overrides + mypy in dev deps | Done | N/A | Match |
| 5. asyncio_mode = "auto" | Added to pytest ini_options | Done; +1 test picked up | N/A | Match |

---

### Findings

**[Blocking]** `pyproject.toml:109-112` — Entry points reference pre-restructure paths

```toml
librarian-api = "agents.librarian.api.app:main"
mcp-snowflake = "agents.librarian.mcp.snowflake_server:main"
mcp-s3 = "agents.librarian.mcp.s3_server:main"
mcp-librarian = "agents.librarian.mcp.librarian_server:main"
```

`agents.librarian.api` and `agents.librarian.mcp` no longer exist — they moved to `agents.librarian.infra.api` and `agents.librarian.infra.mcp` in the earlier restructure. The `main()` functions exist at the correct new paths. Running `librarian-api` or any `mcp-*` CLI command will raise `ModuleNotFoundError` at runtime. Fix:

```toml
librarian-api = "agents.librarian.infra.api.app:main"
mcp-snowflake = "agents.librarian.infra.mcp.snowflake_server:main"
mcp-s3 = "agents.librarian.infra.mcp.s3_server:main"
mcp-librarian = "agents.librarian.infra.mcp.librarian_server:main"
```

---

**[Non-blocking]** `src/agents/librarian/utils/otel.py:45-46` — `provider` is dead code in the Phoenix branch

```python
resource = Resource(attributes={SERVICE_NAME: settings.otel_service_name})
provider = TracerProvider(resource=resource)   # ← created here

if settings.otel_exporter == "phoenix":
    register(...)  # phoenix sets up its own provider internally
    return         # ← provider never used
```

`provider` is built before the branch and discarded in the phoenix path. Phoenix's `register()` creates its own `TracerProvider` internally. Move the `resource`/`provider` construction inside the `else` block, or just drop it from the phoenix branch. No functional impact — it's immediately garbage collected — but it's misleading.

---

**[Non-blocking]** `setup.sh:19` — OTel extra not included in setup sync

```bash
uv sync --extra librarian --extra api --extra mcp
```

A developer who sets `OTEL_ENABLED=true` then runs `setup.sh` won't have the OTel packages installed. The `setup_otel()` soft-fail handles this gracefully (logs a warning), but it's a confusing onboarding experience. Consider either adding `--extra otel` to the sync (opt-in, harmless when disabled) or adding a note to the "next steps" output that OTel requires a separate sync.

---

**[Nit]** `infra/docker/docker-compose.yml:25-26` — `pip install streamlit` in the container command is fragile

```yaml
command: >
  sh -c "pip install streamlit && streamlit run frontend/librarian_chat.py
```

This was pre-existing, but worth flagging now that we're touching the file: `pip install` is blocked by the project's Bash hook and it installs on every container start. Streamlit should be in the Dockerfile or a separate `frontend` stage so it's baked into the image. Low priority given `frontend` is a dev-only convenience.

---

### Post-review fixes applied

- **[Blocking] fixed** — entry point paths corrected in `pyproject.toml` (→ `infra.api.app`, `infra.mcp.*`)
- **[Non-blocking] fixed** — `Resource`/`TracerProvider` moved inside the OTLP `else` branch; unused top-level import guard removed; phoenix branch now clean

### Verdict

- [x] **Approved** — blocking issue fixed inline; 305 tests still pass
