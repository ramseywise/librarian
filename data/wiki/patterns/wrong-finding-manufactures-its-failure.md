---
title: A Wrong Finding Can Manufacture Its Failure
tags: [eval, llm, pattern]
summary: In silent-failure review, a coherent but unverified claim about a framework API is most dangerous because its "fix" looks like a safety improvement and can cause exactly the failure it warns about — so a blocker in that dimension requires observed behaviour (built output, emitted CSS/JS, type definitions), not a persuasive argument.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/skills/review-silent-failure/SKILL.md
  - data/raw/claude-docs/kiez-archive/skills/review-silent-failure/SKILL.md
  - data/raw/claude-docs/diskoe/skills/review-silent-failure/SKILL.md
  - data/raw/claude-docs/playground/skills/review-silent-failure/SKILL.md
---

# A Wrong Finding Can Manufacture Its Failure

## Incident

An agent reviewer in the silent-failure dimension (repo akira) filed a **blocker**: a root
layout applied a font loader's `.variable` property as a class, which the reviewer reasoned
"holds the literal string `--font-…`", so the class matched nothing and the page silently
fell back to a default font. Proposed fix: use `.className` instead.

The reasoning was coherent and the failure mode sounded real. One grep of the build output
disproved it: `.variable` is the generated class that *defines* the CSS custom property.
The proposed fix would have removed that definition — **causing the silent fallback the
finding was written to prevent.**

## Why this dimension is exposed

Silent-failure review is drawn to fallback chains — a font that falls back, a config that
defaults, a value that resolves to empty. That is exactly where a plausible misreading of a
library's API does the most damage, because the "fix" also looks like hardening and passes
casual review.

## Rule

Before filing, **observe** the failure: read the built output, the emitted CSS/JS, or the
package's own type definitions. A blocker in this dimension needs observed behaviour, not
an argument. Also excluded from the dimension: intentional suppression with a stated
reason, best-effort paths that say so, errors handled by a caller you have actually read,
and pre-existing silent failures the diff did not touch.

The same skill's repo-specific checks name the classic masks: "no data" rendered for "no
permission", and untyped query clients (`db as any`) widening the space where a failure can
look like an empty result.

## See Also
- [[Review Reporter Ground Rules]] — extends (observed evidence as the bar for a blocker)
- [[Evidence Classification Model]] — related (reasoned vs observed evidence states)
- [[Fallback Mistaken for the Design]] — related (fallbacks as the dimension's hunting ground)
- [[Fixing an Accidentally Load-Bearing Bug]] — related (a correct fix that removes behaviour something depended on)
