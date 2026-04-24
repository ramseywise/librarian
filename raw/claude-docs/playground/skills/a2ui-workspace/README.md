# a2ui Skill — Eval Workspace

Evaluation runs for the [a2ui skill](../a2ui/SKILL.md).

## Results summary

| Iteration | Change                                                                               | With Skill | Without Skill | Delta     |
|-----------|--------------------------------------------------------------------------------------|------------|---------------|-----------|
| 1         | Initial draft, easy evals (v0.8 vs v0.9 comparison)                                  | 92%        | 100%          | -8pp      |
| 2         | Replaced easy eval with checkout form; fixed debug responses to include JSON example | 94%        | 22%           | +72pp     |
| 3         | Added `action` reminder to Button in skill                                           | **100%**   | 22%           | **+78pp** |

## Eval prompts

| ID | Prompt                                                                                       | Why it's useful                                                                                                           |
|----|----------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------|
| 1  | Write an ADK agent that outputs a product card (image, name, price, Add to Cart button)      | Tests core component generation, ADK integration, correct message structure                                               |
| 2  | Write a checkout form surface with TextField, MultipleChoice, summary Card, and data binding | Tests adjacency list model, path binding, `dataModelUpdate`, complex structure — baseline hallucinates a fake schema here |
| 3  | My surface shows a blank screen after sending `surfaceUpdate` — what's wrong?                | Tests protocol knowledge; baseline gives generic web debugging advice and never mentions `beginRendering`                 |

## Key finding

Without the skill, Claude frequently **halluccinates a fake A2UI schema** — nested `children` trees, `"type": "card"` shorthand, `bind` fields, `expression` fields — none of which exist in the protocol. The skill prevents this entirely.

## Directory structure

```
iteration-1/   Initial 3 evals (easy)
iteration-2/   Revised evals + skill fixes (debug JSON example, harder eval 2)
iteration-3/   Final iteration (Button action fix) — 100% pass rate
  eval-product-card/
    with_skill/    run-1/grading.json, outputs/response.md, timing.json
    without_skill/ run-1/grading.json, outputs/response.md, timing.json
    eval_metadata.json
  eval-checkout-form/   (same structure)
  eval-debug-blank-screen/  (same structure)
  benchmark.json
  benchmark.md
```

## Description optimization

**Not yet run.**

### What it does

The `description` field in a skill's YAML frontmatter is the *only* thing Claude reads when deciding whether to load the skill for a given prompt. Claude never reads the skill body until after it decides to trigger. So a poorly-worded description means the skill either:

- **Under-triggers** — doesn't load when it should (user asks about A2UI, skill sits idle, Claude hallucinates)
- **Over-triggers** — loads on unrelated prompts ("render a chart", "generate UI mockup") wasting context

Description optimization runs an automated loop that:

1. **Evaluates the current description** against a set of 20 test queries — half that *should* trigger the skill, half that *should not*. Each query is run 3 times to get a reliable signal.
2. **Proposes an improved description** based on which queries failed (Claude-as-optimizer, prompted with the failure cases).
3. **Re-evaluates** the new description on both the training queries and a held-out test set (to avoid overfitting).
4. **Iterates up to 5 times**, then returns the best-scoring description.

### Why it matters for this skill

The a2ui skill's current description contains phrases like "agent-generated UI", "server-driven UI", and "structured UI JSON" — these could plausibly match prompts that have nothing to do with A2UI (e.g. someone building a React dashboard or asking about OpenAI function calling). The optimizer finds language precise enough to avoid those false positives while still firing reliably when someone asks about A2UI surfaces, components, or message formats.

### How to run it in a future session

Say: **"optimize the a2ui skill description"**

The skill-creator will:
1. Generate 20 trigger/no-trigger eval queries and show them to you for review/editing in a browser UI. DONE! see .claude/skills/a2ui-workspace/optimize-skill-descriptionm/eval_set.json
2. Run the optimization loop automatically in the background (~10–15 min)
3. Show you the before/after description with scores
4. Update SKILL.md if you approve

The underlying command (run from `.claude/skills/skill-creator/`):

```bash
python -m scripts.run_loop \
  --eval-set <path-to-trigger-evals.json> \
  --skill-path /Users/bifrost/Developer/adk-agent-samples/.claude/skills/a2ui \
  --model claude-sonnet-4-6 \
  --max-iterations 5 \
  --verbose
```
