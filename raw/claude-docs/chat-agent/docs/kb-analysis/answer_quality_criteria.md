# Answer Quality Criteria by Topic Area

For each topic: what a complete, correct answer looks like — and what a partial or wrong answer looks like. Derived from `intercom_kb_analysis.md`.

---

## 1. French e-invoicing reform (RFE)

**Complete/correct answer:**
- Dates are exact: all companies must **receive** e-invoices from **1 September 2026**; large companies (ETI/grandes entreprises) must also **emit** from that date; SMEs and micro-enterprises must **emit** from **1 September 2027**
- States that a plain PDF sent by email is **not compliant** — formats must be Factur-X, UBL, or CII
- States invoices must transit through a certified PA (Plateforme Agréée) or OD platform
- Distinguishes B2B scope (full e-invoicing) from B2C/cross-border (e-reporting only)
- Notes Shine offers free e-invoice reception; emission is still forthcoming; Shine is becoming a PA but was not yet on the official list at time of writing

**Partial/wrong answer:**
- Wrong year — e.g. "all companies must emit from 2026" (only ETI/grandes entreprises)
- Saying plain PDFs are still compliant
- Not mentioning the PA/OD requirement
- Saying Shine is already a registered PA
- Not distinguishing reception from emission, or B2B from B2C scope

---

## 2. Subscription plans and pricing

### Shine Pro

**Complete/correct answer:**
- Free: €0; Start: €11 HT/month (€108/year); Plus: €25 HT/month (€240/year); Business: €80 HT/month (€720/year)
- All prices are **HT (excluding VAT)**
- Correct included quotas: SEPA transfers, cards, sub-accounts, cash withdrawals, cheque deposits per plan
- Annual billing requires 12-month commitment; **not available at sign-up**; micro-enterprises are limited to 6-month commitment
- Annual billing is **non-refundable** if cancelled early

### Shine Facture

**Complete/correct answer:**
- Free: €0, max 5 clients; Start: €11/month (€108/year); Plus: €25/month (€240/year)
- Features gated by plan: multi-currency and automatic payment reminders = Plus only; quote-to-invoice conversion = Start and Plus only

**Partial/wrong answer:**
- Omitting "HT" — prices do not include VAT
- Wrong monthly prices or wrong plan feature attribution (e.g. saying Free supports multi-currency)
- Saying annual billing is available at sign-up
- Saying a committed customer gets a pro-rata refund on early cancellation
- Wrong SEPA transfer quotas or sub-account limits per plan

---

## 3. Invoice creation and compliance (French law)

**Complete/correct answer:**
- Mandatory mentions on all invoices: emission date, buyer/seller identity, invoice number, VAT number (if liable), HT and TTC totals, payment deadline, late-payment penalty rate, €40 flat-rate indemnity mention (B2B)
- SIRET/SIREN of client is **not required when invoicing individuals**
- Missing mention = €15 fine per mention per invoice, capped at 1/4 of invoice amount
- Non-compliance fine: up to €75,000 (natural person) or €375,000 (legal entity)
- Activity-specific mentions: RCS number (commercial), RM number (artisanal), TVA intracommunautaire (VAT-liable), "TVA non applicable, art. 293 B du CGI" (franchise), "Autoliquidation" (BTP sub-contracting)
- Invoice numbering must be **sequential without gaps** — French tax law requirement
- Sent invoices **cannot be deleted** (anti-VAT fraud law 2018); must be duplicated or countered with a credit note (avoir)
- "TEST" prefix does **not** mean a test invoice — it is a real, registered invoice

**Partial/wrong answer:**
- Omitting mandatory mentions or misattributing them (e.g. saying SIRET is required for individual clients)
- Saying non-sequential numbering is just a recommendation
- Telling users they can delete a sent invoice instead of duplicating or issuing an avoir
- Not flagging the financial exposure from non-compliance
- Saying "TEST" is a sandbox prefix

---

## 4. VAT

**Complete/correct answer:**
- Standard French rates: 20%, 10%, 5.5%, 2.1%; additional rates: 13%, 8.5% and 0.9% (purchase-only)
- **Custom VAT rates cannot be created** — only pre-defined rates from the list
- VAT must be changed manually to 0% for non-liable entities (default is 20%)
- Shine's VAT auto-detection from receipts works only when a receipt is attached; untagged transactions are excluded from VAT auto-calculation even when the feature is enabled
- Late payment penalties are calculated on TTC amount and are **not subject to VAT**

**Partial/wrong answer:**
- Saying custom rates can be created
- Implying VAT is always auto-filled without a receipt
- Saying the VAT auto-calculation covers all transactions when untagged ones are silently excluded
- Applying the wrong VAT rate on invoices (e.g. using 20% for a franchise entity)

---

## 5. Transfer operations (SEPA, instant, international)

