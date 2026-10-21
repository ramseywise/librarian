---
title: Tested Decision, Untested Expression
tags: [patterns, eval, pattern]
summary: A feature is three units — the decision, the code that shows it, and the wiring that connects them — and tests tend to cover only the decision; in one ML proof-of-concept the well-tested refusal guard was invisible in three of five report locations because string-anchor injections silently matched nothing.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/galactus/docs/plans/2026-08-11-gal-4-phase2-ml-fraud-poc.md
  - data/raw/repos/galactus/.claude--docs--plans--2026-08-11-gal-4-phase2-ml-fraud-poc.md
---

# Tested Decision, Untested Expression

The galactus fraud proof-of-concept had one job: on a frame too thin to support an
operating point, the run must refuse, and the report must make the refusal impossible to
miss. The refusal logic (`sufficiency.py`) was well tested, with six cases including
min-not-mean and the zero-positive edge. The first review pass called the code sound and
said only the tests were missing.

Writing those tests showed that conclusion was wrong.

## What the review found

Both important findings came from the same root cause. The tested unit was the
**decision**. The untested units were its **expression** (`report.py`, which injects the
refusal banner, the prevalence-floor note, and fairness notes into toolkit HTML) and its
**wiring** (`run.py`, which gates whether thresholds are reported at all).

`report.py` worked by string and regex replacement against anchors like
`<h2>Model comparison</h2>`. When an anchor does not match, `str.replace` and `re.sub`
return the document unchanged and raise nothing. Pinned against a real toolkit report:

| Injection | Against real markup |
|---|---|
| refusal banner | rendered |
| PR-AUC column floor | rendered |
| floor fact row | **silent no-op** |
| floor note paragraph | **silent no-op** |
| fairness notes section | **silent no-op** |

The step's done-condition (the floor contrast and the fairness note "on the page") had
been checked by grepping the write-up document, not the HTML. So the gap lasted the whole
phase, and it failed in exactly the direction the phase existed to prevent: an artifact
that looks complete while the caveat is quietly missing.

## Rules

1. **Injection must fail loudly.** Replace bare `replace`/`sub` with `_replace_once` /
   `_sub_once`, which raise (`ReportAnchorError`) when the anchor matches zero times.
   This is [[Silence Reads as Clean]] at the scale of a single string operation.
2. **Fixtures come from the real upstream output, not invented HTML.** The anchor tests
   were pinned against a report the toolkit had actually produced. *"A fixture that agrees
   with the implementation cannot catch an implementation that disagrees with reality"*.
   This is the same failure as [[A Fake That Conforms to a Broken Seam]], applied to
   markup.
3. **Test the wiring in both directions.** A refusal test checks that thresholds are
   nulled. The test that carries the weight is the opposite one: a *sufficient* verdict
   reports every threshold. Without it, `summarise()` could null thresholds every time and
   every refusal test would still pass.
4. **Keep a negative control on committed artifacts.** The "before" run (the toolkit with
   no guard) was saved and asserted on: it *did* report three threshold dicts, and they
   described zero true positives. Without that control, silence in the guarded run could
   just mean the toolkit never reports thresholds at all, and the guard could never be
   shown to fail ([[Eval Falsifiability]]).
5. **Check done-conditions against the artifact the reader sees.** If the claim is "it is
   on the page", grep the page, not the document that describes the page.

## Refusal by not asking

One thing in the same review held up well: the refusal was **structural**. When the
frame is insufficient, `run.py` holds back the cost inputs, so the classification run has
nothing to optimise a threshold against. No code path computes a threshold and then hides
it. Removing the question removes a whole class of suppression bugs that would otherwise
need their own tests.

## See Also
- [[Data Sufficiency Refusal]] — instance-of (the guard whose expression was broken)
- [[A Fake That Conforms to a Broken Seam]] — extends (fixture agreeing with the implementation)
- [[Eval Falsifiability]] — extends (negative control on the unguarded run)
- [[Silence Reads as Clean]] — instance-of (a non-matching anchor returns the input unchanged)
- [[Red-Then-Green Proof for Fix-Stage Tests]] — extends (both-direction wiring tests)
- [[Verify a Render by Text Extents, Not Pixels]] — extends (check the rendered artifact, not its description)
