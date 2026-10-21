---
title: One-Off Codemod, Permanent Gate
tags: [patterns, pattern]
summary: "Migrate scattered literals to tokens with a throwaway codemod plus a permanent lint gate. Check the result on the built output and the shape of the diff, not on the text substitution. Keep the old-to-new map somewhere versioned, because a deleted script and a gitignored plan leave no archive. Re-review after every fix, because gate fixes tend to bring back the same defect class they closed."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-02-dis48-design-tokens.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-02-dis48-design-tokens.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-02-dis48-design-tokens.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-02-dis48-design-tokens.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-02-dis48-design-tokens.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-02-dis48-design-tokens.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-02-dis48-design-tokens.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-02-dis48-design-tokens.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-02-dis48-design-tokens.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-02-dis48-design-tokens.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-02-dis48-design-tokens.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-02-dis48-design-tokens.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-02-dis48-design-tokens.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-02-dis48-design-tokens.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-04-dis159-colour-contrast.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-04-dis159-colour-contrast.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-04-dis159-colour-contrast.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-04-dis159-colour-contrast.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-04-dis159-colour-contrast.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-04-dis159-colour-contrast.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-04-dis159-colour-contrast.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-14-dis236-token-lint-issue-refs.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-14-dis236-token-lint-issue-refs.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-14-dis236-token-lint-issue-refs.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-14-dis236-token-lint-issue-refs.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-14-dis236-token-lint-issue-refs.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-14-dis236-token-lint-issue-refs.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-14-dis236-token-lint-issue-refs.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-14-dis236-token-lint-issue-refs.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-14-dis236-token-lint-issue-refs.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-14-dis236-token-lint-issue-refs.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-14-dis236-token-lint-issue-refs.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-14-dis236-token-lint-issue-refs.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-14-dis236-token-lint-issue-refs.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-14-dis236-token-lint-issue-refs.md
---

# One-Off Codemod, Permanent Gate

akira's design-token issue replaced about 200 arbitrary Tailwind values (`bg-[#F5F3F0]`,
`text-[10px]`) across 47 `.tsx` files with 13 named colour tokens. It used two tools with
different lifetimes:

- **The codemod is single-use.** It is a script holding an explicit hex-to-token map. It
  runs once and is then deleted, so nobody re-runs it on a tree that has since moved on.
- **The gate is permanent.** `token-lint` fails `make gate` on any raw hex in `.tsx`. It
  has a named `ALLOWLIST`, with one line and one reason per exception. The codemod
  cleans up existing drift, and the gate stops new drift from appearing.

## Choosing the token set

- **Every token cites the design contract, or is marked as not in it.** Five hexes had
  no contract row. For each one, the actual call site was read and a default proposed.
  None was collapsed silently.
- **Don't add a second name for a value the scale already has.** Tailwind's default
  `rounded-xl` is already 12px and was used at 85 sites. A `rounded-card` alias would
  give one value two names, and two names for one value drift apart. The decision was a
  documented convention table instead of new config.
- **Usage and code comments decide which near-duplicate is real.** Two creams 3 RGB units
  apart looked like drift. But one had 8 call sites and a comment saying it matched the
  other placeholders. The other had a single site. The single site was treated as the
  outlier, and the call was raised as an open question rather than settled silently.
- **Collapse only if no function depends on the difference.**
  - A ring shade on a peach card stayed its own token. Collapsing it into `peach` would
    make the ring invisible against the fill it outlines.
  - Three near-blacks were collapsed into `ink`, but one site used the difference
    (`bg-[#1A1A1A] hover:bg-[#333]`). After collapsing it read `bg-ink hover:bg-ink`, a
    hover that no longer changed anything. Before merging two values, check whether any
    site uses the *pair*: hover, focus, selected, or ring-on-fill.
- **Scope the "must not" list explicitly.** Out of scope: the dark admin theme, heading
  sizes (valid utilities, not arbitrary values, so a bracket codemod cannot fix them),
  `focus:` to `focus-visible:` (a behaviour change, owned by the accessibility issue), and
  components. Each item was owned by another issue.