**Complete/correct answer:**
- Standard SEPA: 2–3 business days; SEPA instant: within seconds, 24/7
- Instant transfer limits without "téléphone principal": **€2,000/transfer, €4,000/day**; with primary phone: **€10,000/transfer, €20,000/day**
- Instant not available for: future-dated transfers, recurring transfers, new beneficiary/device (temporary block), recipient bank doesn't support it, non-SEPA recipients
- Beneficiary Verification (VoP) is automatic from 9 October 2025 — name on IBAN must match
- SWIFT transfers go via Wise: sender needs **both** Shine BIC (`SNNNFR22XXX`) and Wise intermediary BIC (`TRWIBEB3`)
- SWIFT delay: 4–5 business days; rejected transfers returned to sender in up to 10 business days
- SWIFT reception fees: Free = €6 HT/transfer; all paid plans = €5 HT/transfer
- Shine accounts receive **euros only** — all FX conversion happens before crediting
- Batch transfers: **Business plan only**; CSV and XML formats; strict character restrictions in CSV

**Partial/wrong answer:**
- Wrong instant transfer limits
- Not mentioning the new beneficiary/device temporary block
- Omitting VoP or saying names don't need to match
- Giving only the Shine BIC for international transfers (Wise intermediary BIC is required)
- Saying SWIFT takes 1–2 days
- Saying Shine accounts can hold foreign currency balances

---

## 6. Cards and contactless payments

**Complete/correct answer:**
- Physical cards: **1 per person maximum** regardless of plan; Free/Start = Mastercard Basic; Plus/Business = Mastercard Premium
- Virtual cards: Free = €2 HT/month/card; Start/Plus/Business = unlimited, no charge; spending limit = **€5,000 / 7 rolling days**; deletion is **permanent and irreversible**
- Replacement card cost: **€5 HT** (Free/Start); **€10 HT** (Plus/Business); block as lost/stolen is **irreversible**
- Contactless ceiling: **€50 (industry standard, non-modifiable)**; PIN trigger: cumulative spend of **€150** OR **5 consecutive contactless payments**, whichever comes first
- Apple/Google Pay max: **€3,000/transaction**; "online payments" option must be active when adding to Apple Pay
- Card payment ceilings vary by plan (Free: €20,000/30 days up to Business: €60,000/30 days)
- ATM daily limit: **€400 (all plans)**; 30-day rolling: Free €500, Start €1,500, Plus/Business €2,500
- Foreign payments outside euro zone fee varies by plan: Free 2%, Start 1.75%, Plus 1.5%, Business 1%
- PIN block after **3 wrong attempts**; CVV block after **5 wrong attempts**; both require support to unblock

