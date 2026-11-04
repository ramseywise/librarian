---
title: Basel IRB Capital Vocabulary
tags: [foundations, reference]
summary: The terms linking a default-probability model to bank capital (PD, LGD, EAD, expected vs unexpected loss, RWA) and the one-factor logic that makes capital grow far more slowly than expected loss as PD rises.
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--06-applied-analyses--notes--02-credit-scoring.md
---

# Basel IRB Capital Vocabulary

Under the internal ratings-based approach, a PD model also feeds the capital requirement.

| Term | Meaning |
|---|---|
| PD | probability of default over one year |
| LGD | loss given default, share of exposure lost |
| EAD | exposure at default |
| Expected loss | PD x LGD x EAD, covered by pricing and provisions |
| Unexpected loss | loss in a bad year above expected, covered by capital |
| K | capital requirement per unit of exposure |
| RWA | K x 12.5 x EAD (12.5 = reciprocal of 8%) |
| F-IRB / A-IRB | bank supplies PD only (regulator sets LGD) / bank also supplies LGD and EAD |

## Mechanism

A one-factor model exposes all borrowers to one systematic factor with correlation R. The formula takes the default rate in a very bad state of that factor (99.9th percentile, about a one-in-a-thousand-year event); capital covers that conditional loss minus expected loss. Retail has no maturity adjustment; for other retail, R declines as PD rises (from 0.16 down to 0.03). The framework adds floors such as a 0.05% PD floor for most retail and a 30% LGD floor for unsecured other retail.

## Numbers (assumed 5,000 unsecured loan, 60% LGD; assumptions, not dataset values)

PD 0.5%: EL 15, K 3.45%. PD 1%: EL 30, K 4.88%. PD 3%: EL 90, K 6.70%. PD 10%: EL 300, K 8.06%. From PD 0.5% to 10%, expected loss rises 20x and capital only 2.3x, because more risk moves into the expected part and R falls. Price has to carry expected loss; capital covers the rest.

A product scorecard is not a capital model: its PDs rest on one prior correction on a small old sample, and a regulator wants long default histories.

## See Also
- [[Weight-of-Evidence Logistic Scorecard]] — related
- [[Prior Shift Correction for Oversampled Defaults]] — related