## Check what ships, not what the text says

The orchestrator checked the result independently of the agent that executed it:

- the `.tsx` diff was **197 added / 197 removed**, so no line was dropped or doubled;
- the **built CSS** emitted every token class with the correct declaration;
- 17 hand-built regex cases (12 must-catch, 5 must-ignore) all behaved correctly;
- mutation tests confirmed the gate fails when its guards are disabled.

A text substitution can look right and still produce no CSS. That happens when the class
is missing from the config or the content glob misses the file. Only the built CSS shows
it. Visual smoke testing was never run because the environment had no browser. That gap
was stated openly, not papered over.

Known limit: a Tailwind 3 token defined as `var(--color-x)` holding a full hex **does not
support opacity modifiers** (`bg-ink/90` needs an `<alpha-value>` channel form). See
[[Adoption Ban Needs an Escape Hatch]] for the overlay that hit it.

## "Git history is the archive" was false

The plan said that deleting the codemod was safe because `git log` would preserve it for
archaeology. Review found that the script had **never been committed**, and that the plans
directory is **gitignored**. So nothing in version control recorded which hex had become
which token. The one part that couldn't be recovered from `globals.css` was the three-way
near-black collapse. The fix moved the map into the design-reference doc as a "Token map"
table. A test parses that table and asserts that every row matches `globals.css`. It was
confirmed to fail on drift. A rule like "it's in history" needs its precondition checked
before anything is deleted.

## Fixes bring back the defect class they close

The gate took three review rounds. Round 2's verdict: *"The fix round introduced two new
important defects. This is the single strongest argument for the loop's 're-review after
every fix' rule."*

| Round | Defect | Class |
|---|---|---|
| 1 | Empty-but-existing ROOT gave `0 colours in 0 files`, exit 0 | silent no-op ([[Scan-Floor Guard Against Silent No-Op Checks]]) |
| 1 | `main()` at module scope: importing for tests scanned the tree and `process.exit(1)`'d, so 0 test results | untestable entry point |
| 1 | Mutating `walk()` to stop recursing cut coverage from 72 files to 2, and all 5 tests still passed | tests exercised the predicate, not the walk |
| 1 | `/#[0-9A-Fa-f]{3,8}\b/` matched issue refs like `#105`. But `#333` is a real colour that is also all digits | false positive |
| 2 | The `#105` fix added a lookbehind (`[ = ' "` or backtick), which **blinded** the gate to `bg-[var(--x,#1a1a1a)]`, `linear-gradient(..., #111111, ...)`, and inline `style="color:#111111"`. All three were verified to compile to real CSS | silent blind spot, introduced by a fix |
| 2 | The hover fix used `hover:opacity-90` but kept `transition-colors`, whose property list excludes `opacity`, so the hover snapped instead of animating | no-op affordance again |
| 3 (in-round) | The first `stripTrailingComment` truncated at `//` unless preceded by `:`, so it still cut at `src="//cdn..."`, hiding any hex after it | blind spot, again |

The final versions:

- `hover:opacity-90 transition-opacity`, confirmed in the built CSS.
- The lookbehind removed. Specificity now comes from the four real CSS hex lengths
  (`8|6|4|3`, so `#10567` cannot match), plus skipping comment-only lines and a
  quote-aware comment stripper, with a test for the escape branch.
- An entry-point guard, so the gate's predicate can be imported and tested.

Every fix to a matcher narrows or widens what it sees. Both directions can recreate the
defect the original review found, so each fix gets a fresh review of its own.

## The issue-reference false positive, settled by content class (2026-09-14)

The `#105` problem came back two weeks later as an issue of its own. Issue references
like `#222` and `#223` in an inline `describe('closes (#223)')` string and in a JSX
comment `{/* #222 */}` set the gate off. The comment-line regex only recognised lines
*starting* with `//`, `/*` or `*`. People had begun **rewording working test names to
satisfy the check**, which is a sign the check, not the code, needs fixing.

