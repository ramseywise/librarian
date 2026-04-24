---
description: Generate a Claude Code usage insights report from your session history
---

# Claude Code Insights

Analyze all your Claude Code sessions and generate a rich HTML report covering:
- What you work on and how you use Claude Code
- Big wins and friction patterns
- Features and usage patterns to try
- Ambitious future workflows

## Steps

1. Load `.claude/skills/insights_analysis.md` — use this as the interpretation framework when reviewing the generated report with the user.

2. Check that `ANTHROPIC_API_KEY` is set in the environment. If not, tell the user:
   > "ANTHROPIC_API_KEY is not set. Please run: `export ANTHROPIC_API_KEY=your_key_here` and then run `/insights` again."
   Then stop.

2. Run the insights script:
   ```
   python3 ~/.claude/scripts/insights.py
   ```

3. Once complete, open the report:
   ```
   open ~/.claude/usage-data/report.html
   ```

4. Tell the user how many sessions were analyzed and the date range covered.

## Options

You can pass arguments to customize the run:

- `--dry-run` — extract stats only, no API call, print JSON to stdout
- `--model claude-sonnet-4-5` — use a faster/cheaper model (default: claude-opus-4-5)
- `--output ~/Desktop/insights.html` — write report to a custom path

Example with options:
```
python3 ~/.claude/scripts/insights.py --model claude-sonnet-4-5
```
