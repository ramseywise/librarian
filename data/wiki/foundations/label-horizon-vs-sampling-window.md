---
title: Label Horizon vs Sampling Window
tags: [foundations, concept]
summary: "A supervised frame's label horizon (the window over which the label's outcome was observed and finalised) is distinct from its label definition and from its sampling window; a public fraud set's two-day `Time` column is routinely misread as a horizon when the labeling window is unstated and unrecoverable — under an 'inferred horizon = unavailable' standard, such a frame fails, and applying that standard to one run but not its sibling is itself the finding."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/galactus/docs/plans/2026-08-18-ml-frame-sourcing.md
  - data/raw/repos/galactus/.claude--docs--plans--2026-08-18-ml-frame-sourcing.md
  - data/raw/claude-docs/galactus/docs/plans/2026-08-18-ml-parity-consolidated.md
  - data/raw/repos/galactus/.claude--docs--plans--2026-08-18-ml-parity-consolidated.md
---

# Label Horizon vs Sampling Window

From the research pass that verified two public frames for an ML prototyping repo
(galactus). See [[ML Frame Sourcing — License, Horizon, Prevalence]] for the decision.

## Three things that get conflated

| Term | Question it answers | Example |
|---|---|---|
| **Label definition** | What does `1` mean? | "1 in case of fraud and 0 otherwise" |
| **Label horizon** | Over what window was the outcome observed and finalised? | "default payment *next month*" = October 2005 for features covering Apr–Sep 2005 |
| **Sampling window** | Over what period were the rows drawn? | `Time` = seconds since the first transaction, about 2 days |

The horizon is what makes a threshold and a cost ratio meaningful. "Predict default next
month" and "predict default ever" are different problems that can share one column name.
Without a horizon, a fraud label carries unknowns: the chargeback lag, when labels were
frozen, and whether late chargebacks were backfilled or left as `0`. Any of these turns
some negatives into unobserved positives.

## The misreading

The fraud set's two-day `Time` span fixes the *sampling* window. The *labeling* window is
independent and unstated. The source closes off recovery ("due to confidentiality issues,
we cannot provide … more background information"), so no amount of further searching
fills the gap. It was left out on purpose. Papers on the dataset discuss chargeback delay
in card fraud generally. None of them binds a horizon to this extract.

## Cite where the horizon actually lives

Even the passing frame's horizon was narrower than the design assumed. "Next month" appears
in the dataset's curated **variables table**, three times across page, API and embedded
metadata. The prose description states no horizon. Cite the variables table, not the
abstract. Record the concrete meaning (October 2005), not just the phrase.

## The horizon decides the leakage list

Under a stated one-month horizon, the latest-month columns (bill amount, payment amount,
repayment status for September) are *inputs* to an October label, not post-outcome
records. If the horizon were restated, those columns would be the first leakage
candidates. That is why the leakage list is written as an argument from the horizon. See
[[Argued Empty List]].

## Applying the standard asymmetrically

The design made "source-stated horizon" a hard constraint ("inferred horizon =
unavailable"). It used that constraint as the decisive argument *for* the credit frame,
then picked a fraud frame that fails it. The research named the asymmetry as the finding.
It went to an operator decision rather than more research, with two options:

- **Narrow the claim.** Adopt the frame, record the horizon as *unknown*, and drop the
  target from "3/3 frames with a stated horizon" to 2/3, permanently.
- **Hold the standard.** Source a frame that publishes its labeling protocol, or go
  synthetic, which is the standard's own unexercised fallback.

Downstream, the change broke a plan premise. A plan titled around "a record for a refusal"
had hard-coded the stand-in frame's refusal values. On the proposed frame the sufficiency
guard passes, so there is no refusal to record. That plan was superseded.

## See Also
- [[ML Frame Sourcing — License, Horizon, Prevalence]] — extends (the sourcing decision this refines)
- [[Profile Then Select]] — extends (Q3 target definition and horizon)
- [[Argued Empty List]] — prerequisite-for (the leakage list is argued from the horizon)
- [[Data Sufficiency Refusal]] — extends