- **Separate the classes by content, not position.** A 3- or 4-digit match counts as a
  colour only if it contains at least one `a-f` letter. Every issue number is all-decimal,
  so one boolean per match fixes both shapes. The rejected alternative (skip matches
  bounded by parentheses or whitespace) depended on context and would also have skipped a
  real colour followed by a trailing space. Teaching the comment regex `{/*` would have
  been narrower still, since it misses the string case.
- **Measure the trade, then accept it in writing.** Treating all-decimal short hex as
  "not a colour" means an authored `#333` is no longer caught. A census found 23
  three-digit hex-shaped matches in the tree, all issue references, with 0 real
  all-decimal colours and 0 four-digit matches of any kind. 6- and 8-digit handling was
  left alone. The trade is documented at the filter and in the test.
- **Filter after the match. Don't touch the regex.** A post-match `isDigitOnlyShortHex`
  left `HEX_RE` unchanged, so every regression test pinned to its four-length alternation
  still held.

All eight review reporters returned no findings. The orchestrator then checked the
rewritten comments against the code and found one that **named the wrong mechanism**. It
claimed a trailing `// #105` was still flagged, when the stripper removes exactly that.
It also called the file-level `ALLOWLIST` a per-colour escape hatch, which it cannot be.
That is the same defect the comment block had been rewritten to fix. Rewritten comments
need checking against the code just as the code does.

## Second migration: palette classes (contrast fix)

Two days later a WCAG contrast bug turned out to be this same migration left unfinished.
The codemod's scope had been bracketed hex literals only. It never touched Tailwind's
built-in palette classes, so 150 `text-zinc-400/500` sites stayed, and 76 of them on the
consumer surface failed AA. The token gate was green the whole time, because its regex
matches `#` and a palette class has none. The fix reused the same pattern:

- **A two-key map** (`text-zinc-400`, `text-zinc-500` → `text-muted`). Each claim of "no
  per-site judgment needed" was checked with a grep, not assumed: no opacity suffix, no
  `dark:` or `hover:` prefix, and no longer class containing the key as a substring.
- **The luminance ceiling decided the token set.** Solving the WCAG ratio against the
  darker of the two backgrounds left only 4 RGB levels between `muted` and the lightest
  passing grey. A second "lighter muted" token would have been two names for one value,
  so every site collapsed onto `muted`. That included a WCAG-exempt disabled control,
  because leaving it would only have tripped the new gate.
- **A narrow gate extension.** The new rule bans only the two failing shades as text
  colours, not the whole palette, with path-prefix allowlists for the separately themed
  admin area. The admin area's own narrow failure (4.12:1 on a dark background) was
  scoped out explicitly and filed separately. Plans warned it could otherwise be assumed
  fixed because the class name is the same.
- **Sibling plans that edit the same line.** A tap-target fix changed other classes on
  the same five `className` strings. The two edits share no characters, so either order
  gives the same file. But git merges line by line, so developing both in parallel
  conflicts whichever order they land in. The tie-break: land the automated codemod
  first, and write the hand edits against the settled file rather than pasting the stale
  plan snippet ([[Readiness Is Pinned to a Tree State]]).

Neither fix could be tested under jsdom. See [[Render-Blind Test Layer]].

## See Also
- [[Scan-Floor Guard Against Silent No-Op Checks]] — extends (the empty-ROOT and lookbehind rounds are instances)
- [[Adoption Ban Needs an Escape Hatch]] — prerequisite-for (the primitives ban that consumed these tokens and hit the opacity limit)
- [[Readiness Is Pinned to a Tree State]] — extends (this issue's new gate invalidated sibling plans' snippets)
- [[Audit the Class, Not the Instance]] — instance-of (each review finding was swept across the whole diff)
- [[Render-Blind Test Layer]] — related (the palette-class follow-up could not be tested under jsdom)
- [[Default-Deny Guard With a Named Allowlist]] — extends (gate exceptions at value granularity, not file)
