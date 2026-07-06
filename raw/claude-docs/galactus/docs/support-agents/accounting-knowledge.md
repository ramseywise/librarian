# Accounting Knowledge — Domain Research

Research reference for building an accounting agent with Danish/SKAT coverage.
Not implementation — maps the domain so we know what rules exist, where they live, and what the knowledge graph would look like.

---

## What an accounting agent needs to reason over

Three layers of knowledge, each with different structure:

| Layer | Examples | Source type |
|---|---|---|
| **Procedural** | "How do I create a credit note?" "What goes on a VAT invoice?" | Help articles (BillyPedia, Intercom KB) |
| **Regulatory rules** | Danish VAT rate, deductibility %, reporting deadlines | SKAT legislation + guidance |
| **Entity relationships** | Which VAT code applies to this expense type, which account it posts to | Knowledge graph / structured data |

Current agents (hc_adk, hc_lg, hc_rag) handle layer 1 well — flat article retrieval.
Layers 2 and 3 are where a knowledge graph earns its keep.

---

## Danish accounting domain (SKAT)

### VAT (Moms)

| Rule | Detail |
|---|---|
| Standard rate | **25%** — one of the highest in EU, no reduced rate |
| Zero-rated (0%) | Exports, intra-EU B2B supplies, specific financial services |
| Exempt (momsfri) | Healthcare, education, financial services, insurance, real estate transfer, passenger transport |
| Exempt with input VAT right | None in Denmark — exempt means no deduction |
| Acquisition VAT | Required on intra-EU goods purchases (reverse charge) |
| Reverse charge (domestic) | Construction services (byggeri) — specific anti-fraud rule |

**VAT periods (momsperioder) by turnover:**

| Annual turnover | Filing frequency | Deadline |
|---|---|---|
| > DKK 50M | Monthly | 25th of following month |
| DKK 5M–50M | Quarterly | 1 month + 10 days after quarter end |
| < DKK 5M | Semi-annual | 1 Aug (H1) / 1 Feb (H2) |

**VAT return (momsangivelse):** Filed on skat.dk via TastSelv Erhverv. Fields: `Salgsmoms` (output VAT), `Købsmoms` (input VAT), `Erhvervelsesmoms` (acquisition VAT).

**Invoice requirements (fakturakrav):** Required for VAT-registered businesses:
- Sequential invoice number
- Issue date
- Seller CVR number and name/address
- Buyer name/address (for B2B > DKK 3,000 incl. VAT)
- Description of goods/services
- Quantity and unit price ex VAT
- VAT rate and amount
- Total incl. VAT

Simplified invoices (forenklet faktura) allowed up to DKK 3,000 — no buyer details required.

---

### Corporate tax (Selskabsskat)

| Item | Rate / Rule |
|---|---|
| Corporate tax rate | **22%** (ApS, A/S) |
| Sole trader (enkeltmandsvirksomhed) | Personal income tax rate (~42–52% all-in) |
| Tax year | Calendar year (Jan–Dec) |
| Preliminary tax (acontoskat) | Paid in March and November |
| Tax return deadline | 6 months after year-end (i.e. 30 June for calendar year) |
| Loss carryforward | Unlimited in time; limited to 60% of taxable income > DKK 9.4M |

---

### Payroll & employment (Løn)

| Contribution | Rate | Who pays |
|---|---|---|
| AM-bidrag (labor market contribution) | 8% of gross | Employee (withheld) |
| A-skat (income tax withholding) | Progressive, ~35–52% | Employee (withheld) |
| ATP (statutory pension) | DKK 284/quarter (full-time) | Split employer/employee |
| Employer pension | Negotiated (typically 8–12% total) | Employer |
| Holiday pay (feriepenge) | 12.5% of salary | Employer (via Feriekonto or payslip) |

Payroll must be reported monthly via **eIndkomst** on skat.dk.

---

### Expense deductibility (Fradrag)

Common categories and their deductibility:

| Expense type | Deductibility | Rule |
|---|---|---|
| Business operating costs | 100% | Statsskattelovens §6a |
| Representation (dining, gifts to clients) | **25%** | Ligningslovens §8 stk. 4 |
| Employee meals (kantineordning) | 100% with conditions | LL §16 |
| Travel — mileage (kørsel) | DKK 2.23/km (2024) | Statens takster |
| Travel — subsistence (rejsegodtgørelse) | DKK 555/day domestic (2024) | Ligningslovens §9A |
| Home office | Partial — complex rules | LL §9B |
| Phone + internet | 100% if primarily business | Standard |
| Car (firmabil) | Taxable benefit if private use | LL §16 stk. 4 |
| Depreciation — equipment | Up to 25%/year (saldoafskrivning) | Afskrivningslovens §5 |
| Depreciation — buildings | 4%/year | Afskrivningslovens §14 |

**Input VAT deductibility on expenses:** Only deductible if the expense relates to VAT-taxable activity. Representation input VAT: **0% deductible** even though the expense itself is 25% deductible for income tax.

---

### Bookkeeping Act (Bogføringsloven)

