---
title: Verbatim Evidence Quote Verification
tags: [patterns, prompting, pattern]
summary: Require every scored tag an enrichment model emits to carry a short verbatim quote from the evidence, verify it after parsing against each evidence block separately (a joined haystack lets a quote straddle two blocks and pass), drop an unverifiable tag through the same channel as an out-of-vocabulary one, and check that every batch path still has the evidence in scope or every tag drops silently.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-23-dis373-venue-probe-v3.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-23-dis373-venue-probe-v3.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-23-dis373-venue-probe-v3.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-23-dis373-venue-probe-v3.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-23-dis373-venue-probe-v3.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-23-dis372-pre-model-evidence-stage.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-23-dis372-pre-model-evidence-stage.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-23-dis372-pre-model-evidence-stage.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-23-dis372-pre-model-evidence-stage.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-23-dis372-pre-model-evidence-stage.md
---

# Verbatim Evidence Quote Verification

From the third version of a venue-enrichment probe (repo akira, 2026-09-23). The first two
versions reached 21/40, then 25/40 on a judge pass. The diagnosis was that crawled site text
was fetched, counted and then thrown away before it ever reached the model. So the model's
tags rested on nothing anyone could check. v3 put the text back in the prompt and made the
model show its work.

## The mechanism

- **One quote per scored value.** Each scored tag and each scored scalar gains a required
  `evidence_quote`: a short verbatim excerpt (about 15 words or fewer) from the description
  or the site text that the value rests on.
- **Verify after parsing, deterministically.** A pure check confirms the quote really occurs
  in the evidence. If it does not, the tag is **dropped**.
- **Reuse the existing drop channel.** Out-of-vocabulary tags were already collected into a
  `dropped[]` list. The unverified-quote drop shares that list and gains a `reason` field.
  The flagging and writeback code downstream already read it, so nothing needs a second
  parallel list. A heuristic flag counts unverified quotes so the rate is visible.
- **Cap the evidence at capture, not at prompt build.** The site text excerpt was capped
  (6 000 chars, a stated guess to replace with a measured value) where it is first written to
  the crawl artifact. Every later reader of that artifact then gets the same bound, not just
  the one prompt builder. A crawler holding thousands of full pages in memory had already
  exhausted a 2 GB heap once.
- **Check what the source allows before the text reaches a model.** A crawler flag for
  site opt-outs that restrict *use* of content, not only fetching, already existed. Nothing
  read it before v3. It now filters text out of the prompt.

## The defects that surfaced while building it

1. **A joined haystack verifies quotes that do not exist.** The first verifier concatenated
   the description and the site text into one string. A "quote" made of the end of one block
   and the start of the next then passed as genuine. Search each evidence block on its own.
2. **A batch path without inputs drops everything.** The batch-collect CLI route had no
   probe inputs in scope when it parsed results. Every tag would have failed verification and
   been dropped: a silent total loss, not a degradation. It now reads the inputs back from
   the batch manifest. Any path that verifies against evidence must be checked for whether the
   evidence is actually present there (see [[Batch Path Through the Synchronous Chain]]).
3. **Fixtures that go through `JSON.stringify` are untyped.** Adding the required field broke
   16 hand-built fixtures. `tsc` caught the object literals. Three parse tests failed only at
   runtime, because their fixtures were serialized strings the type checker never sees (see
   [[A Serialized Blob Is a Prompt Contract]]).

## Costs and limits

- **Storing a verbatim third-party excerpt is a different act from storing a paraphrase.**
  It needed an explicit decision on store/render posture and a retention entry before the
  first real (non-dry-run) write. The quote step was the only one held back for that
  decision. Capturing the text and wiring it into the prompt were independently revertible
  and could ship first.
- **Grounding starves subjective tags.** Atmosphere-style tags rarely have a quotable
  sentence behind them, so a quote requirement suppresses them. See
  [[Starved Tag Triage: Edge, Prompt, or Supply]].
- **It is the one non-additive change.** A required field on a widely fixtured type is
  the step to revert first, and to budget alone (planned at up to 40% of a session for
  fixture updates).

## Reuse

A sibling plan for a pre-model candidate stage in the main enrichment pipeline adopted the
same quote-and-verify mechanism instead of building a second one. It deferred persisting
quotes until the storage decision above was made, and it planned to import the verifier from
a shared location rather than copy it.

## See Also
- [[Evidence-Labelled Generation with Deterministic QC]] — extends (labels-and-cite grounding; this is the quote-level variant with a post-parse check)
- [[Quoted Span as Proof of Reading]] — alternative-to (the same verbatim-span check applied to review findings instead of model tags)
- [[Starved Tag Triage: Edge, Prompt, or Supply]] — related (the suppression cost of requiring a quote)
- [[Closed Judge Vocabulary, Tolerant Parse]] — related (shipped in the same probe version)
- [[Batch Path Through the Synchronous Chain]] — related (the batch route that silently lost its inputs)