**Partial/wrong answer:**
- Saying multiple physical cards can be ordered per person
- Saying the contactless ceiling can be changed
- Wrong replacement card fees by plan
- Saying a blocked (lost/stolen) card can be reactivated
- Wrong ATM 30-day limits (especially Free plan's €500 cap)
- Wrong foreign payment fee percentages per plan

---

## 7. Direct debits and SEPA mandates

**Complete/correct answer:**
- **CORE (B2C) debits**: can be contested up to **8 weeks** after execution; contact creditor first, then contest in-app
- **B2B debits: cannot be contested or refunded after execution** — only future debits can be blocked by suspending the mandate
- B2B mandate references must be **character-perfect** — any error causes the creditor's debit to fail
- To contest a mandate: email `promis_on_repond@shine.fr` (free service)

**Partial/wrong answer:**
- Telling a B2B customer they can get a refund on an already-executed debit
- Not mentioning the 8-week hard deadline for CORE
- Treating CORE and B2B debits identically

---

## 8. Sub-accounts

**Complete/correct answer:**
- Each sub-account has its own unique **French IBAN**
- Plan limits: Free = 0; Start = 1; Plus = 4; Business = 9
- **Cannot** attach a card or set up recurring transfers to a sub-account
- Closure requires zero balance
- A seizure (saisie/ATD) **can** be applied to a sub-account

**Partial/wrong answer:**
- Wrong sub-account limits per plan
- Saying cards or recurring transfers can be attached to sub-accounts
- Saying seizures cannot reach sub-accounts

---

## 9. Team access and roles

**Complete/correct answer:**
- Three invite roles: **Admin** (all rights except closing account or inviting other admins); **Employé** (request cards/transfers — both need holder/admin approval; own transactions only; no invoicing access); **Comptable** (read-only: transactions, receipts, statements, accounting exports; cannot make payments, invite members, or use invoicing)
- Additional access costs: **€5 HT/month/access** on Start and Plus; Business = unlimited, no charge; **Free = no team access at all**
- Pro-rata billing applies: access added mid-period is billed from day of activation
- Employees cannot see company-wide transactions — only their own

**Partial/wrong answer:**
- Saying Free plan can invite team members
- Wrong per-access pricing or omitting pro-rata billing
- Saying Comptable can initiate payments
- Saying Admin can close the account or invite other admins

---

## 10. Tax declaration for micro-enterprises

**Complete/correct answer:**
- Declare **gross revenue (CA encaissé) without applying the abattement** — the tax authority applies it automatically
- Abattements: 71% (merchandise), 50% (commercial services), 34% (liberal services)
- With versement libératoire: boxes 5TA (merchandise), 5TB (commercial services), 5TE (liberal services)
- Without versement libératoire — commercial: boxes 5KO/5KP + 5DB for months of activity; liberal: box 5HQ + 5XI
- Case 5HY at validation step: **not applicable to micro-enterprises — skip it**
- Mandatory online declaration since 2019

**Partial/wrong answer:**
- Telling the user to apply the abattement before declaring
- Wrong abattement percentages per activity type
- Wrong tax boxes
- Not flagging that case 5HY should be skipped

---

## 11. Late payment penalties

**Complete/correct answer:**
- Legal minimum rate: **3× the Banque de France legal rate** (H2 2025 minimum = 8.28%)
- Commonly applied rate: BCE director rate + 10 points (12.15%); Shine default = 13.15% (editable)
- Formula: `(TTC amount × rate) × (days late / 365)`
- Calculated on **TTC amount**, **not subject to VAT**
- The rate mention is **legally required** on every invoice; actually collecting penalties is **optional**
- If collected: issue a new €0 VAT invoice with immediate payment terms

**Partial/wrong answer:**
- Any rate below 8.28% (violates the legal minimum)
- Applying the rate to HT rather than TTC
- Adding VAT to the penalty amount
- Saying both the mention and the collection are optional (only collection is optional; the mention is mandatory)

---

## 12. Account security and sensitive operations

**Complete/correct answer:**
- Lost phone: **immediately contact Shine support** — there is no self-service account lock; support is available 7/7
- Primary phone (téléphone principal): only **one** per user; changing it requires identity verification and deactivates the old device; **it cannot be directly blocked — only replaced**
- Sensitive operations requiring strong auth: adding SEPA beneficiary, new device login, batch transfer creation, virtual card creation, PIN reveal, PAN/CVC display, Apple/Google Pay addition, instant limit changes, 3DS validation
- 3DS notification for unknown payment: **refuse it and block your card immediately**
- PIN reset: only possible from a **previously authenticated device** — impossible from a brand-new device

**Partial/wrong answer:**
- Saying there is a self-service account lock for a lost phone scenario
- Saying a primary phone can be blocked without replacement
- Saying PIN reset can be done from any device
- Telling a user to approve an unknown 3DS notification

---

## 13. Shine's legal status and overdraft

**Complete/correct answer:**
- Shine is a **payment institution (établissement de paiement)**, not a bank — licensed by ACPR (registration 71758)
- **No overdraft** on any plan; insufficient funds = payment simply refused, no penalty fee
- **No credit directly** — financing via partners Defacto and ADIE only
- American Express cards **cannot be linked** (deferred debit requires overdraft capability)
- Shine is **professional use only** — personal accounts cannot be opened; a SIRET is required

**Partial/wrong answer:**
- Saying Shine is a full bank
- Saying overdraft is possible on any plan
- Saying refused payments incur a fee
- Saying personal accounts can be opened

---

## 14. Account opening, KYC, and refunds

**Complete/correct answer:**
- No documents required to open a Shine Facture account; no bank card required; 30-day free trial
- Shine Pro KYC: company documents must be **less than 3 months old**; accepted IDs: valid European CNI/passport/titre de séjour (specific categories excluded: "salarié", "étudiant", "travailleur temporaire", "visiteur")
- Expired CNI valid only if old rectangular format issued after the holder's 18th birthday
- Beneficial owner: anyone with **≥25% capital or voting rights** — all must provide ID
- Refund after withdrawal: only if **all 3 conditions** are simultaneously met (capital not deposited, documents not submitted to authorities, account not yet open); 15-calendar-day window; **written request** required; refund processed within 14 business days

**Partial/wrong answer:**
- Saying the expired CNI is always valid
- Accepting titre de séjour categories that are explicitly excluded
- Saying a refund is possible once the account is open or capital has been deposited
- Not requiring written form for the withdrawal request

---

## 15. Cheques and cash deposits

**Complete/correct answer:**
- Cheque deposit delay: **15 business days** total (mandatory 11-day immobilisation window included)
- Cheque validity: **1 year and 8 days** from issue date
- Physical submission deadline: **15 days from declaring in-app** — missed deadline = encashment cancelled
- Cheque fees per plan: Free = €2 HT (0 free); Start = €2 HT (2 free/month); Plus = €2 HT (6 free/month); Business = €2 HT (15 free/month); rejected cheque = **€25 HT**; returned (incomplete info) = **€5 HT**
- Shine does **not** issue chequebooks
- Cash deposits: via Brink's tobacconist network, **France métropolitaine only** (no DROM-COM); minimum **€100**; credited in under a minute; fees: Free 4%, Start 3%, Plus 2.5%, Business 2% (billed at end of billing period)

**Partial/wrong answer:**
- Saying cheque funds are available faster than 15 business days
- Not mentioning the 15-day physical submission deadline or the 1-year-8-day validity limit
- Wrong cheque fees per plan
- Saying cash deposits work in overseas territories
- Omitting the €25 fee for a rejected cheque