Mandatory for all businesses with annual revenue > DKK 300,000. Key obligations:

- Record every transaction with a **bilag** (voucher/receipt) within reasonable time
- Vouchers must be numbered sequentially and retained **5 years**
- Chart of accounts must map to the Danish standard (standard kontoplan)
- Digital bookkeeping system required from 2024 for large businesses, 2026 for SMEs (lov nr. 700/2021)
- Backup requirement: system must maintain backup independent of the company

---

## Entity/relationship model (knowledge graph sketch)

This is the ontology that would power multi-hop accounting queries.

```
[Business entity type]
  enkeltmandsvirksomhed ─── subject_to ──→ [Tax regime: personal income]
  ApS / A/S             ─── subject_to ──→ [Tax regime: selskabsskat 22%]
        │
        └── has_obligation ──→ [Reporting obligation]
                                    momsangivelse (quarterly)
                                    eIndkomst (monthly)
                                    selvangivelse (annual)

[Expense]
  ├── category ──────────────→ [Expense type]
  │                                representation
  │                                travel
  │                                operating cost
  │
  ├── deductibility_rule ────→ [Tax rule]
  │                                25% (representation)
  │                                100% (operating)
  │                                DKK 2.23/km (mileage)
  │
  ├── vat_treatment ─────────→ [VAT code]
  │                                25% input (fully deductible)
  │                                25% input, 0% deductible (representation)
  │                                0% (exempt purchase)
  │
  └── posts_to ──────────────→ [Account (kontoplan)]
                                    3xxx Revenue
                                    4xxx Cost of goods
                                    5xxx Staff costs
                                    6xxx Other operating costs
                                    7xxx Depreciation
                                    8xxx Financial items

[VAT code]
  └── reported_on ───────────→ [Momsangivelse field]
                                    Salgsmoms (output)
                                    Købsmoms (input)
                                    Erhvervelsesmoms (acquisition)
```

### Multi-hop query examples this graph enables

| Question | Hops required |
|---|---|
| "Can I deduct a client dinner and reclaim the VAT?" | Expense → deductibility_rule + vat_treatment → Tax rule |
| "What account does my phone bill post to and is the VAT deductible?" | Expense → posts_to → Account + vat_treatment → VAT code |
| "When do I file my VAT return given my turnover?" | Business → turnover_band → VAT period → deadline |
| "Do I need to charge VAT on services sold to a German company?" | Supply type → place_of_supply_rule → VAT treatment |

None of these are answerable from a single help article — they require traversing relationships.

---

## Where the rules live (authoritative sources)

| Source | What it covers | URL |
|---|---|---|
| skat.dk — Juridisk vejledning | Full legal guidance — the authoritative SKAT rulebook | skat.dk/data/juridisk-vejledning |
| skat.dk — Momsvejledning | VAT guide for businesses | skat.dk/moms |
| Retsinformation.dk | Primary legislation (Statsskatteloven, Ligningsloven, Afskrivningsloven, Bogføringsloven, Momsloven) | retsinformation.dk |
| Erhvervsstyrelsen | Company registration, annual accounts filing | erhvervsstyrelsen.dk |
| Dansk Revisorråd / FSR | Professional accounting standards | fsr.dk |
| EU VAT Directive | EU-level VAT rules Denmark must comply with | eur-lex.europa.eu |

**SKAT Juridisk Vejledning** is the most important single source — it's SKAT's own binding interpretation of tax law, updated quarterly, and structured by topic (momsregistrering, fradrag, etc.). If we ever ingest external sources, this is the one.

---

## Applicability to our stack

### Accounting agent use case
A KG of the entity/relationship model above would let an accounting agent answer multi-hop questions that are impossible with flat article retrieval. The graph is small (hundreds of nodes, not millions) — Neo4j Community Edition or even a JSON-serialized graph would be sufficient at this scale.

**Recommended approach:** hybrid — Cypher for structured rule lookups (VAT code, deductibility %, deadlines) + vector search (Bedrock or pgvector) for freetext help article retrieval. LangChain's `Neo4jGraph` + `GraphCypherQAChain` is the standard wiring.

### BillyPedia sources
BillyPedia is mostly procedural (layer 1 above). A KG adds less value here than better chunking + CRAG. Exception: if BillyPedia cross-references accounting concepts (e.g. "representation expenses" linked to SKAT rules), extracting those entity links improves cross-article reasoning.

### Semantic cache
No benefit from a KG. The golden dataset seed approach is already the right lever — the cache works on query similarity, not entity traversal.

---

## Open questions before building

1. **Do the Billy/Clara products have a defined chart of accounts (kontoplan)?** If yes, that's the backbone of the graph — map it first.
2. **Which entity type do most Billy customers use?** enkeltmandsvirksomhed vs ApS changes which tax rules are in scope.
3. **Is Clara (German) in scope?** German tax rules (Umsatzsteuer 19%, Gewerbesteuer, HGB) are a separate graph — different enough that mixing them requires explicit locale-scoping on every node.
4. **Do we have any existing structured rule data** (e.g. a VAT code table, a kontoplan CSV) in the Billy product DB or config files?
