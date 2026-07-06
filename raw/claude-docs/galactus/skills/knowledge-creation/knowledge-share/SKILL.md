---
name: knowledge-share
description: "Create a shareable artifact from the current repo state — Notion page, Google Drive doc, or Google Slides deck. Use when you want to communicate work to stakeholders: 'share this as a doc', 'create a summary page', 'make a slide deck of the eval results', 'put this in Notion'."
---

# Share — Create Shareable Artifacts

Turns repo context into a stakeholder-ready artifact. Supports three output formats depending on the ask.

---

## Step 1 — Clarify the ask

Ask the user for:
1. **Audience** — internal team, stakeholder, external? (determines tone and depth)
2. **Format** — text doc (Notion / Google Drive), or visual (Google Slides)?
3. **Scope** — what to cover: eval results, pipeline architecture, methodology, recent changes, or all of the above?
4. **Destination** — Notion (default), Google Drive, or Google Slides?

If already clear from context, skip the question and confirm the draft before creating.

---

## Format decision

| Ask | Format | Tool |
|---|---|---|
| "put in Notion", "create a page", "write it up" | Notion page | `mcp__claude_ai_Notion__notion-create-pages` |
| "google doc", "drive doc", "share as doc" | Google Drive doc | `mcp__claude_ai_Google_Drive__create_file` |
| "slide deck", "presentation", "ppt", "slides" | Google Slides | `mcp__claude_ai_Google_Drive__create_file` (mimeType: Slides) |

---

## Content templates

### Text doc / Notion page

Structure the content as:

```markdown
# [Project / Topic Name]

## What this is
<One paragraph: what galactus is, what problem it solves>

## What was evaluated
<Dataset name, size, source, date range>
<What the data represents (e.g. BKH customer support conversations)>

## Methodology
<Heuristic metrics: what they measure, how computed>
<LLM graders: which ones, what they grade, model used>

## Key metrics
| Metric | Value | Threshold | Pass? |
|---|---|---|---|
| <metric> | <value> | <threshold> | ✓ / ✗ |

## Findings
<2–4 bullet points: what the numbers say, what's working, what needs attention>

## Next steps
<What we're doing about the findings>
```

Pull metric values from the latest `data/bkh/stats/*_stats.json` if available.

### Google Slides deck

Create one slide per section. Use the Drive MCP to create a Slides file, then populate with text content per slide. Slides structure:

1. **Title** — project name, date, audience
2. **What we evaluated** — dataset overview (1 slide)
3. **How we measured it** — methodology at a glance (1 slide)
4. **Results** — metrics table (1 slide per dataset if multiple)
5. **Findings & next steps** — 3–5 bullets (1 slide)

---

## Step-by-step

1. Gather scope from user (or infer from context)
2. Read relevant files:
   - Latest stats JSON: `data/bkh/stats/` (for metric values)
   - `evals/README.md` (for methodology overview)
   - `data/bkh/eval_config.yaml` (for dataset inventory)
3. Draft the content using the template above; show to user for review
4. On confirmation, create via MCP:

```python
# Notion
mcp__claude_ai_Notion__notion-create-pages(
    pages=[{
        "title": "...",
        "content": "...",   # markdown
        "parent_id": "..."  # ask user or leave for default workspace
    }]
)

# Google Drive doc
mcp__claude_ai_Google_Drive__create_file(
    name="Galactus Eval Summary — <date>",
    mimeType="application/vnd.google-apps.document",
    content="..."
)

# Google Slides
mcp__claude_ai_Google_Drive__create_file(
    name="Galactus Eval Deck — <date>",
    mimeType="application/vnd.google-apps.presentation"
)
```

5. Return the link to the created artifact.

---

## Notes

- Always show the draft to the user before creating — don't publish without confirmation
- If metric data isn't available (stats JSON missing), note it as "run `uv run python -m evals.pipelines.run stats --dir <eval_sets_dir>` first" rather than leaving blanks
- For Slides: Drive MCP creates the file but doesn't populate slides natively — generate the text content and tell the user which slide gets what; they can paste or you can use a follow-up tool if available
