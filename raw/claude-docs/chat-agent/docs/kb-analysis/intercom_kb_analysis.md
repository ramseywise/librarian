# Intercom Knowledge Base — Structured Article Analysis

For each article: (1) main topic, (2) key factual claims a chatbot must get exactly right, (3) conditions/exceptions/edge cases, (4) financial consequence flag where a wrong answer would have a direct financial impact on the user.

---

## Article 14134276 — Import contacts (CSV)
- **Topic:** Importing a client list into client-a Facture
- **Key facts:** Import is done via CSV; template file available for download
- **Conditions/exceptions:** None stated
- **Financial risk:** None

---

## Article 13545273 — Connect client-a Pro account to client-a Facture
- **Topic:** Linking client-a banking account to client-a Facture
- **Key facts:** Done from the "Rapprochement" tab; shows all transaction history (not limited to 6 months); real-time sync; connection does not need to be reset periodically
- **Conditions/exceptions:** Must have a client-a Pro account first
- **Financial risk:** Low — a chatbot saying the connection is limited to 6 months of history would be incorrect

---

## Article 13390584 — Billing preferences and layout customisation
- **Topic:** Setting default invoice layout and billing preferences
- **Key facts:** Feature available only on **Start** and **Plus** plans; settings apply to future invoices only (not retroactive); configurable elements include: currency, language, payment terms, default VAT rate, custom notes, contact person, accepted payment methods, logo, font, font colour
- **Conditions/exceptions:** Changes are not retroactive to existing invoices
- **Financial risk:** Low — incorrectly telling a Free-plan user this feature is available could mislead

---

## Article 13390711 — Understanding the e-invoicing reform (RFE)
- **Topic:** French mandatory electronic invoicing reform
- **Key facts:**
  - All French VAT-liable companies are affected (micro to large enterprise)
  - Accepted formats: Factur-X, UBL, CII — a plain PDF sent by email is no longer compliant
  - **1 September 2026:** all companies must be able to *receive* e-invoices; large companies (ETI and grandes entreprises) must also *emit*
  - **1 September 2027:** SMEs and micro-enterprises must also *emit*
  - Invoices must transit through an approved platform (Plateforme Agréée / PA)
  - E-reporting required for B2C and international (cross-border) sales
- **Conditions/exceptions:** E-invoicing mandatory only for B2B between French VAT-registered companies; B2C and cross-border use e-reporting instead
- **⚠️ HIGH financial risk:** Incorrect dates or scope could cause non-compliance, exposing users to fiscal penalties

---

## Article 13401376 — Download client-a Facture mobile app
- **Topic:** How to download client-a Facture on iOS and Android
- **Key facts:** Available on App Store (iPhone) and Google Play Store (Android)
- **Conditions/exceptions:** None
- **Financial risk:** None

---

## Article 13419479 — Contact customer support
- **Topic:** Available support channels
- **Key facts:**
  - Email: `support@client-a.co`, answered Mon–Fri, generally same day
  - Phone support: only available on **Start** and **Plus** plans
  - Chat: available in-app via "centre d'aide"
  - **Free plan has no phone support**
  - Support is fully in-house
- **Conditions/exceptions:** Free plan excluded from phone support
- **Financial risk:** Low — incorrectly telling a Free user they can call support wastes time

---

## Article 13377865 — Connect bank account to client-a Facture
- **Topic:** Bank reconciliation setup via AIIA (open banking provider)
- **Key facts:** Connection done via AIIA; accounts mapped to the accounting plan (default account 100201001); if bank already connected via AIIA, just confirm access
- **Conditions/exceptions:** None
- **Financial risk:** Low

---

## Article 13378352 — Save a purchase invoice as draft
- **Topic:** Creating a draft purchase invoice
- **Key facts:** Path: Dépenses > Factures d'achats > Ajouter une dépense; saved drafts accessible in the "Factures d'achat" tab
- **Conditions/exceptions:** None
- **Financial risk:** None

---

## Article 13378164 — Add and validate a purchase invoice
- **Topic:** Importing and validating purchase receipts/invoices
- **Key facts:** Three import methods: manual upload, Copilot (dedicated supplier email address), or e-invoice reception (RFE); validation requires checking auto-filled fields and associating a payment
- **Conditions/exceptions:** None
- **Financial risk:** None

---

## Article 13401672 — Activate e-invoice reception
- **Topic:** Activating the ability to receive electronic invoices (RFE)
- **Key facts:** Reception of e-invoices is **free and unlimited** for all client-a Facture users; requires identity document submission and client-a team validation before activation
- **Conditions/exceptions:** Requires document validation before use
- **Financial risk:** Low — incorrectly telling users it costs money would be wrong

---

## Article 13544322 — Payment reminders for unpaid invoices
- **Topic:** Sending payment reminder emails to clients
- **Key facts:** Manual reminder via: Factures de ventes > open invoice > Plus > Envoyer un rappel; email subject and message are customisable; **automatic reminders are a forthcoming feature — not yet available**
- **Conditions/exceptions:** Automatic reminders do not yet exist
- **⚠️ Moderate financial risk:** Telling a user automatic reminders exist when they don't could cause them to miss collecting payment

---

## Article 13377816 — Modify VAT rate
- **Topic:** Configuring VAT rates in client-a Facture
- **Key facts:**
  - Standard French VAT rates: 20% (normal), 10% (intermediate), 5.5% (reduced), 2.1% (super-reduced)
  - Additional rates available: 13%, 8.5% (purchases only), 0.9% (purchases only)
  - **Custom VAT rates cannot be created** — only pre-defined rates can be added; fields are greyed out
  - Desktop only
- **Conditions/exceptions:** No custom rate creation; select from pre-defined list only
- **⚠️ HIGH financial risk:** Incorrect VAT rate on invoices leads to wrong tax amounts charged and declared

---

## Article 13390607 — Sales invoice statuses
- **Topic:** Invoice status labels
- **Key facts:** Statuses: Toutes, En retard (past due), Dues (within deadline), Payées (payment recorded); colour-coded dots; filtered by selected fiscal year
- **Conditions/exceptions:** None
- **Financial risk:** Low

---

## Article 13390574 — International invoicing
- **Topic:** Invoicing in foreign languages and currencies
- **Key facts:**
  - Language can be changed per invoice or as default (not retroactive)
  - **Multi-currency invoicing requires the Plus plan**
  - Only one currency per invoice
  - **client-a Facture does not automatically convert exchange rates**
- **Conditions/exceptions:** Multi-currency is Plus-only; no automatic FX conversion
- **⚠️ HIGH financial risk:** If a user is told FX conversion is automatic, they may quote wrong amounts to clients; Plus-plan requirement must be stated accurately

---

## Article 13390543 — Structure sales invoices
- **Topic:** Adding lines, sub-totals, descriptions, and reordering invoice items
- **Key facts:** Can add text descriptions, sub-totals (cumulates lines above the sub-total), drag-and-drop reorder; can toggle visibility of HT/TTC/unit columns; sub-total scope resets at each preceding sub-total
- **Conditions/exceptions:** Sub-total scope resets at the previous sub-total marker
- **Financial risk:** Low — but misconfigured sub-totals could show incorrect partial amounts

---

## Article 13378833 — Modify invoice numbering
- **Topic:** Customising invoice number prefix and sequence
- **Key facts:** Prefix editable via pencil icon; applies only to future invoices; existing invoices unchanged; invoice numbers must be **unique and sequential**; **numbers on sent or posted invoices cannot be changed**; **"TEST" prefix does not mean a test invoice — it is a real, registered invoice**; year-reset allowed if sequence stays logical
- **Conditions/exceptions:** Sent invoices: number cannot be changed; "TEST" is not a sandbox prefix
- **⚠️ HIGH financial risk:** Non-sequential numbering is a tax compliance violation in France; "TEST" confusion could lead to treating real invoices as test records

---

## Article 13390602 — Add items to product/service catalogue (client-a Facture)
- **Topic:** Managing the product/service catalogue
- **Key facts:** Items have: name, unit, type (product/service), price HT/TTC, VAT rate; **catalogue modifications do not apply retroactively to existing invoices**; items can be created on the fly during invoice creation
- **Conditions/exceptions:** Non-retroactive changes only
- **Financial risk:** Moderate — chatbot must not imply modifying an item updates past invoices

---

## Article 13378328 — Add logo to invoices
- **Topic:** Adding or removing a company logo
- **Key facts:** Max file size: 5 MB; recommended format: square PNG; logo size on the invoice is not adjustable; advised not to embed the company name in the logo image
- **Conditions/exceptions:** None
- **Financial risk:** None

---

## Article 13378408 — Finalise a sales invoice
- **Topic:** Options when completing an invoice
- **Key facts:** Options: save as draft, send by email (editable subject/message, option to receive a copy), download as PDF, validate and close
- **Conditions/exceptions:** None
- **Financial risk:** None

---

## Article 13448575 — Convert a quote to an invoice
- **Topic:** Quote-to-invoice conversion
- **Key facts:** Requires **Start or Plus** plan; two-click conversion from the Devis tab; **Free plan cannot convert quotes to invoices**
- **Conditions/exceptions:** Free plan exclusion
- **Financial risk:** Moderate — Free plan users told they can do this would be misled

---

## Article 13378302 — Create and send a sales invoice
- **Topic:** Step-by-step invoice creation
- **Key facts:** Create from Facturation > Factures clients > Créer une facture; required fields: client, date, items (nature, unit, price, VAT); optional: message, client reference, payment terms; can save as draft, email directly, or download PDF
- **Conditions/exceptions:** None
- **Financial risk:** Low

---

## Article 13401438 — Documents needed to create a client-a Facture account
- **Topic:** Account opening requirements
- **Key facts:** **No documents required** to open an account; **no bank card required**; 30-day free trial before choosing a plan
- **Conditions/exceptions:** None
- **Financial risk:** Low

---

## Article 13401421 — Change account language
- **Topic:** Changing the client-a Facture interface language
- **Key facts:** Desktop only; change is applied immediately
- **Conditions/exceptions:** Cannot be done on mobile
- **Financial risk:** None

---

## Article 13401406 — Access client-a Facture on the web
- **Topic:** Login methods and device compatibility
- **Key facts:** Desktop access at `login.client-a.co/login/fr`; **mobile browser access is NOT available** — it redirects to client-a Banking instead; mobile access requires the dedicated client-a Facture app (App Store / Google Play)
- **Conditions/exceptions:** Mobile browser not supported
- **Financial risk:** None — but confusion could prevent a user from accessing their account

---

## Article 13419468 — Difference between client-a and client-a Facture
- **Topic:** Product differentiation
- **Key facts:** client-a = professional bank account; client-a Facture = invoicing tool; separate products but can be linked; connecting both enables reconciliation and payment tracking; each can be used independently
- **Conditions/exceptions:** None
- **Financial risk:** None

---

## Article 13419459 — Available subscription plans
- **Topic:** client-a Facture pricing tiers
- **Key facts:**
  - **Free:** €0/month — max **5 clients**; no quote-to-invoice conversion; no phone support
  - **Start:** €11/month or **€108/year (€9/month)** — up to 3 banks; phone support; quote conversion
  - **Plus:** €25/month or **€240/year (€20/month)** — unlimited clients; sales reports; automatic payment reminders; up to 5 banks; multi-currency; priority phone support
- **Conditions/exceptions:** Free: no quote conversion, limited to 5 clients; Plus required for multi-currency and auto-reminders
- **⚠️ HIGH financial risk:** Wrong prices or wrong plan feature attribution directly affects purchasing decisions

---

## Article 13419449 — Who is client-a?
- **Topic:** Company background
- **Key facts:** French company founded 2017 by Nicolas Reboud and Raphaël Simon; licensed payment institution (établissement de paiement) approved by ACPR (Banque de France), registration number 71758; e-invoice reception is free for all users
- **Conditions/exceptions:** None
- **Financial risk:** None

---

## Article 8954102 — Expense reimbursement request (employer view)
- **Topic:** Employee expense reimbursement flow from the employer's perspective
- **Key facts:** Feature available on **client-a Pro and client-a Business only**; employees submit request with amount, VAT, merchant, and a receipt; employer validates from Mon équipe > Demandes; bank account saved after first submission
- **Conditions/exceptions:** Pro/Business plans only; employees must have accepted invitation and completed profile
- **Financial risk:** Moderate — wrong plan info leads to incorrect feature expectations

---

## Article 8953699 — Expense reimbursement (employee view)
- **Topic:** Employee self-service expense submission
- **Key facts:** No stated reimbursement cap; receipt upload required; bank account saved after first submission; employer must validate before funds are released; available on **client-a Pro and Business plans only**
- **Conditions/exceptions:** Pro/Business plans only
- **Financial risk:** Moderate

---

## Article 8711129 — Sub-accounts (operation, creation, closure)
- **Topic:** client-a sub-accounts
- **Key facts:**
  - Each sub-account has its own unique **French IBAN**
  - **Cannot** attach a physical or virtual card to a sub-account
  - **Cannot** set up recurring transfers from a sub-account
  - Plan limits: **Start: 1 sub-account; Plus: 4; Business: 9** (not available on Free)
  - Closure requires zero balance — transfer funds out first
  - A seizure (saisie/ATD) **can** be applied to a sub-account
- **Conditions/exceptions:** No card attachment; no recurring transfers; sub-accounts unavailable on Free
- **⚠️ HIGH financial risk:** Wrong plan limits mislead users; telling users they can attach a card or set up recurring transfers is incorrect

---

## Article 8680523 — Dashboard: manage finances
- **Topic:** client-a Pro financial dashboard
- **Key facts:** Available from **Start** plan; shows balance history, outflows, inflows, expense categories; data available **from 2023 onwards**; **does not track VAT, outstanding amounts, or debts**; can filter by sub-account
- **Conditions/exceptions:** No VAT or debt tracking; data starts from 2023
- **Financial risk:** Low — implying VAT tracking is available could lead to compliance mistakes

---

## Article 8537771 — Adding team access slots
- **Topic:** Additional user access pricing
- **Key facts:**
  - Free: no additional accesses possible at all
  - Start: no included admin/employee access; additional access = **€5 HT/month/access**
  - Plus: 1 admin/employee access included; extra = **€5 HT/month/access**
  - Business: unlimited admin/employee accesses, no extra charge
  - Accountant access: unlimited on Start/Plus/Business; unavailable on Free
  - Additional access is billed **pro-rata** from the day of activation (example: added on the 15th with 15 days left in billing period = €2.50 HT, then €5 HT/month thereafter)
- **Conditions/exceptions:** Pro-rata billing; no additional admin/employee access on Free plan
- **⚠️ HIGH financial risk:** Wrong pricing or failure to mention pro-rata billing leads to unexpected charges

---

## Article 8442719 — Instant transfers (virements instantanés)
- **Topic:** Sending instant SEPA transfers
- **Key facts:**
  - Default limits: **€2,000 per transfer; €4,000 per day**
  - With "main phone" (téléphone principal) configured: up to **€10,000 per transfer; €20,000 per day**
  - Standard (non-instant) transfer takes **2–3 business days**
  - **Beneficiary Verification (VoP) is automatic from 9 October 2025** for all SEPA transfers — name on IBAN must match
  - Instant not available for: future-dated/recurring transfers, recipient's bank doesn't support it, non-SEPA recipient, recently added beneficiary or new device (temporary security block lasting a few days)
- **Conditions/exceptions:** New beneficiary/device triggers a temporary block; VoP name mismatch must be resolved before sending
- **⚠️ HIGH financial risk:** Wrong transfer limits, failure to mention VoP, or not knowing about the new beneficiary delay can cause payment failures

---

## Article 8490052 — Probative value certification of receipts
- **Topic:** Whether client-a certifies receipts as legally valid digital originals
- **Key facts:** **client-a does not offer probative value (valeur probante) certification**; digital copies on client-a do not replace original paper documents for tax audits; users must keep original paper receipts; client-a is not liable if originals are not presented during a control
- **Conditions/exceptions:** None
- **⚠️ HIGH financial risk:** If the chatbot implies client-a receipts are legally certified, users may discard paper originals and face tax audit penalties

---

## Article 8385519 — Receiving international (SWIFT) transfers
- **Topic:** Receiving cross-border wire transfers
- **Key facts:**
  - SWIFT partner: **Wise**; client-a BIC: `SNNNFR22XXX`; Wise intermediate BIC: `TRWIBEB3` (both must be provided to sender)
  - Transfers converted to euros before crediting — **client-a accounts receive euros only**
  - Typical delay: **4–5 business days**
  - client-a cannot track incoming wires before receipt; if delayed past 5 days, request **MT103** from sender's bank
  - Rejected transfers (ineligible currency/country): automatically returned to sender; refund may take **up to 10 business days**
  - Reception fees: **Free plan = €6 HT/transfer; Start/Plus/Business = €5 HT/transfer** (billed monthly, regardless of volume)
  - Interbancaire charge options: OUR (sender pays all — best for recipient), SHA (shared), BEN (recipient pays all)
  - FX: 90% of virements converted by sender's bank; 10% by Wise at real rate
- **Conditions/exceptions:** Ineligible currency/country = automatic return; FX rate varies and cannot be controlled; amount received may differ from amount sent
- **⚠️ VERY HIGH financial risk:** Wrong SWIFT fees, wrong BIC codes, incorrect FX expectations, or missing return delay info all have direct financial consequences

---

## Article 8198626 — Product/service catalogue (client-a Pro)
- **Topic:** Managing the product catalogue in client-a Pro (banking app)
- **Key facts:** Catalogue available on all plans; desktop-only for viewing/editing existing items; on mobile, new items can be added via invoice creation using the "Add to catalogue" checkbox
- **Conditions/exceptions:** Editing/viewing catalogue is desktop-only
- **Financial risk:** None

---

## Article 8124380 — Transfer initiation by an employee
- **Topic:** Employee-initiated wire transfer requests
- **Key facts:** Available on Start, Plus, Business; employee submits request with recipient info, amount, and **mandatory receipt/justification**; employer validates from Mon équipe > Demandes; employee sees only their own transactions; not available on Free
- **Conditions/exceptions:** Receipt is mandatory; requires prior invitation and identity setup
- **Financial risk:** Moderate

---

## Article 8141173 — Using client-a card before physical card arrives
- **Topic:** Virtual card auto-activation upon ordering a physical card
- **Key facts:** Available for **Start, Plus, Business** (not Free); virtual card automatically created when physical card is ordered; usable online and in-store via contactless; **Free plan users can create a virtual card at €2 HT/month/card**
- **Conditions/exceptions:** Free plan: virtual cards charged €2 HT/month; Start/Plus/Business: unlimited virtual cards at no cost
- **Financial risk:** Moderate — Free users need to know virtual cards are charged

---

## Article 7950097 — Mobile app access for employees (employer view)
- **Topic:** Restricted mobile app view for employees
- **Key facts:** Employee view limited to 4 tabs: Transactions (own only), Cards (view/request), Virements (initiate requests), Profile; employees cannot see company-wide transactions
- **Conditions/exceptions:** None
- **Financial risk:** None

---

## Article 7950186 — Mobile app for employees (employee view)
- **Topic:** Employee-facing mobile app description
- **Key facts:** Restricted to 3 tabs in this article: Transactions (own + receipt upload), Cards (view/request), Profile; employees cannot see company-wide transactions
- **Conditions/exceptions:** Employee role only
- **Financial risk:** None

---

## Article 7109039 — What is a client-a invitation?
- **Topic:** Roles available when invited to join a client-a account
- **Key facts:**
  - **Admin:** same rights as account holder except cannot close the account or invite other admins; requires identity verification
  - **Employé:** can request cards/transfers (both require validation from holder); sees own transactions only; can upload receipts
  - **Comptable:** read-only access to all transactions, receipts, statements, accounting exports; cannot make payments or invite members
- **Conditions/exceptions:** Admin cannot close account or invite other admins
- **Financial risk:** None

---

## Article 7060816 — Card ordering for employees
- **Topic:** How employees order payment cards
- **Key facts:**
  - Account holder **cannot** directly order a card for an employee — the employee must initiate the request
  - Plus: **2 physical cards included** (additional: €5 HT/month/card); Business: **10 physical cards included**
  - Virtual cards: unlimited at no cost on Plus and Business
  - Employer approves/rejects requests and sets spending limits
- **Conditions/exceptions:** Card requests must be employee-initiated; physical card limits differ by plan
- **⚠️ HIGH financial risk:** Wrong physical card limits or fees per plan have direct cost implications

---

## Article 6852230 — Secure online payment with Mastercard client-a (3DS V2)
- **Topic:** Online payment authentication
- **Key facts:** 3DS V2 requires confirming payment in the client-a app (notification or manual login); **if you receive a 3DS notification for an unknown payment, refuse it and immediately block your card** to prevent a retry
- **Conditions/exceptions:** None
- **⚠️ HIGH financial risk:** Failure to explain the fraud response procedure (refuse + block) could result in fraudulent charges being processed

---

## Article 6715420 — Mandatory invoice mentions
- **Topic:** Legal requirements for French invoices and quotes
- **Key facts:**
  - Mandatory for all invoices: emission date, buyer/seller identity, invoice number, VAT number (if applicable), HT and TTC totals, payment date/deadline, late-payment penalty rate, €40 flat-rate indemnity mention (B2B clients)
  - SIRET/SIREN of client: **not required when invoicing individuals**
  - Missing/incorrect mention = **€15 fine per mention per invoice, capped at 1/4 of invoice amount**
  - General non-compliance fine: up to **€75,000 (natural person) or €375,000 (legal entity)**
  - Special mentions by activity: TVA franchise → "TVA non applicable, art. 293 B du CGI"; BTP sub-contracting → "Autoliquidation"; artisans with mandatory professional insurance → must state policy details; members of an approved management association → specific mention required
- **Conditions/exceptions:** France only; B2B vs. B2C differences; activity-specific mentions vary
- **⚠️ VERY HIGH financial risk:** Missing mandatory mentions exposes users to substantial fines; the chatbot must accurately relay which mentions are required and for which situations

---

## Article 6485664 — Team access management
- **Topic:** Inviting team members to client-a
- **Key facts:** Three roles: Admin, Employé, Comptable; invite via Mon équipe > Gestion de l'équipe; Free plan cannot invite any team members
- **Conditions/exceptions:** Free plan: no team access at all
- **Financial risk:** Low

---

## Article 6426418 — Roles and account access
- **Topic:** Detailed permissions per role
- **Key facts:**
  - **Titulaire:** all rights including account closure and inviting admins
  - **Admin:** all rights except closing account and inviting other admins
  - **Employé:** request cards/transfers (both need holder/admin validation); own transactions only; upload receipts; no access to invoicing tool
  - **Comptable:** see all transactions + receipts, download statements, generate/schedule accounting exports; cannot make payments, invite members, or use invoicing tool
  - Role changes may require email identity re-verification before taking effect
- **Conditions/exceptions:** Some role changes trigger identity verification; new role not effective until validated
- **Financial risk:** Moderate — wrong permissions info could lead to unauthorised access or missing access

---

## Article 6365046 — Detecting transactions on old IBAN
- **Topic:** Transition period after account migration
- **Key facts:** Old BIC: `TRZOFR21`; "Ancien IBAN" tag marks affected transactions; weekly summary email sent; client-a auto-forwards funds from old IBAN for **3 months** post-migration; **do not revoke existing mandates** on the old IBAN during transition
- **Conditions/exceptions:** Must update IBAN with all clients and debit originators; do not cancel old mandates prematurely
- **⚠️ HIGH financial risk:** Revoking old mandates too early can cause failed payments (e.g., tax direct debits, supplier payments)

---

## Article 6310223 — Updating tax direct debit after migration
- **Topic:** Changing IBAN for tax payments on impots.gouv
- **Key facts:** New IBAN must be added on `impots.gouv` and the new mandate must also be registered in client-a; **do not revoke the old mandate** — tax authorities may still use it for the next payment cycle before the update is processed; if the new mandate is not added to client-a, the tax debit will not go through on the new IBAN
- **Conditions/exceptions:** Both steps required (impots.gouv + client-a); old mandate must not be revoked
- **⚠️ HIGH financial risk:** Revoking old mandate before transition is complete could cause a missed tax payment

---

## Article 6302541 — Why account migration?
- **Topic:** Migration from Treezor infrastructure to client-a's own
- **Key facts:** Accounts opened before May 2022 were on Treezor; migration to client-a's own infrastructure from July 2022; new IBAN issued; for **3 months** post-migration client-a auto-forwards funds arriving on old IBAN and honors direct debits if balance is sufficient; users must update their IBAN with clients and direct debit originators within that 3-month window
- **Conditions/exceptions:** Automatic forwarding lasts only 3 months
- **Financial risk:** Moderate — users need to update their IBAN before the window closes

---

## Article 6302504 — New Terms of Service
- **Topic:** CGU update triggered by migration
- **Key facts:** New CGUs apply from the day the new IBAN is issued; no additional obligations for users vs. prior CGUs; account closure delay was reduced
- **Conditions/exceptions:** None
- **Financial risk:** None

---

## Article 6020340 — Batch transfers (virements groupés)
- **Topic:** Sending multiple transfers via file upload
- **Key facts:**
  - **Business plan only**
  - Compatible formats: `.CSV` and `.XML`
  - CSV format requirements: max 140 characters per cell, no special characters (é, à, &, @…), amounts use a decimal point with 2 decimal places, currency is EUR only
  - Compatible payroll/accounting software: Payfit, Skello, vendor-b
- **Conditions/exceptions:** Business plan only; EUR only; strict character restrictions in CSV
- **⚠️ HIGH financial risk:** Wrong plan information misleads users; format errors cause failed batch payments

---

## Article 5576939 — Pay with Apple Pay
- **Topic:** Adding client-a card to Apple Pay
- **Key facts:** Must activate "Paiements en ligne" option before adding to Apple Pay (can be disabled afterwards); **max €3,000 per transaction via Apple Pay**; contactless payments above €50 are allowed (no upper limit from client-a up to €3,000); merchant may impose a lower limit
- **Conditions/exceptions:** Online payments option must be active at the time of adding to Apple Pay; merchant-imposed limits may be lower
- **Financial risk:** Moderate — wrong transaction limit info could cause payment failures

---

## Article 5227458 — Pay with Google Pay
- **Topic:** Adding client-a card to Google Pay
- **Key facts:** **Max €3,000 per transaction**; same payment limits as physical card; contactless payments above €50 allowed; confirmation via SMS code during setup; merchant may impose a lower limit
- **Conditions/exceptions:** Merchant-imposed limits may be lower
- **Financial risk:** Moderate

---

## Article 5161289 — SEPA zone countries
- **Topic:** Which countries are in the SEPA zone
- **Key facts:** SEPA includes all EU countries (including non-euro EU members: Bulgaria, Croatia, Denmark, Hungary, Poland, Czech Republic, Romania, Sweden) plus non-EU: Andorra, Iceland, Liechtenstein, Norway, Monaco, UK (incl. Gibraltar), Switzerland, San Marino, Vatican; France includes overseas territories (Guadeloupe, Martinique, Guyane, Mayotte, Réunion, Saint-Pierre-et-Miquelon, etc.)
- **Conditions/exceptions:** Non-euro SEPA members have dual systems (SEPA for EUR + local for own currency)
- **Financial risk:** Moderate — labelling a non-SEPA country as SEPA leads to wrong transfer routing and fees

---

## Article 5096371 — Virtual cards
- **Topic:** Virtual card functionality and pricing
- **Key facts:**
  - **Free plan: €2 HT/month/card** (optional add-on)
  - **Start, Plus, Business: unlimited virtual cards, no charge**
  - Virtual card spending limit: **€5,000 over 7 rolling days**
  - Usable online (recurring or one-off) and contactless via Google Pay/Apple Pay
  - **Deletion is permanent and irreversible**
- **Conditions/exceptions:** Free plan charged; 7-day rolling limit applies; deletion is irreversible
- **⚠️ HIGH financial risk:** Wrong pricing for Free plan or wrong spending limit can cause unexpected charges or payment failures

---

## Article 5086738 — Disable charge estimation on client-a app
- **Topic:** Micro-enterprise charge estimation module
- **Key facts:** Estimation is **indicative only** and may differ from URSSAF amounts; can be toggled on/off at any time; historical calculations are retained in the database
- **Conditions/exceptions:** Micro-enterprises only
- **Financial risk:** Moderate — users must understand this is an estimate, not an official URSSAF figure

---

## Article 5076758 — Declare self-employment income for tax
- **Topic:** Annual tax declaration for auto-entrepreneurs (form 2042 C PRO)
- **Key facts:**
  - Mandatory online declaration since 2019 (exceptions: no internet at home, or first declaration without prior credentials)
  - Declare **gross revenue (CA encaissé) without applying the abattement yourself** — the tax authority applies it automatically
  - Abattements: **71%** for merchandise sales, **50%** for commercial services, **34%** for liberal services
  - With versement libératoire: use boxes 5TA (merchandise), 5TB (commercial services), 5TE (liberal services)
  - Without versement libératoire (commercial): box 5KO (merchandise), 5KP (commercial services); box 5DB for months of activity
  - Without versement libératoire (liberal): box 5HQ; box 5XI for months of activity
  - Case 5HY at validation step: **not applicable to micro-enterprises** — skip it
- **Conditions/exceptions:** Versement libératoire = income tax already paid periodically, but declaration still required; declare revenue without applying abattement
- **⚠️ VERY HIGH financial risk:** Wrong declaration boxes, manually applying the abattement before declaring, or mishandling the versement libératoire leads to incorrect tax assessment and potential penalties

---

## Article 4859103 — Subscription tracking and billing
- **Topic:** Monitoring client-a subscription charges and invoices
- **Key facts:** Accessible via Mon abonnement; shows subscription details, additional usage fees, and consumption counters; some fees billed at usage (card use, cash deposit, FX transfers, card-based invoice collection); others billed monthly at renewal; an alert appears if client-a cannot debit the subscription
- **Conditions/exceptions:** Usage counters reset at each billing period end
- **Financial risk:** Moderate — helps users understand unexpected charges

---

## Article 4703305 — Data collected by client-a
- **Topic:** Privacy and data use
- **Key facts:** Data categories and purposes: identifiers (marketing), personal info (analysis/marketing/ID), location (fraud prevention), user content (identity verification), device usage (analytics/fraud/support), financial data (regulatory), biometric/sensitive data (account opening), diagnostics (app performance)
- **Conditions/exceptions:** None
- **Financial risk:** None

---

## Article 4680080 — Additional required invoice information by activity
- **Topic:** Activity-specific mandatory fields on invoices
- **Key facts:**
  - Commercial activity: must include **RCS number** (SIREN + "RCS" + registration city)
  - Artisanal activity: must include **RM number** (SIREN + "RM" + Chambre des Métiers code)
  - VAT-liable: must include **TVA intracommunautaire number** (FR + 2-character key + SIREN)
  - TVA franchise: must include "TVA non applicable, art. 293 B du CGI"
  - BTP sub-contracting: must include "Autoliquidation"
  - International invoicing: requires an additional declaration
- **Conditions/exceptions:** Requirements vary by legal status and tax regime
- **⚠️ HIGH financial risk:** Missing required identifiers on invoices is a compliance violation with potential fines

---

## Article 4602902 — Company registration document for client-a account
- **Topic:** Required company documents for KYC
- **Key facts:** Documents must be **less than 3 months old**; legal persons (SAS, SARL…): INPI extract or Kbis; individuals: SIRENE notice or INPI extract; Kbis available free at MonIdenum or for a fee on Infogreffe; only digital formats accepted (PDF/image — no paper copies)
- **Conditions/exceptions:** Under 3 months validity required; no paper copies
- **Financial risk:** None

---

## Article 4305211 — What is a beneficial owner (bénéficiaire effectif)?
- **Topic:** Legal definition and KYC requirement
- **Key facts:** A beneficial owner holds **≥25% of capital or voting rights**, or exercises control over the company; must be a natural person; indirect control (via another company) is also in scope; **all beneficial owners must be identified** to open a client-a account; if a company is owned/controlled by another legal entity, that entity's statutes are also required
- **Conditions/exceptions:** All BOs required, not just the applicant; indirect control counts
- **Financial risk:** None

---

## Article 4111100 — Add custom mentions to invoices
- **Topic:** Adding custom legal text to invoices
- **Key facts:** Can add custom mentions before sending; **cannot add mentions to an already-sent invoice without duplicating it**; duplicate + edit + resend workflow required for sent invoices; client must be sent the updated invoice again
- **Conditions/exceptions:** Sent invoices require duplication; re-sending to client is mandatory
- **Financial risk:** Moderate — failure to re-send a corrected invoice with mandatory mentions = compliance risk

---

## Article 4062963 — Calculating late payment penalties
- **Topic:** Legal late payment penalty rates and calculation method
- **Key facts:**
  - Legal minimum rate: **3× the Banque de France legal interest rate** — for H2 2025: **8.28% minimum**
  - Commonly applied rate: BCE director rate + 10 points = currently **12.15%**; client-a default = **13.15%** (editable)
  - Formula: `(TTC amount × rate) × (days late / 365)`
  - Penalties calculated on **TTC amount**; **not subject to VAT**
  - Mentioning the penalty rate on invoices is **legally required** (Code de Commerce)
  - **Actually collecting the penalties is optional** — you can choose to waive them
  - If charged: issue a new invoice at €0 VAT with immediate payment terms
- **Conditions/exceptions:** Rate mention is mandatory; collection is optional; minimum legal floor is 8.28%
- **⚠️ VERY HIGH financial risk:** Wrong rate information affects invoice compliance, client relationships, and potential legal disputes

---

## Article 3864336 — Modify an invoice
- **Topic:** Invoice modification rules
- **Key facts:** Can only directly edit invoices **not yet sent**; sent invoices must be **duplicated** (not deleted) and resent; this is required by the **anti-VAT fraud law of January 2018**, which prohibits deleting invoices already presented to a client; alternatively, a credit note (avoir) can be issued
- **Conditions/exceptions:** Sent invoices: must duplicate, not delete; law mandates this
- **⚠️ HIGH financial risk:** Deleting or backdating sent invoices is illegal; chatbot must guide users to the duplication or avoir workflow

---

## Article 3693082 — Transmitting company statutes for account opening
- **Topic:** Required company documents (statutes for SAS, SARL, EURL, SASU)
- **Key facts:** Must submit final validated statutes as PDF; information in statutes must match signup data (beneficial owners, APE code, address); no paper copies accepted; if only paper available: scan all pages and merge into one PDF
- **Conditions/exceptions:** Statutes must be the final version validated by the State
- **Financial risk:** None

---

## Article 3815636 — Documents to prove company existence
- **Topic:** KYC document requirements by activity type
- **Key facts:** All documents must be **less than 3 months old**; liberal/commercial: SIRENE notice or INPI extract; artisanal: D1 extract or SIRENE notice (D1 may be paid — SIRENE is the free alternative); all types can alternatively use an INPI extract from Guichet Unique
- **Conditions/exceptions:** Under 3 months validity required; D1 may be chargeable
- **Financial risk:** None

---

## Article 3629915 — Contesting a SEPA direct debit
- **Topic:** SEPA direct debit disputes
- **Key facts:**
  - **CORE (B2C) debits:** can be contested; **time limit: cannot contest debits made more than 8 weeks ago**; contact creditor first; if no response, contest via app (transaction > Besoin d'aide > Contester)
  - **B2B debits: cannot be contested or refunded** once executed; only future debits can be blocked by suspending the mandate
- **Conditions/exceptions:** B2B = no refund after execution (this is stated in the mandate itself); CORE = 8-week hard deadline
- **⚠️ VERY HIGH financial risk:** Telling a B2B user they can get a refund is incorrect; missing the 8-week window for CORE means the user loses their right to contest

---

## Article 3565695 — Cheque deposit delays
- **Topic:** Cheque encashment timeline
- **Key facts:**
  - Total delay: **15 business days** before funds are credited
  - Breakdown: 1–2 days (client-a validation) + 3 days (banking partners) + **11 days immobilisation** (contestation window — mandatory)
  - **Cheque validity: 1 year and 8 days** from issue date — cheques older than this cannot be deposited
  - Cheque must reach client-a within **15 days of being declared in the app**; otherwise encashment is cancelled
  - client-a does **not** offer chequebooks
- **Conditions/exceptions:** 15-day physical submission window; 11-day immobilisation is non-negotiable
- **⚠️ HIGH financial risk:** Users relying on faster access to cheque funds face cash flow problems; the cheque validity and submission deadlines are hard limits

---

## Article 3590609 — Schedule one-off or recurring transfers
- **Topic:** Programmed transfers
- **Key facts:** Schedule via Paiements > Effectuer un virement > Virement programmé; can be one-off (future date) or recurring (with frequency); manage/suspend from Paiements > Virements Programmés; instant transfer **not available** for future-dated or recurring transfers
- **Conditions/exceptions:** Instant transfer unavailable for scheduled/recurring transfers
- **Financial risk:** None

---

## Article 3306088 — Invoice for referral bonuses
- **Topic:** Creating a self-billed invoice to justify referral income for accountants
- **Key facts:** client-a's billing details: client-a SAS, TVA `FR18828701557`, 122 rue Amelot, 75011 Paris; TVA rate: 0%; send completed invoice to `hello@client-a.fr`; client-a validates within 24h; mark invoice as "paid" after validation
- **Conditions/exceptions:** Amount must match bonuses paid; must send to client-a for validation
- **Financial risk:** Moderate — wrong data causes accounting issues

---

## Article 3155257 — Add a B2B SEPA direct debit mandate
- **Topic:** Setting up a B2B SEPA mandate
- **Key facts:** Mandate references must be **exact** — errors cause the creditor's debit to fail; acceptable file formats: PDF, JPEG, PNG; confirmed via secret code; mandates can be added to a sub-account; wrong creditor SEPA ID triggers an error message in the app
- **Conditions/exceptions:** References must be character-perfect; sub-account mandate assignment is supported
- **⚠️ HIGH financial risk:** Incorrect mandate references cause failed tax or supplier payments

---

## Article 3124917 — Cash flow / investment credit
- **Topic:** Financing partners available through client-a
- **Key facts:**
  - **Defacto:** short-term loans, 1 day to 4 months; rate **0.05%/day** on amount actually borrowed; no early repayment penalty; eligibility: registered at RCS, no collective proceedings in last 24 months, min 3 months of bank data; **excludes:** associations, SCI, liberal professions
  - **ADIE:** non-bank loan; rate **9.87%**; amount **€300–€12,000**; max repayment **48 months**; available even to those on banking blacklist but a **guarantor is required**
- **Conditions/exceptions:** Defacto: excludes associations, SCI, liberal professions, and those under or recently under collective proceedings; ADIE: guarantor mandatory
- **⚠️ HIGH financial risk:** Wrong interest rates, eligibility criteria, or loan limits directly influence financial decisions

---

## Article 3122320 — Cheque encashment fees
- **Topic:** Cheque deposit costs by plan
- **Key facts:**
  - **Free:** 0 free deposits/month, then **€2 HT/deposit**; limit: €5,000/cheque, €10,000/30 days
  - **Start:** 2 free/month, then **€2 HT**; same limits
  - **Plus:** 6 free/month, then **€2 HT**; same limits
  - **Business:** 15 free/month, then **€2 HT**; same limits
  - Rejected cheque (fraud/insufficient funds): **€25 HT**
  - Returned cheque (missing/incomplete info): **€5 HT**
  - Overage fees billed at monthly renewal; client-a does **not** issue chequebooks
- **Conditions/exceptions:** 30-day rolling limit resets on billing date; Free plan has no free deposits
- **⚠️ HIGH financial risk:** Wrong deposit limits or rejection fees by plan lead to unexpected charges

---

## Article 10063938 — Adding VAT to transactions
- **Topic:** Manually or automatically recording VAT on bank transactions in client-a Pro
- **Key facts:** Uploading a receipt triggers automatic VAT detection (rate and amount filled in automatically); the pencil icon allows manual correction; VAT data feeds the micro-enterprise charge estimation tool for more accurate results; accountant access (Start/Plus/Business) lets a comptable download receipts
- **Conditions/exceptions:** Auto-fill depends on a receipt being attached — transactions without a receipt require manual entry; accountant access is only available on paid plans
- **Financial risk:** Low — but if a chatbot implies VAT is always auto-filled without a receipt, users may leave VAT blank and get an inaccurate charge estimation

---

## Article 10221385 — VAT calculation in the charge estimation tool
- **Topic:** Automatic VAT calculation within the micro-enterprise social charge estimator
- **Key facts:** Automatic VAT calculation can be toggled on/off; when on, it uses VAT-inclusive invoices collected on the account and transactions where a VAT rate has been entered; manual override is always possible; if some transactions have no VAT, those are excluded from the automatic calculation and must be completed manually
- **Conditions/exceptions:** Partial coverage: transactions without VAT entered are excluded — result may be incomplete if not all transactions are tagged; the option must be explicitly activated by the user
- **⚠️ Moderate financial risk:** If the chatbot implies VAT is automatically and fully calculated when the option is on, users may under-declare VAT because untagged transactions are silently excluded

---

## Article 10289941 — client-a joins Ageras
- **Topic:** Acquisition of client-a by Ageras group and reassurance for existing customers
- **Key facts:** client-a is now part of Ageras (European accounting/finance software group); **IBAN remains unchanged**; funds remain ring-fenced in Société Générale books; ACPR authorisation is maintained; the same team continues (customer service 7/7); **no action required from customers**; client-a keeps its name; the Ageras group name will eventually adopt the "client-a" brand internationally; Société Générale sold client-a as part of a refocus on core activities; client-a was won "Élu Service Client de l'Année" in 2024, 2025, and 2026
- **Conditions/exceptions:** Nothing changes contractually for existing customers; no account number change; no new CGU obligation stated
- **Financial risk:** None — but incorrectly stating that funds are no longer with Société Générale or that the IBAN has changed would cause unnecessary alarm or erroneous actions

---

## Article 10437076 — What is a sensitive operation?
- **Topic:** List of account actions requiring strong authentication (sensitive operations)
- **Key facts:** Current sensitive operations: adding a SEPA beneficiary, validating login on a new device, creating a batch transfer (virement groupé), creating a virtual card, revealing PIN, displaying card details (PAN + CVC), adding card to Apple Pay / Google Pay, modifying instant transfer limits (increase or decrease), validating a 3DS transaction; pending operations viewable in the app under Profile > Sécurité > Opérations à valider; the list is actively expanded by client-a's security team
- **Conditions/exceptions:** Requires the "téléphone principal" (primary phone) to be configured; the list may grow over time
- **⚠️ Moderate financial risk:** If a chatbot incorrectly states that adding a beneficiary or a 3DS confirmation does not require strong auth, users may be confused when they are blocked — or may lower their guard to a phishing attempt

---

## Article 10437144 — Primary phone (téléphone principal)
- **Topic:** Setting up and managing the trusted device used for sensitive operations
- **Key facts:** A primary phone is a mobile device designated as the trust anchor for sensitive operations; only **one** primary phone per user at a time; must have the client-a mobile app installed; replaces SMS codes for sensitive operations (SMS is less secure); adding a primary phone requires a 6-digit SMS code; changing the primary phone requires identity verification and automatically deactivates the old device; a primary phone **cannot be directly blocked** — it is deactivated only by replacing it with a new primary phone; primary phone is also required to increase/decrease instant transfer limits
- **Conditions/exceptions:** Only one primary phone allowed at a time; changing requires identity verification; blocking requires replacement
- **⚠️ Moderate financial risk:** If a user loses their phone and is told they can just "block" it from settings, they may be left unable to perform sensitive operations (including transfers); the chatbot must guide them through the replacement flow

---

## Article 10485933 — When do the new pricing plans apply?
- **Topic:** Rollout timeline for client-a's new subscription pricing (March 2025)
- **Key facts:**
  - Official communication was sent to existing customers during the week of **3 March 2025** by email and in-app notification
  - Existing customers keep their current subscription at the current price for **6 weeks** after that communication date
  - During those 6 weeks, customers can voluntarily switch to a new plan
  - After those 6 weeks, customers are **automatically migrated** to their mapped new plan with another **6-week trial period** at the most favourable price (old plan price for Basic/Plus; new price for Pro/Business)
  - After the second 6-week period, the new price applies permanently with monthly billing
  - Customers on 6-month or 12-month legacy commitments: automatically migrated after 6 weeks, but **cannot switch plans before their commitment ends**
  - New subscribers see the new pricing immediately
- **Conditions/exceptions:** Committed customers cannot change plans mid-commitment; the "most favourable price" rule differs by legacy plan (Basic/Plus = keep old price; Pro/Business = new price from day 1 of trial)
- **⚠️ HIGH financial risk:** Wrong migration timeline or misrepresenting whether a committed customer can change plans could cause users to make decisions under false assumptions about their costs

---

## Article 10490725 — Why are client-a's prices changing?
- **Topic:** Explanation and context for the 2025 pricing revision
- **Key facts:** Plans had not been revised since 2021; the revision was driven by product evolution and customer feedback — not by the Ageras acquisition; a Free (€0) plan was introduced to lower the barrier to entry; **the price change is explicitly stated as unrelated to the ownership change**; Ageras enables new tools (accounting, invoicing) but is not the cause of repricing; client-a remains licensed by ACPR; customer support remains 7/7; no features are being removed
- **Conditions/exceptions:** None
- **Financial risk:** None — but asserting the price change is due to Ageras is factually wrong and potentially damaging to user trust

---

## Article 10490776 — New client-a Pro account plans
- **Topic:** Detailed breakdown of the four new client-a Pro subscription tiers
- **Key facts:**
  - **Free: €0/month** — 1 physical card; €20,000 payment ceiling/30 days; 5 SEPA transfers/debits included (€0.40/extra); no virtual cards included (€2 HT/card/month); cheque deposit: €2 HT/deposit (limit €5,000/deposit, €10,000/month); no team access
  - **Start: €11 HT/month** (or €9 HT/month annualised = €108/year) — unlimited virtual cards; €40,000 ceiling; 30 SEPA included; 2 cheque deposits included; 2 cash withdrawals included; 1 sub-account; financial dashboard; team access at €5 HT/access/month
  - **Plus: €25 HT/month** (or €20 HT/month annualised = €240/year) — 2 Mastercard Premium; €60,000 ceiling; 100 SEPA included; 6 cheque deposits included; 4 cash withdrawals included; 4 sub-accounts; 1 team access included; insurance cover (hospitalisation, phone screen, travel delays, fraud, legal, debt recovery)
  - **Business: €80 HT/month** (or €70 HT/month annualised = €720/year) — 10 Mastercard Premium; €60,000 ceiling; 500 SEPA included; 15 cheque deposits included; 10 cash withdrawals included; 9 sub-accounts; unlimited team access; batch transfers
  - All prices are **HT (excluding VAT)**
  - Overage fees apply per plan for SEPA, cash deposits, international transfers, etc.
- **Conditions/exceptions:** Free plan has no included virtual cards (charged separately); international transfer fees differ by plan; annualised pricing requires 12-month commitment
- **⚠️ HIGH financial risk:** Wrong monthly prices, wrong included quotas (especially SEPA transfers and card limits), or failing to mention HT pricing directly affects purchasing decisions and can cause unexpected charges

---

## Article 10495320 — New company creation offers
- **Topic:** client-a's bundled offers combining company creation services with a pro account
- **Key facts:**
  - **Micro-enterprise creation:** from **€59 HT** (excl. mandatory legal fees); 1 free month on any plan OR Free plan; if committed to annual billing, creation fees are waived
  - **Capital deposit:** from **€69 HT**; 1 free month on any plan OR Free plan; if committed, deposit management fees are waived
  - **SASU creation:** from **€168 HT** (excl. mandatory legal fees); 1 free month or Free plan; if committed, creation fees are waived
  - **SAS/SARL:** from **€238 HT**; **SASU/EURL:** from **€168 HT**; **SCI/other:** from **€188 HT** — all excluding mandatory legal fees
  - Company creation (SAS/SARL/SASU/EURL etc.) is in partnership with **LegalStart** — the administrative part redirects to LegalStart's platform
  - All offers available without account commitment (can choose Free plan)
- **Conditions/exceptions:** Fees quoted exclude mandatory legal/government fees; fee waivers only apply if customer commits to annual billing; creation handled by LegalStart for corporate forms (not client-a directly)
- **⚠️ HIGH financial risk:** Quoting creation prices without the "excl. legal fees" caveat, or implying fees are waived without commitment, directly misleads users about real costs

---

## Article 10495791 — Annual billing
- **Topic:** How annual (pre-paid) subscriptions work and the discounts they offer
- **Key facts:**
  - Annual billing = pay 12 months upfront at a discounted monthly rate
  - Discounts vs monthly billing: **Start: €9/month (vs €11) = €108/year, saving €24 (18.2%)**; **Plus: €20/month (vs €25) = €240/year, saving €60 (20%)**; **Business: €70/month (vs €80) = €720/year, saving €240 (25%)**; **Free plan has no annual option**
  - Annual billing is **not offered at initial sign-up** — it becomes available once the account is open
  - Micro-enterprises get only a **6-month commitment** option (not 12)
  - Annual billing also unlocks discounts on company creation fees and capital deposit fees (see article 10495320)
  - All prices are **HT (excluding VAT)**
- **Conditions/exceptions:** Free plan excluded; micro-enterprise capped at 6-month commitment; not available at sign-up; only accessible post-account-opening
- **⚠️ HIGH financial risk:** Quoting wrong annualised prices, incorrectly telling a micro-entrepreneur they can get 12-month billing, or implying annual billing is available at sign-up all lead to incorrect financial expectations

---

## Article 1175378 — Is client-a a bank?
- **Topic:** client-a's legal status as a payment institution, not a traditional bank
- **Key facts:** client-a is licensed by the ACPR (Autorité de contrôle prudentiel et de résolution) as a **payment institution (établissement de paiement)**, not a bank; ACPR registration number **71758**; client-a provides bank-like services (Mastercard, transfers, withdrawals, direct debits) but **cannot offer overdrafts** and **cannot offer credit without third-party partners**; the ACPR is the French banking and insurance supervisor
- **Conditions/exceptions:** Credit only available via partners (e.g., Defacto, ADIE); no overdraft possible on any plan
- **Financial risk:** Moderate — if a chatbot implies client-a is a full bank or that overdraft is possible, users may attempt to spend beyond their balance

---

## Article 1175387 — Differences between client-a and a traditional bank
- **Topic:** Side-by-side comparison of client-a (payment institution) vs. traditional banks
- **Key facts:** client-a provides the same core services (Mastercard Business, transfers, withdrawals, direct debits, accounting exports, invoicing) but two key limitations apply: **no overdraft** possible; **credit requires third-party partners** (not offered directly); client-a is registered with ACPR; customer support is 7/7; product offerings include company creation, capital deposit, invoicing, insurance, and community resources
- **Conditions/exceptions:** Same limitations as article 1175378 — no overdraft, no direct credit
- **Financial risk:** Moderate — a user told they can overdraft will face declined payments or unexpected account blocks

---

## Article 1175483 — client-a is a professional account only
- **Topic:** client-a does not offer personal accounts; professional use only
- **Key facts:** **Personal accounts cannot be opened on client-a**; available for sole traders (entreprises individuelles) and legal entities (SAS, SASU, SARL, SCI…); requires a SIRET for existing companies; company creation and capital deposit journeys are available for those not yet registered
- **Conditions/exceptions:** No personal accounts under any circumstances
- **Financial risk:** None — but answering a personal account request incorrectly wastes user time and creates a failed onboarding

---

## Article 1175607 — Opening multiple client-a accounts
- **Topic:** Rules and process for managing multiple client-a accounts across different companies
- **Key facts:** Multiple client-a accounts are permitted — **each must be linked to a different company (different SIRET)**; all accounts share the same phone number and email address; each account has its own **distinct IBAN and card**; a **separate subscription is billed per account** (different plans can be chosen per account); for multiple accounts under the same company, use **sub-accounts (sous-comptes)**, not multiple main accounts
- **Conditions/exceptions:** One main account per company; multiple accounts for the same entity = sub-accounts; subscription fee applies per account
- **⚠️ Moderate financial risk:** Telling a user they can manage two separate companies under one account would cause them to commingle funds and potentially face compliance issues; failing to mention the per-account subscription fee means unexpected billing

---

## Article 1175739 — Is the client-a subscription commitment-free?
- **Topic:** Cancellation rights and commitment rules for monthly vs. annual billing
- **Key facts:** Two billing modes: **monthly (no commitment)** — can cancel at any time, no fee; **annual (12-month commitment)** — can also cancel at any time but **no refund is given for unused months if the account is closed before the 12-month period ends**; plan changes are possible at any time; account closure can be done directly from the client portal
- **Conditions/exceptions:** Annual billing = **non-refundable if cancelled early**; monthly billing = no penalties
- **⚠️ HIGH financial risk:** If a chatbot tells a user on annual billing that they will receive a pro-rata refund on early cancellation, they may close their account expecting a reimbursement that will not come

---

## Article 1176231 — Creating and activating a client-a account
- **Topic:** Identity and company document requirements for opening a client-a account
- **Key facts:** Accepted IDs: **valid European CNI, European passport, or titre de séjour**; an expired CNI is still valid if it was issued after the holder's 18th birthday and is the **old rectangular format** (extended 5 years); **titre de séjour marked "salarié", "étudiant", "travailleur temporaire", or "visiteur" is NOT accepted**; companies need a Kbis, SIRENE notice, or validated statutes; if multiple beneficial owners exist, **each must provide ID and proof of address**; documents can be uploaded via app or web
- **Conditions/exceptions:** Expired CNI only valid for specific old format; four specific titre de séjour categories are rejected; all beneficial owners must submit documents
- **Financial risk:** None — but incorrect ID requirements cause failed onboarding

---

## Article 10503171 — Capital deposit with client-a
- **Topic:** client-a's share capital deposit service — pricing and process overview
- **Key facts:**
  - Available from **€69 HT without commitment**; **with 12-month commitment, capital deposit fees are waived** (€0)
  - Combined cost (deposit + subscription, all HT): Free: €69; Start no commitment: €190 (≈first year); Start 12-month: €108; Plus no commitment: €344; Plus 12-month: €240; Business no commitment: €949; Business 12-month: €720
  - All prices are **HT (excluding VAT)**
  - Eligibility criteria exist — covered in a separate article; funds must come from an eligible country (France incl. DOM-TOM, Belgium, Spain, Germany, Italy, Portugal) and from an account in the depositor's name
  - Capital attestation issued within 72h of notary validation; funds released 2–3 business days after Kbis is received
- **Conditions/exceptions:** Fee waiver requires 12-month plan commitment; fund origin is restricted to specific countries; eligible from the depositor's own account only
- **⚠️ HIGH financial risk:** Quoting the deposit fee without mentioning the commitment requirement for the waiver, or omitting "HT", directly misleads users about the real cost they will pay

---

## Article 10673790 — Refund conditions after withdrawal (rétractation)
- **Topic:** When and how users can obtain a refund after signing up for client-a services
- **Key facts:** Users have a **15 calendar-day withdrawal window** from the date of initial payment and CGU signature; a refund is only granted if **all three conditions are met simultaneously**: (1) capital has not yet been deposited (for capital/creation services), (2) company creation documents have not been submitted to authorities, (3) the bank account is not yet open; withdrawal request must be submitted **in writing** (letter or email); if eligible, refund is processed within **14 business days** of receiving the request
- **Conditions/exceptions:** All 3 conditions must be met; written form mandatory; 15-day window is a hard calendar deadline; once any condition is no longer met, refund rights are lost
- **⚠️ HIGH financial risk:** Telling a user they can get a refund after their account is open or after capital has been deposited is incorrect; the 15-day limit and conditions are strict legal terms from the CGU (article 36.4)

---

## Article 10944628 — Viewing and hiding account balance
- **Topic:** How to consult or hide the account balance on mobile and web
- **Key facts:** Mobile: balance shown in the Banque tab, top-left; Web: balance shown in the Compte pro section at the top; multiple accounts: click "Compte principal" to switch between accounts; balance can be toggled hidden/visible using the eye icon (available on both mobile and web)
- **Conditions/exceptions:** None
- **Financial risk:** None

---

## Article 10944693 — Downloading the client-a app
- **Topic:** How to download the client-a mobile app on iOS and Android
- **Key facts:** iOS: available on the **App Store**; Android: available on **Google Play**; the same app is used for both new account creation and logging in to an existing account; web access also available at `app.client-a.fr`
- **Conditions/exceptions:** None
- **Financial risk:** None

---

## Article 10944719 — Accessing client-a on the web
- **Topic:** Step-by-step web login process for client-a
- **Key facts:** Web app URL: **app.client-a.fr**; login requires: phone number (without leading 0), then the **4-digit PIN** (same code used on the mobile app), then a **6-digit SMS confirmation code**; forgotten PIN: use "Code secret oublié" when logged out — **PIN reset is only possible from a device where the user was previously logged in**; the 4-digit code is identical across web and mobile
- **Conditions/exceptions:** PIN reset cannot be done from a brand-new device — must use a previously authenticated device
- **Financial risk:** None — but incorrect reset instructions could prevent a user from accessing their account

---

## Article 11459151 — E-invoicing reform: what you need to know
- **Topic:** Overview of the French mandatory B2B e-invoicing reform (Réforme de la Facturation Électronique)
- **Key facts:**
  - **September 2026:** all SMEs, micro-enterprises, and large companies must be able to **receive** e-invoices; large companies (ETI/grandes entreprises) must also **emit** e-invoices and do e-reporting
  - **September 2027:** SMEs and micro-enterprises must also **emit** e-invoices and do e-reporting
  - Accepted formats: **Factur-X, UBL, CII** — plain PDF sent by email is not compliant
  - All companies must transit invoices through a certified platform: **Plateforme Agréée (PA)** or **Opérateur de Dématérialisation (OD)**
  - Reception is mandatory for **all companies** regardless of size, legal form, revenue, or VAT status
  - Emission and e-reporting apply only to **French VAT-liable companies doing domestic B2B** transactions; B2C and cross-border = e-reporting only
  - client-a will become a PA — **e-invoicing will be free and included in all plans**
  - At time of writing, only **reception** is available on client-a; emission is forthcoming
- **Conditions/exceptions:** Emission scope = French VAT-liable B2B only; reception is universal; PA list was not yet finalised at time of writing
- **⚠️ HIGH financial risk:** Wrong dates, wrong scope (e.g., telling a small company they don't need to receive until 2027), or failing to flag that plain PDFs are non-compliant could cause regulatory non-compliance and fiscal penalties

---

## Article 11459160 — client-a as a future Plateforme Agréée (PA)
- **Topic:** client-a's roadmap to becoming an accredited e-invoicing platform
- **Key facts:** A Plateforme Agréée (PA, formerly called PDP — Plateforme de Dématérialisation Partenaire) is a state-certified platform for exchanging e-invoices; client-a is becoming a PA and will handle both sending and receiving e-invoices; **client-a's PA solution was not yet on the official registered list at the time of writing** (in development); the solution will be ready before the reform deadline; **e-invoicing (both reception and emission) will be free and included in all plans once available**; reception is already activatable; emission is still forthcoming
- **Conditions/exceptions:** PA registration not finalised at time of writing; "PDP" has been renamed to "PA" by the French tax administration — both terms refer to the same thing
- **Financial risk:** Low — but telling users client-a is already a registered PA could cause misplaced compliance reliance; failing to mention that emission is not yet available could cause planning errors

---

## Article 11721305 — How to receive e-invoices on client-a
- **Topic:** Activation steps and features for e-invoice reception on client-a Pro
- **Key facts:** E-invoice reception is mandatory for all companies from **1 September 2026**; client-a offers this for free with no hidden fees; activation: web app via Comptabilité > E-factures fournisseurs > Activer gratuitement, or mobile app via Plus > Comptabilité > E-factures fournisseurs; once active, users can receive, process, approve, or reject e-invoices; requires identity document verification before activation (separate onboarding step)
- **Conditions/exceptions:** Feature must be explicitly activated (not on by default); identity verification required before use; legal deadline of 1 September 2026 applies to all companies
- **Financial risk:** None for the how-to itself — but failure to activate before the legal deadline exposes the company to non-compliance

---

## Article 1176295 — Resetting the account PIN
- **Topic:** Procedure for resetting the client-a 4-digit access code when forgotten
- **Key facts:** PIN reset triggered via "Code secret oublié?" on the login screen (both web and mobile); user enters their phone number, defines a new PIN, and confirms it via a 6-digit SMS code; **reset is only possible from a device that has already been authenticated (trusted device)** — it cannot be done from a brand-new device
- **Conditions/exceptions:** Trusted-device requirement is a hard constraint — a user on a new phone cannot reset their PIN without first having logged in on that device
- **Financial risk:** None — but wrong instructions (e.g., "reset from any device") could leave a user completely locked out of their account

---

## Article 1176407 — Blocking account after losing phone
- **Topic:** Emergency procedure when a phone is lost and account security is at risk
- **Key facts:** User must **immediately contact client-a customer support** to have the account blocked; this is the only described method — there is no self-service account lock available for a lost-phone scenario (since the phone is needed for most in-app actions); support is available 7/7
- **Conditions/exceptions:** No in-app self-service block for this scenario; urgency is stressed — immediate contact required
- **Financial risk:** Moderate — any delay in contacting support leaves the account exposed to unauthorised access and transactions

---

## Article 1176688 — Closing a client-a account
- **Topic:** How to close a client-a pro account
- **Key facts:** Account closure requires a **zero balance** — any remaining funds must first be transferred to an external account; closure initiated from: mobile app: Accueil > profile icon > Informations de l'entreprise > Clôturer le compte; web: profile > Mon entreprise > Clôturer le compte; **check for pending card refunds before initiating closure**; client-a has no exit fee
- **Conditions/exceptions:** Balance must be exactly €0; pending refunds must be resolved before closing or they may be lost
- **Financial risk:** Moderate — closing with a pending refund in progress could result in the refund being lost

---

## Article 1179187 — Transaction processing times
- **Topic:** How long debit and credit operations take on a client-a account
- **Key facts:**
  - Inbound card payment: **immediate**
  - Inbound standard SEPA transfer: **2–3 business days**
  - Inbound SEPA instant transfer: **instant, 24/7**
  - Inbound international (SWIFT) transfer: **4–5 business days**
  - Outbound SEPA instant: **within seconds** (debited simultaneously)
  - Outbound standard SEPA transfer: **2–3 business days** (debit and recipient credit happen at the same time)
  - SEPA direct debits (prélèvements): **2–3 business days** from the scheduled debit date
- **Conditions/exceptions:** "Business days" excludes weekends and public holidays; instant transfer is always 24/7 regardless of day
- **⚠️ Moderate financial risk:** Incorrect timing information can cause cash flow planning errors (e.g., a user expecting same-day SEPA payment to cover a supplier deadline)

---

## Article 1179200 — No overdraft on client-a
- **Topic:** Overdraft policy and why client-a cannot offer one
- **Key facts:** **client-a does not offer any overdraft facility**; accounts are payment accounts (comptes de paiement) — funds are ring-fenced outside client-a's balance sheet; if a payment or transfer is attempted with insufficient funds, it is **simply refused with no penalty fee**; **American Express cards cannot be linked to client-a** because Amex uses deferred debit, which would require overdraft capability; financing alternatives via Defacto and ADIE are available through client-a partners
- **Conditions/exceptions:** No overdraft under any plan; Amex incompatible; refused card payment = no fee
- **Financial risk:** Low — but a user told they have an overdraft or that a refused payment incurs a fee would be misled

---

## Article 1179228 — Cash deposits (dépôt d'espèces)
- **Topic:** Cash deposit service via partner tobacconists (buralistes)
- **Key facts:**
  - Cash deposited at partner Brink's tobacconist network; initiated via the mobile app; **France métropolitaine only — DROM-COM (overseas territories) not supported**
  - **Minimum deposit: €100**
  - **Credited in under a minute**
  - Fees and 30-day rolling limits per plan (all prices HT):
    - Free: **4%**, max €2,500/deposit, €9,500/30 days
    - Start: **3%**, same limits
    - Plus: **2.5%**, same limits
    - Business: **2%**, same limits
  - Over **1,600 partner points** across France; open avg. 8h–20h Mon–Sat, 8h–12h Sun
  - Fees billed at end of billing period (not deducted from the deposit immediately)
- **Conditions/exceptions:** Overseas territories excluded; minimum deposit €100; percentage fee varies by plan
- **⚠️ HIGH financial risk:** Wrong fee percentage per plan or wrong deposit limits directly affect the cost users pay; not mentioning the overseas territory exclusion causes a failed deposit attempt

---

## Article 1180102 — Card not received
- **Topic:** What to do when a client-a physical card hasn't arrived
- **Key facts:** Cards shipped by **La Poste**; standard delivery: **1–2 working weeks**; tracking number accessible in the app (card details section); if still not received after **3 weeks**, contact customer support; virtual card workaround while waiting: Start/Plus/Business automatically get a virtual card after ordering physical; **Free plan can order a virtual card for €2 HT/month** (cancellable at any time)
- **Conditions/exceptions:** Free plan virtual card is charged; 3-week threshold before escalating to support; complete address required for delivery
- **Financial risk:** Low — Free plan users must know the virtual card is not free

---

## Article 1180106 — Activating a client-a card
- **Topic:** Step-by-step process to activate a newly received physical card
- **Key facts:** Activation done in-app or web: Compte Pro > Carte bancaire > Activer ma carte; requires entering the **token printed on the back of the card**; once activated, card is immediately usable for online payments, in-store, and ATM withdrawals; if activation fails, contact support at support@client-a.fr
- **Conditions/exceptions:** Token on the card back is required; activation cannot proceed without it
- **Financial risk:** None

---

## Article 1180646 — Ordering a client-a card
- **Topic:** How to order a client-a physical card and key delivery / renewal details
- **Key facts:** Order via mobile (Plus > Cartes bancaires) or web (Compte pro > Cartes bancaires); requires choosing a PIN and confirming the delivery address; delivery: **1–2 working weeks**; the **delivery address becomes the billing address for online purchases** (used for anti-fraud verification); card renewal is **automatic** — notification sent by email + in-app during the last month before expiry; without address confirmation, card is sent to the account address on file; **maximum 1 physical card per person** regardless of plan; virtual cards available as a supplement
- **Conditions/exceptions:** 1 physical card per person hard limit; delivery address used as billing address for fraud protection
- **Financial risk:** Low — but failing to mention the 1-card-per-person limit or the delivery/billing address link could cause purchasing or onboarding confusion

---

## Article 1180658 — Adjusting the card payment ceiling
- **Topic:** Card payment limits by plan and how to adjust them
- **Key facts:**
  - Payment ceilings (all per plan, all modifiable within the stated max):
    - Free (Mastercard Basic): up to **€5,000 / 7 rolling days; €20,000 / 30 rolling days**
    - Start (Mastercard Basic): up to **€10,000 / 7 rolling days; €40,000 / 30 rolling days**
    - Plus (Mastercard Premium): up to **€15,000 / 7 rolling days; €60,000 / 30 rolling days**
    - Business (Mastercard Premium): up to **€15,000 / 7 rolling days; €60,000 / 30 rolling days**
  - Higher ceiling possible by contacting support (case by case, not guaranteed)
  - **Contactless ceiling is fixed at €50 and cannot be changed** — this is an industry-wide standard, not a client-a-specific restriction
  - No instalment payments via client-a card; PayPal can be used for up to 4 instalments online
- **Conditions/exceptions:** Contactless limit is non-modifiable; extra ceiling increase requires support approval
- **⚠️ Moderate financial risk:** Wrong plan payment limits affect whether a user can complete large transactions; incorrect ceiling info per plan could cause payment failures

---

## Article 1182854 — Using card abroad: commission rates
- **Topic:** Foreign transaction fees for payments and ATM withdrawals by plan and zone
- **Key facts:**
  - **In euro zone — payments:** no fees on any plan
  - **In euro zone — ATM withdrawals:** Free: €1 HT/withdrawal; Start: 2 free then €1 HT; Plus: 4 free then €1 HT; Business: 10 free then €1 HT
  - **Outside euro zone — payments:** Free: **2%**; Start: **1.75%**; Plus: **1.5%**; Business: **1%**
  - **Outside euro zone — ATM withdrawals (all plans):** €1 HT + **1.90% HT** per withdrawal
  - Fees billed at end of billing period, not deducted immediately
- **Conditions/exceptions:** Euro zone vs outside euro zone is the key distinction; outside-euro ATM fee structure is identical across all plans; payment fee percentage varies by plan
- **⚠️ HIGH financial risk:** Wrong foreign payment fee percentages or wrong ATM fee structure directly increase travel and international business costs; a wrong percentage even by 0.25% matters on large transactions

---

## Article 1182858 — ATM withdrawals
- **Topic:** ATM withdrawal limits, card types, and fees per plan
- **Key facts:**
  - **Daily ATM limit: €400 (all plans)**
  - **30-day rolling ATM limit:** Free: **€500**; Start: **€1,500**; Plus/Business: **€2,500**
  - Card types: Free/Start = Mastercard Basic; Plus/Business = Mastercard Premium
  - **Fees in euro zone:** Free: €1 HT/withdrawal; Start: 2 free then €1 HT; Plus: 4 free then €1 HT; Business: 10 free then €1 HT
  - **Fees outside euro zone (all plans):** €1 HT + 1.90% HT per withdrawal
  - Fees billed at end of billing period
- **Conditions/exceptions:** 30-day limit differs significantly by plan (Free's €500/month is a severe constraint); daily €400 cap is universal
- **⚠️ HIGH financial risk:** Wrong 30-day limits (especially the Free plan's €500 cap) can cause serious cash flow issues; wrong per-zone fees result in unexpected charges

---

## Article 1182877 — Contactless payments
- **Topic:** Enabling/disabling contactless, spending limits, and mandatory PIN triggers
- **Key facts:** Contactless toggled on/off per card via app (Plus > Carte bancaire > options) or web (Cartes bancaires > card settings); **contactless ceiling: €50 per transaction** (since March 2021, industry standard — non-modifiable); mandatory PIN is triggered when: **cumulative contactless spend reaches €150**, OR after **5 consecutive contactless payments** — whichever comes first; these thresholds reset after the PIN is entered
- **Conditions/exceptions:** €50 contactless ceiling cannot be changed by client-a or the user; PIN trigger is cumulative (not per transaction); examples: 3 × €50 = PIN required at 4th payment; 5 payments under €20 = PIN required at 6th
- **Financial risk:** Low — but misquoting the ceiling or PIN trigger logic could cause confusion at point of sale

---

## Article 1183030 — Blocking a card (opposition)
- **Topic:** How to block a client-a card reported lost or stolen, and ordering a replacement
- **Key facts:**
  - Block via mobile: Plus > Carte bancaire > Bloquer ma carte bancaire > "J'ai perdu ma carte" / "Ma carte a été volée"
  - Block via web: Cartes bancaires > select card > Bloquer ma carte bancaire
  - **A card blocked as lost or stolen CANNOT be reactivated — the block is permanent and irreversible**
  - Replacement card cost: **€5 HT (Free and Start plans); €10 HT (Plus and Business plans)**
  - Replacement delivered in **1–2 weeks**
  - Interim access: Start/Plus/Business automatically get a virtual card after ordering replacement; Free plan can order a virtual card at **€2 HT/month** (cancellable any time)
- **Conditions/exceptions:** Block is irreversible — must not confuse with temporary freeze; replacement fee differs by plan; Free plan virtual card is charged
- **⚠️ HIGH financial risk:** Quoting wrong replacement fees per plan; telling a user a blocked card can be reactivated is incorrect and could delay them taking the right action

---

## Article 1183053 — Card declined at a merchant
- **Topic:** Troubleshooting a refused card payment
- **Key facts:** Main causes and resolutions: (1) insufficient funds — top up via transfer; (2) wrong PIN — **3 consecutive wrong PINs block the card**, requires support to unblock; tip: change PIN after 2 wrong attempts to avoid block; (3) wrong CVV — **5 wrong CVV entries block the card**, requires support; (4) payment ceiling exceeded — check/adjust limits; (5) merchant guarantee deposits (hotels, petrol stations, toll roads, VTC) may pre-authorise more than the available balance — top up in advance; declined card payments incur **no fees**
- **Conditions/exceptions:** PIN block = 3 attempts (cumulative, not necessarily consecutive in one session); CVV block = 5 attempts; both require support to unblock; guarantee pre-authorisations may temporarily reduce available balance
- **⚠️ Moderate financial risk:** A user who does not know the 3-PIN / 5-CVV thresholds may keep retrying and block their card; a user unaware of guarantee pre-authorisations may not fund their account enough before a hotel stay

---

## Article 1183099 — Making a bank transfer
- **Topic:** How to initiate a SEPA standard or instant transfer from client-a
- **Key facts:** Web: Compte Pro > Paiements > Effectuer un virement > Programmer; mobile: Paiements > Effectuer un virement > Programmer; requires: beneficiary, amount, label; confirmed with secret code; **instant transfer is offered automatically when eligible, at no extra charge** (standard transfer is the default via "Programmer"); transfer attestation (justificatif de virement) downloadable as PDF from the transaction detail — **only available once client-a has validated the transfer**; international transfers handled via a separate article
- **Conditions/exceptions:** Attestation only available post-validation; instant is automatic if eligible, not manually selectable as a first step
- **Financial risk:** None

---

## Article 1183197 — Delay to receive a transfer on client-a
- **Topic:** Expected processing times for incoming transfers and what to do when delayed
- **Key facts:**
  - SEPA instant: **a few seconds** (rarely a few minutes); if sender's bank validated, it will arrive shortly
  - SEPA standard: **2–3 business days** depending on sender's bank
  - International (SWIFT): **4–5 business days**
  - If SEPA standard is overdue: sender should verify they used the correct client-a IBAN and BIC (**SNNNFR22XXX**); if confirmed sent, provide client-a with a transfer attestation containing the unique end2end/EBA reference, RIB, amount, and execution date
  - If international is overdue: sender must have used **both BICs**: client-a BIC `SNNNFR22XXX` and Wise intermediary BIC `TRWIBEB3`
- **Conditions/exceptions:** Business days only (weekends and public holidays excluded); both BICs mandatory for international
- **⚠️ Moderate financial risk:** Incorrect BIC codes (especially missing the Wise intermediary BIC for international) mean the transfer may be lost or returned; providing wrong investigation steps wastes time

---

## Article 1183201 — client-a IBAN not recognised by another bank
- **Topic:** Why some traditional banks reject or flag transfers to client-a accounts
- **Key facts:** Some traditional bank branches have internal security policies that block outgoing transfers to certain institutions (**IBAN discrimination**); client-a is fully licensed by ACPR so the refusal has no legal basis; this is typically a knowledge gap, not a deliberate block; resolution: the sender should contact their account manager at the sending bank — the issue typically resolves through direct dialogue; neobanks are still unfamiliar to some traditional branches
- **Conditions/exceptions:** The issue lies with the sending bank, not client-a; client-a's IBAN is valid
- **Financial risk:** Moderate — a user told their IBAN is invalid may unnecessarily change account providers or miss expected incoming payments

---

## Article 1183407 — Contesting a direct debit (opposition)
- **Topic:** How to oppose/block a SEPA direct debit on a client-a account
- **Key facts:** Opposition requested by emailing **promis_on_repond@client-a.fr**; the service is **free**
- **Conditions/exceptions:** This article is very brief and does not distinguish between CORE (B2C) and B2B mandates — see article 3629915 for the complete rules: CORE has an 8-week contestation deadline; **B2B direct debits cannot be refunded after execution** — only future debits can be blocked; a chatbot relying only on this article would give dangerously incomplete guidance
- **⚠️ HIGH financial risk:** Without the context from article 3629915, a chatbot could incorrectly tell a B2B user they can get a refund, or fail to warn a CORE user about the 8-week deadline

---

## Article 1184066 — Creating an invoice or quote on client-a
- **Topic:** Step-by-step invoice and quote creation in the client-a mobile and web apps
- **Key facts:** Invoices are **unlimited for all plans including Free**; quotes are **unlimited for all plans**; invoice creation: Factures tab (mobile) or Facturation (web) > Créer une facture; required fields: client, title, line items (description, quantity, price, VAT rate); **if not VAT-liable, the default 20% VAT rate must be manually changed to 0%**; discounts entered as negative amounts; invoice numbers must be **sequential without gaps** (French tax law requirement); if migrating from another tool, continue numbering from the last number used there; two send modes: "Envoyer avec client-a" (client-a sends email) or "Envoyer vous-même" (download PDF)
- **Conditions/exceptions:** Sequential numbering is a legal requirement; default VAT is 20% and must be corrected for non-liable entities; quotes: creation process identical but no numbering constraint
- **⚠️ HIGH financial risk:** Leaving the default 20% VAT on a non-liable invoice bills the wrong tax amount to the client; non-sequential invoice numbering is a tax compliance violation

---

## Article 11873457 — Create a delivery note (test template)
- **Topic:** Template/test article about creating delivery notes — migrated Zervant content
- **Key facts:** This article references **Zervant** (not client-a) and describes delivery note creation within Zervant's invoicing interface; it appears to be a test template or legacy content imported during a platform migration and is **not representative of current client-a functionality**
- **Conditions/exceptions:** Content is not client-a-native; UI paths described do not match client-a's interface
- **Financial risk:** None — but the article should not be surfaced as authoritative client-a guidance; flag as stale migrated content

---

## Article 11875356 — Draft
- **Topic:** Empty draft article — no content present
- **Key facts:** No content
- **Financial risk:** None — should not be indexed or surfaced to users

---

## Article 11876683 — Steps for company creation with client-a
- **Topic:** End-to-end timeline and process for creating a company (SASU-focused) through client-a
- **Key facts:**
  1. Document submission via online form → **verified within 48h** (business days)
  2. Capital deposit: notary partner's IBAN sent by email; **2–3 business days** for funds to reach notary
  3. Statutes drafted and sent by client-a → signed electronically via **Yousign**
  4. Dossier filed with the greffe (tribunal de commerce): **3–7 business days** for commercial or liberal activities; **up to 1 month** for artisanal activities (due to Répertoire des Métiers inscription)
  5. KBIS + SIRET issued → client-a pro account opened
  6. Capital released to client-a account: **2–3 business days** after immatriculation
- **Conditions/exceptions:** Artisanal activities face a significantly longer immatriculation window (up to 1 month); timelines assume documents pass validation first time
- **⚠️ Moderate financial risk:** If a chatbot quotes 3–7 days for an artisanal activity, the user may have unmet expectations about when their capital and account will be available, affecting operational planning

---

## Article 11883623 — Untitled public article
- **Topic:** Empty article — no content present
- **Key facts:** No content
- **Financial risk:** None — should not be indexed or surfaced to users

---

## Article 11884043 — Untitled public article
- **Topic:** Empty article — no content present
- **Key facts:** No content
- **Financial risk:** None — should not be indexed or surfaced to users

---

## Article 11886319 — Documents required to create a SASU
- **Topic:** Complete list of documents required for SASU creation through client-a
- **Key facts:**
  1. **Valid ID** (colour, legible, not cropped): European CNI (recto/verso), European passport (double page with photo and signature), or valid French titre de séjour for non-EU nationals
  2. **Professional address proof** less than 3 months old: utility bills (electricity, gas, water, internet), tax notice, commercial lease, or domiciliation contract; **handwritten rent receipts and screenshots are not accepted**
  3. **Décorpus-ation de non-condamnation** (non-conviction declaration): template provided by client-a
  4. **Pouvoir du mandataire** (power of attorney): template provided by client-a; authorises client-a to file the dossier and receive official documents (KBIS, SIRET)
  5. If capital **≥ €5,000**: proof of origin of funds required
  6. If **regulated activity**: may require professional card, diploma, or experience attestation
  7. **Capital deposit**: wire must come from a personal account in the shareholder's name only
  8. Statutes signed electronically via **Yousign** — no paper documents needed
  - If home address used as siège social: a domiciliation attestation is required (client-a provides the form)
- **Conditions/exceptions:** Address proof must be under 3 months; handwritten/screenshot documents rejected; hosted-address scenario requires extra docs; all signing is electronic
- **Financial risk:** None — but incorrect document requirements cause onboarding failure and delay capital access

---

## Article 11886479 — Difference between activité exercée and objet social
- **Topic:** Legal distinction between a company's declared activity (activité) and its statutory purpose clause (objet social) for SASU creation
- **Key facts:** **Objet social** = formal legal clause in the statutes; defines the scope of what the company is authorised to do; can be broad; lives in the statutes; **Activité exercée** = the concrete day-to-day activity; declared at immatriculation; drives the APE/NAF code assignment; determines the applicable social/fiscal regime and supervisory body (URSSAF, CMA, etc.); **inconsistency between the two can cause**: blocked immatriculation (activity not covered by the objet social), wrong APE code (impacts cotisation rates and collective agreement), insurance refusal, legal liability for directors; client-a provides objet social templates and files the activité declaration automatically
- **Conditions/exceptions:** The activité must be covered by the objet social; a narrow objet social can restrict future activities; changing the objet social after incorporation requires a statutory amendment
- **⚠️ Moderate financial risk:** A wrong APE code affects social cotisation rates and applicable collective agreement — incorrect guidance here has ongoing financial consequences

---

## Article 11886636 — Cancel or edit a bill (test template)
- **Topic:** Template/test article about cancelling or editing purchase invoices — migrated Zervant content
- **Key facts:** This article references **Zervant** product and describes: cancelling a bill (creates an offsetting voucher automatically, sets status to "Cancelled"), editing an approved bill (date, description, category, VAT rate, price, attachments via "Update approved bill"), and generating credit notes; accessed via Expenses > Bills; this appears to be a **test template or legacy content from a Zervant migration** and is not representative of current client-a Facture functionality
- **Conditions/exceptions:** Content references Zervant — not current client-a; UI paths may not match client-a Facture
- **Financial risk:** None — but should not be surfaced as authoritative client-a guidance; flag as stale migrated content

---

## Article 11887061 — SASU registration via the Guichet Unique
- **Topic:** How client-a handles SASU immatriculation through the INPI's Guichet Unique, with timelines per activity type
- **Key facts:** Since **1 January 2023** all company registrations in France must go through the **Guichet Unique** (managed by INPI); client-a files the full dossier on the user's behalf once documents are validated and statutes signed; the Guichet Unique routes to the appropriate body:
  - **Commercial or liberal activity** → Greffe du tribunal de commerce / URSSAF: **3–7 business days**, result = KBIS
  - **Artisanal activity** → Chambre de Métiers et de l'Artisanat (CMA): **~1 month**, result = KBIS + RNE extract
  - User notified by email at each stage; client-a handles all back-and-forth with the administration
- **Conditions/exceptions:** Artisanal activities take up to 1 month vs. 3–7 days for commercial/liberal; if the administration requests additional documents, client-a handles the exchange on the user's behalf
- **⚠️ Moderate financial risk:** Wrong processing timelines affect capital planning — especially the artisanal 1-month delay; funds deposited for capital remain locked until the KBIS is issued

---

## Article 11892207 — Can I customise my SASU statutes?
- **Topic:** Which parts of client-a-generated SASU statutes are customisable and which are fixed
- **Key facts:** client-a's statutes are drafted by legal experts and pre-validated for immatriculation; **customisable elements**: objet social, accounting year-end date (can differ from 31 December), capital amount and type (fixed or variable), number of shares, registered address (siège social); **non-customisable**: director remuneration clauses, decision-making rules, share transfer rules, dissolution conditions; for non-standard needs (capital en nature, bespoke clauses): use a lawyer/accountant for statute drafting and client-a only for the capital deposit; statutes can be amended after incorporation via a qualified provider
- **Conditions/exceptions:** If custom statutes are needed, client-a acts only as capital deposit and account-opening partner; statute amendments post-incorporation require a third party
- **Financial risk:** Low — but telling a user they can modify non-editable clauses would lead to failed expectations and delays

---

## Article 11892264 — Invalid SASU creation dossier — what to do?
- **Topic:** Common reasons a SASU creation dossier is rejected and how to resolve each
- **Key facts:**
  - **Address mismatch:** siège social in statutes must exactly match the address proof; consumption/delivery address takes precedence over postal address if different; fix via creation.societes@client-a.fr
  - **Objet social too vague:** must clearly describe the activity for correct APE code attribution; using custom phrasing instead of client-a's suggested categories delays the dossier
  - **Missing supplementary documents:** artisanal activity requires a diploma or 3+ years experience attestation (CMA requirement); regulated activities need additional professional credentials
  - **ID quality failure:** document is blurry, cropped, photocopied, scanned, or a screen capture — must photograph the physical original; all 4 corners must be visible
  - **Unsupported ID type:** driving licences and non-European IDs without VISA/titre de séjour are not accepted
  - **Outdated address proof:** must be **under 3 months** old
  - **Wrong address proof type:** commercial lease or domiciliation contract required for non-home siège social; home address accepts utility bills or tax notices; handwritten rent receipts not accepted
- **Conditions/exceptions:** Consumption address trumps postal address (greffe requirement); each rejection round extends the immatriculation delay and keeps capital locked
- **Financial risk:** None direct — but each invalidation cycle delays KBIS issuance and prolongs capital lockup, with real financial cost

---

## Article 1195281 — Customising invoices in client-a
- **Topic:** Invoice personalisation options — logo and default billing parameters
- **Key facts:** Logo upload available on **all plans**; done via **web only** (not mobile): Facturation > Informations de facturation; default billing parameters (pre-fillable for all future invoices): email, custom legal mentions, quote validity period, invoice payment deadline, late payment penalty rate; **default VAT rate is 20%**; for non-VAT-liable users, set 0% — client-a then automatically adds the mandatory "TVA non applicable, art. 293 B du CGI" mention; all settings accessible from Facturation > Paramètres de facturation (web only)
- **Conditions/exceptions:** Logo upload is desktop-only; default 20% VAT must be manually overridden for non-liable users; changes apply to future invoices only
- **⚠️ Moderate financial risk:** If a non-liable user leaves the default 20% VAT in their billing settings, every invoice they create will incorrectly charge VAT — a systematic error affecting all clients

---

## Article 1195292 — Sending an invoice from client-a
- **Topic:** Two methods for sending an invoice to a client from client-a Pro
- **Key facts:** Method 1 — "Envoyer avec client-a": client-a sends the email to the client directly; web: click invoice > "Envoyer à [client]"; mobile: click invoice > "Envoyer avec client-a"; option to BCC yourself and send a test email first; **email is sent under client-a's name/address — replies from the client go to the user's client-a account email**; Method 2 — "Télécharger en PDF": download the PDF to send manually; or copy a share link so the client can view/pay online by card (if card payment is enabled on the invoice)
- **Conditions/exceptions:** Reminder email replies route back to the user's client-a email, not client-a support
- **Financial risk:** None

---

## Article 1195312 — Deleting or cancelling an invoice
- **Topic:** Rules governing invoice deletion and cancellation in client-a Pro
- **Key facts:** **Unsent (draft) invoices**: can be freely deleted — irreversible, but no accounting obligation since the invoice was never emitted; **Emitted invoices** (status "Envoyée", "En retard", or any downloaded PDF): **cannot be deleted** — must be cancelled via "Changer le statut > Cette facture a été refusée"; cancellation is also **irreversible**; cancelled invoices remain visible under "Voir les factures annulées"; a **downloaded PDF counts as an emitted invoice** even if never sent to the client; basis in French accounting law: financial records must be inalienable (anti-VAT fraud law)
- **Conditions/exceptions:** Downloaded PDF = emitted invoice legally; cancellation and deletion are both irreversible; distinction between the two depends entirely on the invoice's emission status
- **⚠️ HIGH financial risk:** Telling a user they can delete an emitted invoice violates French accounting and anti-VAT fraud law; the chatbot must always direct users to the cancellation workflow for emitted invoices

---

## Article 1195328 — Customising VAT per invoice item
- **Topic:** How to set different VAT rates per line item on a single invoice
- **Key facts:** VAT rate is configurable **per item** (not just per invoice); a single invoice can carry multiple VAT rates simultaneously (e.g., an artist-author combining an intellectual property cession at a reduced rate with a service at standard rate); change per item by tapping "TVA" on the item and entering the desired rate; **micro-entrepreneurs are NOT subject to VAT by default** unless they have exceeded the CA threshold or opted out of the franchise en base
- **Conditions/exceptions:** Micro-entrepreneurs must not apply a non-zero VAT rate unless they have crossed the threshold or opted in; setting non-zero VAT for a non-liable entity creates a false tax obligation
- **⚠️ HIGH financial risk:** Applying a non-zero VAT rate to a non-liable micro-entrepreneur invoice over-bills clients and creates a tax declaration problem; failing to apply VAT when required is an equally serious compliance failure

---

## Article 1195405 — Which VAT rate to apply on invoices
- **Topic:** VAT rates by activity type and taxpayer status, with rules for international invoicing
- **Key facts:** **Micro-entrepreneurs** (auto-entrepreneurs): in the vast majority of cases **not subject to VAT**; if not liable, the mention "TVA non applicable, art. 293 B du CGI" is mandatory and added automatically by client-a when rate is 0%; once CA threshold is exceeded, VAT must be charged; main rates for VAT-liable entities:
  - **20%** — services (prestations de services)
  - **10%** — renovation/maintenance works (BTP)
  - **5.5%** — original artworks sold by their author, food products, books
  - Special cases apply in DOM (overseas territories)
  - For **international invoices**: must add the TVA intracommunautaire number (requested from the SIE at the centre des impôts)
- **Conditions/exceptions:** DOM territories have their own rules; the intracommunautaire number must be obtained before invoicing foreign clients; threshold-crossing triggers VAT liability
- **⚠️ VERY HIGH financial risk:** Applying the wrong rate causes incorrect client billing and erroneous tax declarations; applying 20% to a non-liable micro-entrepreneur is a serious error; omitting the mandatory "TVA non applicable" mention when rate is 0% is also a compliance violation

---

## Article 1196863 — Does client-a replace an accountant?
- **Topic:** Scope of client-a's accounting tools versus the role of a chartered accountant
- **Key facts:** **client-a does not replace an accountant**; client-a cannot produce a compte de résultat (income statement) or file a liasse fiscale with the SIE; client-a facilitates accountant collaboration via: a dedicated accountant access feature (**not available on Free plan**) and automated recurring accounting exports; client-a also provides a directory of partner accounting firms
- **Conditions/exceptions:** Accountant access unavailable on Free plan; file submission to tax authorities is entirely outside client-a's scope
- **Financial risk:** None — but telling a user client-a replaces their accountant could leave them without mandatory tax filings, leading to penalties

---

## Article 1200519 — Micro-enterprise revenue thresholds
- **Topic:** Revenue ceilings and VAT franchise thresholds for the micro-enterprise regime
- **Key facts (2022 figures — ⚠️ updated annually by the State):**
  - Services (commercial/artisanal BIC or BNC): CA threshold **€72,600**; VAT franchise threshold **€34,400**
  - Purchase/resale or accommodation (BIC): CA threshold **€176,200**; VAT franchise threshold **€85,800**
  - If threshold exceeded for **2 consecutive years**: exits micro-enterprise regime on **1 January of the 3rd year**
  - Consequences of exit: becomes VAT-liable, new accounting obligations, changed tax/social regime (BNC → décorpus-ation contrôlée; BIC → régime réel simplifié)
  - Thresholds prorated for mid-year start: (days since registration / days in year) × threshold
  - ACRE benefit also ends if micro-enterprise regime is lost
  - client-a sends a notification when the user is approaching the threshold
- **Conditions/exceptions:** Thresholds are **reviewed and updated each year** — the figures above are from 2022 and may be outdated; 2 consecutive years of excess required before losing the regime; proratisation applies for partial years
- **⚠️ VERY HIGH financial risk:** Citing outdated thresholds could cause a user to unknowingly become VAT-liable or lose their regime without preparation; the chatbot must note that current figures should be verified on the official government source

---

## Article 1200572 — What to do when a client doesn't pay
- **Topic:** Automated payment reminders and debt recovery escalation
- **Key facts:** client-a alerts users when an invoice is overdue and offers automated email reminders; reminders can be enabled on existing invoices (via invoice detail > "..." > Gérer les emails de relance) or during invoice creation; **minimum late payment penalty rate for the reminder feature: 14.76%**; the late payment rate and reminder frequency are configurable; reminder emails are sent under client-a's name/address but **client replies are routed to the user's client-a email**; if reminders fail: escalate to specialist debt recovery firms (examples: Legalstart, d'Ormane, Recogest); reminders stop automatically when the invoice is marked as paid
- **Conditions/exceptions:** Minimum rate of 14.76% must be respected; reminder emails appear to come from client-a
- **⚠️ Moderate financial risk:** Setting the penalty rate below the legal minimum (14.76%) creates a non-compliant invoice; the chatbot must not quote a lower rate

---

## Article 12067200 — Processing a received e-invoice
- **Topic:** How to review, approve, reject, and pay e-invoices received via client-a
- **Key facts:** Requires e-invoice reception to be activated first; access: web via Comptabilité > E-factures fournisseurs, mobile via Plus > Comptabilité > E-factures fournisseurs; invoice statuses: "À traiter" (received, unprocessed), "À payer" (approved, pending payment), "Payée" (settled), "Refusée" (rejected with optional reason, supplier is notified); payment options once approved: pay directly via SEPA transfer in-app ("Payer la facture"), or mark as already paid; **all e-invoices stored for 10 years** (regulatory requirement); **critical exception: refusing an e-invoice does NOT block payment if linked to a standing order, automatic transfer, or pre-authorised direct debit** — must contact the supplier directly in such cases
- **Conditions/exceptions:** Refusal does not cancel pre-authorised payments; 10-year retention is mandatory by law
- **⚠️ Moderate financial risk:** A user who believes refusing an e-invoice automatically stops a pre-authorised payment will still be charged; must be directed to contact the supplier directly for disputes

---

## Article 12139786 — Untitled public article
- **Topic:** Empty article — no content present
- **Key facts:** No content
- **Financial risk:** None — should not be indexed or surfaced to users

---

## Article 1227397 — Standard tax regime for micro-entrepreneurs (no versement libératoire)
- **Topic:** How income tax works for micro-entrepreneurs under the standard (non-liberatory) regime
- **Key facts:** Without versement libératoire, the standard regime applies: commercial/artisanal activity = **micro-BIC**; liberal activity = **micro-BNC**; must file form **2042-C Pro** as a supplement to the annual income tax return; must declare **gross CA (BIC) or recettes (BNC) — do not apply the abattement before declaring**; the tax authority applies the abattement automatically: **71%** for purchase/resale or accommodation; **50%** for other BIC activities; **34%** for BNC (liberal); minimum abattement: **€305**; the resulting taxable profit is added to the total household income for income tax calculation; only those under the micro social/fiscal regime can use versement libératoire
- **Conditions/exceptions:** Abattement is applied by the administration — users must declare gross revenue; the minimum €305 abattement applies even if the calculated abattement is lower
- **⚠️ VERY HIGH financial risk:** Pre-applying the abattement before declaring (e.g., declaring CA net of 50% instead of gross CA) misrepresents taxable income and leads to tax adjustment + penalties; using the wrong rate (e.g., 34% instead of 50% for BIC services) has the same effect

---

## Article 12276485 — Titre (formatting template)
- **Topic:** Test/template article with placeholder formatting content only — no real user-facing information
- **Key facts:** Contains only structural placeholders: Header 1, Header 2, bullet lists, numbered lists, callout block, button banner, and a table marker; this is a formatting reference article, not help content
- **Financial risk:** None — should not be indexed or surfaced to users

---

## Article 13378031 — Identifying and Fixing Bank Reconciliation Errors
- **Topic:** Bank reconciliation error detection and correction in client-a Facture
- **Key facts:** For compliant accounting, the bank account balance in client-a Facture must match the actual bank balance. The three most common errors are: (1) double entry — a bank line recorded twice; (2) missing entry — a bank line not recorded; (3) missing opening balance — account used without an opening balance. Errors are diagnosed via Rapports > Exports > Soldes des comptes.
- **Conditions/exceptions:** Article does not explain how to correct errors once identified — it only describes how to find them.
- **Financial risk:** Moderate — incorrect reconciliation leads to non-compliant accounting and may cause errors in VAT declarations or financial statements; however the article itself contains no figures or thresholds where a wrong answer causes direct harm.

---

## Article 13377516 — Exporting Your Data (client-a Facture)
- **Topic:** Data export functionality in client-a Facture
- **Key facts:** Export path: Rapports > Exports; options include Transactions et documents liés (ZIP with one folder per accounting entry, PDF + attachments), client/supplier account statements, invoices. Exports are available at any time, unlimited. Exports do not modify accounting documents. Each export is independent and can be archived outside client-a Facture.
- **Conditions/exceptions:** For all clients/suppliers: Rapports > Export de données; for a single contact: Facturation > Client·es > Plus > Télécharger le relevé (formats: PDF, HTML, CSV, Excel). Note: 13377607 is a near-duplicate covering only the client/supplier sub-path.
- **Financial risk:** None — procedural export instructions with no financial figures.

---

## Article 13377607 — Exporting Client/Supplier Data (client-a Facture)
- **Topic:** Exporting client and supplier account statements from client-a Facture
- **Key facts:** Two paths: all clients/suppliers via Rapports > Export de données (download Relevé de compte client / fournisseur); individual contact via Facturation > Client·es or Dépenses > Fournisseurs > Plus > Télécharger le relevé; export formats: PDF, HTML, CSV, Excel.
- **Conditions/exceptions:** Near-duplicate of 13377516 but scoped only to client/supplier data; no transactions/invoices export covered here.
- **Financial risk:** None — procedural only.

---

## Article 13377914 — Disconnecting a Bank Account (client-a Facture)
- **Topic:** How to disconnect a bank account from client-a Facture and update payment methods
- **Key facts:** Path: Paramètres > Mon entreprise > Comptabilité > Modifier le plan comptable; select account > Corriger > uncheck "Compte bancaire" and "Autoriser les paiements" > Enregistrer. After disconnecting, must update payment methods on invoices: Paramètres > Facturation > Modes de paiement — delete old default, create new one with new account details. New invoices will automatically use the new account.
- **Conditions/exceptions:** Failure to update payment methods after disconnecting means clients may attempt to pay the old account, causing missed or misdirected payments.
- **Financial risk:** Moderate — if the chatbot does not mention the mandatory payment method update step, clients could send payments to a closed/disconnected account.

---

## Article 13377675 — Modifying VAT Periodicity (client-a Facture)
- **Topic:** How to change the VAT reporting frequency in client-a Facture
- **Key facts:** Path: Paramètres > Mon entreprise > Comptabilité > modify VAT periodicity > Enregistrer. Article contains only the navigation steps with no explanation of available periods or consequences.
- **Conditions/exceptions:** No details on what periodicity options exist (monthly, quarterly, annual) or tax authority notification requirements.
- **Financial risk:** Moderate — changing VAT periodicity incorrectly relative to tax authority registration can lead to mismatched declarations and late-payment penalties; however the article itself is too thin to create a wrong-answer risk.

---

## Article 13378638 — Modifying or Cancelling a Purchase Invoice (client-a Facture)
- **Topic:** How to edit, cancel, or add a credit note for a purchase (supplier) invoice in client-a Facture
- **Key facts:** Modify: Dépenses > Factures d'achats > edit fields > Mettre à jour (if not finalized) or Approuver. Cancel: invoice disappears from the list. Add credit note (avoir): Ajouter un avoir > fill fields > Approuver.
- **Conditions/exceptions:** These are *received* purchase invoices (from suppliers), not emitted client invoices. The anti-VAT fraud law restrictions (no deletion of emitted invoices) do not apply here — purchase invoices are inbound documents. The cancellation simply removes the record.
- **Financial risk:** Low — purchase invoice management; no legal prohibition on cancelling received invoices.

---

## Article 13390371 — Modifying or Deleting a Client Invoice (client-a Facture)
- **Topic:** How to correct an already-created or already-sent client invoice in client-a Facture
- **Key facts:** Two distinct workflows: (1) Invoice not yet sent — cancel it via 3-dots menu > "Annuler la facture" > "Rendre la facture nulle"; (2) Invoice already sent — cancel via 3-dots menu > "Annuler la facture" > "Créer un avoir" (credit note). The avoir method "guarantees compliant accounting."
- **Conditions/exceptions:** The correct path depends entirely on whether the invoice has been sent. Using "Rendre la facture nulle" on a sent invoice would violate the anti-VAT fraud law (emitted invoices cannot be deleted — only cancelled via avoir). Cross-reference with article 1195312 which covers the same rule in the context of downloaded PDFs also counting as emitted.
- **Financial risk:** HIGH — a chatbot telling a user to delete a sent invoice rather than create an avoir exposes them to violation of French anti-VAT fraud law (loi anti-fraude TVA 2018). Emitted invoices must be traceable; deletion is illegal.

---

## Article 13378947 — Types of Invoice Lines and Their Use
- **Topic:** Placeholder/empty article — no content
- **Key facts:** Article has no body content (empty draft). Title suggests it would cover invoice line types in client-a Facture.
- **Financial risk:** None — should not be indexed or surfaced to users.

---

## Article 13377564 — Untitled Public Article
- **Topic:** Empty/untitled draft article
- **Key facts:** No content, no URL, no title.
- **Financial risk:** None — should not be indexed or surfaced to users.

---

## Article 12320536 — Everything About Verification of Payee (VoP)
- **Topic:** EU Verification of Payee (VoP) regulation for SEPA transfers, mandatory from 9 October 2025
- **Key facts:** Regulation basis: EU Regulation 2024/886. VoP automatically compares the beneficiary name entered against the name registered with the recipient's bank. Applies when: adding a new beneficiary, modifying an existing one, making a SEPA transfer, making a grouped transfer. Four possible results: ✅ Full match (names match exactly); 🔶 Partial match (typo/spelling — bank's known name is suggested); ❌ No match (no correspondence between name and IBAN); ⚠️ Verification impossible (technical issue, closed account, connectivity problem). In case of no match or impossible, user may proceed, modify the beneficiary name, or cancel. **User bears full liability if they validate a transfer despite a non-match.** client-a allows a custom label to be added to a beneficiary to help identify them independently of the legal name.
- **Conditions/exceptions:** VoP applies only to SEPA transfers to external current accounts. Internal transfers (e.g., to client-a sub-accounts) are NOT subject to VoP. For sole traders, the name entered must be first and last name; for legal entities, the exact company name (raison sociale).
- **Financial risk:** HIGH — if a chatbot incorrectly describes which VoP result types block a transfer, or fails to communicate that the user is liable for losses when proceeding despite a non-match, the user could fall victim to fraud (fake IBAN/identity spoofing) and have no recourse.

---

## Article 13051581 — "Your First Public Article (client-a Facture)"
- **Topic:** Intercom platform template article — not client-a content
- **Key facts:** Contains generic Intercom Help Center onboarding text: how to use articles, collections, Fin AI Agent, etc. This is the default template article auto-created by Intercom when a new Help Center workspace is set up.
- **Financial risk:** None — should not be indexed or surfaced to users (identical issue to article 11873457 seen in Batch 4).

---

## Article 12683808 — Managing Instant Transfer Limits
- **Topic:** Adjusting SEPA instant transfer (virement instantané) limits in client-a
- **Key facts:** Managed via Paiement > Gestion des plafonds virements SEPA (mobile app only). Default limits: 2,000 € per transfer, 4,000 € per day. With a configured "téléphone principal": up to 10,000 € per transfer, 20,000 € per day. Limits can be increased or decreased. Configuring téléphone principal: Paramètres > Sécurité > Téléphone principal.
- **Conditions/exceptions:** For business/multi-user accounts: **all users must have configured their téléphone principal** for the higher limits to be available. This is a critical edge case — a single unconfigured user blocks the higher limits for the entire account.
- **Financial risk:** Moderate — a user expecting to send 8,000 € instantly (within the "up to 10,000 €" limit) may be blocked if not all account users have configured their téléphone principal; wrong chatbot answer could cause failed time-sensitive payments.

---

## Article 12672874 — Sanctions Related to E-Invoicing: What You Need to Know
- **Topic:** Financial penalties for non-compliance with the French e-invoicing reform
- **Key facts:** Reform enters into force progressively from September 2026. Two categories of sanction: (1) 15 € per invoice not emitted in compliant electronic format, capped at 15,000 € per year; (2) 250 € per missing or incorrect data transmission, capped at 15,000 € per year. **First infraction is generally tolerated** if corrected quickly; sanctions apply from the second infraction onwards. Compliance options include choosing an accredited platform (PDP) compatible with invoicing tools.
- **Conditions/exceptions:** First-offence tolerance is conditional on rapid regularisation — not a guaranteed grace period. client-a includes e-invoicing reception in all plans for free from the start.
- **Financial risk:** VERY HIGH — a chatbot giving wrong penalty figures, wrong timelines, or incorrectly stating that the first infraction is always forgiven could lead users to underestimate compliance urgency and face compounding fines.

---

## Article 12548842 — Are You Affected by the E-Invoicing Reform?
- **Topic:** Scope of the French e-invoicing reform — which companies are affected and notable edge cases
- **Key facts:** The reform affects **all companies in France**. The article redirects to a personalised questionnaire for specific obligations and deadlines. Notable special-case entities that may have different obligations: associations, companies based in DOM/COM (overseas territories), furnished rental companies (loueurs en meublé), sociétés civiles (including SCI), copropriété syndics.
- **Conditions/exceptions:** The special cases listed may have distinct obligations or exemptions not detailed in this article. Users in these categories need to check their specific situation via the questionnaire.
- **Financial risk:** HIGH — if a chatbot incorrectly tells an association, SCI, or DOM/COM company that they are exempt from e-invoicing obligations, they may miss compliance deadlines and incur the penalties detailed in article 12672874.

---

## Article 13390593 — Customising Your Invoicing Email (client-a Facture)
- **Topic:** Customising email content and sender address when sending invoices from client-a Facture
- **Key facts:** Subject and body of the invoice email can be edited via the editor (Terminer > Envoyer par e-mail). Sender address cannot be changed — all emails come from noreply@documents.client-a.me. To send from your own address, download the invoice as PDF and attach it to a personal email. Client replies are automatically redirected to the contact email registered in the client-a account.
- **Conditions/exceptions:** No option to configure a custom sender domain within client-a Facture.
- **Financial risk:** None — procedural customisation; no figures or compliance rules involved.

---

## Article 13390686 — Customising Invoice Language and Currency (client-a Facture)
- **Topic:** Setting default invoice language and billing currency in client-a Facture
- **Key facts:** Both language and currency are configured at Paramètres > Mon entreprise > Facture. Language can be overridden per individual invoice. Only one currency per invoice is supported. **client-a Facture does not automatically convert exchange rates** — the user must manage FX manually.
- **Conditions/exceptions:** Note: despite the article title "Personnaliser votre email de facturation", the content covers language and currency settings, not email customisation (13390593 covers email). The title appears mislabelled.
- **Financial risk:** Low — if a user bills in a foreign currency without accounting for exchange rates, invoiced amounts may not match received funds; however the article clearly states no auto-conversion.

---

## Article 13399551 — Untitled Public Article
- **Topic:** Empty/untitled draft article
- **Key facts:** No content, no URL, no title.
- **Financial risk:** None — should not be indexed or surfaced to users.

---

## Article 13401371 — Download the client-a Facture App
- **Topic:** Empty/untitled draft article
- **Key facts:** No content, no URL. Title suggests it would cover downloading the client-a Facture mobile application.
- **Financial risk:** None — should not be indexed or surfaced to users.

---

## Article 13401639 — Are You Affected by the E-Invoicing Reform?
- **Topic:** Scope of the French e-invoicing reform — questionnaire redirect
- **Key facts:** States that the reform affects all companies in France and directs users to a personalised questionnaire to determine their specific obligations and deadlines. Near-duplicate of article 12548842 but without the special-case list (associations, DOM/COM, loueurs en meublé, SCI, syndics).
- **Conditions/exceptions:** Less complete than 12548842 — the special-cases detail is absent here.
- **Financial risk:** HIGH — same risk as 12548842: blanket "all companies" without nuance may mislead edge-case entities. Cross-reference with 12548842 and 12672874 for full context.

---

## Article 13401652 — Untitled Public Article
- **Topic:** Empty/untitled draft article
- **Key facts:** No content, no URL.
- **Financial risk:** None — should not be indexed or surfaced to users.

---

## Article 13402315 — Sending Electronic Invoices (client-a Facture)
- **Topic:** How to create and send an e-invoice (e-facture) from client-a Facture
- **Key facts:** Required fields on an e-invoice: sender's SIRET or EU VAT number; sender's full postal address (postcode + city); client name/legal name; client's full postal address; **client's electronic invoicing address** (format: TVA, GLN, DUNS, OVT, etc.); at least one invoice line with amount > 0 €; payment conditions; IBAN, bank name, BIC/SWIFT. Path: Facturation > Factures clients > Créer une facture > fill fields > Terminer > Envoyer comme e-facture. Transmission is via Basware to the client's e-invoice operator. Delivery statuses: ✅ "E-facture livrée avec succès au destinataire"; ❌ "Livraison e-facture échouée à cause d'un contenu invalide" or "E-facture rejetée par le destinataire".
- **Conditions/exceptions:** The client's electronic invoicing address is mandatory — if absent or invalid, the e-invoice cannot be delivered. See article 13670580 for a full list of rejection reasons.
- **Financial risk:** HIGH — if a chatbot omits the client e-invoice address as a required field, or doesn't tell users to check delivery status, invoices can fail silently, delaying or preventing payment.

---

## Article 14111323 — Test
- **Topic:** Empty test article
- **Key facts:** No content, no URL. Title is "Test".
- **Financial risk:** None — should not be indexed or surfaced to users.

---

## Article 13859730 — Creating a Credit Note (Avoir) in client-a Facture
- **Topic:** How to create a credit note (avoir) to cancel or adjust an emitted client invoice
- **Key facts:** An avoir cancels or reduces the amount owed by a client. Path: Facturation > Factures client·es > open invoice > 3-dot menu > Annuler la facture > Oui (if already sent) > Créer un avoir > Terminer > Envoyer. **Partial avers are currently not supported** — only full-cancellation credit notes can be created on client-a Facture.
- **Conditions/exceptions:** The "Créer un avoir" option only appears if the invoice was already sent (Oui confirmation step). For unsent invoices, use "Rendre la facture nulle" instead (see article 13390371). No partial avoir = if only part of an invoice needs correcting, a workaround is required (reissue a new corrected invoice after full cancellation).
- **Financial risk:** HIGH — (1) if a chatbot implies partial credit notes are possible when they are not, users may expect a feature that doesn't exist; (2) the avoir workflow is legally mandatory for sent invoices (anti-VAT fraud law) — failing to guide users to it risks illegal invoice deletion.

---

## Article 13670580 — Main Reasons for E-Invoice Delivery Failure
- **Topic:** Why an e-invoice sent from client-a Facture may be rejected or fail to deliver
- **Key facts:** Five rejection causes: (1) incorrect or invalid client e-invoice address (accepted formats: TVA, GLN, DUNS, OVT, etc.); (2) character limits exceeded — company name max 80 characters, message field max 1024 characters; (3) missing required client fields (e.g. purchase order number, buyer reference required by the client's system); (4) routing problems between operators (format/rule misalignment between PDPs); (5) unsupported attachment format — only PDF attachments are accepted. Diagnosis path: Facturation > Factures clients > open invoice > Historique tab.
- **Conditions/exceptions:** Some clients require additional fields (order number, buyer reference) that are not standard on all invoices — this is buyer-dependent.
- **Financial risk:** Moderate — a rejected e-invoice means the client never received it, which delays payment. If users don't check delivery status or don't know how to fix rejections, invoices may go unpaid indefinitely.

---

## Article 13653871 — Untitled Public Article
- **Topic:** Empty/untitled draft article
- **Key facts:** No content, no URL.
- **Financial risk:** None — should not be indexed or surfaced to users.

---

## Article 13557767 — What Is client-a Facture?
- **Topic:** Overview and positioning of client-a Facture vs client-a
- **Key facts:** client-a Facture = standalone online invoicing and quoting tool, aimed at professionals who do not need a bank account. client-a = full banking + invoicing suite for freelancers and businesses. client-a Facture can be used alone or alongside a client-a pro account. The two products have separate Help Centers.
- **Conditions/exceptions:** Users asking about invoicing who have a client-a pro account already have the invoicing module included — client-a Facture as a standalone product is for non-banking users.
- **Financial risk:** None — informational/positioning article.

---

## Article 13544336 — Untitled Public Article
- **Topic:** Empty/untitled draft article
- **Key facts:** No content, no URL.
- **Financial risk:** None — should not be indexed or surfaced to users.

---

## Article 1369683 — Administrative Steps After Creating a Micro-Enterprise
- **Topic:** Post-SIRET administrative checklist for new micro-entrepreneurs
- **Key facts:** Steps required after receiving a SIRET: (1) Register on the Urssaf auto-entrepreneur site — **must wait 30 to 90 days after SIRET issuance** before the account can be activated; (2) **File initial CFE (Cotisation Foncière des Entreprises) declaration with the tax office before 31 December of the creation year** — CFE exemptions exist (age, income, geography, first year, etc.); (3) Create a professional account on impôts.gouv.fr for income tax declarations; (4) Request an EU VAT number if billing foreign clients or if VAT-liable; (5) Apply for ACRE (social charge reduction for new entrepreneurs) at Urssaf; (6) Request versement libératoire (simplified income tax prepayment) at Urssaf. Additional steps may apply depending on activity type.
- **Conditions/exceptions:** ACRE eligibility conditions are not detailed here — the article only mentions the option. CFE exemption eligibility can be checked via an inline questionnaire. 30-90 day Urssaf activation delay is a hard technical constraint, not a choice.
- **Financial risk:** HIGH — (1) missing the CFE declaration by 31 December of the creation year exposes the entrepreneur to back-taxes; (2) failing to apply for ACRE within the eligible period means losing the social charge reduction (cannot be claimed retroactively); (3) forgetting to request EU VAT number when billing foreign clients leads to billing non-compliance.

---

## Article 1410893 — Updating Your Phone Number
- **Topic:** How to change the phone number associated with a client-a account
- **Key facts:** Phone number is treated as sensitive security information — it cannot be changed via self-service settings. Users must contact client-a via: in-app secure messaging (if still logged in), the login page, or support@client-a.fr. client-a's team verifies identity before processing the change.
- **Conditions/exceptions:** No self-service option — always requires human verification.
- **Financial risk:** None — security procedure; no direct financial consequence from wrong answer.

---

## Article 1464557 — Can My Clients Pay Me by Card with client-a?
- **Topic:** Card payment collection for client-a invoices — fees, limits, and TPE partnership
- **Key facts:** Card payments are credited immediately. Card payment is only available for invoices **under 500 €**. Fee structure: within Euro zone — 0.20 € fixed + 1.20 % of the transaction; outside Euro zone (SEPA countries only) — 0.20 € fixed + 2.70 %. Out-of-Euro-zone card payments are available only for these SEPA countries: Bulgaria, Croatia, Czech Republic, Denmark, Hungary, Poland, Romania, Sweden. Card-collected payments do **not** count toward the monthly SEPA transfer/debit quota. SumUp physical terminal (TPE) partnership: 29 € (normally 49 €) with 1.49 % transaction fee (normally 1.75 %).
- **Conditions/exceptions:** 500 € invoice ceiling strictly applies to online card payment — no exceptions stated. Out-of-zone fee (2.70 %) applies only to the listed SEPA countries, not all international cards.
- **Financial risk:** HIGH — wrong fee rates (1.20 % vs 2.70 %) or omitting the 500 € ceiling could lead users to underprice their services or attempt to collect large invoices by card and be surprised when it fails.

---

## Article 1470511 — Disputing a Payment After Card Theft or Loss
- **Topic:** How to contest a fraudulent payment made with a stolen or lost client-a card
- **Key facts:** Step 1 — **block the card immediately** (app: "Plus" tab > Cartes bancaires; web: Cartes bancaires section). Step 2 — contest the specific transaction in the mobile app: tap transaction > Besoin d'aide > Contester cette opération. Step 3 — send a copy of the police report (dépôt de plainte) directly in the support request. client-a then investigates eligibility for reimbursement. **Contestation is only possible if the card was used without the holder's authorisation.**
- **Conditions/exceptions:** Police report is mandatory for the contestation to be processed. client-a does not guarantee reimbursement — eligibility is determined after investigation. The card must be blocked first to prevent further fraudulent transactions.
- **Financial risk:** HIGH — if a chatbot omits the card-blocking step, additional fraudulent transactions may occur before the card is stopped; if it omits the police report requirement, the user's contestation may be rejected, and the fraudulent charges not reimbursed.

---

## Article 1494117 — Managing Transfer Beneficiaries
- **Topic:** Adding, editing, and deleting SEPA transfer beneficiaries in client-a
- **Key facts:** Add a beneficiary via Paiements > Ajouter un bénéficiaire. Name must match exactly: sole traders → first and last name; legal entities → exact raison sociale. client-a auto-fills the BIC from the IBAN. Custom label can be added for internal identification. **After adding a new beneficiary, instant transfers may be temporarily unavailable for security reasons** — standard SEPA transfers remain available immediately. IBAN cannot be modified; to correct it, delete the beneficiary and create a new one. Duplicate beneficiaries (same IBAN) cannot be added. VoP (Verification of Payee) is automatic from 9 October 2025 for every addition and SEPA transfer (see article 12320536 for full VoP details).
- **Conditions/exceptions:** Instant transfer delay after new beneficiary addition is a security measure — no specific duration given ("dans quelques jours").
- **Financial risk:** Moderate — incorrect beneficiary name triggers VoP mismatch; IBAN correction requires full delete-and-recreate (user may send a transfer to a wrong IBAN if they don't realise IBAN is immutable).

---

## Article 1495189 — Download or Delete a Payment Receipt
- **Topic:** Managing payment receipts (justificatifs) for transactions in client-a
- **Key facts:** Add a receipt: tap transaction > "Joindre un reçu" > photo or import. A transaction can also be flagged as personal ("Transaction personnelle") so it is excluded from contribution calculations. Delete a receipt: tap transaction > ••• next to "Afficher le reçu" > delete. From the Start plan onwards, an accountant can be granted access to consult receipts and generate exports.
- **Conditions/exceptions:** Marking a transaction as personal removes it from cotisation calculations (relevant for micro-entrepreneurs — see article 1616755 for details).
- **Financial risk:** None — procedural document management.

---

## Article 1501896 — Writing a Hosting Certificate (Attestation d'Hébergement)
- **Topic:** Template and guidance for the accommodation attestation required when a micro-entrepreneur is hosted by a third party
- **Key facts:** The attestation must be **signed by the host in handwriting** — electronic signatures are not accepted. It is required for CFE validation (INSEE, URSSAF, CMA, Greffe du Tribunal de Commerce). Incomplete or incorrect attestation can delay immatriculation — and the article notes this can sometimes be costly ("refus parfois payant"). A downloadable template is provided. If not applying for micro-enterprise creation, the corresponding mention can be removed.
- **Conditions/exceptions:** Electronic signatures are explicitly rejected. Any error requiring resubmission can delay the registration timeline and may incur additional fees.
- **Financial risk:** Moderate — errors in this document can delay company registration, with potential cost implications noted in the article.

---

## Article 1522537 — Why Is My Charge Estimate Incorrect?
- **Topic:** Troubleshooting inaccurate social contribution estimates in the client-a estimation tool
- **Key facts:** Four causes of inaccuracy: (1) incorrect turnover amount — payments received on other accounts are not auto-included; personal transactions on client-a must be marked as "personnelle" or they inflate the estimate; (2) wrong activity type — must distinguish liberal, commercial, artisanal; mixed activity must be explicitly selected; (3) outdated situation settings — must update if switching to versement libératoire, changing declaration frequency, becoming TVA-liable, or obtaining ACRE; (4) non-micro-entrepreneur — the tool only works for micro-entrepreneurs; régime artistes-auteurs is incompatible with micro-enterprise status. Contact support with CA declaration PDF if estimate remains wrong after these checks.
- **Conditions/exceptions:** The tool is explicitly an estimator — a margin of error is always possible and it may differ from the official URSSAF figure.
- **Financial risk:** Moderate — an incorrect estimate that a user takes as definitive could lead to under-reporting or underpaying contributions to URSSAF, potentially resulting in regularisation demands with penalties.

---

## Article 1523571 — Closing an Old Bank Account
- **Topic:** How to close an existing bank account (at any bank) and migrate to client-a
- **Key facts:** You can switch to client-a immediately without waiting for old account closure. Account closure is free at all banks. Process: send a registered letter with acknowledgement (lettre recommandée avec AR) **at least 30 days before the desired closure date**, including: full name, email, account number, desired closure date, request for a closure attestation; attach: ID photocopy (recto/verso), RIB, payment instruments (card cut in 2, cheques torn) or an attestation de destruction if instruments are no longer available. **Before closing: ensure positive balance and update all direct debit mandates to the new client-a RIB** (phone/mobile, tax authorities, autoentrepreneur.fr). ⚠️ If the account balance is negative at closure and direct debits or cheques arrive after, management fees will be charged.
- **Conditions/exceptions:** Negative balance at closure triggers fees for each failed payment. The 30-day notice is a hard minimum.
- **Financial risk:** HIGH — failing to update SEPA direct debit mandates before closing the account causes failed payments (potentially for taxes, phone, insurance) and management fees. A chatbot that glosses over the mandate-transfer step could cause direct financial harm.

---

## Article 1536035 — Duplicating an Invoice in client-a
- **Topic:** How to duplicate an existing invoice in client-a (web and mobile)
- **Key facts:** Web path: Facturation > Factures > select invoice > Dupliquer > assign a new invoice number. Mobile path: Factures tab > select invoice > ••• (top right) > Dupliquer. The duplicate must be renumbered.
- **Conditions/exceptions:** Invoice numbering must remain sequential and without gaps — a duplicate that reuses or breaks the sequence violates French invoicing law (see article 1184066).
- **Financial risk:** Low — procedural; risk only arises if the user re-uses a number or ignores the required renumbering.

---

## Article 1536163 — Changing Business Address (Domiciliation)
- **Topic:** How a micro-entrepreneur updates their business address with Urssaf and the tax office
- **Key facts:** Via autoentrepreneur.urssaf.fr: Gérer mon auto-entreprise > Modifier mon auto-entreprise; tick both "Changement de domicile personnel" (box 16P) and "Modification du lieu d'exercice" (boxes 11P, 54P, 80P); enter the change date; complete personal info (SIRET, name, birth date/place, new address). After validation, a new SIRET corresponding to the new administrative address will be issued. **Separately, the user must notify their tax office (Service des Impôts des Entreprises) using a specific form, transmitted before the 2nd working day following 1 May.**
- **Conditions/exceptions:** The SIE notification has a hard deadline (2nd working day after 1 May) that is independent of the Urssaf update. Failure to notify the SIE is a separate regulatory obligation.
- **Financial risk:** HIGH — missing the SIE notification deadline (2 May equivalent) is a regulatory violation; failing to update the SIRET address can cause mismatches in invoices, URSSAF correspondence, and tax filings.

---

## Article 15385105 — Not Found
- **Topic:** Article ID 15385105 was not found in the knowledge base (no `## Article: 15385105` entry in INTERCOM.md).
- **Key facts:** This ID may be a collection ID, a deleted article, or a data entry error.
- **Financial risk:** None — should not be indexed; verify whether this ID should be replaced.

---

## Article 1597194 — Writing a Certificate of Destruction of Payment Instruments
- **Topic:** Template letter attesting that payment instruments (card, cheques) have been destroyed, for use when closing a bank account
- **Key facts:** Template includes: date, holder name, account number, address, bank name, date of destruction, card number (XXXX XXXX XXXX XXXX), cheque range (from N° to N°), handwritten signature. **This document is NOT required for closing a client-a account** — the article explicitly notes this.
- **Conditions/exceptions:** Required only when closing a non-client-a account and the instruments are no longer available to physically return/destroy in front of the bank.
- **Financial risk:** None — template/procedural document.

---

## Article 1613127 — How to Download My client-a RIB
- **Topic:** Where to find and download the client-a account RIB (bank details)
- **Key facts:** Mobile: Banque tab > 3-dot button (top right) > Afficher le RIB; can copy-paste details or share via SMS, email, Dropbox, Google Drive. Web: app.client-a.fr > Compte Pro > Transactions > Voir l'IBAN (top right).
- **Financial risk:** None — procedural navigation.

---

## Article 1613477 — How to Change My APE Code
- **Topic:** Requesting a change to the APE (NAF) code for a micro-entrepreneur
- **Key facts:** APE code is assigned by INSEE based on the main activity declared on form P0. It has no legal value — the P0 activity declaration takes legal precedence. However APE code matters for tender pre-selection and (critically) affects applicable cotisation rates and collective agreements. To change it: download the INSEE form; fill in SIRET, activity description (be precise — e.g. "e-commerçant de chaises en bois de chêne", not "Vente de meubles"), employees = 0, CA % per activity (must total 100 %); sign and send to coordinates on page 3. **Must first complete activity change at the relevant CFE before requesting APE modification.**
- **Conditions/exceptions:** CFE change is a prerequisite for APE change (cannot reverse the order). The form cannot be used to declare a code as main activity during initial P0 registration.
- **Financial risk:** Moderate — wrong APE code can affect cotisation rates and collective agreement obligations (cross-reference article 11886479), and disqualify from certain tenders.

---

## Article 1613967 — What Is an Attestation de Vigilance and How to Get It?
- **Topic:** Certificate of social compliance (attestation de vigilance) — purpose, obligations, and how to obtain it
- **Key facts:** Required by clients for any contract worth **≥ 5,000 € HT** (cumulative value, even if billed in instalments), and by certain platforms (Uber Eats, Deliveroo). Proves the holder is current on all social contribution declarations and payments. Client must request at contract signing, then **every 6 months**. If subject to a travail dissimulé (undeclared work) enforcement, the certificate will not be issued until related contributions are paid. **Micro-entrepreneurs:** autoentrepreneur.urssaf.fr > Mes documents > Mes attestations > Demander une nouvelle attestation > Attestation de vigilance. **Other statuses (EI, EURL, SASU, SAS, liberal):** urssaf.fr > Échanges avec mon URSSAF > Mes attestations. Two blocking conditions: (1) cannot create Urssaf account until 3–6 weeks after business creation; (2) cannot obtain the attestation if no CA declaration has yet been made — first declaration is only possible from 90 days after creation.
- **Conditions/exceptions:** The 5,000 € threshold applies to the total contract value, not per invoice. Timing constraints (3–6 weeks Urssaf activation + 90-day first declaration) mean new micro-entrepreneurs cannot obtain the certificate for several months post-creation.
- **Financial risk:** HIGH — without the attestation de vigilance, contracts ≥ 5,000 € HT cannot legally begin; wrong guidance on eligibility timing could lead users to sign contracts they cannot fulfil the compliance requirement for.

---

## Article 1616755 — Marking a Payment as Personal
- **Topic:** How to flag a transaction as personal (excluded from contribution calculations) in client-a
- **Key facts:** Available for micro-entrepreneurs. Tap a transaction > "Marquer comme personnel". All transactions are professional by default. Reversible: tap again > "Marquer comme professionnelle". Personal transactions are excluded from the client-a cotisation estimator.
- **Conditions/exceptions:** Only affects the client-a estimator — does not replace the obligation to declare the correct CA to URSSAF. If a business income is marked personal, it won't appear in client-a's estimate but must still be declared to URSSAF independently.
- **Financial risk:** Low — incorrect flagging leads to a distorted contribution estimate; the real risk is if users take the client-a estimate as their only reference and forget to declare professional income marked as "personal."

---

## Article 1617824 — Required Documents for Creating a client-a Account
- **Topic:** Document checklist for opening a client-a account (KYC requirements)
- **Key facts:** All beneficial owners (mandataires sociaux + shareholders ≥ 25 %) must provide: valid ID + proof of company existence. Valid IDs: European CNI (if issued before 18 — must check validity on Services Publics), European passport, or titre de séjour with valid status. **Titre de séjour mentions explicitly rejected:** "salarié", "étudiant", "travailleur temporaire", "visiteur" — account cannot be opened with these. Proof of address (< 3 months): internet/box bill, electricity/water/gas bill — **mobile phone bills are not accepted**. If hosted by a third party: host's valid ID + host's proof of address (< 3 months) + handwritten attestation d'hébergement (**electronic signatures not accepted**). For companies, client-a auto-retrieves statuts and avis SIRENE, but may require manual submission for very recent creations or SIRENE-masked micro-enterprises. Proof of domicile required only for creation via client-a Micro.
- **Conditions/exceptions:** Multiple beneficial owners: each one must separately submit their own ID and address proof. Mobile phone bills are explicitly excluded as proof of address.
- **Financial risk:** Moderate — a chatbot confirming "any utility bill works" when mobile phone bills are excluded, or confirming that a "travailleur temporaire" titre de séjour suffices, would block account opening and potentially delay business launch.

---

## Article 1674083 — Can a Foreign Student Be a Micro-Entrepreneur?
- **Topic:** Whether foreign nationals studying in France can legally create a micro-enterprise
- **Key facts:** According to the French government, a student visa generally **does not authorise the creation of a micro-enterprise**. **Exception:** Algerian nationals with "étudiant" on their titre de séjour may still exercise micro-entrepreneur activity. To change status in order to create a micro-enterprise: contact the préfecture or call SDAE at **34 30** (Mon–Fri 09:00–16:00, 0.06 €/min + call cost). Other visa types are covered in a separate article.
- **Conditions/exceptions:** The Algerian exception is a specific bilateral treaty right — it does not extend to other nationalities. Any other foreign student must request a visa change before registration.
- **Financial risk:** Moderate — incorrectly telling a foreign student (other than Algerian) that they can create a micro-enterprise could lead to an invalid registration and administrative/legal consequences.

---

## Article 17201594 — Collection ID, Not an Article
- **Topic:** 17201594 appears only as a `**Collection:**` value in other articles, never as an `## Article:` header. It is a client-a Facture Help Center collection identifier, not an article.
- **Financial risk:** None — should not be indexed.

---

## Article 17892018 — Collection ID, Not an Article
- **Topic:** 17892018 appears only as a `**Collection:**` value (seen assigned to article 13377516), never as an `## Article:` header. It is a client-a Facture Help Center collection identifier, not an article.
- **Financial risk:** None — should not be indexed.

---

## Article 17931482 — Collection ID, Not an Article
- **Topic:** 17931482 appears only as a `**Collection:**` value (seen in multiple client-a Facture articles: 13377675, 13378638, and others), never as an `## Article:` header. It is a client-a Facture Help Center collection identifier, not an article.
- **Financial risk:** None — should not be indexed.

---

## Article 1766872 — Changing the Card PIN
- **Topic:** How to change the client-a card PIN and what to do if it is blocked
- **Key facts:** Mobile path: Plus tab > Carte bancaire > Changer le code PIN. Web path: Cartes bancaires > select card > Changer le code PIN. **An ATM operation (withdrawal or other ATM transaction) must be performed after the change to validate the new PIN — the change is not complete until then.** If the account is on the Free plan or the monthly ATM quota is already exhausted, the validating withdrawal costs 1 € HT. Blocked PIN (3 wrong attempts): contact support for reactivation. To view the current PIN: card details > "Voir PIN" > SMS authentication.
- **Conditions/exceptions:** The ATM validation step is mandatory and is not optional. The 1 € HT fee only applies to Free plan users or when the quota is exceeded.
- **Financial risk:** Low — minor unexpected fee if a Free-plan user performs a validation withdrawal; chatbot should mention the ATM validation step to avoid a confusing incomplete state.

---

## Article 1782334 — When to Pay Contributions for the First Time (Quarterly Payment)
- **Topic:** First URSSAF contribution declaration schedule for micro-entrepreneurs on a quarterly cycle
- **Key facts:** The first declaration covers all turnover from the start of activity to the end of the relevant quarter. First filing window by start quarter: Jan/Feb/Mar → declare until 30 Jun → file in July; Apr/May/Jun → until 30 Sep → file in October; Jul/Aug/Sep → until 31 Dec → file in January (following year); Oct/Nov/Dec → until 31 Mar (following year) → file in April (following year). The first declaration therefore covers up to 6 months rather than the usual 3 months.
- **Conditions/exceptions:** This extended first period applies only to the very first declaration — subsequent declarations follow the normal quarterly cycle. See article 1984835 for the equivalent monthly schedule.
- **Financial risk:** HIGH — a chatbot giving the wrong first filing month causes late URSSAF declarations, which attract surcharges and penalties. The extended first period (up to 6 months) is a non-obvious rule that many new entrepreneurs miss.

---

## Article 1849615 — Receiving Your SIRET Number
- **Topic:** How company creation and SIRET issuance works when using client-a
- **Key facts:** The avis de situation SIRENE is the company's identity document, issued by INSEE after registration. client-a creation process (5 steps): online form → documents submission → bank account verification < 48 h → team validation → submission to administration → SIRET received by post. Required documents: décorpus-ation de non-condamnation + mandat du mandataire; additional documents possible per activity type. Processing times after client-a submits the file: commercial (1–5 weeks via Greffe du Tribunal de Commerce); liberal (a few days to 2 weeks via INSEE); artisanal (1–3 months via CMA). For artisans: also receive extrait RNE; for commercial: extrait KBIS. Can start working before receiving SIRET by noting **"SIRET en cours d'attribution"** or "Entreprise en cours d'immatriculation" on invoices. For faster processing: documents must be valid, legible, and complete (no cut-off corners, no blurry images). If deadline exceeded, contact client-a via secure messaging.
- **Conditions/exceptions:** SIRET arrives by post — email delivery is only available "if available". Artisanal timelines are up to 3 months, which is critical for financial planning (capital needs during waiting period).
- **Financial risk:** Moderate — wrong timeline estimates (especially artisanal: up to 3 months) can cause cash-flow miscalculations; not knowing the "SIRET en cours d'attribution" mention can prevent billing during the waiting period.

---

## Article 1849657 — Creating a Micro-Enterprise with client-a
- **Topic:** The client-a Micro company creation service — process, pricing, timelines, and exclusions
- **Key facts:** 5-step process via app. Required documents: décorpus-ation de non-condamnation + mandat du mandataire (+ activity-specific docs). Can bill clients during the wait by noting "SIRET en cours d'attribution". Processing times: commercial 1–5 weeks; liberal few days–2 weeks; artisanal 1–3 months. **Pricing at time of writing (likely outdated — uses old plan names):** 59 € TTC (creation + 6 months Basic); 86 € TTC (+ 6 months Plus); 167 € TTC (+ 6 months Pro). Post-6-month subscription: Basic 7.90 € HT/month, Plus 14.90 € HT/month, Pro 29 € HT/month. Cases where client-a cannot create the micro-enterprise: restricted activities, non-EU students, titre de séjour with an unauthorised mention ("salarié", "étudiant", etc.).
- **Conditions/exceptions:** ⚠️ Plan names in this article (Basic/Plus/Pro) are old branding; current plans are Free/Start/Plus/Business (see article 10490776). Pricing and post-trial amounts may no longer be accurate.
- **Financial risk:** Moderate — stale pricing and plan names could mislead users on actual cost; artisanal 3-month delay is a key financial planning constraint.

---

## Article 1849671 — Cancelling a Card Payment
- **Topic:** Whether a client-a card payment can be cancelled — it cannot
- **Key facts:** **Card payments cannot be cancelled.** If a fraudulent payment is detected: (1) temporarily block the card via app (Plus > Cartes bancaires); (2) follow the contestation procedure for the unrecognised transaction (see article 1470511). In case of card theft or loss: block via the dedicated opposition feature in the mobile app.
- **Conditions/exceptions:** No exceptions — cancellation of card payments is not possible regardless of circumstances.
- **Financial risk:** HIGH — a chatbot implying that card payments can be cancelled is directly false and could cause users to delay the only valid remedies (card blocking + contestation), during which time further fraudulent charges may occur.

---

## Article 1849674 — How to Pay Contributions as a Micro-Entrepreneur
- **Topic:** Step-by-step guide to declaring CA and paying URSSAF social contributions
- **Key facts:** 3 steps: (1) Create Urssaf account on autoentrepreneur.urssaf.fr — **must wait 90 days after business creation** before account can be activated; (2) Declare CA via "Télédécorpus-ation en cours" — must use the correct activity box: liberal services (développeur, consultant, etc.); commercial/artisanal services (coursier vélo, coiffeur, etc.); merchandise sales. client-a's estimate should match the URSSAF calculated amount after entering CA. If versement libératoire applies: income tax is paid at the same time as contributions; (3) Payment options: card, bank transfer, or SEPA direct debit with client-a IBAN. **net-entreprises.fr is no longer valid since September 2019 — must use autoentrepreneur.urssaf.fr exclusively.**
- **Conditions/exceptions:** Wrong activity CA box = wrong contribution rate applied. 90-day activation delay is mandatory. Platform migration from net-entreprises.fr is complete since 2019.
- **Financial risk:** HIGH — using the wrong activity box (e.g. liberal instead of commercial) applies the wrong cotisation rate, causing under- or over-payment; URSSAF may apply penalties for incorrect declarations; net-entreprises.fr reference in this article is outdated.

---

## Article 1849697 — Renting a Car with the client-a Card
- **Topic:** Using the client-a card to rent a car for professional travel
- **Key facts:** The client-a card can be used for car rentals. The account must have sufficient balance to cover both the rental cost and the security deposit (dépôt de garantie). The deposit is refunded within **a maximum of 11 days**; in rare cases this can extend to **30 days**.
- **Conditions/exceptions:** The 30-day delay is described as rare but possible. The deposit blocks that amount from the account for the full duration.
- **Financial risk:** Moderate — a user unaware of the deposit block may face unexpected declined payments elsewhere; incorrect refund timeline (11 vs 30 days) could affect cash-flow planning.

---

## Article 1947108 — Understanding Contribution Calculation (Micro-Enterprises)
- **Topic:** How the client-a social contribution estimation tool works for micro-entrepreneurs
- **Key facts:** The tool estimates social contributions, income tax, and VAT (if applicable). It totals all transactions marked "professional" on the client-a account for the period (monthly or quarterly). The CA figure can be manually adjusted. If VAT-liable, amounts shown are TTC — client-a calculates HT automatically. The contribution rate varies by activity type (liberal, commercial, artisanal) and **changes regularly** — the article directs to the official government site rather than quoting a specific rate. CFP (professional training contribution) is added on top of the rate. Rate is adjusted for ACRE and versement libératoire. Estimation is visible in the Banque view, below the balance. **The Free plan does not include the estimation tool** — an upgrade is required.
- **Conditions/exceptions:** The tool is an estimator — a margin of error is always possible and results may differ from URSSAF's official figure. Rate changes over time; any specific rate cited by a chatbot risks being outdated.
- **Financial risk:** Moderate — if a chatbot quotes a specific contribution rate (which changes regularly), users may base URSSAF payments on a stale figure; Free plan users not knowing the tool is unavailable may be unaware they need to upgrade.

---

## Article 1983082 — Changing APE Code for Bike Delivery Workers
- **Topic:** Specific APE code correction guide for freelance bike delivery workers (livreurs à vélo)
- **Key facts:** INSEE commonly assigns code **5610C** (restauration rapide — fast food) to bike delivery workers, which is incorrect. The correct code for all bike delivery workers is **53.20Z "Autres activités de poste et de courrier"**. Having the wrong code directly affects the cotisation amount paid to URSSAF. Same form and process as article 1613477. CA percentage: if delivery is the only independent activity → 100 %, regardless of also being a salaried employee or student in another capacity.
- **Conditions/exceptions:** The 100 % CA rule applies to the independent activity only — salaried income is separate.
- **Financial risk:** HIGH — incorrect APE code (5610C vs 53.20Z) means the wrong cotisation rate is applied, resulting in over- or under-payment to URSSAF; under-payment leads to regularisation demands and penalties.

---

## Article 1984835 — When to Pay Contributions for the First Time (Monthly Payment)
- **Topic:** First URSSAF contribution declaration schedule for micro-entrepreneurs on a monthly cycle
- **Key facts:** The first monthly declaration covers the **1st month of activity plus the 3 following months** (a 4-month initial period), filed in the month after that period ends. Example: start 3 March → first declaration in July (covers March–June, filed by 31 July). Full table: start January → file in May; February → June; March → July; April → August; May → September; June → October; July → November; August → December; September → January next year; October → February next year; November → March next year; December → April next year. Platform: autoentrepreneur.urssaf.fr — net-entreprises.fr invalid since September 2019.
- **Conditions/exceptions:** The 4-month first period is specific to monthly filers. See article 1782334 for the quarterly equivalent (which has a different calculation). The 4-month rule is counterintuitive and easy to miss.
- **Financial risk:** HIGH — a chatbot giving the wrong first filing month triggers a late URSSAF declaration; the 4-month special window is a common source of confusion for new monthly-payment micro-entrepreneurs.

---

## Article 19003103 — Not an Article (client-a ORIAS Registration Number)
- **Topic:** 19003103 is client-a's ORIAS insurance intermediary registration number (Intermédiaire en assurance enregistré à l'ORIAS sous le numéro 19003103), appearing in article footers — not an article or collection ID.
- **Financial risk:** None — should not be indexed.

---

## Article 2046039 — How to Recognise Fraudulent Mail
- **Topic:** Warning about fraudulent correspondence targeting newly created micro-entrepreneurs
- **Key facts:** New entrepreneurs frequently receive fraudulent letters from private companies impersonating state bodies (RSI, CIPAV, INSEE, etc.) demanding payment. Warning signs: includes CGV (general sales conditions), poor French or spelling errors, non-French tribunal jurisdiction, marked "offre commerciale facultative". **Never respond or send money.** The only legitimate body for APE matters is INSEE, and it is free. Social contributions must be paid only on autoentrepreneur.urssaf.fr (⚠️ the article incorrectly cites net-entreprises.fr, which has been invalid since September 2019 — see article 1849674).
- **Conditions/exceptions:** The article's reference to net-entreprises.fr for contribution payments is outdated.
- **Financial risk:** HIGH — failing to recognise a fraudulent letter and making a payment is a direct financial loss with no recourse; chatbot must clearly communicate that any invoice or demand from unofficial bodies is a scam.

---

## Article 2046331 — Writing a Décorpus-ation de Non-Condamnation
- **Topic:** Template and guidance for the non-conviction declaration required for micro-enterprise or company creation
- **Key facts:** The declaration attests on the honour that the signatory has not been subject to criminal interdictions that would prohibit exercising as an auto-entrepreneur. Can be handwritten. **A criminal record (casier judiciaire) must NOT be submitted in its place** — it is explicitly not accepted as a substitute. Important for CFE validation (INSEE, URSSAF, CMA, Greffe). Errors can cause costly rejection and delay immatriculation ("refus parfois payant"). Downloadable template provided.
- **Conditions/exceptions:** The handwriting requirement is acceptable; electronic signatures are not mentioned but see article 1617824 which rejects electronic signatures for similar documents.
- **Financial risk:** Moderate — submitting casier judiciaire instead causes rejection; a delayed immatriculation can incur fees and delay the start of business operations.

---

## Article 2046412 — Writing a Spousal Information Attestation (Attestation de Délivrance de l'Information au Conjoint)
- **Topic:** Template for the attestation proving that a spouse or PACS partner has been informed of the business creation
- **Key facts:** Required when creating a company while married or PACSed under the **régime de la communauté des biens** (community property matrimonial regime). Can be handwritten. Required for CFE validation (CMA or Greffe du Tribunal de Commerce specifically — not all CFEs). Errors may cause rejection, which can be costly and delay immatriculation. Downloadable template provided.
- **Conditions/exceptions:** Only applies to the specific matrimonial regime — those under séparation de biens or who are single/divorced do not need this document.
- **Financial risk:** Moderate — an incorrect or missing document delays company registration (sometimes at cost); a chatbot that does not mention this requirement for community-property couples could cause users to submit incomplete dossiers.

---

## Article 2055055 — Writing the Mandataire Power of Attorney
- **Topic:** Template for the power of attorney (pouvoir du mandataire) that authorises client-a to register the entrepreneur's micro-enterprise on their behalf
- **Key facts:** Gives client-a the legal mandate to file the company creation with the relevant CFE on the user's behalf. Can be handwritten. Downloadable template provided. Errors can cause rejection — noted as "parfois payant" and delaying immatriculation.
- **Conditions/exceptions:** Required only when creating a company through client-a's client-a Micro service — not needed for self-filed registrations.
- **Financial risk:** Moderate — errors or omissions cause a rejected dossier, which may incur costs and delay business start.

---

## Article 2090492 — Declaring Revenue When Attached to Parents' Tax Household
- **Topic:** How to declare micro-entrepreneur income when the entrepreneur is still part of their parents' tax household
- **Key facts:** Parents must include the income in their own return and also file the supplementary form 2042 C-PRO, marking the section as "personne à charge" instead of "décorpus-ant 1." They must declare the correct income type per activity: BNC for liberal non-commercial services (developer); BIC for commercial, artisanal, or commercial service activities (biker, e-commerce). Form fields differ for those with versement libératoire vs those without. Eligible to remain on parents' return if: under 21 at 1 January of the declaration year, or under 25 and studying at 1 January or 31 December of that year.
- **Conditions/exceptions:** Age and student conditions determine eligibility. Once over-age or no longer studying, the entrepreneur must file their own return.
- **Financial risk:** HIGH — using the wrong income category (BNC vs BIC) on the parents' tax return is a tax misclassification that can trigger reassessment; wrong form field (e.g. 5MO vs 5MP) also leads to incorrect tax calculations.

---

## Article 2096397 — Understanding the Difference Between Amount Paid and Amount Debited
- **Topic:** Why the amount debited from a client-a account may differ from the price paid (bank pre-authorisation)
- **Key facts:** The difference is a security deposit / bank imprint (empreinte bancaire / pré-autorisation). Merchants request authorisation for more than the final amount to certify sufficient funds. Common cases: self-service petrol stations, vehicle rental, restaurant reservations, hotel bookings. The account is only ultimately debited for the actual amount consumed/used. Just wait for the difference to resolve.
- **Conditions/exceptions:** See article 2311904 for a more detailed explanation of all pre-authorisation scenarios and the legal maximum duration (11–30 days).
- **Financial risk:** None — informational/reassurance article.

---

## Article 2096888 — 1 € Debit on My Account
- **Topic:** Why a 1 € charge appears on a client-a account
- **Key facts:** Merchants verify card validity by requesting a small amount, often exactly 1 €. This is a bank imprint (empreinte bancaire) — it is not a real charge and is automatically cancelled after a few days. Traditional banks hide this because they only show real-time notifications for client-a.
- **Conditions/exceptions:** The charge is temporary and automatic — no action required.
- **Financial risk:** None — reassurance article.

---

## Article 2104919 — Requesting an EU VAT Number as a Bike Delivery Worker
- **Topic:** How bike delivery workers obtain an EU intra-community VAT number (numéro de TVA intracommunautaire)
- **Key facts:** Required even for non-VAT-liable micro-entrepreneurs when billing EU-based companies (e.g. Uber Eats BV in the Netherlands). Process: download the form from the SIE; fill in name, address, phone number, SIRET; sign and date; send by registered letter with acknowledgement (lettre recommandée avec AR) to the SIE (Service des Impôts des Entreprises) the entrepreneur depends on. Then wait for issuance.
- **Conditions/exceptions:** The EU VAT number is required regardless of whether the entrepreneur is VAT-liable — it is needed for billing foreign EU entities and for the Décorpus-ation Européenne de Service (DES).
- **Financial risk:** HIGH — issuing invoices to EU-based companies without an EU VAT number is a compliance violation; missing this number also means the monthly DES declaration cannot be completed (see article 2144881).

---

## Article 2136626 — Creating a Handwritten Identity Proof (Preuve d'Identité Manuscrite)
- **Topic:** How to produce the handwritten identity attestation required for company creation dossiers
- **Key facts:** Certifies on the honour that the identity document copy is a true copy of the original. Must include a handwritten statement + signature. If no scanner: place ID on white sheet and write everything by hand; for CNI, recto and verso must be done separately (two photos). If titre de séjour is expired: must attach the récépissé de demande de renouvellement. Errors cause rejection — described as "parfois payant" and delaying immatriculation.
- **Conditions/exceptions:** The handwritten aspect is mandatory — a printed attestation is not sufficient.
- **Financial risk:** Moderate — incorrect or incomplete document causes dossier rejection, which may be costly and delays registration.

---

## Article 2141522 — Invoicing Euro Zone Clients Without Being VAT-Liable (Autoliquidation)
- **Topic:** How to add the mandatory "autoliquidation" (VAT reverse charge) mention when invoicing EU clients while not VAT-liable
- **Key facts:** When billing an EU-based company (e.g. Uber Eats Netherlands) as a non-VAT-liable entrepreneur, the invoice **must include the mention "autoliquidation"** — this signals that the client handles VAT under the reverse charge mechanism. In client-a: add "autoliquidation de TVA" to the invoice title, and **set the VAT rate to 0 %**. The EU VAT number is also required (see article 2104919).
- **Conditions/exceptions:** Applies only when billing EU-domiciled companies as a non-VAT-liable entrepreneur. Different rules apply if the entrepreneur is VAT-liable.
- **Financial risk:** HIGH — omitting the "autoliquidation" mention on such invoices is a legal compliance violation; applying a non-zero VAT rate is also incorrect and creates a false tax liability.

---

## Article 2144881 — Billing Euro Zone Clients (Monthly DES Declaration)
- **Topic:** Rules and monthly Décorpus-ation Européenne de Service (DES) obligation when billing EU-zone clients
- **Key facts:** A monthly DES must be filed with the douanes for every month a service is provided to an EU-zone client. **Only non-VAT-liable entrepreneurs can use the paper form** — VAT-liable ones must declare online. Purpose: customs control of TVA collection on cross-border EU services. Invoices must be in French for legal validity (translations can be sent alongside). For EEA clients: include the client's EU VAT number on the invoice, even if the entrepreneur is VAT-exempt. Hors-EEE clients: same billing rules as French clients, no DES required. French-domiciled micro-enterprise = French tax resident regardless of physical location.
- **Conditions/exceptions:** The monthly DES is per-service-month — if no service was rendered to an EU client that month, no DES is needed. DES obligation applies even to non-VAT-liable entrepreneurs billing EU clients.
- **Financial risk:** HIGH — missing a monthly DES = customs regulatory violation with potential fines; not including the client's EU VAT number on EEA invoices is a compliance violation; double-taxation risk for expats without a bilateral tax treaty (mentioned in article 2330203).

---

## Article 2157556 — Pending Card Payment
- **Topic:** Why card payments appear as "En attente" (pending) on a client-a account
- **Key facts:** client-a displays all transactions in real-time, including those not yet validated. The "En attente" status reflects the merchant's authorisation request, not an immediate debit. Validation takes 1–3 working days. For petrol stations, hotels, and car rental companies: a pre-authorisation (empreinte) for a higher amount than the final bill is shown as pending and updates once settled. **If the pre-authorisation amount exceeds the account balance, the payment is refused for insufficient funds — even if the actual final amount would be covered.**
- **Conditions/exceptions:** Traditional banks don't show this pending state (only show validated transactions after 3 days) — client-a's transparency may surprise users used to other banks.
- **Financial risk:** Moderate — uninformed users may attempt payments expecting available balance, only to be declined because a pending pre-auth has reserved funds; chatbot should explain pre-auth blocking.

---

## Article 2180615 — Identifying a B2B SEPA Direct Debit
- **Topic:** Understanding the difference between B2C/CORE and B2B/Interentreprises SEPA direct debit mandates
- **Key facts:** Two SEPA debit types: (1) B2C/CORE — most common; just provide IBAN, accepted automatically on client-a, no manual setup needed; (2) B2B/Interentreprises — for company-to-company or public body payments (DGFIP, SIE for VAT remittance); identified by the word "INTERENTREPRISES" on the mandate; must be added manually in the client-a app. Key clarification: **income tax and CFE payments to the Finances publiques use B2C mandates, not B2B** — despite being to a public body.
- **Conditions/exceptions:** B2B mandates require manual configuration in client-a; forgetting to add them means the debit will fail.
- **Financial risk:** Moderate — failing to add a B2B mandate for VAT payments to DGFIP causes a failed tax payment, which triggers penalties.

---

## Article 2207488 — Can You Be a Micro-Entrepreneur with a Criminal Record?
- **Topic:** Whether having a criminal record prevents someone from registering as an auto-entrepreneur
- **Key facts:** Depends on activity type: (1) Liberal non-regulated (e.g. developer, consultant) — no non-condamnation declaration required; criminal record does not block registration; (2) Liberal regulated (e.g. architect) — non-condamnation declaration not required, but the required diploma/authorisation must be held; (3) Commercial or artisanal — non-condamnation declaration is mandatory; if subject to a commerce interdiction (up to 5 years), registration is blocked; otherwise, can proceed.
- **Conditions/exceptions:** The commerce interdiction blocking rule applies specifically to commercial and artisanal activities — it does not apply to liberal activities.
- **Financial risk:** Moderate — incorrect guidance that says a criminal record blocks all registrations could prevent someone from legitimately starting a liberal activity; conversely, saying it never matters could allow an ineligible person to attempt a commercial registration.

---

## Article 2211725 — What Are Débours (Freelance Expense Disbursements)?
- **Topic:** What disbursements (débours) are for independent professionals and how to handle them
- **Key facts:** Débours = expenses paid by the freelancer on behalf of and for a specific client (e.g. postage costs for a client's invitations). The client reimburses the exact TTC amount. **The reimbursement is not counted as revenue → no social contributions are applied to it.** Critical requirement: the original invoice for the expenditure must be made out in the **client's name** (not the freelancer's); the freelancer keeps the copy. Must be recorded in accounting records. A note de débours is then sent to the client for reimbursement. **Cannot be used for: kilometric allowances, meal costs, or accommodation expenses.**
- **Conditions/exceptions:** The exemption from revenue only applies if the original invoice is correctly made out to the client's name. Meals, accommodation, and mileage are explicitly excluded — these are refundable as frais but are different from débours.
- **Financial risk:** Moderate — incorrectly including reimbursed débours as revenue inflates the CA and triggers excess cotisations; using débours for ineligible expenses (meals, accommodation) is tax non-compliance.

---

## Article 2212780 — Filling In the CFE Premises Questionnaire (Centre des Finances Publiques)
- **Topic:** How to complete the premises questionnaire sent by the tax centre when registering as an auto-entrepreneur
- **Key facts:** Questionnaire is sent when a professional address is declared on registration. Used by the tax authority to calculate the CFE (Cotisation Foncière des Entreprises) tax rate. **Must be returned within 15 to 30 days of receiving the letter** (deadline is stated on the letter). No fees are payable for this questionnaire. If no accountant: write "Je suis micro-entrepreneur et je n'ai pas de comptable." Auto-entrepreneurs: do not fill in the "clôture du premier exercice" field.
- **Conditions/exceptions:** Deadline (15–30 days) is stated on the individual letter — varies per CFE. Failure to respond affects CFE computation.
- **Financial risk:** HIGH — missing the response deadline can affect the CFE tax calculation and constitute a regulatory violation with potential penalties; a chatbot that doesn't flag the deadline urgency could cause the user to miss it.

---

## Article 2213049 — Filling In the Social Security Option Form (Droit d'Option) as a Salaried Worker
- **Topic:** How to elect a different social security regime when simultaneously salaried and self-employed
- **Key facts:** When holding both salaried and independent activities, social security defaults to the regime of the main activity. Since 2020, self-employed protection defaults to the régime général. The droit d'option form allows choosing the other activity's regime. Form available on Ameli.fr. Must attach ID copy and IBAN.
- **Conditions/exceptions:** Since 2020, self-employed protection is automatically under the régime général — the option form is needed only if the user wishes to change this.
- **Financial risk:** Low — administrative election; no direct financial harm from wrong chatbot answer.

---

## Article 2216713 — Adding a Second Activity to a Micro-Enterprise
- **Topic:** How to add a second professional activity to an existing micro-enterprise (form P2-P4)
- **Key facts:** Use form P2-P4: tick Modification + activity type of existing main activity; Cadre 1: SIREN, name, birth details; Cadres 2–6: not required; Cadre 7: start date of new activity, tick "permanente", describe new activity, tick relevant domain; Cadre 8: specify whether secondary or becoming principal (using exact wording "Adjonction de l'activité secondaire/principale"); Cadre 9: personal address/phone/email; Cadre 10: SIRENE visibility preference (being masqué can hinder partnerships but reduces fraudulent mail); Cadre 11: sign and date. Must complete both copies. Send to CFE for the new activity's domain. Note: some CFEs may require extra documents or charge filing fees.
- **Conditions/exceptions:** Commercial second activity → CCI; artisanal → CMA; liberal → URSSAF. Some CFEs charge dossier fees — article recommends calling ahead.
- **Financial risk:** Moderate — incorrect Cadre 8 wording (secondary vs principal) affects activity classification and potentially cotisation rates; missing the correct CFE could cause misfiled paperwork; possible unexpected filing fees.

---

## Article 2220027 — Adding a Second Activity to a Micro-Enterprise (Duplicate)
- **Topic:** Near-identical duplicate of article 2216713 — same form P2-P4 process for adding a second activity
- **Key facts:** Content is functionally identical to 2216713 (same form, same cadres, same CFE routing rules, same SIRENE masking note). One minor wording difference in cadre 6 ("ne doit par être rempli" vs "ne doit pas être rempli" — typo in one version).
- **Conditions/exceptions:** ⚠️ This is a near-identical duplicate of 2216713. If indexed, a RAG system may return either; responses should be consistent.
- **Financial risk:** Moderate — same as 2216713; duplicate indexing may cause inconsistent chatbot answers.

---

## Article 2245891 — Closing an Auto-Entrepreneur Activity (Artisans and Merchants)
- **Topic:** How to formally cease an artisanal or commercial auto-entrepreneur activity
- **Key facts:** File form P4 (in duplicate): tick CESSATION + COMMERCIALE or ARTISANALE; fill cadres 1, 2, 9, 10, 11 only (cadres 3–7 not required; cadre 8 optional for observations). Cadre 2: cessation date of the entrepreneur's choice. Attach valid ID copy (recto/verso). Send to the relevant CFE. Will receive an accusé de réception confirming the declaration. **Closure and deregistration are free of charge.**
- **Conditions/exceptions:** Failing to formally file the cessation means URSSAF may continue charging social contributions even after activity stops.
- **Financial risk:** Moderate — informal cessation (stopping activity without filing) leads to continued URSSAF contribution demands; a chatbot must not imply simply stopping work is sufficient.

---

## Article 2246136 — Closing an Auto-Entrepreneur Activity (Liberal Professions)
- **Topic:** How liberal-profession auto-entrepreneurs formally cease their activity via the Urssaf platform
- **Key facts:** Via autoentrepreneur.urssaf.fr: Gérer mon auto-entreprise > Cesser mon activité; select the exact domain/activity (e.g. INTERNET > DÉVELOPPEUR); complete the form with email; attach handwritten identity proof (preuve d'identité manuscrite); click télédéclarer; download the cessation proof. **Closure and deregistration are free of charge.**
- **Conditions/exceptions:** Must select the precise activity domain — a broad/wrong selection may cause the form to fail. For artisans and merchants, use article 2245891's process (form P4) instead.
- **Financial risk:** Moderate — same as 2245891: without formal closure, URSSAF contributions continue.

---

## Article 2311904 — Understanding Card Pre-Authorisations (Empreintes Bancaires)
- **Topic:** Detailed explanation of all scenarios involving bank card pre-authorisations
- **Key facts:** Four pre-auth scenarios: (1) Balance check — merchant reserves more than the expected final amount to confirm sufficient funds (e.g. hotel, car rental); (2) Card validity check — merchant sends an authorisation for a small amount (≤ 1 €) to verify the card is active; (3) Residual authorisation — if the pre-auth exceeded the final bill (e.g. shortened car rental), the residual stays visible until released; (4) FX exchange rate variance — foreign-currency payment pre-auths may be higher due to rate fluctuation. Pre-auths show as "En attente." Legal maximum holding time: **11 calendar days**; rare cases up to **30 days**. Estimated release date visible in the client-a app. **If pre-auth amount exceeds available balance → payment refused, even if actual final bill is covered.** For accounting: always use validated debit amounts, not pre-auth amounts.
- **Conditions/exceptions:** The accounting note is important for micro-entrepreneurs: recording the pre-auth amount as a charge rather than the settled amount leads to incorrect bookkeeping.
- **Financial risk:** Moderate — users unaware of pre-auth blocking may experience declined payments; incorrect accounting of pre-auth amounts (rather than settled amounts) leads to bookkeeping errors.

---

## Article 2329981 — National ID Card (CNI) Validity Rules
- **Topic:** Validity rules for French CNI for use in account opening at client-a
- **Key facts:** Since 1 January 2014, CNI validity is 15 years (not 10) for adults at the time of issue. The automatic 5-year extension applies to: CNIs issued from 2 January 2004 to 31 December 2013 to adults; CNIs issued from 1 January 2014 onwards to adults. **The expiry date printed on the card is not updated** — the card appears expired but is still valid. Extension does NOT apply to cards issued to minors (still 10 years). Validity can be checked at the Services Publics website.
- **Conditions/exceptions:** Only applies to CNI issued to persons who were adults (≥ 18) at the time of issue. Cards issued to minors always expire as printed.
- **Financial risk:** Moderate — incorrectly rejecting a valid-but-apparently-expired CNI (issued 2004–2013) blocks account or company creation; telling a user with a genuinely expired card that it is valid is also harmful.

---

## Article 2330203 — Being a French Auto-Entrepreneur While Living Abroad
- **Topic:** Conditions, billing rules, and tax implications for French micro-entrepreneurs based outside France
- **Key facts:** Eligible if: French national + business address in France (can be domiciled at family/friends' address). Free choice of French or foreign clients. **Invoices and legal documents must be in French** — other languages have no legal value in France (translations can also be sent). For EEA clients: include the client's EU VAT number on each invoice even if VAT-exempt; also file a monthly DES. Hors-EEE clients: same rules as French clients. Taxes: paid to France only (French fiscal resident by domicile, regardless of time spent abroad). **Risk of double taxation in countries without a bilateral tax treaty with France**, particularly when also earning income in the host country. Entrepreneurs should check host country tax policy.
- **Conditions/exceptions:** The monthly DES obligation applies to all EU-zone clients (not just Uber Eats). Double taxation risk only arises for non-EEA income if no treaty exists.
- **Financial risk:** HIGH — double taxation risk if the user does not check for a bilateral tax treaty before establishing themselves abroad; missing monthly DES = customs violation; missing client EU VAT number = compliance violation.

---

## Article 2338549 — Filing the Food Transport Declaration (Bike Delivery Workers)
- **Topic:** Mandatory hygiene declaration for bike delivery workers transporting food of animal origin
- **Key facts:** Legally required for any bike delivery worker transporting food. Filed online via the DDCSPP (Direction Départementale de la Cohésion Sociale et de la Protection des Populations) platform. Key form answers: employees in contact with foodstuffs = 0; premises type = mixed private/professional; category = "Activités de transport ou d'entreposage"; surface = 0; status = "Prestataire"; no other food-related activity = Non. Must download and retain the récépissé (also sent by email). Article labels this as "Première décorpus-ation."
- **Conditions/exceptions:** Only required for delivery workers transporting food of animal origin (e.g. meal delivery) — not all courier activity.
- **Financial risk:** Moderate — failure to file this declaration is a regulatory violation subject to DDCSPP inspection.

---

## Article 2349529 — How to Obtain the Prime d'Activité as a Micro-Entrepreneur
- **Topic:** How to apply for the prime d'activité (activity income supplement) at the CAF as a micro-entrepreneur
- **Key facts:** Available if monthly income ≤ approx. 1,500 € (thresholds vary by household situation). Apply via the CAF website. Must select correct activity type on the form: bike delivery / e-commerce → "Commerciale"; developer → "libérale"; hairdresser → "artisanale". Declare **gross monthly CA** (not net after abattement) in Revenus non salariés. Must send to CAF by registered letter: extrait Kbis or certificat d'inscription au répertoire Sirene (for liberal activities) + explanatory letter. Can provide client-a IBAN for payment.
- **Conditions/exceptions:** This article's cotisation regime field ("ASI (RSI)") references the former RSI which was dissolved in 2018 — the field may have changed; users should verify the current form labels.
- **Financial risk:** Moderate — wrong activity category or declaring net instead of gross CA causes incorrect CAF processing; the RSI reference is stale (dissolved 2018) and may confuse form completion.

---

## Article 2353516 — Template Letter for CAF Activity Benefit (Prime d'Activité)
- **Topic:** Boilerplate letter for auto-entrepreneurs to accompany a CAF prime d'activité application, attesting auto-entrepreneur (not TNS) status.
- **Key facts:** Letter is addressed to CAF and explains the entrepreneur is auto-entrepreneur, not a "travailleur non salarié". Used to supplement an online CAF application.
- **Conditions/exceptions:** Article uses a fictional name and address (Sean Combs, Paris) as a fill-in-the-blank template — users must substitute their own details. Only relevant for auto-entrepreneurs applying for prime d'activité.
- **Financial risk:** Low — The letter template itself is fine, but the use of a placeholder identity may confuse users unfamiliar with the format. No direct financial consequence of getting the letter wrong, but an incorrect submission could delay benefit receipt.

---

## Article 2359483 — Getting a Trade Name (Nom Commercial) as a Liberal Micro-Entrepreneur
- **Topic:** Step-by-step guide for liberal activity micro-entrepreneurs to register a trade name via URSSAF using form P2-P4.
- **Key facts:** Use form P2-P4 (2 copies); check "Modification" and "Libérale"; fill cadre 1 (identity + SIREN), cadre 3 (date + name), cadre 7 (activity date + type), cadre 8 ("Ajout de nom commercial" + the trade name), cadres 9–10–11; send both copies to URSSAF. Processing takes a few weeks.
- **Conditions/exceptions:** Applies only to liberal activities; commercial micro-entrepreneurs send to CCI; artisans send to CMA (see article 2361761 for those).
- **Financial risk:** None — procedural only; no financial penalty described for errors.

---

## Article 2361761 — Getting a Trade Name (Nom Commercial) as a Commercial or Artisan Micro-Entrepreneur
- **Topic:** Step-by-step guide for commercial or artisan micro-entrepreneurs to register a trade name via CCI or CMA using form P2-P4.
- **Key facts:** Use form P2-P4 (2 copies); check "Modification" + activity type (commercial or artisanale); cadre 8: "Adjonction du Nom Commercial Suivant" + trade name; send to CCI if commercial (e.g. bikers), CMA if artisan.
- **Conditions/exceptions:** Commercial → CCI; artisan → CMA; liberal → URSSAF (article 2359483). Fill exactly 2 copies.
- **Financial risk:** None.

---

## Article 2367997 — Filling In the Initial CFE Declaration
- **Topic:** How to complete the initial Cotisation Foncière des Entreprises (CFE) declaration form.
- **Key facts:** Article is **effectively empty** — content only says "download this form and follow the steps in this article" with no actual guidance.
- **Conditions/exceptions:** N/A — article has no substantive content.
- **Financial risk:** Low — the article is a stub. The CFE initial declaration has a real deadline (31 December of the year of business creation), and failing to file can affect CFE calculation, but this article provides no actionable information. Should not be indexed.

---

## Article 2437290 — Getting SIRET/Kbis More Than 6 Weeks After Filing
- **Topic:** What to do if SIRET number or Kbis extract hasn't arrived 6+ weeks after submitting the company creation dossier.
- **Key facts:** Check infogreffe.fr by searching name; Kbis purchasable online (under €5) if found. If not found, contact client-a. Important: Kbis is only for **commercial** micro-entrepreneurs; artisans get an **extrait D1** via SIREN; liberal professions get an **avis de situation au répertoire SIRENE**.
- **Conditions/exceptions:** Kbis is not issued to all micro-entrepreneurs — nature of activity determines the correct document type.
- **Financial risk:** Low — delays prevent starting partnerships (e.g. Uber Eats requires proof of registration), but no direct financial penalty described.

---

## Article 2489132 — Getting the Avis de Situation au Répertoire Sirene
- **Topic:** How to download the official company record (Sirene directory statement) using SIREN number from INSEE.
- **Key facts:** Use the INSEE online form with SIREN number; click "Télécharger l'avis de situation". This document replaces the Kbis for Uber Eats and Deliveroo partnerships. If company info was set to hidden at creation, must contact INSEE directly via their contact form.
- **Conditions/exceptions:** Cannot download if user chose to mask their Sirene information at registration — direct INSEE contact required.
- **Financial risk:** None.

---

## Article 2491213 — Changing URSSAF CA Declaration Periodicity (Monthly ↔ Quarterly)
- **Topic:** How to switch between monthly and quarterly URSSAF social contribution declaration cycles.
- **Key facts:** Done via URSSAF account messaging: "Nouveau message" → "Faire évoluer mon auto-entreprise" → "Je souhaite modifier la périodicité de mes décorpus-ations." Critical: **if the business has been active for more than 3 months, the change only takes effect from January of the following year** — not immediately.
- **Conditions/exceptions:** 3-month rule: no immediate periodicity change if active > 3 months. This can surprise users expecting an immediate switch.
- **Financial risk:** Moderate — a user switching periodicity hoping to align payments immediately may continue on the old cycle, leading to unexpected cash flow obligations or missed declarations.

---

## Article 2512470 — Downloading Bank Statements and Annual Fee Statement
- **Topic:** How to download monthly bank statements and the annual banking fees summary from client-a.
- **Key facts:** Statements in Comptabilité > Export comptable > Accéder aux relevés de compte; monthly statements published at start of the following month; "Relevé de frais annuel" available from web app only. Closed accounts: email support@client-a.fr with SIREN + phone number + list of required statements; team verifies identity before sending.
- **Conditions/exceptions:** Annual fee statement only accessible from web app (not mobile). Accountant access (for downloading on behalf of client) requires Start/Plus/Business plan.
- **Financial risk:** None.

---

## Article 2518551 — Adding SIRET Number to client-a Profile
- **Topic:** How to enter or update SIRET, APE code, and registration date in the client-a app.
- **Key facts:** Mobile-only (not available on web); Accueil > profile icon > Informations de l'entreprise > SIRET field. Can also enter APE code and immatriculation date. Contact client-a support if update fails or correction needed.
- **Conditions/exceptions:** Web app does not have this feature — mobile only.
- **Financial risk:** None.

---

## Article 2536735 — EURL Manager: Which Social Security Regime?
- **Topic:** Which social protection regime applies to EURL managers (gérant-associé unique vs gérant non-associé).
- **Key facts:** Gérant-associé unique (sole owner-manager) → TNS (travailleurs non salariés), affiliated to SSI (ex-RSI). Gérant non-associé (manager who is not the owner) → régime général (assimilés-salariés), affiliated to régime général. **Article is INCOMPLETE** — the contribution calculation sections are left as "xxxx" placeholders.
- **Conditions/exceptions:** The distinction between the two types of gérance is important for social contribution rates and social protection levels — the article acknowledges this but provides no actual figures.
- **Financial risk:** Moderate — article is a stub with placeholder content and should NOT be indexed. The TNS vs. régime général classification has major implications for contribution amounts and social protection level; a wrong answer could lead to significant miscalculation.

---

## Article 2611564 — Régime Général (CPAM) for Independents in 2019
- **Topic:** Explanation of the 2018–2020 transition from RSI/SSI to CPAM for independent workers.
- **Key facts:** All new independents from 2019 onward automatically affiliated to CPAM (via URSSAF, no action needed); pre-2019 independents transferred to CPAM by 2020; form 750 (Mutation) from ameli.fr for early transfer; single interlocutor: CPAM / ameli.fr.
- **Conditions/exceptions:** **Outdated article** — the RSI→SSI→CPAM transition is entirely complete as of 2020. RSI and SSI are defunct. LMDE, Harmonie Mutuelle as health insurers for independents are also obsolete.
- **Financial risk:** Low — Directing users to RSI/SSI processes would send them down a dead-end. Article should not be indexed or surfaced.

---

## Article 2611630 — Keeping Student Health Insurance as an Independent in 2019
- **Topic:** Explanation of the student health insurance (LMDE, SMEREP) transition to régime général (CPAM) during 2019.
- **Key facts:** All student health insurance schemes (LMDE, SMEREP, etc.) were merged into CPAM/régime général from 2019; students who become independents are auto-affiliated to CPAM; form 750 for transfer from prior regime.
- **Conditions/exceptions:** **Fully outdated** — student health insurance schemes no longer exist; the transition described was completed in 2020.
- **Financial risk:** Low — Outdated content; should not be indexed. No direct financial consequence but could direct users to defunct institutions (LMDE, Harmonie Mutuelle as student insurer).

---

## Article 2636733 — Transfer Pricing (Cost of SEPA Transfers)
- **Topic:** Cost structure for SEPA transfers and international FX transfers by client-a plan.
- **Key facts:** Included SEPA movements per billing period: Free=5, Start=30, Plus=100, Business=500. Each additional movement beyond quota: **€0.40 HT**, billed monthly with subscription. Counter resets each billing period (≈30 days). International FX transfers billed separately with specific fees (not counted in SEPA quota).
- **Conditions/exceptions:** Quota is for both outgoing SEPA transfers and incoming SEPA direct debits combined. International non-SEPA transfers have different pricing entirely.
- **Financial risk:** Moderate — incorrect information about per-transfer pricing or quota limits could lead users to underestimate monthly banking costs, especially for high-volume plans.

---

## Article 2636985 — Subscription Fee Debiting
- **Topic:** How and when client-a debits monthly subscription fees, and what happens with insufficient funds.
- **Key facts:** Monthly debit on the account creation anniversary date; first month is free. Per-use fees (card usage, cash deposit, FX wire, invoice-by-card payment) billed end of month with subscription. If funds insufficient after multiple attempts: account may be restricted or blocked; reactivated by topping up. Usage tracking in app: Mon abonnement > Usage.
- **Conditions/exceptions:** Article mentions "client-a Micro" plan (old naming). Prélèvement mensuel alone does not count as account "activity" for dormancy purposes.
- **Financial risk:** Low — account restriction for non-payment is operationally disruptive but not a regulatory risk. Users need to keep account funded on anniversary date.

---

## Article 2637043 — Understanding Banking Fees with client-a
- **Topic:** Where to find information about client-a's banking fees and how they are charged.
- **Key facts:** Fee-generating transactions display the fee amount directly. Per-use fees (card, cash deposit, FX transfers, card invoice collection) billed at end of month. Quota and real-time usage visible in Mon abonnement > Usage. Full tariff list on client-a website or in-app.
- **Conditions/exceptions:** None.
- **Financial risk:** None.

---

## Article 2637211 — Cost of Micro-Enterprise Creation with client-a
- **Topic:** Pricing for client-a's micro-enterprise creation service.
- **Key facts:** **Outdated content** — article references "client-a Start" pack (59€ TTC including creation + 6 months "client-a Basic"), then 7.90€ HT/month, with "client-a Premium" add-on at +25.90€. These are old plan names (Basic/Premium); current plans are Free/Start/Plus/Business.
- **Conditions/exceptions:** Partner discount may apply. Pricing is likely no longer current.
- **Financial risk:** Low — stale pricing and plan names could mislead prospects about actual costs. Should not be indexed without update.

---

## Article 2659532 — Exporting Accounting Entries
- **Topic:** How to generate accounting exports (transactions, receipts, invoices, VAT) from client-a.
- **Key facts:** Via Plus > Comptabilité > Générer un export comptable (mobile) or Comptabilité tab (web). Formats: CSV, OFX, QIF. CSV includes 2 date columns: initiation date and value date (date de valeur); QIF/OFX use value date only; bank statements show value date. Accountant can generate exports if given dedicated access (Start/Plus/Business required). Monthly scheduled exports can be cancelled from the same page.
- **Conditions/exceptions:** Initiation date ≠ value date — this distinction matters for accounting reconciliation. Accountant access only on Start/Plus/Business plans.
- **Financial risk:** None.

---

## Article 2771398 — Why client-a Asks for Patrimoine and Annual Revenue
- **Topic:** Legal basis and purpose of client-a's KYC wealth and income collection.
- **Key facts:** Legal basis: decree 2009-1087 (AML/CTF obligations). Data confidential, not shared with third parties. All users: annual income + patrimoine (net assets, select from brackets). Additional for US citizens or non-French fiscal residents. Additional for legal entities (SASU, SARL, SAS…): annual revenue + employee count. Filled via notification on app home screen.
- **Conditions/exceptions:** Required from all client-a users; US citizens and foreign fiscal residents trigger additional checks (see articles 2831449, 2869225).
- **Financial risk:** None.

---

## Article 2831449 — Restrictions for US Citizens
- **Topic:** client-a currently cannot accept US citizens as customers due to IRS/FATCA compliance constraints.
- **Key facts:** IRS imposes strict obligations on European banks for accounts held by US citizens; constraints are too significant for client-a to accommodate currently. Sign-up form available for notification when this changes.
- **Conditions/exceptions:** Applies to US citizenship, not necessarily US fiscal residence. No exception or workaround described.
- **Financial risk:** None — informational only.

---

## Article 2869225 — Fiscal Residence Outside France
- **Topic:** Conditions under which non-French fiscal residents can open a client-a account.
- **Key facts:** Account opening possible if: (1) existing company (not a new creation or capital deposit), AND (2) eligible country (some countries excluded due to international sanctions). Being a citizen of another country does not automatically mean foreign fiscal residence.
- **Conditions/exceptions:** Cannot open account for company creation or capital deposit with foreign fiscal residence. Sanctions-listed countries excluded. See article 2912143 for how foreign fiscal residence is determined.
- **Financial risk:** None — eligibility filter only.

---

## Article 2912143 — Why client-a Asks About Foreign Fiscal Residence
- **Topic:** CRS (Common Reporting Standard) compliance and how client-a determines foreign fiscal residence.
- **Key facts:** CRS is a G8/G20 initiative for automatic exchange of financial information between tax authorities. client-a must report account balance and financial income to the tax authority of a user's foreign fiscal residence country. Three cumulative criteria for foreign fiscal residence: (1) less than 183 days/year in France, (2) principal professional activity not in France, (3) less than 50% of total income from France. If the user answers "no" to at least one criterion → obligatorily taxed in France only, no foreign fiscal residence to declare.
- **Conditions/exceptions:** All three criteria must be true simultaneously for a non-French fiscal residency to apply. Answering "no" to even one = France is the only fiscal residence.
- **Financial risk:** None — compliance/informational.

---

## Article 2914588 — Declaring Billed vs. Received Revenue (Encaissé vs. Facturé)
- **Topic:** Auto-entrepreneurs must declare RECEIVED amounts (encaissé), not invoiced amounts (facturé), to URSSAF.
- **Key facts:** Legal basis: Loi de Financement de la Sécurité Sociale 2011. Must declare amounts actually received (encaissé), not invoiced. Declaration periodicity (monthly or quarterly) chosen at business creation. **Penalties:** Late declaration = 1.5% of PASS (≈€50); absent declaration = 5% surcharge per missing monthly declaration, or 15% per missing quarterly declaration. Deadline for all prior-year declarations: 31 January of the current year.
- **Conditions/exceptions:** Applies to all auto-entrepreneurs regardless of activity type. Late penalty is per-declaration, and surcharges compound.
- **Financial risk:** HIGH — Declaring invoiced instead of received revenue overstates CA → overpayment of cotisations. Missed declarations trigger 5–15% surcharges on top of cotisations due. Users must understand the encaissé basis is mandatory, not optional.

---

## Article 2975813 — Filing Tax Return as a Bike Delivery Worker
- **Topic:** Step-by-step guide for bike couriers filing annual income tax using form 2042 C-PRO.
- **Key facts:** First-year filers must use paper form; subsequent years can file online. Must complete 2042 C-PRO in addition to standard return. Box 5TB = delivery CA (non-Vienne); box 5TE = delivery CA (Vienne residents); box 5DB = number of months active in the year; box 5KP also required. BNC for non-commercial services; BIC for commercial/artisan/delivery. Prélèvement libératoire filers declare CA in the micro-entrepreneur section.
- **Conditions/exceptions:** **Heavily outdated** — article references 2017 tax year and 2018 filing procedures. Tax form box numbers change annually; the specific codes cited (5TB, 5TE, 5DB, 5KP) may differ in current forms. Vienne department distinction may also have changed.
- **Financial risk:** Moderate — outdated box references could lead to incorrect tax filing, potentially resulting in missed income declarations or incorrect tax computation. Should not be indexed without update.

---

## Article 2980273 — How to Get a Kbis Extract
- **Topic:** How micro-entrepreneurs obtain their Kbis (or equivalent) after company creation via client-a.
- **Key facts:** client-a submits the creation dossier to the state; Kbis arrives by post within a few weeks. Can also be downloaded online (paid option). **Critical: Kbis is only issued for commercial activities.** Liberal professions get an **avis de situation au répertoire SIRENE** (via SIRET on INSEE); artisans get an **extrait RNE** from INPI. If company information was hidden in the SIREN directory at creation, online download is impossible — must wait for postal delivery.
- **Conditions/exceptions:** Hidden SIREN = no online Kbis download. Liberal and artisan micro-entrepreneurs do not have a Kbis and should not be directed to seek one.
- **Financial risk:** Low — directing a liberal or artisan entrepreneur to obtain a Kbis (which doesn't exist for their status) wastes their time and could delay partner onboarding (e.g. Uber Eats).

---

## Article 2998190 — Attaching Receipts and Invoices to Transactions
- **Topic:** How to associate receipts and invoices with client-a transactions for accounting purposes.
- **Key facts:** Receipts and invoices can be stored digitally in client-a via photo or file upload. **Critical warning:** digital copies stored in client-a do NOT replace original documents in case of a tax audit — "ces copies numériques ne remplacent pas les documents originaux en cas de contrôle. Les reçus enregistrés sur client-a n'ont pas de valeur probante." Paper originals must still be kept. client-a can automatically link incoming payments to matching client-a invoices. TVA lines should be added per receipt. Accountant access (for downloading receipts) requires Start/Plus/Business.
- **Conditions/exceptions:** Digital client-a receipts have no legal probative value; original paper documents are still required by law. Auto-linking only works for client-a-generated invoices.
- **Financial risk:** Moderate — a user who believes client-a's digital receipts are sufficient for a tax audit (contrôle fiscal) could face penalties for missing original documents. This caveat must be clearly communicated.

---

## Article 3005099 — Identity or Address Document Rejected
- **Topic:** Why client-a rejects ID or proof of address during account opening, and how to resolve it.
- **Key facts:** Proof of address: must be under 3 months old; acceptable types = energy/gas/water bill, fixed internet or landline phone bill (mobile bills NOT accepted); must show full name and matching address. If hosted: need signed/dated hébergement attestation + host's ID (recto/verso) + host's proof of address under 3 months. ID: must be valid; CNI valid up to 5 years after the printed expiry if issued after majority; CNI/titre de séjour: both recto and verso required; passport: double-page with photo required. Resubmit via in-app chat; response within 48 hours.
- **Conditions/exceptions:** CNI 5-year extension applies only if issued to a person of legal age (majeur). Mobile phone bills are not accepted under any circumstances.
- **Financial risk:** None — administrative, but delays account activation.

---

## Article 3068070 — How to Become an Uber Eats Courier
- **Topic:** Guide to signing up as an Uber Eats delivery courier.
- **Key facts:** **Heavily outdated** — article references 2018-era Uber Eats conditions: 3.50€+1€/km rate structure, 25% commission, Uber Eats operating in 27 French cities, equipment including isothermal bag and armband, Facebook group "Les Coursiers Français." Pay rates, commission structures, and onboarding procedures have changed significantly.
- **Conditions/exceptions:** All figures and processes described are outdated; this is not client-a's core content.
- **Financial risk:** Low — outdated third-party pay and fee information could mislead couriers about expected earnings. Should not be indexed.

---

## Article 3074279 — Capital Deposit Eligibility Criteria
- **Topic:** Who can use client-a's capital deposit service (dépôt de capital) and what the eligibility conditions are.
- **Key facts:** Eligible legal forms: EURL, SARL, SAS, SELARLU, SASU, SCI immatriculated in France (incl. Martinique, Guadeloupe, Réunion). All beneficial owners must be French residents; EEE associates with ≤10% non-controlling stake accepted. Valid ID required (EU CNI/passport/French titre de séjour). Capital range: **€1 to €150,000** (above €150k: contact depot@client-a.fr). **Liberation minimums: SA/SAS/SASU = 50% at creation; SARL/EURL = 20% at creation.** US persons (FATCA) are not accepted. Minor shareholders accepted with additional documents (livret de famille; parents become beneficial owners if minor holds >25%).
- **Conditions/exceptions:** SAS/SASU must liberate at least 50%; SARL/EURL at least 20%. These are legal minimums enforced by the notary. Corporate shareholders (personne morale) require Kbis <3 months + statuts + subscriber list.
- **Financial risk:** HIGH — confusing the 50% vs 20% liberation minimum by legal form can result in a rejected dossier, delayed registration, and administrative costs. FATCA ineligibility is absolute with no workaround.

---

## Article 3074289 — Required Content for Company Articles of Association (Statuts)
- **Topic:** What a company's statuts project must contain to use client-a's capital deposit service.
- **Key facts:** Required elements: future activity, address, share count + nominal value + capital liberated at creation (must be stated explicitly), identity/DOB/personal address of all associates, management rules. Share allocation must appear in statuts or annexe; director nomination in statuts or annexe (or emailed to depot@client-a.fr). **Two mandatory verbatim insertions for client-a capital deposit:** (1) In "Apports" section: standard notary mention (Maître Quentin Fourez, Pont-Audemer). (2) In optional annexe: client-a's full legal identification with ACPR number 71758, Treezor number 63512, and ORIAS number 19003103.
- **Conditions/exceptions:** Both boilerplate insertions are verbatim requirements — any deviation may block the dossier. If no annexe, second insertion is optional. Capital libéré amount must be stated explicitly (e.g. "capital libéré à la création: X€").
- **Financial risk:** Moderate — missing or incorrectly worded mandatory statuts mentions will block the capital deposit process, delaying company registration and potentially incurring legal amendment costs.

---

## Article 3074902 — Wiring the Capital Deposit Funds
- **Topic:** How to wire funds to client-a for the capital deposit after document validation.
- **Key facts:** client-a sends a dedicated IBAN by email after validating documents. **Each associate must wire exactly the amount stated in the statuts (to the cent) — not a combined wire.** Wire must come from a **traditional European bank** — neobank wires (e.g. Lydia, Nickel, Revolut) are **systematically rejected**. Wire must come from an account in the associate's own name.
- **Conditions/exceptions:** Neobank wires are rejected with no exception. Each co-associate must wire their own share separately. Exact amount required to the cent.
- **Financial risk:** HIGH — wiring from a neobank or wrong account, or the wrong amount, causes rejection of the wire, delays the capital deposit and company registration. Users with neobanks as their main account are at particular risk of this error.

---

## Article 3074930 — Understanding the Capital Deposit Process Steps
- **Topic:** End-to-end process overview for client-a's capital deposit service (6 steps).
- **Key facts:** Step 1: Submit dossier (statuts + ID for all shareholders). Step 2: Document verification (up to 2 working days). Step 3: client-a sends IBAN for fund transfer. Step 4: Notary verifies (a) **eligible origin country** for the wire — accepted: France (incl. DOM-TOM), Belgium, Spain, Germany, Italy, Portugal — and (b) full dossier completeness → attestation de dépôt within 72h. Step 5: After immatriculation, **submit final signed Kbis** to client-a → client-a validates account and releases funds (2–3 working days). Step 6: Funds appear in client-a account.
- **Conditions/exceptions:** Wire origin is strictly limited to France+5 EU countries — wires from other countries (incl. other EU members) are rejected by the notary. Final Kbis must be transmitted to client-a before funds are released — failure to do so keeps funds locked indefinitely.
- **Financial risk:** HIGH — wiring from an ineligible country blocks fund release. Forgetting to transmit the final Kbis after immatriculation means company funds remain locked in the notary account and the client-a account is not activated.

---

## Article 3080543 — How to Refuse ACRE to Preserve It for a Later Business
- **Topic:** Strategy and procedure for refusing ACRE (new business social contribution reduction) at first business creation, to use it for a subsequent, more serious venture.
- **Key facts:** ACRE can be refused voluntarily. Rationale: if opening a short-duration or test business first, refusing ACRE preserves it for the real business later. Procedure: send **registered letter with acknowledgement of receipt** (recommandé avec AR) to the relevant URSSAF, stating the refusal, business start date, SIRET number, and social security number. URSSAF address determined by department.
- **Conditions/exceptions:** Must be sent after immatriculation. Registered letter with AR is required (not email, not simple letter) to have proof of the refusal.
- **Financial risk:** Moderate — if the letter is not sent correctly (e.g. simple letter instead of registered, or no AR), client-a cannot confirm the refusal was received. ACRE is automatically granted and consumed for the first business, with no second chance. The strategy only works if the formal refusal is properly executed.

---

## Article 3119252 — Cheque Deposit (Encaissement d'un Chèque)
- **Topic:** How to deposit cheques with client-a and the associated costs, limits, and process.
- **Key facts:** All plans can deposit cheques. Monthly included deposits: Free=0, Start=2, Plus=6, Business=15; overage fee: **€2 HT per extra cheque**. Per-deposit limit: **€5,000**; 30-day cumulative limit: **€10,000**. Process: (1) Register in mobile app only; (2) Fill cheque details + take photo + sign on back; (3) **Mail the physical cheque to client-a within 15 days** of app registration; (4) client-a must receive the cheque within 15 days; (5) Funds available after **15 working days**. Rejected cheques incur additional fees.
- **Conditions/exceptions:** 15-day hard deadline to physically post the cheque after registering in-app — no extension described. Mobile app only (no web). Free plan users pay for every single cheque deposit. Limits are per billing period, not calendar month.
- **Financial risk:** Moderate — missing the 15-day physical mailing deadline results in a rejected cheque process. Users also face surprise at the €5,000 single-cheque limit (cheques above this cannot be deposited). Free plan users may not realise each deposit costs €2.

---

## Article 3120009 — What Insurance Is Offered by client-a?
- **Topic:** Overview of insurance coverage bundled with client-a Plus and Business subscription plans.
- **Key facts:** Insurance is **only available on Plus and Business plans** (not Free or Start). Four categories: (1) **Travel**: transport delays up to €1,000 (Plus: €50/hr from 2nd hour; Business: €100/hr, cumulative for outbound/return/en-route); vehicle rental excess rachat up to €5,000/year (Business only); foreign health coverage up to €155,000 (Business only). (2) **Payment fraud**: card fraud up to €1,500/year (Plus) / €3,000/year (Business); identity theft assistance up to €1,000/year (Business only). (3) **Equipment and accident**: screen repair up to €200/person/year (Plus, €50 deductible) or unlimited (Business); laptop repair/replacement up to €3,000/event (Business only); hospitalisation €100/night (Plus: from first night, max 3 nights; Business: from first day, max 30 days); casse/vol of goods up to €1,250 (Business, 60-day coverage window). (4) **Legal assistance**: 6 days/week phone access, max 10 calls/year (Plus/Business); debt collection support (Plus/Business). Coverage applies only to items purchased with the client-a card for professional use.
- **Conditions/exceptions:** Items must be bought with client-a card to be covered. Travel health insurance covers illnesses/accidents occurring outside home country. Transport delay starts from 2nd hour for Plus.
- **Financial risk:** None — descriptive. Misquoting coverage levels could cause financial planning errors.

---

## Article 3120540 — Differences Between the Two Card Types
- **Topic:** Comparison of Mastercard Basic (Free/Start plans) vs Mastercard Premium (Plus/Business plans).
- **Key facts:** Basic = Free and Start plans; Premium = Plus and Business plans. Key differences: **Non-euro payment fee**: Free=2%/Start=1.75% (Basic); Plus=1.5%/Business=1% (Premium). **30-day payment ceiling**: Free=€20,000; Start=€40,000; Plus/Business=€60,000. **Insurance**: Basic=none; Premium=material, travel, legal, payment fraud. Cards are immediate debit (no deferred debit), no overdraft (exceptional cases only), no instalment payments via client-a card. Compatible with Apple Pay and Google Pay.
- **Conditions/exceptions:** No deferred debit or instalment payment available on any client-a card. Non-euro fee percentages differ by plan within the Basic tier.
- **Financial risk:** None — informational.

---

## Article 3122250 — Cash Withdrawal Abroad: What Does It Cost?
- **Topic:** ATM withdrawal fees by client-a plan, within and outside the eurozone.
- **Key facts:** Free plan: no free withdrawals; **every ATM withdrawal costs €1 HT** (eurozone). Start: 2 free per billing period, then €1 HT each. Plus: 4 free, then €1 HT each. Business: 10 free, then €1 HT each. **Outside eurozone (all plans):** €1 HT + **1.90% HT** of the withdrawn amount on top. Fees charged immediately at point of use; shown on monthly subscription invoice.
- **Conditions/exceptions:** Free plan users pay for every single ATM withdrawal — no free withdrawals included. Out-of-eurozone surcharge is percentage-based on top of the flat fee and applies to all plans.
- **Financial risk:** Low — Free plan users and travellers may be surprised by per-withdrawal costs, especially the 1.90% surcharge outside eurozone.

---

## Article 3123153 — Getting a Payment Terminal (TPE) with client-a
- **Topic:** Three partner payment terminal options available to client-a users: SumUp, Yavin, and Square.
- **Key facts:** **SumUp**: Solo Lite terminal at €29 (vs €49); 1.49% per transaction (vs 1.75%); best for low-volume card payments. **Yavin**: €25/month subscription (vs €29); terminals €229–€329; 0.5%+Interchange per transaction; fixed fee per transaction waived; best for established merchants with recurring higher volumes. **Square**: first €4,000 CA with no transaction fees (via client-a partnership); then standard Square pricing; suitable for omnichannel (in-store + online). Important: Square-to-client-a transfers count against the SEPA movement quota. client-a does not offer a domiciliation card (not compatible with all TPEs).
- **Conditions/exceptions:** Square virements toward client-a are counted in SEPA quota — users should programme weekly transfers to manage their quota. No domiciliation bancaire card is available.
- **Financial risk:** None.

---

## Article 3152490 — Collection ID, Not an Article
- **Note:** 3152490 is a collection ID in the Intercom knowledge base (used as the **Collection** value for several articles including 2912143 and 3005099). No `## Article: 3152490` entry exists in INTERCOM.md. This ID should not be queried as an article.

---

## Article 3152647 — Collection ID, Not an Article
- **Note:** 3152647 is a collection ID (used as `**Collection:**` for card-related articles such as 3120540 and 1180106). No `## Article: 3152647` entry exists in INTERCOM.md.

---

## Article 3152648 — Collection ID, Not an Article
- **Note:** 3152648 is a collection ID (used as `**Collection:**` for cheque and payment-related articles such as 3119252). No article entry exists.

---

## Article 3152649 — Collection ID, Not an Article
- **Note:** 3152649 is a collection ID (used as `**Collection:**` for transfer-related articles such as 5697789). No article entry exists.

---

## Article 3159999 — Required Documents for Goods Delivery Workers
- **Topic:** What documents a delivery worker needs depending on mode of transport (bicycle vs motorised vehicle).
- **Key facts:** Bicycle delivery: a signed "décorpus-ation à vélo" (attestation on honour, client-a-specific document) is required — it covers delivery by any non-motorised means (bicycle, foot, scooter without motor). For **motorised vehicle delivery** (scooter, car): two sequential requirements: (1) Obtain an **attestation de capacité de transport de marchandises** = 105-hour training (typical cost €500–€2,500) + qualifying exam, from an approved body (e.g. Centre national de formation, AFTRAL); (2) **Then register** in the registre des transporteurs et loueurs with the attestation — with the regional authority: **DRIEA** (Île-de-France), **DREAL** (mainland France), or **DEAL** (Overseas territories).
- **Conditions/exceptions:** The capacité attestation alone is **not sufficient** — registration in the transporteur registry is a separate mandatory step. The relevant authority varies by region.
- **Financial risk:** HIGH — a delivery worker with a motorised vehicle who obtains the training certificate but skips the registry inscription is operating illegally as a commercial transporter. Sanctions apply. The article's warning ("l'attestation de capacité ne suffit pas") is critical to relay correctly.

---

## Article 3353670 — How to Get a Proof of Address (Justificatif de Domicile)
- **Topic:** Which documents client-a accepts as proof of address for account opening.
- **Key facts:** Must be under 3 months old. Accepted: fixed internet or landline phone bill (mobile bills NOT accepted — Orange Freebox, Bouygues, SFR, Free accepted; mobile plans are not), energy contract attestation or electricity/gas bill (EDF, Engie). Must show full name (nom + prénom), or hébergeur's name if hosted. Address must exactly match the one given at registration. PDF format preferred.
- **Conditions/exceptions:** Mobile phone bills are never accepted. Must match the registered address exactly.
- **Financial risk:** None — administrative only; wrong document delays account opening.

---

## Article 3364541 — Collection ID, Not an Article
- **Note:** 3364541 is a collection ID (used as `**Collection:**` for eligibility/account access articles such as 2831449 and 2869225). No article entry exists.

---

## Article 3364584 — Collection ID, Not an Article
- **Note:** 3364584 is a collection ID (used as `**Collection:**` for accounting/export articles such as 2659532, 2512470, and 2998190). No article entry exists.

---

## Article 3364593 — Collection ID, Not an Article
- **Note:** 3364593 is a collection ID (used as `**Collection:**` for capital deposit articles such as 3074289, 3074279, and 3074930). No article entry exists.

---

## Article 3364595 — Collection ID, Not an Article
- **Note:** 3364595 is a collection ID (used as `**Collection:**` for company creation articles such as 2980273, 2518551, and 3159999). No article entry exists.

---

## Article 3365691 — Collection ID, Not an Article
- **Note:** 3365691 is a collection ID (used as `**Collection:**` for subscription/billing articles such as 2636985). No article entry exists.

---

## Article 3365908 — Collection ID, Not an Article
- **Note:** 3365908 is a collection ID (used as `**Collection:**` for invoicing tool articles such as 3123153). No article entry exists.

---

## Article 3367398 — Collection ID, Not an Article
- **Note:** 3367398 is a collection ID (used as `**Collection:**` for card management articles such as 5230385). No article entry exists.

---

## Article 3367540 — Collection ID, Not an Article
- **Note:** 3367540 is a collection ID in the Intercom knowledge base. No `## Article: 3367540` entry exists in INTERCOM.md.

---

## Article 3183664 — How to Upload Documents in the App
- **Topic:** Step-by-step guide for uploading identity documents and proof of address to complete client-a account registration.
- **Key facts:** Two documents required: (1) photo of ID recto/verso; (2) proof of address under 3 months. Documents uploaded via in-app camera or file import. Must accept client-a T&Cs during submission. Validation takes 1–2 working days. Note: the article contains a copy-paste error (steps 1 and 2 are identically worded as "prendre la photo de votre pièce d'identité").
- **Conditions/exceptions:** Article content is minimal and has a duplicated step — low informational value. Account only activated after validation.
- **Financial risk:** None.

---

## Article 3191158 — Getting Reimbursed for Pre-Incorporation Expenses
- **Topic:** How company founders can be reimbursed by the company for expenses incurred before its official creation (e.g. client-a capital deposit invoice).
- **Key facts:** client-a invoices for the capital deposit are issued to the individual, not the future company (which doesn't yet legally exist). Pre-incorporation expenses can be reimbursed by the company post-creation if: (1) expenses are directly linked to business launch; (2) a receipt exists naming the future company; (3) expense date is within **3–6 months before company creation**. If no receipt in company name: the founder can re-invoice the expense to the company after creation, **but TVA is not recoverable** in this case. Accountably recorded as credit to the "compte de l'exploitant individuel."
- **Conditions/exceptions:** 3–6 month pre-creation window is strict. Receipt must name the future company to allow TVA recovery. Re-invoicing post-creation is a fallback but forfeits TVA deductibility.
- **Financial risk:** Moderate — founders who don't keep receipts naming the future company, or who exceed the 3–6 month window, lose the right to reimburse expenses and recover TVA. A wrong chatbot answer omitting these conditions could lead to unrecoverable costs.

---

## Article 3162258 — Logging Into client-a from a Computer
- **Topic:** How to access the client-a web app from a browser.
- **Key facts:** Go to client-a website, click "Se connecter", enter registration phone number, enter 4-digit PIN code, confirm with SMS code. **Outdated article** — written when web login was new, notes "new features coming soon."
- **Conditions/exceptions:** Requires the phone number used at account creation. Two-factor: PIN + SMS.
- **Financial risk:** None.

---

## Article 3396199 — What Is the Capital Deposit Attestation?
- **Topic:** Definition and purpose of the attestation de dépôt de capital — the mandatory document required to register a company.
- **Key facts:** The capital deposit attestation is a legally required document for company creation; it certifies the total contributions made by each shareholder. Funds must be deposited with a bank, the Caisse des dépôts et consignations (CDC), or a notary. client-a uses a notary partner. client-a sends the attestation by email once the deposit is validated. Without it, the company creation dossier cannot be submitted to the greffe.
- **Conditions/exceptions:** None — applies to all company forms using client-a's capital deposit service.
- **Financial risk:** Low — informational; but users who don't understand that this document gates their immatriculation may be unprepared for the sequence.

---

## Article 3396213 — Cost of Company Creation with client-a (SAS, SASU, EURL, SARL, SCI)
- **Topic:** Pricing for client-a's company creation service for incorporated structures (as opposed to micro-enterprise).
- **Key facts:** SASU created by client-a: capital deposit (€69) + creation fee (€99) = **from €168 HT** (excluding mandatory legal fees). Creation fee waived with 12-month account commitment. Other forms (EURL, SARL, SAS via Legalstart): **from €168 HT**; SCI: **from €238 HT**. Prices are **HT and exclude mandatory third-party legal fees** (frais légaux obligatoires — publication in a legal gazette, greffe fees, etc.). Monthly account from €0/month.
- **Conditions/exceptions:** The "frais légaux obligatoires" are additional and not included in the listed prices — total out-of-pocket cost is higher. Legalstart partnership used for all forms except SASU.
- **Financial risk:** Low — the exclusion of mandatory legal fees from the headline price could mislead users about total creation cost. A chatbot should always mention that additional mandatory fees apply.

---

## Article 3399375 — Getting an EU VAT Number When Non-VAT-Liable
- **Topic:** How to obtain an EU intra-community VAT number even when in franchise de base de TVA (not VAT-liable), when billing EU-based clients.
- **Key facts:** **Mandatory** to have a VAT number when billing any EU-country client, even if not subject to TVA. Process: (1) Download/copy the form; (2) Fill in identity + SIRET; (3) Indicate reason — goods acquisition from EU (if <€10,000/year, can opt in or out; if >€10,000/year, must register) or service provision/acquisition to/from EU non-French entity; (4) Send by **registered letter with acknowledgement (recommandé avec AR)** to the relevant **SIE** (Service des Impôts des Entreprises).
- **Conditions/exceptions:** Applies even to micro-entrepreneurs in franchise de base. Goods acquisition threshold of €10,000/year determines whether opting in is mandatory or optional. Services to/from EU: VAT number always required regardless of amount.
- **Financial risk:** HIGH — invoicing EU clients without an intra-community VAT number violates invoicing obligations. A chatbot answering "you don't need a VAT number because you're non-VAT-liable" to an entrepreneur with EU clients would be giving dangerously wrong advice.

---

## Article 3406382 — Apps/Software That Can Auto-Fetch Transaction History
- **Topic:** Third-party accounting software or apps that can automatically retrieve client-a transaction history.
- **Key facts:** Article is **completely empty** — no content beyond the title.
- **Conditions/exceptions:** N/A.
- **Financial risk:** None — empty stub; should not be indexed.

---

## Article 3490555 — Choosing or Updating Your client-a Subscription
- **Topic:** Overview of client-a's 4 subscription plans and how to change between them.
- **Key facts:** Four plans: **Free** (basic features), **Start** (daily management tools, accountant access, employee access at €5/month/access), **Plus** (growth tools, employee access included), **Business** (team use, higher limits). Changes can be made at any time from app or web. **Timing rules:** Downgrade (any billing cycle) = end of current billing period. Upgrade monthly→monthly = **immediate, prorated**. Upgrade annual→annual = **immediate, prorated**. Any change involving a shift between monthly and annual billing = end of current period. Additional fees may apply on plan change (shown before confirmation).
- **Conditions/exceptions:** Annual plan users wishing to downgrade must wait until the end of the annual period. Free plan has no employee access.
- **Financial risk:** None — informational; timing of plan changes is worth noting for users expecting immediate downgrades.

---

## Article 3549525 — Documents Required for Capital Deposit
- **Topic:** What documents client-a needs to process a capital deposit request.
- **Key facts:** Required: (1) Valid ID for **all shareholders** (EU CNI, EU passport, or French titre de séjour; if expired titre de séjour: provide renouvellement récépissé); (2) Statuts project containing the two **mandatory verbatim insertions** — the notary apport mention (in "Apports" section) and the client-a legal identification (in optional annex). Self-drafted statuts must have both additions; Legalstart/partner-drafted statuts come pre-filled. Upload via client-a personal space or email to depot@client-a.fr.
- **Conditions/exceptions:** ID required from every shareholder without exception. Missing mandatory statuts mentions = dossier rejected. Expired titre de séjour must be paired with renewal receipt.
- **Financial risk:** Moderate — incomplete or incorrectly worded statuts block the capital deposit and delay company registration, potentially causing timing and legal cost issues.

---

## Article 3549575 — How Long Does Capital Deposit Dossier Verification Take?
- **Topic:** Timeline for client-a's validation of a capital deposit dossier.
- **Key facts:** Standard: **48 working hours** once dossier is complete (statuts + ID documents submitted). Delays caused by: (1) illegible, blurry, or cropped documents; (2) statuts missing the mandatory "Apports" mention (and sometimes the annex mention); (3) discrepancies between registration info and statuts (wrong amounts, wrong company name). Once validated, client-a sends RIB → attestation de dépôt issued within **72 working hours** of wire receipt.
- **Conditions/exceptions:** 48h is only guaranteed if all documents pass on first submission. Statuts discrepancies trigger an email and restart the clock.
- **Financial risk:** Low — informational about timing; key takeaway is that statuts errors and document quality are the main sources of delay.

---

## Article 3549713 — How to Complete the Capital Deposit Wire Transfer
- **Topic:** Detailed conditions that must be met for the capital deposit wire to be accepted by the notary.
- **Key facts:** Wire must: (1) come from an **eligible country**: France (incl. DOM-TOM), Belgium, Spain, Germany, Italy, or Portugal; (2) come from a **credit institution** (not a neobank — Lydia, Nickel explicitly excluded); (3) come from an **account in the associate's own name** (joint accounts: need RIB to verify; company accounts only valid for personne morale associates); (4) use the exact **wire label format**: "client-a - Apport de M/Mme PRENOM NOM - SOCIÉTÉ"; (5) be **exactly the amount stated in the statuts** — each associate must wire their own contribution separately; (6) if >€5,000: provide **proof of funds origin** + RIB of sending account.
- **Conditions/exceptions:** Wires from ineligible countries or non-credit institutions (neobanks) are rejected by the notary with no exception. Wire label is mandatory — abbreviated if bank doesn't allow full text.
- **Financial risk:** HIGH — any of the 5 conditions not met causes notary rejection of the wire, delaying the entire capital deposit process. Neobank users are particularly at risk of rejection without realising it.

---

## Article 3551393 — Transmitting the Kbis to client-a
- **Topic:** How and when to send the final Kbis and signed statuts to client-a to trigger fund release after company registration.
- **Key facts:** After the greffe validates the company (using the attestation de dépôt), the entrepreneur receives their **final Kbis and SIREN**. They must then transmit the **final Kbis + signed final statuts** to client-a via their personal space. client-a verifies the documents and releases the deposited funds within a few working days. The client-a account can be used (invoicing, RIB access) before the funds are released.
- **Conditions/exceptions:** **Both** the Kbis AND the signed final statuts are required — submitting only one is not sufficient. Funds are not released until both are received and verified.
- **Financial risk:** HIGH — users who don't know they must proactively transmit these two documents will have their company funds remain locked in the notary account indefinitely. This is a non-obvious post-immatriculation step.

---

## Article 3551636 — Why client-a Requests Additional Documents
- **Topic:** Explanation of why the greffe may request additional supporting documents during micro-enterprise creation.
- **Key facts:** Certain activities require activity-specific documentation: e.g. bicycle delivery workers must provide a delivery declaration. The greffe may also request attestations or diplomas for certain regulated activities. When creating via client-a, required additional documents are listed on the "Ma micro-entreprise" page after the form is completed. client-a verifies documents within 1–3 working days before sending the dossier to the administration.
- **Conditions/exceptions:** Activity-specific requirements vary — the article doesn't list all of them.
- **Financial risk:** Low — missing supplementary documents delays registration; errors can incur retry costs.

---

## Article 3551671 — How Long Does Document Verification Take?
- **Topic:** Timeline for client-a's identity and address document verification during account opening.
- **Key facts:** Standard: **2 working days** (Monday–Friday). The 48-hour guarantee applies only if all documents pass on the **first submission**. Checks performed: ID and proof of address are valid, legible, and uncropped (all 4 corners visible); additional activity-specific documents correctly completed and signed; co-associates' documents meet the same standards.
- **Conditions/exceptions:** Any document issue restarts the clock. Co-associate documents must all be valid for the dossier to proceed.
- **Financial risk:** None — informational about timing.

---

## Article 3563079 — ICS/Direct Debit: Can I Charge My Clients Directly with client-a?
- **Topic:** client-a does not offer ICS (SEPA direct debit initiator number) and explains the associated risks of direct debits.
- **Key facts:** client-a does not provide ICS numbers or direct debit initiation. Key risks of SEPA direct debits (even via other providers): clients can contest within **8 weeks** after account credit; if no valid mandate: contestation window extends to **13 months**; if contested without valid mandate, client is **automatically refunded**. This can leave the creditor's account at zero or negative. client-a recommends card payments (SumUp, 3D Secure via invoicing) or SEPA transfers as these cannot be reversed.
- **Conditions/exceptions:** Contestation windows are EU law (SEPA regulation), not client-a-specific.
- **Financial risk:** Moderate — a user who sets up SEPA direct debits (via a third party) without understanding the 8-week/13-month contestation risk could face sudden account deficits. Key to flag clearly.

---

## Article 3565711 — Why client-a Has Constraints on Cheque Deposits
- **Topic:** Explanation of the 15-day processing delay and €5,000 per-cheque limit for cheque deposits.
- **Key facts:** Background: cheques are processed by the issuing bank within 24h of physical receipt (compensation). client-a receives funds ~24h later, but the issuing bank has **up to 10 days to reject** the credit (e.g. if account is frozen or overdrawn). Without the 15-day hold, client-a would credit funds that could later be recalled, potentially leaving the depositor's account negative. The 15-day hold protects both the customer and client-a. client-a recommends preferring card payments (SumUp) or transfers, which are final.
- **Conditions/exceptions:** The 10-day late rejection window is the core reason for the constraint — this is a banking industry-wide rule, not specific to client-a.
- **Financial risk:** None — explanatory article; but useful for understanding cheque deposit risk.

---

## Article 3596846 — Collection ID, Not an Article
- **Note:** 3596846 is a collection ID (used as `**Collection:**` for employee card access articles such as 7105066). No `## Article: 3596846` entry exists in INTERCOM.md.

---

## Article 3606170 — How to Apply for ACRE
- **Topic:** How new entrepreneurs apply for ACRE — the social contribution reduction for the first year of activity.
- **Key facts:** ACRE is a partial exoneration of social contributions for the first year. Eligibility: job-seeker (indemnified or registered at Pôle Emploi ≥6 months in the past 18 months), RSA/ASS recipient, under 26 years old, under 30 with disability or insufficient chômage duration, employee of business in judicial proceedings, CAPE holder, QPV (priority urban area) business, prestation partagée d'éducation recipient. Form: fill cadres 1, 2, 4 (only if Pôle Emploi), 5 (date/sign). Submit online to URSSAF with eligibility document, P0 form, and ID copy. **Critical: must be submitted within 45 days of P0 declaration to the state.**
- **Conditions/exceptions:** 45-day deadline is absolute — missing it forfeits ACRE with no recourse. Micro-entrepreneurs do not fill cadre 3.
- **Financial risk:** HIGH — ACRE typically halves social contribution rates for the first year (potentially hundreds to thousands of euros saved). Missing the 45-day window = entire benefit lost, no second chance.

---

## Article 3606432 — Non-Accepted Business Activities
- **Topic:** Exhaustive list of business activities that prevent account opening (or trigger account closure) at client-a.
- **Key facts:** Non-accepted categories include: associations, political/religious organisations, financial asset management (gestionnaire de patrimoine), fund management, factoring, payment services/prepaid card sales, sexual activities (pornography, massage, striptease), tobacco sales, cannabis/drugs/nitrous oxide, weapons/war vehicles, auctions/art galleries, pharmacies, MLM/pyramid schemes, casinos/gambling/gaming, cartomancy/astrology, **cryptocurrencies** (trading, exchange, investment, mining, NFT), trading/brokerage/forex/precious metals/gems platforms, bulk SIM card sales, jewellery manufacturing/sales, CEE (energy savings certificate) activities including insulation, online file sharing, reputational harm activities, mining/fossil fuels/oil extraction. This list is non-exhaustive. If account is already open with a prohibited activity, client-a may terminate the relationship.
- **Conditions/exceptions:** Even partial overlap of a company's objet social with this list may cause rejection. Crypto personal investing (not professional) is tolerated separately (see article 5124267).
- **Financial risk:** Low from a direct financial standpoint — but account closure of an active business causes severe operational disruption. A chatbot that fails to flag eligibility issues could cause a user to open an account and later face unexpected closure.

---

## Article 3674717 — Paying or Being Paid by Traite or LCR (Bill of Exchange)
- **Topic:** client-a does not support traite (lettre de change) or LCR (lettre de change relevé) — deferred payment instruments used between professionals.
- **Key facts:** A traite is a deferred payment instrument; non-payment generates an automatic adverse bank filing (protêt). **client-a does not accept or issue traites** — incoming traite requests are automatically returned as unpaid to the issuer without warning to the client-a account holder. Entrepreneurs using client-a must specify accepted payment methods on invoices and contracts. Accepted at client-a: SEPA and FX transfers (no limit), instant transfers, card (up to €500/payment), cheque (up to €5,000/deposit), cash (up to €2,500/deposit).
- **Conditions/exceptions:** Traite rejection is automatic and silent — the client-a customer is not proactively notified that an incoming traite was rejected.
- **Financial risk:** Moderate — a client-a user who agrees to receive payment by traite from a client will have it silently rejected, potentially creating a late-payment dispute without realising the traite was returned. Must not mention traite as a payment method in contracts.

---

## Article 3760789 — How to Write a FAQ Article
- **Topic:** Internal editorial guidelines for client-a's content team on writing help centre articles.
- **Key facts:** This is an **internal client-a content guide** — not customer-facing. Covers formatting rules (titles as questions, emojis, headers, bullet points), tone, and writing style. References Notion for more general guidelines.
- **Conditions/exceptions:** Not intended for customers — describes internal workflows.
- **Financial risk:** None — internal document; should not be indexed in the customer-facing RAG pipeline.

---

## Article 3925407 — [Covid-19] Cheque Processing Suspension
- **Topic:** Temporary suspension of cheque encashment during the COVID-19 lockdown.
- **Key facts:** client-a temporarily suspended cheque processing during the COVID-19 lockdown (2020). Users were asked to keep their cheques and wait. This is a **fully outdated, COVID-era article** — cheque processing was restored long ago.
- **Conditions/exceptions:** Entirely obsolete.
- **Financial risk:** None — but surfacing this article could mislead users into thinking cheques are still unavailable at client-a. Should not be indexed.

---

## Article 4119056 — How to Number Quotes (Devis)
- **Topic:** Rules (or lack thereof) for quote numbering, and best-practice recommendations.
- **Key facts:** Quote numbering is **not legally mandatory** (unlike invoice numbering, which must follow strict sequential rules). Entrepreneurs are free to use any system. Recommended: unique number per quote, consecutive/chronological sequence, a distinct prefix (e.g. "D-01"), avoid deleting quotes and keep them as long as possible.
- **Conditions/exceptions:** Important contrast: invoice numbering IS legally required and must be strictly sequential without gaps — this does not apply to quotes.
- **Financial risk:** None.

---

## Article 4147470 — Gambling and Sports Betting: What You Need to Know
- **Topic:** client-a's policy on gambling and sports betting transactions on a professional account.
- **Key facts:** Gambling/sports betting is not accepted as a primary business activity — use a personal account. Very small bets at the national lottery or state-approved sites (ARJEL/ANJ) are tolerated if: (1) amounts are very small relative to company CA; (2) not a regular activity; (3) the company manages all accounting reconciliation itself (client-a provides no assistance); (4) any winnings over **€200** are accompanied by a justification document. Non-compliance with these conditions can lead to **account closure**.
- **Conditions/exceptions:** The €200 threshold for mandatory justification is key. "Very small" and "not regular" are qualitative — no exact thresholds are given.
- **Financial risk:** Low — misunderstanding the tolerance conditions could lead to account closure. A chatbot must not suggest that gambling transactions are freely acceptable on a client-a account.

---

## Article 4243851 — Collection ID, Not an Article
_4243851 is an Intercom collection (section) ID, not an article. No analysis._

---

## Article 4323055 — Foreign Nationality and Micro-Entrepreneur Registration
- **Topic:** Whether non-French nationals can register as auto-entrepreneurs in France and what documents are required.
- **Key facts:** EU/EEA/Swiss nationals: same rules as French nationals — no additional document required. Non-EU nationals: must hold a titre de séjour (residence permit). Accepted: permanent resident card, temporary resident card with work authorisation. Not accepted: student visa; salarié visa (work permit tied to a specific employer — allows working in France but not creating an independent business, though some prefectural tolerance exists in practice). Non-EU nationals cannot register with a tourist visa or any stay without work authorisation.
- **Conditions/exceptions:** Salarié visa holders are in a grey zone — the article notes some prefectural tolerance but does not endorse it as a valid path. A chatbot should not advise a salarié visa holder to simply register.
- **Financial risk:** Moderate — advising an ineligible foreigner to register could lead to URSSAF registration being refused or revoked, with back-contributions owed.

---

## Article 4345589 — Artiste-Auteur: Social Contributions and Filing
- **Topic:** How artiste-auteur (author/artist) self-employed workers pay URSSAF contributions and which body manages them.
- **Key facts:** Since January 2020, URSSAF Limousin manages all artiste-auteur contributions (replacing Maison des Artistes for visual artists and AGESSA for authors/composers). Contributions are paid quarterly (4 times per year). Two income regimes: BNC (bénéfices non commerciaux) or T&S (traitements et salaires). Specific portals: visual artists still register with Maison des Artistes as a professional association (not for cotisations); authors/composers register with AGESSA as association (not for cotisations). Cotisation declarations and payments are all via URSSAF Limousin regardless.
- **Conditions/exceptions:** Maison des Artistes and AGESSA still exist as professional bodies but no longer collect contributions. A chatbot using pre-2020 information would misdirect users to defunct payment processes.
- **Financial risk:** Moderate — directing an artiste-auteur to pay contributions to the wrong body post-2020 will result in missed URSSAF payments, late penalties, and contribution gaps.

---

## Article 4432945 — Quote Refused by a Client
- **Topic:** How to handle a quote that a client has declined.
- **Key facts:** Two options in the client-a invoicing tool: (1) Mark as "refusé" — archives the quote permanently; (2) Mark as "doit être corrigé" — triggers automatic duplication of the quote for editing and resubmission. There is no bulk-refuse action; each quote is handled individually.
- **Conditions/exceptions:** "Refusé" is irreversible archiving. To re-use the content, choose "doit être corrigé" instead.
- **Financial risk:** None — purely UI/workflow guidance.

---

## Article 4433229 — Converting a Quote to an Invoice
- **Topic:** How to transform an accepted quote into an invoice in the client-a invoicing tool.
- **Key facts:** Change the quote status to "accepté" — a "transformer en facture" option then appears. The resulting invoice inherits all quote line items and details.
- **Conditions/exceptions:** The transform option is only available after setting status to "accepté". A quote in any other status cannot be directly transformed.
- **Financial risk:** None — purely UI/workflow guidance.

---

## Article 4433528 — Modifying a Quote
- **Topic:** How to edit a quote after it has been sent.
- **Key facts:** Change quote status to "doit être corrigé" — client-a automatically duplicates the quote as a new draft for editing. The original quote is archived. Edit the new duplicate and resubmit.
- **Conditions/exceptions:** Direct editing of a sent quote is not possible; duplication is the only path.
- **Financial risk:** None — purely UI/workflow guidance.

---

## Article 4448791 — Which Companies Can Open a client-a Account
- **Topic:** Eligible and ineligible legal forms for opening a client-a professional account.
- **Key facts:** Eligible: SASU, SAS, SARL, SCI, EURL, EI (entreprise individuelle, including EIRL), micro-entreprise. Not eligible: associations (loi 1901). No other entity types are currently supported.
- **Conditions/exceptions:** SCI (société civile immobilière) is explicitly included. Associations are explicitly excluded.
- **Financial risk:** None — factual eligibility information.

---

## Article 4448820 — Who Founded client-a
- **Topic:** Company founding history and French RIB guarantee.
- **Key facts:** client-a was co-founded by Nicolas Reboud and Raphaël Simon in 2017. client-a is a French établissement de paiement, guaranteeing a French RIB (IBAN starting with FR).
- **Conditions/exceptions:** None.
- **Financial risk:** None — purely informational.

---

## Article 4556245 — Updating Your Address and Email
- **Topic:** How to update home address, business address, and email on a client-a account.
- **Key facts:** Home address: self-service update directly in the client-a app. Business address: requires uploading an updated Sirene statement (extrait de situation) or Kbis — cannot be changed without a document. Email: can only be changed from the web app (not the mobile app); enter new email, confirm by clicking the link sent to it.
- **Conditions/exceptions:** Business address change requires official documentation; app self-service is not available for it. Email change is web-only — the mobile app does not offer this option.
- **Financial risk:** None — procedural guidance.

---

## Article 4576890 — Associate Registration Tutorial
- **Topic:** Step-by-step guide for a company associate to activate their client-a access.
- **Key facts:** Web-only process (not available on mobile). Steps: (1) Click the invitation link received by email; (2) enter phone number and email address; (3) set a 4-digit PIN; (4) enter SMS verification code. Access is activated once all steps are complete.
- **Conditions/exceptions:** Only accessible via the email invitation link; cannot self-register. Mobile app cannot be used for initial registration.
- **Financial risk:** None — onboarding tutorial.

---

## Article 4593291 — Titulaire vs Admin Roles on a client-a Account
- **Topic:** Difference in permissions between account titulaire (owner) and admin associates.
- **Key facts:** Titulaire: full rights including changing the subscription plan and closing the account. Admin: all same rights as titulaire except cannot change subscription or close the account. Both can make payments, manage cards, access transactions, and invite team members.
- **Conditions/exceptions:** Only the titulaire can change plan or close the account — an admin cannot do either even if delegated verbally.
- **Financial risk:** None — role/permission information.

---

## Article 4596122 — Ordering a Card for an Associate
- **Topic:** How to order a bank card for a company associate on client-a.
- **Key facts:** Associates can receive their own client-a Mastercard. Card ordering is managed by the account titulaire or an admin. The article references legacy "client-a Entreprise" plan naming and old per-card pricing (€4/€6 per extra card) — this content appears outdated and incomplete (article body ends with "etc."). Current plan-based card pricing should be verified against the current pricing articles.
- **Conditions/exceptions:** Article content is incomplete and references legacy plan names. Do not rely on the pricing figures cited here — use current subscription/pricing articles instead.
- **Financial risk:** Low — outdated pricing or plan names could mislead users about card costs.

---

## Article 4602240 — Why client-a Requests Justification for Operations
- **Topic:** Legal basis for client-a requesting justification documents for certain transactions (AML/CTF compliance).
- **Key facts:** client-a is legally required under Article L563-3 of the Code monétaire et financier to conduct due diligence on transactions. Both client-a and its partner Treezor bear this surveillance responsibility. Users must provide requested justification documents. Refusal to justify an operation can lead to: (1) suspension of the operation; (2) termination of the commercial relationship; (3) report to authorities (Tracfin). This is not optional or negotiable.
- **Conditions/exceptions:** client-a cannot legally waive this requirement. The obligation applies regardless of transaction size or client history.
- **Financial risk:** Moderate — users who do not understand this legal obligation may be caught off-guard by account suspension or closure when they refuse to provide documents.

---

## Article 4602862 — Why client-a May Terminate a Commercial Relationship
- **Topic:** Circumstances and process for client-a closing a customer's account.
- **Key facts:** Standard closure: 30-day advance notice required by law (Article L312-1 CMF); account balance transferred to another European bank account provided by the client. Immediate closure (without notice): if the client has violated client-a's CGU (terms of service) — no prior notice is required in this case. client-a is legally prohibited from disclosing the reason for closure if a fraud or money-laundering investigation is ongoing. Prohibited activities (per CGU) that can trigger immediate closure include high-risk or illicit activities listed in article 3606432.
- **Conditions/exceptions:** Immediate closure bypasses the 30-day notice entirely. client-a does not need to give a reason if an investigation is active.
- **Financial risk:** Moderate — users unaware of prohibited activities may face sudden account closure with no warning and no stated reason, causing immediate operational disruption.

---

## Article 4623245 — Anti-Fraud TVA Certification and client-a Invoicing
- **Topic:** Whether client-a's invoicing tool is subject to the anti-fraud TVA certification requirement (loi anti-fraude TVA 2018).
- **Key facts:** The anti-fraud TVA certification obligation applies exclusively to caisse enregistreuse (POS/cash register) systems and logiciels de caisse. It does NOT apply to invoicing tools. client-a's invoicing feature is explicitly an invoicing tool, not a caisse system, and is therefore NOT subject to this certification requirement. Users do not need to obtain or verify a certification for client-a's invoicing.
- **Conditions/exceptions:** If a business uses a separate POS system alongside client-a invoicing, that POS system may still be subject to the obligation independently.
- **Financial risk:** None — this article clarifies a common misunderstanding; knowing this prevents unnecessary compliance anxiety.

---

## Article 4623268 — How to Make a Complaint to client-a
- **Topic:** The formal complaint process and escalation paths for client-a customers.
- **Key facts:** Step 1: contact client-a customer support via chat. Step 2: if unresolved, submit a formal written complaint via client-a's online form or by post to: client-a, 122 rue Amelot, 75011 Paris. client-a must acknowledge the complaint within 24 hours and resolve within 15 working days (maximum 35 working days for complex cases). Important exclusion: **professional account holders (entreprises) are NOT eligible for banking mediation (médiation bancaire)** — this is reserved for particuliers. client-a's mediator contact is provided for completeness but cannot be used by business customers.
- **Conditions/exceptions:** Businesses cannot escalate to banking mediation regardless of complaint outcome. The 15/35 working day resolution window is a regulatory maximum, not a service-level target.
- **Financial risk:** Low — a chatbot that incorrectly tells a business customer they can use banking mediation sets false expectations and wastes time.

---

## Article 4703268 — Dormant Account Policy
- **Topic:** What happens to a client-a account that becomes inactive and the associated fees.
- **Key facts:** An account becomes dormant after **9 consecutive months** of inactivity. Subscription debits do NOT count as account activity. Dormant status: subscription is suspended (no further plan charges). After **1 year** of inactivity: a flat fee of **€25/year** is charged. The account is reactivated automatically by any login or any financial movement (credit, debit, or transfer).
- **Conditions/exceptions:** The 9-month inactivity clock ignores subscription debits — a user paying their subscription but doing nothing else will still trigger dormancy. The €25/year fee kicks in after the full year mark, not at the 9-month mark.
- **Financial risk:** Low — users unaware of the €25/year fee may be surprised; the subscription-not-counting-as-activity rule is counter-intuitive.

---

## Article 4725622 — Documents Required to Prove ACRE Eligibility
- **Topic:** Complete list of documents needed to prove eligibility for each of the 9 ACRE eligible categories.
- **Key facts:** Required baseline for all applicants: P0 registration form, ACRE application form (Cerfa 13584), and a copy of national ID. Additional documents vary by eligibility category: job-seeker (ARE/AREF) → attestation Pôle Emploi; RSA recipient → attestation CAF; under-26 (or under-30 if disabled) → just ID; beneficiary of minimum disability income → attestation; employee in judicial restructuring/liquidation → court document; CAPE beneficiary → CAPE contract; QPV resident → certificate of residence; returning from parental leave → certificate from previous employer.
- **Conditions/exceptions:** This article is the document companion to article 3606170 (ACRE application process). The 45-day filing deadline from P0 is covered there. Missing even one document from the required list will result in application rejection.
- **Financial risk:** None — the risk (missing the 45-day deadline) is covered in article 3606170; this article is purely a document checklist.

---

## Article 4838783 — Creating a Professional Space on impots.gouv.fr
- **Topic:** How to create a professional taxpayer account on impots.gouv.fr, required for CFE payment and TVA declarations.
- **Key facts:** Required from year 2 for CFE payment; required from year 1 if TVA-liable or if the business has been assigned an EU VAT number. Steps: register at impots.gouv.fr with SIREN and email → receive email confirmation within 72 hours → **activation code arrives by post within 2 weeks** → **must be entered within 60 days of the email confirmation date**. If the 60-day window expires, the entire registration process must be restarted (with a 60-day wait before using the same email or SIREN again). If the email address was previously used on impots.gouv.fr, it will be blocked and a different email must be used.
- **Conditions/exceptions:** The 60-day activation deadline is absolute — missing it resets the process with an additional 60-day delay before retry. This can block CFE payment entirely in year 2. TVA-liable businesses need this from year 1 and cannot file TVA without it.
- **Financial risk:** Moderate — missing the 60-day activation code window means CFE cannot be paid (late payment penalties) and TVA declarations may be missed (fiscal penalties). A chatbot must proactively mention the 60-day deadline.

---

## Article 4854578 — How to Change Your Activity (Navigation Article)
- **Topic:** Navigation/routing article directing users to the correct process for changing their business activity.
- **Key facts:** Two paths: (1) changing within the same liberal activity category → see article 4854613 (URSSAF autoentrepreneur.urssaf.fr process); (2) changing to an activity under a different CFE (Centre de Formalités des Entreprises) → see article 4855374 (P2-P4 form process). This article itself contains no procedural content.
- **Conditions/exceptions:** The routing depends on whether the activity change stays within the same CFE jurisdiction.
- **Financial risk:** None — routing article only.

---

## Article 4854613 — Modifying a Liberal Activity (URSSAF)
- **Topic:** How to change a liberal (professional services) activity declaration with URSSAF as a micro-entrepreneur.
- **Key facts:** Process is done via autoentrepreneur.urssaf.fr. Use form 67P (modification of activity). **Critical step:** after filling in all fields, the user MUST click the "Télédéclarer" button to actually submit the declaration. Filling in the form without clicking Télédéclarer does NOT submit it — the declaration is not registered. Processing time: 1 to 4 weeks. The new activity is effective from the declaration date.
- **Conditions/exceptions:** The Télédéclarer button is the final and mandatory submission step. Users frequently miss it, leaving their declaration in a draft/incomplete state without knowing it.
- **Financial risk:** Moderate — if the user fails to click Télédéclarer, their activity change is not registered with URSSAF. Operating under an unregistered activity can create compliance issues with cotisations and tax declarations.

---

## Article 4855374 — Changing Activity When It Falls Under a Different CFE
- **Topic:** Process for changing business activity when the new activity is managed by a different CFE (Centre de Formalités des Entreprises) than the current one.
- **Key facts:** Must complete form P2-P4 (modification/cessation declaration). The form must be sent to BOTH the original CFE (for cessation of old activity) and the new CFE (for registration of new activity). Required documents vary by activity type: commercial activities → Chambre de Commerce; liberal activities → URSSAF; artisanal activities → Chambre de Métiers. All communications to CFEs must be sent by registered letter with acknowledgement of receipt (AR).
- **Conditions/exceptions:** Sending to only one CFE will result in the old activity remaining active or the new one not being registered. Registered letter with AR is mandatory — regular mail is not sufficient proof.
- **Financial risk:** Moderate — failure to notify both CFEs creates a situation where the entrepreneur is registered for the wrong activity, leading to incorrect cotisation calculations and potential regulatory violations.

---

## Article 4877489 — Masking Your Business from the SIREN Public Registry
- **Topic:** How a micro-entrepreneur can hide their personal information from the public SIREN registry (INSEE).
- **Key facts:** Masking (non-diffusion) is done via the INSEE France Connect portal. The change takes effect within 24 hours. Important limitation: data already scraped by third-party websites (Google, Societe.com, etc.) before the masking request remains publicly accessible on those sites — masking does not retroactively remove already-scraped data.
- **Conditions/exceptions:** Non-diffusion only prevents future lookups on INSEE; it cannot reach third-party databases that have already copied the information.
- **Financial risk:** Low — users expecting complete privacy after masking may be disappointed when their data still appears on Google; this sets realistic expectations.

---

## Article 4877782 — EU Imports and Exports as a Micro-Entrepreneur
- **Topic:** Customs and VAT obligations for micro-entrepreneurs buying from or selling to other EU countries (goods and services).
- **Key facts:**
  - **Goods imported from EU:** DEB (Décorpus-ation d'Échanges de Biens) only required if annual purchases exceed **€460,000**. An EU VAT number is required if: (a) annual EU professional purchases exceed **€10,000**, or (b) the business is not in franchise de base.
  - **Services exported to EU (DES):** A **DES (Décorpus-ation Européenne de Services)** must be filed **every month** with French customs (douanes). Additionally, an EU VAT number is always required for service exports to EU professionals. This obligation applies even to micro-entrepreneurs in franchise de base.
  - **Services imported from EU:** An EU VAT number is required, plus the business must file a TVA declaration (autoliquidation — the business self-declares the VAT due).
- **Conditions/exceptions:** The DES obligation for service exports is monthly, unconditional, and applies regardless of VAT status. Missing a DES filing = customs violation. The €10,000 threshold for goods import VAT number applies per calendar year.
- **Financial risk:** HIGH — the monthly DES for EU service exports is frequently overlooked by micro-entrepreneurs (especially those in franchise de base who assume they have no EU obligations). Missing filings constitute customs violations with fines. A chatbot that fails to mention DES when a user asks about billing EU clients is providing dangerously incomplete advice.

---

## Article 4879145 — Non-EU Import/Export as a Micro-Entrepreneur
- **Topic:** Customs and administrative obligations for micro-entrepreneurs importing from or exporting to non-EU countries (pays tiers).
- **Key facts:** Both importers and exporters must obtain an **EORI number** (Economic Operator Registration and Identification) from the customs authority (douanes); can be requested online or by mail. **Import from non-EU country:** must file a DAU (Décorpus-ation d'Admission Unique) on the Delt@ application at douane.gouv.fr; TVA is due on import; customs duties apply based on product classification, origin, and value; TVA cannot be deducted if the entrepreneur is in franchise de base. **Export to non-EU country:** must file a DAU on Delt@; goods exports to non-EU countries are VAT-exempt (exonérées TVA); exports must be recorded in accounting books.
- **Conditions/exceptions:** The franchise de base VAT exemption does not exempt from paying import TVA. Exports are only VAT-exempt with proper customs declaration (DAU). The EORI number is mandatory for both import and export — operating without one is a customs violation.
- **Financial risk:** Moderate — missing the EORI registration or failing to file DAUs constitutes customs violations with fines. A chatbot must distinguish this article (non-EU) from article 4877782 (EU-specific rules, which has different and more complex obligations).

---

## Article 4910941 — Choosing and Protecting a Commercial Name
- **Topic:** How a micro-entrepreneur can choose, protect, and register a commercial name (nom commercial / marque).
- **Key facts:** A micro-entrepreneur's legal name is always their first + last name (no choice). A commercial name is optional — it has no legal value but serves as a brand. Protection: automatic from first use (limited to geographic area and sector); broader protection requires INPI trademark deposit (€190, valid 10 years). Availability must be checked before use: by product/service class (same class = conflict; different class = OK), phonetic similarity, and intellectual resemblance (not just exact spelling). Must declare commercial name to CFE on form P0 (section 10 for commercial/artisanal; section 9 for liberal activities). Cheques: commercial name may appear only if the legal first+last name is also present. INPI does not monitor infringement — the owner must watch and file oppositions themselves.
- **Conditions/exceptions:** INPI registration doesn't guarantee automatic enforcement. Protection without INPI deposit is geographically limited.
- **Financial risk:** Low — omitting the cheque rule (legal name required alongside commercial name) could lead to rejected cheques.

---

## Article 5124267 — Cryptocurrency: What You Need to Know
- **Topic:** client-a's policy on cryptocurrency transactions and related activities.
- **Key facts:** client-a does not accept cryptocurrency transactions. Activities directly linked to crypto (blockchain, mining, etc.) are not accepted as they require regulatory compliance procedures client-a has not implemented. It is also not permitted to invest client funds in crypto platforms or receive crypto payments on a client-a account. Tolerated exceptions: (1) using personal funds to invest in personal crypto accounts; (2) cryptocurrency investment advisory activities.
- **Conditions/exceptions:** The two tolerated cases are specifically defined — they relate to personal investments and advisory, not to running a crypto exchange or accepting crypto payments.
- **Financial risk:** Low — a user incorrectly told that crypto transactions are acceptable could face account closure. The chatbot must distinguish the prohibited (direct crypto transactions) from the tolerated (advisory, personal investing).

---

## Article 5144541 — Fraudulent Use of a Virtual Card
- **Topic:** What to do if a virtual card is used fraudulently.
- **Key facts:** Virtual card numbers are stored by merchant platforms and can be stolen if a platform is hacked. The article body is **truncated in the knowledge base** — content ends mid-sentence ("Si vous constatez une transaction qui n'a pas été ef..."). For the complete virtual card fraud response procedure, see article 5227769 (which covers blocking the card and filing a Perceval declaration) and article 1470511 (which has the full card fraud contestation process).
- **Conditions/exceptions:** Article content is incomplete — do not rely on this article alone.
- **Financial risk:** Low — the incomplete content makes this article unreliable; the chatbot should direct users to 5227769 or 1470511 for actionable guidance.

---

## Article 5227718 — Why My Transfer Was Not Validated
- **Topic:** Why client-a may cancel or hold a transfer and what justification documents are required.
- **Key facts:** Transfers can be blocked when a justification document is missing, non-compliant, or when additional information is awaited. Required documents by transfer type: salary payment → payslip; supplier payment → corresponding invoice; dividend distribution → PV d'AG (shareholder meeting minutes) + official RIB of beneficiary; inter-company cash transfer → signed trésorerie convention + official RIB of recipient account. Documents should be sent to mesdocuments@client-a.fr with an explanation of the situation.
- **Conditions/exceptions:** Providing an informal justification (e.g., a simple note) is not sufficient — official documents matching each transfer type are required.
- **Financial risk:** None — procedural guidance, but important for users whose transfers are blocked.

---

## Article 5227769 — Contesting an Online Card Payment
- **Topic:** How to contest a fraudulent online card transaction.
- **Key facts:** If not at origin of the transaction: (1) **immediately block the card** in the client-a app (Plus > Carte bancaire > report as stolen); (2) file a declaration on the government Perceval portal (service-public.fr) against bank card fraud; (3) fill in client-a's contestation form and send it with the Perceval declaration copy. On the Perceval form: select "Autre organisme" as the bank; the opposition number field is optional. Processing is sometimes lengthy due to verification procedures.
- **Conditions/exceptions:** Both the card block AND the Perceval declaration are required — the Perceval step cannot be skipped or delayed. Failure to block the card first may allow additional fraudulent charges before the contestation is reviewed.
- **Financial risk:** Moderate — omitting the Perceval declaration step will delay or prevent reimbursement of fraudulent charges. A chatbot must not suggest only blocking the card without also filing Perceval.

---

## Article 5230385 — Modifying the Card Withdrawal Limit
- **Topic:** How to adjust the ATM withdrawal limit on a client-a card.
- **Key facts:** Withdrawal limits by plan:
  - Free: €400/24h daily, €500 on a rolling 30-day period
  - Start: €400/24h daily, €1,500 on a rolling 30-day period
  - Plus: €400/24h daily, €2,500 on a rolling 30-day period
  - Business: €400/24h daily, €2,500 on a rolling 30-day period
  The default is set to the plan maximum. Users can only **decrease** their limit — they cannot increase it above the plan ceiling. Modification is done in the client-a app (Plus > Carte Bancaire > select card > Plafonds) or on the web app. Note: individual ATMs often impose their own limit (200–300€) independently of client-a.
- **Conditions/exceptions:** Lowering the limit is irreversible via self-service up to the plan ceiling — the ceiling itself is fixed by the plan.
- **Financial risk:** Low — citing wrong plan limits could lead to unexpected ATM failures.

---

## Article 5263421 — Transfer Not Received
- **Topic:** Troubleshooting a SEPA transfer that hasn't appeared on a client-a account.
- **Key facts:** Normal processing time: 2–3 working days (Monday–Friday, excluding public holidays). Weekend transfers queue until Monday and arrive by Wednesday at the latest. client-a has no visibility on incoming transfers until they are received. If no credit after 4+ working days: ask the issuing bank to verify: (1) correct RIB (IBAN + BIC); (2) it is a SEPA transfer — **client-a does not accept international SWIFT transfers**; (3) transfer has actually been executed. If all correct: request an attestation de virement from the issuing bank (must contain RIB, amount, date, end-to-end/EBA reference); client-a will investigate with the SEPA network. Banking regulations allow the issuing bank to defer or refuse a transfer — the sender must contact their own bank for details.
- **Conditions/exceptions:** SWIFT (international) transfers are not supported by client-a — they will be rejected and must be resent as SEPA. This is a common source of missing transfers.
- **Financial risk:** Low — the SWIFT vs SEPA distinction is important; a chatbot that doesn't mention it leaves users puzzled by missing international transfers.

---

## Article 5276083 — Card Blocked During 3D Secure Online Payment
- **Topic:** Why a client-a card gets blocked during 3D Secure verification.
- **Key facts:** A card is temporarily blocked after **3 incorrect 3DS code entries** (the SMS confirmation code). If the user made the errors themselves: contact client-a support to unblock the card. If the user was NOT at the origin of the errors: a third party attempted multiple fraudulent payments but failed 3DS — in this case, permanently block the card (report stolen: Plus > Carte bancaire > Bloquer > Ma carte a été volée) and order a new card.
- **Conditions/exceptions:** Temporary block (user errors) vs permanent block (suspected theft) are two distinct responses. A user who was the victim should not simply request unblocking — they should declare the card stolen.
- **Financial risk:** None — security guidance. Important to distinguish the two scenarios clearly.

---

## Article 5279734 — Possible Additional Fees (Company Creation)
- **Topic:** Variable extra fees that may arise during micro-enterprise creation through client-a.
- **Key facts:** Most cases: no extra fees beyond the chosen client-a pack. Some CFEs charge variable additional fees which client-a cannot predict or circumvent. Possible triggers: (1) an error in the dossier; (2) being married/PACSed under community of assets; (3) some Chambres des Métiers (CMA) charge RM (Répertoire des Métiers) inscription fees; (4) certain regional CMAs (e.g., Brittany); (5) having a prior non-closed company. If extra fees arise: user can choose to continue or abort. **Important:** if the process has already been initiated, the client-a Start pack is **not refundable**. Greffe fees must be paid to avoid surcharges; CMA dossier fees can be cancelled if the user abandons.
- **Conditions/exceptions:** The Start pack non-refundability applies once administrative steps have begun — users must be aware before starting.
- **Financial risk:** Low — users who discover unexpected extra fees and want to stop should know the client-a pack is not refunded even if they abort.

---

## Article 5281010 — Why ATM Withdrawals Fail
- **Topic:** Common causes of failed cash withdrawals with a client-a card.
- **Key facts:** Main causes: (1) card not activated; (2) insufficient funds; (3) withdrawal limit exceeded. Limits: €400/day (daily); €1,500/30-day rolling for Basic plan users; €2,500/30-day rolling for Premium/Business plan users (note: article uses old plan names Basic/Premium — corresponds to current Start vs Plus/Business). **Important behaviour:** if a withdrawal fails at an ATM but the machine didn't dispense cash, the transaction appears as a pending "empreinte bancaire" (bank imprint) — funds are held and automatically released within **11 working days** maximum. Funds are unavailable until the imprint is lifted; client-a cannot accelerate this.
- **Conditions/exceptions:** The 11-working-day hold on failed withdrawal funds is critical cash-flow information. The article uses legacy plan names (Basic/Premium) — the limits correspond to Start (1,500€) and Plus/Business (2,500€).
- **Financial risk:** Low — a user unaware of the 11-day hold may think funds are lost; the Free plan limit (500€) is not mentioned in this article — use article 5230385 for the complete per-plan limits.

---

## Article 5281040 — SEPA Direct Debit Appearing Early on Account
- **Topic:** Why a SEPA direct debit appears debited from the account before the expected payment date.
- **Key facts:** client-a's banking partner checks the account balance at the moment the creditor sends the debit request — not at the actual scheduled debit date. If a creditor sends the request 10 days in advance, the balance is verified 10 days before the expected date. Solutions: (1) deposit funds on the account before the debit request is submitted; (2) ask the creditor to send the request closer to the actual debit date.
- **Conditions/exceptions:** This behaviour is determined by the creditor's submission timing, not by client-a. Users cannot change it unilaterally.
- **Financial risk:** None — explanatory; helps users avoid accidental insufficient-funds situations.

---

## Article 5341474 — Company Dormancy (Mise en Sommeil)
- **Topic:** How to declare a temporary suspension of business activity, and the implications for a client-a account.
- **Key facts:** Two distinct concepts: (1) **company dormancy** (cessation temporaire d'activité / mise en sommeil) and (2) **client-a account dormancy** — these are separate and must not be confused. Company dormancy procedure: for EI (entreprise individuelle) → form P2 to the relevant CFE, marking "Cessation totale d'activité avec maintien de l'immatriculation au RCS au RM" in section 4B, specifying it is temporary and giving the reason in section 17. For a société → form M2, indicating the dormancy date in section 8 "Mise en sommeil par cessation totale d'activité." **client-a account consequence:** once the company is dormant, the client-a account cannot be used (it is strictly a professional account); client-a will require the account to be closed.
- **Conditions/exceptions:** Dormant company ≠ dormant client-a account. If company becomes dormant, the client-a account must be closed entirely — it cannot simply be paused as a non-commercial personal account.
- **Financial risk:** Low — a user who confuses company dormancy with account dormancy may think they can keep using the client-a account, leading to compliance issues.

---

## Article 5352549 — Criteria for Engagement Bonus on a client-a Loan
- **Topic:** Conditions under which a client-a professional loan qualifies for a reduced interest rate (engagement bonus).
- **Key facts:** At least **2 criteria** from the following 4 categories must be met to qualify for a reduced rate. Categories: **Environment** (energy efficiency, waste reduction, water reduction, ecological purchasing policy, eco-training, formal environmental policy, impact evaluation, carbon footprint goals, etc.); **Society** (positive social impact, inclusive hiring process, equitable workplace, salary ratio policy, diversity training, local purchasing, civic engagement); **Employees** (professional training policy, transparent equitable pay with gender equality, employee evaluation process, parental leave policy, satisfaction measurement); **Governance** (criteria relating to company governance practices).
- **Conditions/exceptions:** Meeting criteria requires formal policies or programmes — not informal practices. Requires meeting 2 criteria across any categories.
- **Financial risk:** None — informational product feature; knowing this helps users potentially access a better rate.

---

## Article 5356202 — Instalment Payments with client-a Card
- **Topic:** Whether the client-a professional card can be used for instalment payment (paiement en plusieurs fois) with credit providers.
- **Key facts:** Some credit organisations (e.g., Oney) refuse professional cards for instalment payment. client-a cannot guarantee in advance whether a given merchant's instalment option will work with the client-a card. No workaround is available from client-a's side — users are advised to pay in full (comptant) instead.
- **Conditions/exceptions:** This limitation is set by the credit provider, not by client-a.
- **Financial risk:** None — informational; prevents users from counting on instalment payments for cash-flow purposes.

---

## Article 5393688 — Why Amazon Business Doesn't Accept client-a
- **Topic:** Why Amazon Business rejects client-a accounts as a payment method.
- **Key facts:** client-a is an agent of Treezor (a PSP licensed by ACPR). Amazon Business blocked all Treezor agents due to fraud/abuse by other agents in various countries. client-a contacted Amazon to be whitelisted as a trusted provider — the article states they were awaiting Amazon's response. Users affected can contact client-a at promis_on_repond@client-a.fr for an alternative solution. Note: this article appears to reflect an in-progress situation and may be outdated.
- **Conditions/exceptions:** The Amazon Business restriction applies to all Treezor agents, not specifically to client-a. The situation may have resolved since the article was written.
- **Financial risk:** Low — users relying on Amazon Business for procurement may be caught off-guard; the contact email provides a path forward.

---

## Article 5544130 — Professional Liability Insurance (RC Pro)
- **Topic:** Whether and when professional liability insurance (Responsabilité Civile professionnelle) is required.
- **Key facts:** RC Pro is **mandatory** for 60 regulated professions (professions réglementées), including: legal professionals (avocats, huissiers, notaires); financial professionals (bankers, insurance agents, accountants); health professionals (doctors, pharmacists, nurses, osteopaths, etc.); well-being, real estate, media, and personal services professionals. For all others, RC Pro is not legally required but is strongly recommended. For EI/micro-entrepreneurs specifically: unlike a société, an EI does not protect personal assets — RC Pro provides additional protection for personal property (though primary residence is already protected by law). client-a partners with Assurup to offer RC Pro online in 3 minutes via the app (Plus > Assurances > RC pro).
- **Conditions/exceptions:** The list of 60 mandatory professions is not exhaustive — users in regulated fields must verify their specific obligation.
- **Financial risk:** Moderate — a chatbot that fails to flag the mandatory RC Pro requirement for a regulated profession leaves the user exposed to uninsured liability claims that could threaten their business or personal assets.

---

## Article 5585670 — Why client-a Has No Hidden Fees
- **Topic:** Marketing/informational article about client-a's fee transparency.
- **Key facts:** Article body in the knowledge base contains only "Démarrer mon inscription" — this is effectively a stub or empty marketing page with no substantive content.
- **Conditions/exceptions:** No factual content to analyze.
- **Financial risk:** None — empty stub; chatbot should not use this article as a source for fee information.

---

## Article 5627382 — Selfie Required for Certain Operations
- **Topic:** Why client-a requires a selfie (with ID) for account opening, closure, and certain sensitive operations.
- **Key facts:** A selfie + ID is required for: opening an account, closing an account, and certain sensitive operations (e.g., changing contact details). Legal basis: DSP2 (European Payment Services Directive 2) and RTS SCS standards, equivalent to in-branch identity verification at a traditional bank. Technology used: detects fake documents; matches selfie to ID photo. client-a principle: closing an account is no harder than opening one (symmetric experience).
- **Conditions/exceptions:** The selfie requirement cannot be waived — it is a regulatory obligation under DSP2.
- **Financial risk:** None — security/compliance information.

---

## Article 5697789 — Attaching a Receipt to a Transfer
- **Topic:** Which justification documents to attach to different types of outgoing transfers in the client-a app.
- **Key facts:** Required documents by transfer type: **salary payment** → payslip; **supplier payment** → corresponding invoice; **inter-company cash transfer** → signed trésorerie convention + official RIB of the recipient; **dividend payment** → PV d'AG (shareholder meeting minutes) + official RIB of recipient; **vehicle purchase** → order/invoice or signed price document (for private sales) + cession certificate + grey card copy + seller's official RIB. Documents should be attached promptly after initiating the transfer to ensure processing and validation by the banking partner.
- **Conditions/exceptions:** The "official RIB" requirement (as opposed to an informal account number) applies to several transfer types — an informal document is insufficient.
- **Financial risk:** None — compliance guidance; companion to article 5227718.

---

## Article 5779244 — Professional Credit Interest Rate
- **Topic:** Interest rates for client-a's professional loan product and how they compare to traditional banks.
- **Key facts:** client-a's professional credit rates range from **5.50% to 7.50%** (article also states "6 ou 7%" in practice), offered via partner Franfinance. Comparable traditional bank rates: ~3–4%, but those require personal or asset-based guarantees. client-a's higher rate reflects a **no-guarantee model**: no personal guarantee, no asset pledge, no balance sheets required — just basic company/project information. Loan decision and funds released within **72 hours** on average. Amount is confirmed upfront before application finalises. Reduced rate available for companies meeting at least 2 engagement criteria (see article 5352549).
- **Conditions/exceptions:** The 72-hour release is an average, not a guarantee. The rate range (5.50–7.50%) is set by Franfinance based on the applicant's situation.
- **Financial risk:** Moderate — citing the rate as simply "lower" or comparable to standard bank rates without context would mislead a user about the real cost of the loan. The no-guarantee trade-off must be explained alongside the rate.

---

## Article 5809667 — Who Are We (client-a Company Info)
- **Topic:** Brief company overview for client-a.
- **Key facts:** client-a was founded in 2017 by Nicolas Reboud and Raphaël Simon. 150,000+ customers. Paris-based (offices and customer service). Recognised as "Service Client de l'Année 2024." Holds B Corp certification. Has joined the Ageras group (European leader in accounting/finance management software for independents and small businesses) — detailed in companion article 10289941.
- **Conditions/exceptions:** None.
- **Financial risk:** None — purely informational.

---

## Article 5809680 — Data Security and Fund Protection
- **Topic:** How client-a protects client data and funds.
- **Key facts:** **Fund protection:** client funds are held in a cantonnement (segregated) account at Société Générale, outside client-a's own balance sheet. If client-a were to fail, client funds would be completely safe (no limit — cantonnement guarantees full protection). **FGDR (Fonds de Garantie des Dépôts et de Résolution):** Société Générale is a FGDR member — in the event of Société Générale's failure (not client-a's), the FGDR covers up to €100,000 per client. client-a **cannot** issue an "attestation de garantie de fonds." This two-layer protection model is standard for all European bank accounts.
- **Conditions/exceptions:** The €100,000 FGDR limit applies only to a failure of Société Générale (the cantonnement bank), not to a failure of client-a itself (which is covered by cantonnement with no limit). The two scenarios must not be conflated.
- **Financial risk:** Low — a chatbot that incorrectly says client funds are only guaranteed up to €100,000 understates the cantonnement protection in the event of client-a's own insolvency.

---

## Article 5809693 — How client-a's Customer Service Works
- **Topic:** client-a's customer service channels, hours, and plan-based access.
- **Key facts:** Available 7 days/week including weekends. Channels: (1) chat/email (7d/7; typically responds same day, may be next working day at peak times); (2) phone (request callback or call directly). **Phone support is not available for Free plan users** — only Start, Plus, and Business plans. Plus and Business plans benefit from **priority support** on the phone line. Recognised as "Élu Service Client de l'Année 2026" in the online banking for businesses category.
- **Conditions/exceptions:** Free plan users are limited to chat/email — they cannot call client-a support.
- **Financial risk:** None — service information, but important for users expecting phone support on a Free plan.

---

## Article 5809767 — What Is B Corp Certification?
- **Topic:** Explanation of the B Corp certification and client-a's status.
- **Key facts:** B Corp is an international label rewarding companies that aim to be "the best for the world" (not just best in the world). Evaluation covers 5 domains: governance, employees, community, environment, and clients. The certification process takes several months. client-a obtained B Corp certification in 2020 and continues annual improvement efforts.
- **Conditions/exceptions:** None.
- **Financial risk:** None — purely informational.

---

## Article 5817496 — Differences Between client-a Subscriptions
- **Topic:** Overview of client-a subscription plan differences.
- **Key facts:** **This article is outdated.** It references legacy plan names and prices: "client-a Basic" (€7.90 HT/month, 20 SEPA transfers, Mastercard Basic) and "client-a Premium" (€14.90 HT/month, 50 SEPA transfers, Mastercard Business World Debit with insurance coverage). Current client-a plans are Free, Start, Plus, and Business — as documented in articles 13419459 and 10490776. The pricing and plan names in this article do not match current offerings.
- **Conditions/exceptions:** Do not use this article as an authoritative source for current pricing or plan names — it predates the current plan structure.
- **Financial risk:** Moderate — a chatbot citing this article for pricing will give wrong prices and wrong plan names, leading to bad purchase decisions or incorrect financial expectations.

---

## Article 6007559 — Account Access on client-a (Empty Article)
- **Topic:** Account access overview.
- **Key facts:** Article body in the knowledge base is completely empty — no content.
- **Conditions/exceptions:** Empty stub.
- **Financial risk:** None — no content to analyse.

---

## Article 6015464 — How to Subscribe to client-a Business
- **Topic:** Step-by-step guide for upgrading to the client-a Business plan.
- **Key facts:** **Outdated article** — uses legacy plan names "client-a Basic" and "client-a Premium." Subscription change is only possible from the mobile app (not the web app). Steps: (1) update the client-a app; (2) go to Plus > "client-a Premium" and click "Obtenir client-a Premium"; (3) order premium cards (delivery ~10 days). Pro-rata pricing applies if upgrading mid-month (e.g., upgrading on the 15th = 50% old plan + 50% new plan for that month). Note: companies created via client-a with associates are subscribed to client-a Business by default (old naming).
- **Conditions/exceptions:** Article uses legacy plan names — the current flow and plan names differ. Plan change is mobile-only.
- **Financial risk:** Low — the pro-rata billing principle is valid but plan names and steps may not match the current UI.

---

## Article 6194187 — Why client-a Requires a French Proof of Domicile
- **Topic:** Legal basis and accepted documents for the French proof of address required to open a client-a account.
- **Key facts:** Required by AML/CTF law (blanchiment/financement du terrorisme). Mandatory: must be domiciled in France. Document must be less than 3 months old. Accepted documents: electricity/gas bill (EDF, Direct Energie), internet box bill (Orange/SFR/Bouygues/Free), last tax notice from impots.gouv (only if the company is already registered). If hosted by someone else: need signed/dated attestation d'hébergement from the host + host's ID (front and back) + host's proof of domicile. For multi-associate companies: these rules apply to all beneficial owners (bénéficiaires effectifs).
- **Conditions/exceptions:** Mobile phone bills are not accepted (only box/landline internet bills). The tax notice is only accepted if the company is already registered.
- **Financial risk:** None — onboarding requirement explanation.

---

## Article 6302531 — How to Access Your New client-a RIB
- **Topic:** How to find the new client-a RIB/IBAN after the 2022 account migration.
- **Key facts:** Migration context: client-a became its own établissement de paiement. New BIC: **SNNNFR22** (replacing old TRZOFR21). The entire IBAN has changed — not just the BIC. Access via: mobile app (Plus > Partager mon RIB client-a) or web app (Banque > Information bancaires). After obtaining the new RIB: (1) send to all clients who pay by wire; (2) update all organisations making direct debits (via their client portals or by asking your accountant).
- **Conditions/exceptions:** The IBAN has changed entirely — users must transmit the full new IBAN to all counterparties, not just the BIC.
- **Financial risk:** Low — continuing to give out the old IBAN could cause missed incoming payments.

---

## Article 6302622 — Email Template: Banking Details Change Notification
- **Topic:** Copy-paste email template for notifying clients and creditors of a new IBAN.
- **Key facts:** Context: RIB migration (July 2022). Template covers: notification of banking detail change, request for confirmation of update. Reminder: attach the new RIB PDF to the email; optionally include the full IBAN in the email body to simplify for the recipient.
- **Conditions/exceptions:** Template is migration-specific but reusable for any RIB change scenario.
- **Financial risk:** None — template document.

---

## Article 6309428 — How to Update Banking Details for Direct Debits
- **Topic:** General process for updating IBAN with organisations that debit client-a directly.
- **Key facts:** Most organisations allow self-service IBAN update in their client portal. **Critical distinction:** For standard SEPA CORE debits (phone/utilities/etc.) → update IBAN in creditor's portal; the existing mandate in client-a auto-updates. For **SEPA B2B mandates** (taxes, URSSAF for non-micro) → must create a NEW mandate on the creditor's site AND add it manually in client-a (Paiements > Ajouter un mandat). **Critical warning across all cases: do NOT revoke old mandates already present in client-a** — they will auto-update on the next debit. Revoking = future debits rejected.
- **Conditions/exceptions:** The B2B mandate flow requires a two-step process (creditor site + client-a); CORE mandate update is one-step (creditor site only). Revoking old mandates is explicitly prohibited — it causes payment failures.
- **Financial risk:** Moderate — revoking old SEPA mandates or failing to add new B2B mandates in client-a causes missed tax/URSSAF/supplier payments. A chatbot must always include the "do not revoke" warning.

---

## Article 6309432 — Updating Banking Details at Bouygues Telecom
- **Topic:** Step-by-step guide for changing IBAN in a Bouygues Telecom client account.
- **Key facts:** Done online: login → click name → Mes infos personnelles → Mon mode de paiement → edit IBAN → validate. Warning: do NOT revoke the existing client-a mandate — it will auto-update on the next debit.
- **Conditions/exceptions:** Standard SEPA CORE mandate — self-service update only.
- **Financial risk:** Low — same mandate-revocation risk as 6309428.

---

## Article 6312415 — How to Update URSSAF Direct Debit
- **Topic:** Step-by-step for updating IBAN on URSSAF debit (micro-entrepreneur and other legal forms).
- **Key facts:** For micro-entrepreneur: login to autoentrepreneur.urssaf.fr → Mon compte → Gérer mon auto-entreprise → Mes moyens de paiement → add new SEPA mandate with new client-a coordinates. For other legal forms: use your accountant or follow the equivalent process on net-entreprises.fr / impots.gouv. Warning: do NOT revoke old mandate — it auto-updates.
- **Conditions/exceptions:** The URSSAF process differs between micro (autoentrepreneur portal) and other statuts (impots/net-entreprises).
- **Financial risk:** Low — missing URSSAF contribution payments cause late penalties; always include the do-not-revoke warning.

---

## Article 6337768 — Updating Banking Details at Sosh / Orange
- **Topic:** Step-by-step for changing IBAN in an Orange/Sosh client account.
- **Key facts:** Done online via Orange Telecom portal: login → name → Gérer votre compte → Moyens de paiement → select contract → Modifier → Modifier vos coordonnées bancaires → enter new IBAN. Applies to both Orange and Sosh. Warning: do NOT revoke old client-a mandate.
- **Financial risk:** Low — same mandate-revocation risk as 6309428.

---

## Article 6339948 — Updating Banking Details at Total Energies
- **Topic:** Step-by-step for changing IBAN at Total Energies.
- **Key facts:** Done online: login to Total Energies Espace Client → Mon compte → Mes coordonnées bancaires → Modifier → enter new IBAN → Je valide. Warning: do NOT revoke old client-a mandate.
- **Financial risk:** Low — same mandate-revocation risk as 6309428.

---

## Article 6341663 — Updating Banking Details at Free
- **Topic:** Step-by-step for changing IBAN in a Free (internet) client account.
- **Key facts:** Done online via Free Espace Abonné: login → Mon abonnement → Facturation → Consulter / Modifier mon compte bancaire → Modifier mon compte bancaire → enter new IBAN + BIC → save. Warning: do NOT revoke old client-a mandate.
- **Financial risk:** Low — same mandate-revocation risk as 6309428.

---

## Article 6345310 — Why My Inscription Certificate Is Not Accepted
- **Topic:** Why the INSEE certificat d'inscription is insufficient for opening a client-a account.
- **Key facts:** The certificat d'inscription (issued by INSEE when declaring at a CFE) lacks information confirming the company is active — client-a cannot use it. Required alternatives: for **EI** (entreprise individuelle): Avis au répertoire SIRENE, OR Avis INPI, OR Extrait D1. For **société**: Extrait Kbis, OR Avis INPI. All documents must be **less than 3 months old**.
- **Conditions/exceptions:** The inscription certificate is commonly missubmitted by new entrepreneurs — it looks official but is insufficient for client-a.
- **Financial risk:** Low — submitting the wrong document delays account opening; knowing which document to substitute unblocks the process.

---

## Article 6348997 — Updating Banking Details at Red by SFR
- **Topic:** Step-by-step for changing IBAN in a Red by SFR client account.
- **Key facts:** Done online: login → click contract gear icon → Factures → Modifier mes coordonnées bancaires → enter SMS verification code → Modifier → enter new IBAN and BIC → Continuer. Warning: do NOT revoke old client-a mandate.
- **Financial risk:** Low — same mandate-revocation risk as 6309428.

---

## Article 6354338 — Migration Operating Procedure for client-a Accounts (API / Technical)
- **Topic:** Technical documentation for client-a Connect API partners regarding the 2021 account migration from Treezor to client-a's own EP.
- **Key facts:** This is an **API/developer article**, not customer-facing. Key facts for API partners: client-a obtained its own EP licence in 2021; BIC changed from TRZOFR21XXX to SNNNFR22XXX; new client-a bank code: 17418. During migration: two accounts returned per user (old balance = 0, new account has all data). Hidden compensatory transactions are created (use `isHidden` attribute to filter). Replace `includeHidden` parameter with `includeHiddenFees` to get bank charges but exclude compensatory transactions. 3-month overlap period where both IBANs supported incoming transfers/debits.
- **Conditions/exceptions:** Not relevant for customer-facing chatbot. API documentation only.
- **Financial risk:** None — technical developer documentation.

---

## Article 6474913 — Authorising a New Device
- **Topic:** How to authorise a new device (phone/computer) to access a client-a account.
- **Key facts:** Security system requires authentication from a previously verified device. Re-verification is triggered when: using private browsing mode, cookies cleared after each session, or switching browsers. Recommendation: use normal (non-private) browsing and preserve cookies; keep the client-a mobile app updated. If previous authorised device is lost: send a selfie with ID held next to face to promis_on_repond@client-a.fr. The mobile app does not require re-verification each session.
- **Conditions/exceptions:** Private browsing mode will always trigger re-verification — this is by design, not a bug.
- **Financial risk:** None — security guidance; if a user is locked out of their account this is the resolution path.

---

## Article 6485710 — Creating Accountant Access (Business Only)
- **Topic:** How to give an accountant read-only access to a client-a account (older article, Business plan only).
- **Key facts:** This article states accountant access is **only available for client-a Business subscribers**. Accountant permissions: view all transactions (unlimited history), download RIB, add/edit/delete receipts and VAT rates on transactions, access accounting section (generate and schedule exports, access bank statements). Cannot: order cards, make payments, access invoicing tool or toolkit. Process: web-only → Mon équipe > Gestion de l'équipe → Inviter un nouveau membre → assign "comptable" role.
- **Conditions/exceptions:** **Conflicts with article 6671728** which states the feature is available on Start, Plus, and Business plans. Article 6671728 appears more up-to-date. A chatbot should not use 6485710 alone to determine plan eligibility for accountant access.
- **Financial risk:** Low — telling a Start or Plus subscriber they cannot create accountant access (based on this article alone) would be incorrect.

---

## Article 6594338 — Collection ID, Not an Article
_6594338 is an Intercom collection (section) ID, not an article. No analysis._

---

## Article 6594343 — Collection ID, Not an Article
_6594343 is an Intercom collection (section) ID, not an article. No analysis._

---

## Article 6594513 — Collection ID, Not an Article
_6594513 is an Intercom collection (section) ID, not an article. No analysis._

---

## Article 6604661 — Collection ID, Not an Article
_6604661 is an Intercom collection (section) ID, not an article. No analysis._

---

## Article 6610540 — Collection ID, Not an Article
_6610540 is an Intercom collection (section) ID, not an article. No analysis._

---

## Article 6610574 — Collection ID, Not an Article
_6610574 is an Intercom collection (section) ID, not an article. No analysis._

---

## Article 6610764 — Collection ID, Not an Article
_6610764 is an Intercom collection (section) ID, not an article. No analysis._

---

## Article 6671728 — Creating Accountant Access (Start, Plus, Business)
- **Topic:** How to give an accountant or financial team member access to the client-a account.
- **Key facts:** Available for **Start, Plus, and Business** subscribers (more inclusive than article 6485710). Accountant permissions: view accounts and transaction receipts, access bank statements, generate one-time and scheduled accounting exports. Process: web → Mon équipe > Gestion de l'équipe → Inviter un nouveau membre → enter first name, last name, email → assign desired role (comptable or employé·e). Associates can also be invited directly.
- **Conditions/exceptions:** See note on article 6485710 — the two articles conflict on plan eligibility; 6671728 (Start/Plus/Business) appears more current.
- **Financial risk:** None — using this article gives the correct, broader eligibility.

---

## Article 6740984 — Capital Increase (Augmentation de Capital)
- **Topic:** What a capital increase is and how to do one via client-a.
- **Key facts:** A capital increase modifies the capital social during the company's life. Types: cash (numéraire — requires new certificate de dépôt), in-kind (nature), reserve incorporation, debt compensation. client-a eligibility: active client-a account + cash increase + funds wired from EU bank account (excluding Luxembourg; UK and Switzerland not in EU) + not crowdfunding. Funds must come from **individual subscribers domiciled in France**. Documents required: updated draft statuts, subscriber list, valid ID or Kbis (<3 months) per new associate, signed/dated PV deciding increase, proof of domicile <3 months per individual subscriber, attestation d'origine des fonds per subscriber. Capital variable: if the increase stays within the variable capital ceiling defined in statuts, no new certificate de dépôt is needed and greffe formalities are reduced.
- **Conditions/exceptions:** Luxembourg is explicitly excluded (despite being EU). UK and Switzerland are not EU. Crowdfunding platforms are excluded. Each individual subscriber must be domiciled in France.
- **Financial risk:** Moderate — wrong eligibility information (e.g., claiming Luxembourg-based funds are acceptable, or that overseas subscribers can participate) could cause an entire capital increase process to be invalid.

---

## Article 6740992 — Partial Capital Liberation
- **Topic:** Rules for paying in only a portion of capital at company creation, and completing the rest later.
- **Key facts:** Legal minimums at creation: **SA, SAS, SASU: at least 50%** of cash contributions; **SARL, EURL: at least 20%**; EARL (special case): at least 10%. **5-year window from RCS registration** to pay the remaining balance. Completing the liberation later is NOT an augmentation de capital — no certificate de dépôt needed; associates wire from personal account to company account and keep the wire proof. Formal process for completion: call for payment (can be by LRAR), hold extraordinary general meeting (AGE), associates wire funds, transmit PV + updated statuts to Guichet Unique.
- **Conditions/exceptions:** The liberation thresholds differ by legal form — getting them wrong invalidates the dossier at creation. The 5-year deadline is from RCS immatriculation, not from company creation.
- **Financial risk:** Low — the 50%/20% thresholds are key facts already covered in article 3074279; repeating them here reinforces their importance.

---

## Article 6741006 — Variable Capital
- **Topic:** How variable capital works and when it simplifies capital changes.
- **Key facts:** Variable capital allows modifying capital social within defined limits without holding an extraordinary general meeting. Must define in statuts: **capital plancher** (floor — must be ≥10% of initial subscribed capital and ≥ legal minimum) and **capital plafond** (ceiling — no legal upper limit). Modifications within the defined range: no AGE needed. Modifications outside the range: must follow formal augmentation de capital process (see article 6740984).
- **Conditions/exceptions:** The 10% floor rule for the plancher is mandatory and cannot be set lower.
- **Financial risk:** None — informational about capital structure flexibility.

---

## Article 6741018 — Requesting the Capital Deposit Certificate by Post
- **Topic:** Whether and how to request a paper copy of the capital deposit certificate.
- **Key facts:** For online registration (Guichet Unique): **paper certificate is not required**. If desired regardless: email depot@client-a.fr with the postal address. Cost: **€5 HT**, debited from the client-a account. Delivery: approximately 15 days by post.
- **Conditions/exceptions:** The paper certificate is optional for online creation — requesting it adds cost (€5) and delay (~15 days).
- **Financial risk:** None — purely informational.

---

## Article 6741039 — I've Received My Kbis — What's Next?
- **Topic:** Steps to unlock capital deposit funds and finalise account opening after receiving the Kbis.
- **Key facts:** After immatriculation via Guichet Unique: documents to transmit to client-a: (1) final Kbis bearing the RCS immatriculation number, dated less than 3 months; (2) final statuts — dated, initialled (paraphés), and signed. Upload directly in the client-a personal space. client-a reviews and sends email notification upon account opening. **Funds are released within 3 working days** after account opening.
- **Conditions/exceptions:** Kbis must be the final version (with RCS number), not a provisional receipt. Both documents are required — sending only one is insufficient.
- **Financial risk:** None — companion to article 3551393 (which covers the same step from the capital deposit side).

---

## Article 6741054 — Understanding Capital Deposit
- **Topic:** Introductory explanation of what a capital deposit is and how it works.
- **Key facts:** Purpose: endows the new company with its own assets separate from the founders; creates associate rights (votes, dividends). Three types of contributions: numéraire (cash), nature (property/assets), industrie (skills — labour contribution). Capital must be deposited with: a bank, the CDC (Caisse des dépôts et consignations), or a notaire. Result: attestation de dépôt des fonds — required to obtain Kbis and begin activities. After immatriculation: all deposited funds are returned in full to the company's professional account.
- **Conditions/exceptions:** The industrie (skill) contribution does not require cash deposit. Only numéraire contributions must be deposited with the three authorized custodians.
- **Financial risk:** None — introductory overview.

---

## Article 7053471 — Searching and Filtering Transactions
- **Topic:** How to use advanced search and filter features in the client-a transaction view.
- **Key facts:** Available on mobile app and web app. Filters: free text, date (exact or range), amount (exact/min/max), payment method (card/wire/cheque/cash/direct debit/other), status (validated/pending/refused), direction (incoming/outgoing), transactions without receipts. Filters can be combined. Accountant access users (Start/Plus/Business) can also use these filters.
- **Conditions/exceptions:** None.
- **Financial risk:** None — feature documentation.

---

## Article 7105066 — Employee: Requesting a Card from the Employer
- **Topic:** How an employee with client-a access can request a bank card from their employer.
- **Key facts:** Three card types: physical Mastercard Business World Debit (number varies by plan), virtual cards (unlimited for "client-a Pro" and "client-a Business"), budget virtual cards (defined spending and validity). **Only available for client-a Pro and client-a Business subscribers** — employees on other plans cannot request cards. Note: article uses old plan name "client-a Pro" (likely corresponds to current Plus or Business). Process: login to app.client-a.fr → Cartes bancaires → Demander une nouvelle carte → select type → employer validates. Virtual cards are instantly usable after employer validation.
- **Conditions/exceptions:** This feature is plan-gated (Pro/Business only). Physical card delivery takes ~10 days. The "client-a Pro" naming may be outdated.
- **Financial risk:** Low — telling an employee on an ineligible plan that they can request a card would be incorrect.

---

## Article 7127637 — Adding a Logo to client-a Invoices
- **Topic:** How to add a company logo to invoices and quotes created in the client-a invoicing tool.
- **Key facts:** Available for all client-a plans. **Web only** — cannot be done from the mobile app. Steps: Facturation > Paramètres de facturation > click "Personnalisez vos devis et factures avec votre logo." Logo applies automatically to all future invoices and quotes. Technical requirements: JPG or PNG format; max 2 MB. If logo appears too small: it may have excessive white space around it — crop before uploading. Logo can be modified or deleted in the same settings.
- **Conditions/exceptions:** Web-only — users who only use the mobile app cannot add a logo.
- **Financial risk:** None — feature documentation.

---

## Article 7139198 — Creating a Deposit Invoice (Facture d'Acompte) on client-a
- **Topic:** How to create an advance/deposit invoice and the associated final invoice (facture de solde).
- **Key facts:** Prerequisite: a detailed quote showing total amount, payment method, and acompte amount (% or value). **Mandatory mentions on a deposit invoice:** all standard invoice mentions + **"facture d'acompte"** label + quote reference number. Deposit invoices are numbered in the same sequence as regular invoices. **Since 1 January 2023: TVA is due on deposit invoices for both goods AND services.** Final invoice (facture de solde) must reference: quote number, each acompte amount, and for TVA-registered entities, the acompte invoice number/date/TVA amount already paid. If the total increases vs the quote: must create a formal avenant and get client approval — the change cannot be made only on the final invoice.
- **Conditions/exceptions:** The "facture d'acompte" label and quote reference are mandatory. The TVA-on-acomptes rule (since Jan 2023) applies to both goods and services — a pre-2023 practice of not applying TVA to service deposits is now non-compliant. Price increases require a signed avenant to be enforceable.
- **Financial risk:** Moderate — missing the "facture d'acompte" label or quote reference = non-compliant invoice; missing TVA on acomptes since 2023 = tax error; price increase without avenant = client legally not obligated to pay the difference.

---

## Article 7328841 — Guide to the SEPA Network
- **Topic:** What the SEPA network is, how it operates, and its geographic scope.
- **Key facts:** SEPA (Single Euro Payments Area): interbank network for wire transfers and direct debits. Geographic scope: 28 EU member states + EEA members + Switzerland, Andorra, Monaco, San Marino, and the Vatican. SEPA operates only on working days (Monday–Friday); closed on weekends and certain public holidays (2025 closure dates listed: 1 Jan, 18 Apr, 21 Apr, 1 May, 25 Dec, 26 Dec). Transfers on closed days are deferred to the next working day. **Exception: instant transfers (virements instantanés) are NOT subject to SEPA closure** — they operate 24/7/365.
- **Conditions/exceptions:** Standard SEPA transfers cannot be sent or received on SEPA closure days (weekends + the 6 listed holidays). Instant transfers bypass this limitation.
- **Financial risk:** Low — users who need urgent payment on a SEPA closure day should use instant transfer instead. A chatbot must clarify the instant vs standard transfer distinction.

---

## Article 7918917 — Writing a Third-Party Communication Authorisation
- **Topic:** Template document authorising the CMA to share your professional information in their register with third parties.
- **Key facts:** This document is used during artisanal business creation (CMA registration). Can be handwritten. Guides the creator to complete the document for submission with their CFE dossier.
- **Conditions/exceptions:** Relevant only for artisanal activity registrations at the CMA.
- **Financial risk:** None — administrative template.

---

## Article 7960107 — Can I Name My client-a Cards?
- **Topic:** Card renaming feature in the client-a web app.
- **Key facts:** Available to all client-a clients. Cards can be renamed from the web app (Cartes Bancaires tab) to help track which card is used for which purpose. Example: rename a virtual card "Adobe" for monthly Adobe subscription payments. This does not change the name engraved on a physical Mastercard — only the in-app label.
- **Conditions/exceptions:** Web app only — not available from the mobile app for renaming.
- **Financial risk:** None — feature documentation.

---

## Article 7978373 — Why Are My Company Statuts Not Accepted?
- **Topic:** What version of statuts client-a requires and what to do if they are rejected.
- **Key facts:** client-a retrieves statuts from Pappers (public database) when available. If not on Pappers: submit a digital PDF with the **greffe validation page** (the page stamped by the Registre du Commerce). Alternatives accepted: (1) statuts + récépissé de dépôt du Greffe as first page (if very recent and greffe stamp not yet available); (2) "Synthèse INPI" document titled "Synthèse-Version définitive - Formalité validée" (downloadable from procedures.inpi.fr). Email address for submission: domicile@client-a.fr (or via the app).
- **Conditions/exceptions:** Draft statuts without the greffe validation page are rejected. The récépissé de dépôt and INPI synthèse are only accepted as temporary alternatives for very new companies.
- **Financial risk:** Low — submitting incorrect statuts delays account opening; knowing the exact alternatives (récépissé or INPI synthèse) prevents unnecessary back-and-forth.

---

## Article 8010261 — Protecting Against Fake Advisors (Phishing / Vishing)
- **Topic:** How to identify and protect against fraudsters impersonating client-a customer advisors.
- **Key facts:** client-a will **NEVER** ask for confidential information (account codes, card numbers, IBAN, login credentials) by SMS, phone call, or email link. Never click links in suspicious emails/SMS — type the URL manually. Correct client-a web URL: **https://app.client-a.fr** only. Vishing tactic: fraudsters spoof client-a's phone number and create urgency around "account verification" or "suspicious payment validation." client-a advisors NEVER ask to: validate operations remotely, cancel or validate payments/refunds through the app, confirm login credentials by phone. If fraud detected: block cards in app immediately; contact client-a via in-app secure messaging; file a report at internet-signalement.gouv.fr.
- **Conditions/exceptions:** Legitimate client-a advisors may call proactively, but they will never ask for credentials or remote action. When in doubt: hang up and call back using the official client-a number.
- **Financial risk:** Moderate — vishing and phishing are live threats targeting new entrepreneurs; a chatbot must be proactive in reminding users of what client-a will and will never ask for.

---

## Article 8124145 — Employee: Initiating a Wire Transfer Request
- **Topic:** How an employee with client-a access can initiate (not execute) a wire transfer request.
- **Key facts:** Employees can initiate wire requests with no amount limit — but the request must be validated by the employer before execution. **Only available on client-a Pro and client-a Business plans.** Process: web app → Virements → Initier un virement → fill recipient IBAN, business name, amount, reference, justification → Envoyer ma demande. Employer then validates or rejects.
- **Conditions/exceptions:** Employee cannot execute transfers directly — only initiate a request for employer approval.
- **Financial risk:** None — the employer retains full control and must approve all requests.

---

## Article 8317409 — Account Holder: Validating Identity Documents
- **Topic:** Step-by-step guide for completing the identity verification (KYC) process.
- **Key facts:** Triggered by QR code scan or SMS. Steps: (1) select country of document issue; (2) select document type; (3) photograph ID front (once straight, once tilted); (4) photograph ID back (once straight, once tilted); (5) face video (turn head left to right); (6) continue. Rejection reasons: blurry or cropped photo; expired document; for EU ID cards and titres de séjour: BOTH front AND back required; for EU passports: the double page with the photo must be shown. Special note: French ID cards issued after reaching majority are valid for up to **5 years past their expiry date** — check at service-public.fr if in doubt.
- **Conditions/exceptions:** The 5-year post-expiry validity extension for French IDs is non-obvious and frequently misunderstood.
- **Financial risk:** None — onboarding verification guidance.

---

## Article 8320272 — Identity Verification Overview
- **Topic:** Which individuals must verify their identity to open a client-a account, and what documents are accepted.
- **Key facts:** Identity verification is required for every **bénéficiaire effectif**: the mandataire social (company director) AND any shareholder holding **at least 25%** of the company. Accepted documents: valid EU national ID card (if older than 10 years, check validity at service-public.fr), EU passport, titre de séjour (if expired, the renewal récépissé is also required). If none of these documents are available: notify client-a for individual case analysis. Two distinct verification flows exist: titulaire (article 8317409) and bénéficiaire effectif/associé (article 8320275).
- **Conditions/exceptions:** The 25% threshold is the legal cutoff — shareholders below 25% are not required to verify identity at account opening.
- **Financial risk:** None — KYC onboarding guidance.

---

## Article 8320275 — Beneficial Owner / Associate: Validating Identity Documents
- **Topic:** Step-by-step KYC process for associates and beneficial owners (not the titulaire).
- **Key facts:** Steps: (1) photograph ID front; (2) photograph ID back; (3) face video (turn head left to right, repeat); (4) validate. Quality requirements: document must be in full view, sharp, and not cropped. EU ID and titre de séjour: both front and back required. EU passport: double page with photo. French ID issued after majority: valid for up to 5 years past its expiry date. If rejected: resubmit immediately via app; client-a reviews within 48 hours.
- **Conditions/exceptions:** Different flow than the titulaire process (no QR code, no tilted photo step). Same document validity and quality requirements apply.
- **Financial risk:** None — KYC process guidance for associates.

---

## Article 8385614 — Receiving an International (SWIFT) Transfer: Fees
- **Topic:** Cost structure for receiving international SWIFT wire transfers on a client-a account.
- **Key facts:** Three distinct cost components: (1) **client-a reception fee** — billed with the monthly subscription (not per transaction in real time): **€6 HT/transfer on Free**, **€5 HT/transfer on Start/Plus/Business**. (2) **Interbank fees** — determined by the sender's charge option: OUR (sender pays all), SHA (split between sender and recipient), BEN (recipient pays all); amount varies by sender's bank and cannot be predicted. (3) **FX conversion fees** — client-a account only holds euros; if the sender transfers in another currency, it is converted during transit. In ~90% of cases the sender's bank converts at its own rate; in some cases Wise (client-a's partner) receives the original currency and converts at the mid-market rate (more favourable for the recipient). To avoid interbank fees: ask sender to select the OUR option; this can be specified in contracts or on invoice payment terms.
- **Conditions/exceptions:** The article includes a note dated 25/02/2025 about plan evolution — fees above apply to accounts opened or migrated after that date. The BEN option means the recipient can receive significantly less than the nominal amount without advance warning.
- **Financial risk:** Moderate — users unaware of the BEN option risk receiving less than invoiced. A chatbot must explain that SWIFT fees have three separate components and that the OUR option protects the recipient.

---

## Article 8417263 — Contesting a Wire Transfer
- **Topic:** When and how to contest an outgoing wire transfer that was sent in error or fraudulently.
- **Key facts:** Four contestable situations: (1) fraud/scam; (2) wrong beneficiary bank details; (3) wrong amount; (4) duplicate transfer. **Fraud case:** a police report (dépôt de plainte) is mandatory before client-a can process the contestation. **Wrong IBAN (non-existent):** if the IBAN belongs to no account, funds return automatically within approximately 10 days. **Wrong IBAN (existing account):** funds are credited to the wrong recipient's account; the only recourse is client-a sending a "rappel de virement" (recall request) to the receiving bank — but the receiving bank must consent to return the funds; **there is no guarantee of recovery.** Process: mobile app → tap on the transaction → "Besoin d'aide" → "Contester cette opération."
- **Conditions/exceptions:** Recovery of funds sent to a real but wrong IBAN depends entirely on the receiving bank's cooperation. There is no legally enforceable mechanism for forced return in all cases.
- **Financial risk:** Moderate — users who send to a wrong IBAN must understand recovery is not guaranteed. A chatbot that implies funds will always be returned sets false expectations and may discourage timely police reporting (required for fraud cases).

---

## Article 8717818 — Test Article (Placeholder)
- **Topic:** Internal test/template article.
- **Key facts:** Body contains heading format tests only (H1, H2, H3, H4, normal text). Not customer-facing content.
- **Conditions/exceptions:** Empty test article — no factual content.
- **Financial risk:** None.

---

## Article 8721840 — Test Article (Placeholder)
- **Topic:** Internal test/template article.
- **Key facts:** Body contains only "Tapez votre texte" placeholder. Not customer-facing content.
- **Conditions/exceptions:** Empty test article — no factual content.
- **Financial risk:** None.

---

## Article 8833450 — How client-a Protects You from Phishing
- **Topic:** Security measures client-a has in place against phishing and identity theft.
- **Key facts:** Phishing/vishing aims to obtain personal information to make fraudulent payments, transfers, or direct debits. client-a's protective measures: secure password per login; new device verification for unrecognised devices; strong in-app authentication for sensitive operations (payments, transfers); identity verification for all phone/non-chat interactions. **Note: article is incomplete** — contains a visible "In progress ⏳" placeholder mid-article. The key user-facing warning is present: "client-a ne vous demandera en aucun cas de divulguer ce type de données" (client-a will never ask you to share confidential data). For the complete guidance on fake advisors, use article 8010261.
- **Conditions/exceptions:** Article is unfinished — do not use as the sole source. Article 8010261 provides more complete and actionable guidance.
- **Financial risk:** Low (incomplete) — the content that exists is consistent with 8010261 but less complete.

---

## Article 8870922 — When Will My Capital Deposit Funds Be Released?
- **Topic:** Timeline for receiving capital deposit funds into the client-a account after company registration.
- **Key facts:** After client-a receives the final Kbis and signed statuts: team performs final verification → email notification confirms account opening. Once dossier validated: client-a requests fund release from the notaire immediately; notaire wires the funds at end of day. SEPA transfer timeline: **2–3 working days** (Monday–Friday, no weekends or public holidays) → funds credited after that delay. **The client-a account can be used immediately upon opening**, even before the deposited funds arrive.
- **Conditions/exceptions:** The 2–3 working day SEPA delay applies after the notaire wires; if the account opens on a Friday, funds may not arrive until Wednesday the following week.
- **Financial risk:** None — timeline guidance; knowing the account is usable before funds arrive prevents unnecessary delays for new users.

---

## Article 8870933 — Capital Deposit Dossier Invalid — Empty Article
- **Topic:** What to do when a capital deposit dossier is rejected.
- **Key facts:** Article body is **empty** — no content in the knowledge base.
- **Financial risk:** None — empty stub.

---

## Article 8870935 — Identity Documents for Capital Deposit — Empty Article
- **Topic:** Identity documents required for the capital deposit process.
- **Key facts:** Article body is **empty** — no content in the knowledge base.
- **Financial risk:** None — empty stub.

---

## Article 8870941 — Address / Commercial Name Changes Post-Registration — Empty Article
- **Topic:** Whether address or commercial name changes can be made after immatriculation.
- **Key facts:** Article body is **empty** — no content in the knowledge base.
- **Financial risk:** None — empty stub.

---

## Article 8870945 — Am I Subject to VAT? — Empty Article
- **Topic:** Determining TVA liability.
- **Key facts:** Article body is **empty** — no content in the knowledge base.
- **Financial risk:** None — empty stub (TVA rules covered in existing articles 1195405, 3399375, etc.).

---

## Article 8870948 — What Aid Is Available for My Micro-Enterprise? — Empty Article
- **Topic:** Financial aid for micro-entrepreneurs.
- **Key facts:** Article body is **empty** — no content in the knowledge base.
- **Financial risk:** None — empty stub.

---

## Article 8870950 — What Is the Benefit of Versement Libératoire? — Empty Article
- **Topic:** Explanation of the versement libératoire tax option.
- **Key facts:** Article body is **empty** — no content in the knowledge base.
- **Financial risk:** None — empty stub (versement libératoire is covered in article 1227397).

---

## Article 8870952 — Creating Your Micro-Enterprise with client-a
- **Topic:** client-a's micro-enterprise creation service — process, timelines, and pricing.
- **Key facts:** 100% online creation service. Documents required: signed/dated décorpus-ation de non-condamnation; pouvoir du mandataire authorising client-a to act; additional documents may be required depending on activity. After submission: user receives décorpus-ation de début d'activité and dossier number — **can start working immediately**, noting "SIRET en cours d'attribution" on invoices. Processing times (indicative): liberal activity = from 24h; commercial = from 1 week; artisanal = from 2 weeks; commercial agent = variable (depends on greffe). Pricing (HT): liberal = €39; commercial = €49; artisanal = €59; commercial agent = €89. **Cannot create if:** activity is on the prohibited list; non-EU student; titre de séjour has "salarié", "étudiant", or non-business mention.
- **Conditions/exceptions:** Prices are all HT (excluding VAT). Timelines are indicative. Some activities require extra documents.
- **Financial risk:** None — informational service description.

---

## Article 8870956 — Conditions for Combining Micro-Enterprise with Salaried Employment — Empty Article
- **Topic:** Rules for running a micro-enterprise while employed.
- **Key facts:** Article body is **empty** — no content in the knowledge base.
- **Financial risk:** None — empty stub.

---

## Article 8870957 — Can I Hire an Employee, Intern, or Apprentice? — Empty Article
- **Topic:** Whether micro-entrepreneurs can hire staff.
- **Key facts:** Article body is **empty** — no content in the knowledge base.
- **Financial risk:** None — empty stub.

---

## Article 8870961 — Is a Professional Account Mandatory for Micro-Entrepreneurs? — Empty Article
- **Topic:** Whether a dedicated professional bank account is legally required.
- **Key facts:** Article body is **empty** — no content in the knowledge base.
- **Financial risk:** None — empty stub (note: a dedicated account is mandatory above certain CA thresholds — covered in other articles).

---

## Article 8870972 — Can I Combine Multiple Activities in One Micro-Enterprise? — Empty Article
- **Topic:** Whether a single micro-enterprise can cover multiple business activities.
- **Key facts:** Article body is **empty** — no content in the knowledge base.
- **Financial risk:** None — empty stub.

---

## Article 8870977 — Is My Activity Eligible for Micro-Enterprise Status?
- **Topic:** Which activities are excluded from the micro-entreprise (auto-entrepreneur) regime.
- **Key facts:** The following activities are **not eligible** for the micro-entreprise regime: (1) **Artiste-auteur activities** subject to the artiste-auteur regime (composers, audiovisual authors, writers, illustrators, graphic arts); (2) **Regulated liberal professions**: medical (doctors, nurses, vets, pharmacists), legal (lawyers, huissiers, notaires), financial (experts-comptables, insurance agents, agricultural experts); (3) **Agricultural activities**: livestock, market gardening, landscaping, B&B/table d'hôtes as extension of agricultural exploitation; (4) **Real estate activities**: marchand de biens, agent immobilier, lotisseur; (5) **Special cases**: journalists, interpreters, private investigators, traders. These activities require a different legal form (EI without micro regime, EURL, SASU, etc.).
- **Conditions/exceptions:** The list is not exhaustive — when in doubt, users should verify their specific activity.
- **Financial risk:** Moderate — a user in an ineligible profession who registers as a micro-entrepreneur faces registration refusal or post-registration compliance issues (back-taxes, penalties). A chatbot must flag this check before helping someone register.

---

## Article 8870981 — Has My RCS Registration Been Completed? — Empty Article
- **Topic:** How to check if company registration at the RCS is complete.
- **Key facts:** Article body is **empty** — no content in the knowledge base.
- **Financial risk:** None — empty stub.

---

## Article 8870984 — The ACRE Application — Empty Article
- **Topic:** How to apply for ACRE (social contribution reduction for new businesses).
- **Key facts:** Article body is **empty** — no content in the knowledge base.
- **Financial risk:** None — empty stub (ACRE covered in articles 3606170 and 4725622).

---

## Article 8870986 — Valid Experience Documents for a Regulated Artisanal Activity — Empty Article
- **Topic:** Which documents prove experience/qualification for regulated artisanal activities.
- **Key facts:** Article body is **empty** — no content in the knowledge base.
- **Financial risk:** None — empty stub.

---

## Article 8871057 — Wrong APE Code After Registration with client-a
- **Topic:** What to do if the APE code assigned by INSEE does not match the declared activity.
- **Key facts:** The APE code (Activité Principale Exercée) is assigned by INSEE based on the main activity declared during registration. It is primarily statistical and has no legal value — the declared activity itself is legally binding. client-a has no control over the APE code assigned — that is exclusively INSEE's decision. The registration form does not allow specifying an APE code directly (codes are categories, not precise activity descriptors). If the APE code seems wrong: request a change via the "Comment changer mon code APE?" process.
- **Conditions/exceptions:** An incorrect APE code does not invalidate the company registration. However, some collective agreements (conventions collectives) and cotisation rates reference the APE code — a persistent mismatch can eventually cause issues.
- **Financial risk:** Low — immediately after registration, a wrong APE code causes no financial harm; but it should be corrected as it can affect convention collective applicability and statistical classification (see also article 11886479).

---

## Article 8981213 — Contacting Customer Service
- **Topic:** How to reach client-a's customer support, both for prospects and existing clients.
- **Key facts:** **Non-clients:** email contact@client-a.fr or phone (number in article). **Existing clients:** 7 days/week via in-app secure messaging (Centre d'aide); email contact@client-a.fr (from address associated with the client-a account); phone for **Start, Plus, and Business subscribers only** (Free plan: no phone support). Team of 8 dedicated advisors. Recognised as "Élu Service Client de l'Année 2026."
- **Conditions/exceptions:** Free plan clients cannot access phone support — chat/email only.
- **Financial risk:** None — contact information.

---

## Article 9042063 — Why Was My Capital Deposit Dossier Rejected?
- **Topic:** Reasons a capital deposit dossier is invalidated, covering both statuts document errors and identity document rejections.
- **Key facts:** **Statuts rejection reasons:** (1) Company name in statuts does not match the name used on client-a; (2) Share capital amount inconsistency between statuts sections; (3) Missing share distribution table (who holds what percentage); (4) Missing director nomination clause; (5) Missing mandatory wording in the "Apports" clause; (6) Inconsistent associate information across sections. **ID rejection reasons:** blurry or cropped scan; photocopy/non-live photo; expired document; non-EU ID without a valid VISA; driving licence not accepted. For rejected dossiers, contact: depot@client-a.fr.
- **Conditions/exceptions:** All associates must provide a valid ID, regardless of shareholding percentage. Driving licence is never accepted for capital deposit regardless of EU membership.
- **Financial risk:** Moderate — a rejected dossier delays company incorporation and locks deposited capital. Chatbot must enumerate rejection criteria precisely so users can self-diagnose before resubmitting.

---

## Article 9042102 — Identity Documents Accepted for Capital Deposit
- **Topic:** Which identity documents are accepted (and rejected) for capital deposit dossiers submitted through client-a.
- **Key facts:** **Who must verify:** ALL associates, including those holding as little as 1% of shares. **Accepted documents:** CNI (national ID card), EU national ID, EU passport, titre de séjour with renewal receipt if expired, long-stay VISA type D accompanied by a passport (non-directors only). **Not accepted:** driving licence; non-EU ID without a valid VISA; titre de séjour or VISA mentioning "salarié", "étudiant", "saisonnier", or "visiteur" — these categories are not accepted for company creators. **Format:** must be a live photo taken at the time of submission; scans, photocopies, and screenshots are rejected.
- **Conditions/exceptions:** Even 1%-shareholders cannot skip the ID verification step. A titre de séjour marked "étudiant" or "salarié" is NOT sufficient for a company creator.
- **Financial risk:** Moderate — submitting incorrect documents for even one associate blocks the entire dossier. Chatbot must flag the 100%-associate rule and the salarié/étudiant exclusion to prevent repeated rejections.

---

## Article 9099961 — Social Contribution Estimator (Micro-Enterprise)
- **Topic:** The built-in social contribution estimator tool for micro-entrepreneurs on client-a paid plans.
- **Key facts:** Available on **Start, Plus, and Business plans only** (not Free). Estimates cotisations sociales, TVA, and income tax in real time based on incoming payments. Requires initial configuration: declaration periodicity (monthly/quarterly), TVA status (franchise de base or subject to TVA), activity type (BIC sales, BIC services, BNC, or mixed), whether versement libératoire is applied, ACRE status, and IR calculation method. Mixed-activity users must manually split their CA across activity categories — the tool does not do this automatically.
- **Conditions/exceptions:** Tool is not available on the Free plan. Estimates are indicative — final amounts depend on actual declarations.
- **Financial risk:** None — informational tool; accuracy depends on user configuration, not chatbot guidance.

---

## Article 9188995 — Transactions on a Sub-Account
- **Topic:** How money moves in and out of client-a sub-accounts and what operations are (not) possible.
- **Key facts:** Sub-accounts can receive funds via: (1) internal transfer from the main account (free, instant, unlimited, does NOT count toward monthly transfer quota); (2) direct external wire from any IBAN (including instant transfers). Each sub-account has its own IBAN and generates its own bank statements. B2B SEPA mandates can be associated with sub-accounts. **Not possible:** linking a client-a card to a sub-account; moving a subscription debit to a sub-account.
- **Conditions/exceptions:** Internal transfers between own accounts are free and do not consume the plan's monthly transfer quota. Cards cannot be linked to sub-accounts — payments always debit the main account.
- **Financial risk:** None — operational clarification; no direct financial harm from misunderstanding.

---

## Article 9241450 — Why Did a SEPA Direct Debit Fail?
- **Topic:** Common reasons a SEPA direct debit is rejected on a client-a account.
- **Key facts:** Main failure causes: (1) **Insufficient funds** at debit time; (2) **Missing B2B mandate** — especially relevant for DGFIP (tax authority) debits which require a B2B mandate to be pre-registered with client-a; (3) **Incorrect RUM** (Référence Unique de Mandat) on the mandate — must match exactly; (4) **Traites/LCR** — client-a does not support commercial paper (lettres de change relevé); these are rejected automatically. Only the creditor (not client-a) controls debit dates — users cannot move or delay a debit unilaterally.
- **Conditions/exceptions:** DGFIP (impôts) always uses B2B direct debit — users must register the B2B mandate in their client-a account before the first debit or it will fail. Traites/LCR are silently rejected.
- **Financial risk:** Low — a failed debit can trigger late payment penalties from creditors (e.g. URSSAF, DGFIP). Chatbot must mention B2B mandate requirement for tax debits.

---

## Article 9241500 — Referral Program (Parrainage)
- **Topic:** How the client-a referral program works — rewards for referring new clients.
- **Key facts:** Referrer earns up to €200 per successful referral, amount depending on the plan chosen by the referred person. The referred friend receives 1 additional free month. Progress tracked via Profile > Parrainage in the app. Programme rules were updated on 15/07/2025.
- **Conditions/exceptions:** Reward amount varies by referred person's plan — chatbot should not state a fixed amount without qualifying it.
- **Financial risk:** None — marketing/referral program.

---

## Article 9250660 — Is a Professional Bank Account Mandatory for Micro-Entrepreneurs?
- **Topic:** Legal obligation (or lack thereof) for micro-entrepreneurs to hold a dedicated professional bank account.
- **Key facts:** A professional bank account is **NOT generally mandatory** for micro-entrepreneurs. However, under the **PACTE law (2019)**, a dedicated account — either personal or professional, but bearing a professional mention — is mandatory if CA exceeds **€10,000 for two consecutive years**. The account must clearly show it is used for professional activity; a personal account used exclusively for business purposes is acceptable if it meets this condition.
- **Conditions/exceptions:** The €10,000/2-year threshold triggers the obligation — below this, no mandatory account. The law requires a "dedicated" account, not specifically a professional one, but it must bear a professional mention.
- **Financial risk:** Moderate — incorrectly telling a user they are or are not required to open a professional account can lead to non-compliance with PACTE law obligations. Chatbot must state the threshold precisely.

---

<!-- 9296028: Collection ID — not an article. No analysis. -->

## Article 9367043 — Suspending or Revoking a SEPA Direct Debit Mandate
- **Topic:** How to suspend or revoke a SEPA direct debit mandate on client-a, and the limits of what client-a can do.
- **Key facts:** **Mobile app:** Paiements > Prélèvements SEPA; select mandate > suspend or revoke. **Web app:** Compte Pro > Paiements > Prélèvements SEPA. Revoking a mandate stops all future debits on that mandate permanently. **Card-based direct debits** (subscriptions charged to a client-a card number, not via SEPA) **cannot be stopped by client-a** — the user must contact the merchant directly to cancel the subscription.
- **Conditions/exceptions:** Revoking a SEPA mandate is permanent for that mandate reference. Card subscriptions are outside client-a's control — only the creditor can cancel them.
- **Financial risk:** Low — chatbot must distinguish between SEPA mandate revocation (client-a can do) and card-based subscription cancellation (client-a cannot do); giving wrong guidance leaves user unable to stop unwanted charges.

---

## Article 9414732 — Can I Cancel a SEPA Transfer?
- **Topic:** How and when a standard (non-instant) outgoing SEPA transfer can be cancelled.
- **Key facts:** **Mobile app:** tap the transfer transaction > "Annuler ce virement." Cancellation is **only possible before the transfer has been sent to the SEPA network** — i.e., while it is still queued/pending. Once the transfer has been validated and dispatched to SEPA, it **cannot be recalled** by client-a — the only remedy is to contact the beneficiary and request a return.
- **Conditions/exceptions:** Instant transfers cannot be cancelled at all (sent immediately). Standard transfers have a brief window before network submission. The cancellation button disappears once the transfer is in transit.
- **Financial risk:** Moderate — chatbot must not imply transfers can always be cancelled. Wrong guidance delays recovery of erroneous payments. Must always mention the "contact beneficiary" fallback.

---

## Article 9414797 — Activating Notifications
- **Topic:** How to enable and configure push notifications on the client-a mobile app.
- **Key facts:** Notifications are configured in the **mobile app only** (not web): Profile icon > Préférences. Users can toggle notification types independently: incoming payments, outgoing transfers, direct debits, invoice events, receipt reminders.
- **Conditions/exceptions:** Notifications are mobile-only — no equivalent setting in the web dashboard.
- **Financial risk:** None — notification preferences, no financial risk.

---

## Article 9423284 — Jedéclare.com Integration via EBICS
- **Topic:** How to connect client-a to Jedéclare.com for automatic bank data synchronisation (for tax declarations).
- **Key facts:** Uses the EBICS protocol. Setup is initiated by the **accountant** on the Jedéclare platform, who requests synchronisation; the client then signs the mandate. Data is transmitted daily. Synchronisation can start from any historical date. The mandate must go through the accountant to Jedéclare — clients cannot set this up directly.
- **Conditions/exceptions:** The client cannot initiate the Jedéclare connection themselves — it must be set up by their accountant.
- **Financial risk:** None — third-party integration setup.

---

## Article 9431413 — Can I Send an International Transfer from client-a?
- **Topic:** Summary article confirming international wire capability and directing to the detailed guide.
- **Key facts:** Yes, client-a supports outgoing international transfers in 10 currencies. Step-by-step process is in the app. Refers to article 9707350 for full details on fees and supported currencies.
- **Financial risk:** None — pointer article; see 9707350 for fee details.

---

## Article 9552428 — Engagement Bonus: Reduced Loan Rate via CNED Training
- **Topic:** How to earn a reduced interest rate on client-a financing by completing a free online training course.
- **Key facts:** Users can unlock an "engagement criterion" that reduces their loan rate by completing a free CNED online training on climate and biodiversity (~7 hours, 5 chapters). Completing all chapters earns 5 individual badges and a "Super badge." The Super badge must be submitted to client-a to validate the engagement criterion.
- **Conditions/exceptions:** The training must be fully completed to earn the Super badge — partial completion does not qualify.
- **Financial risk:** None — loan rate reduction incentive, no financial risk from wrong chatbot guidance.

---

## Article 9561237 — Adding a Credit Note (Avoir) or Discount to an Invoice
- **Topic:** How to create a credit note (avoir) or apply a commercial discount using client-a's invoicing tool.
- **Key facts:** **Credit note (avoir):** create a new invoice with a **negative price** and label it "Facture d'avoir n°X" referencing the original invoice number. **Discount:** add a line item "Remise commerciale" with a negative amount. The article does not mention a "partial avoir" functionality.
- **Conditions/exceptions:** **Conflict with article 13859730** — that article explicitly states partial avoirs are not supported. Chatbot should use article 13859730 as the authoritative source for avoir creation.
- **Financial risk:** Low — incorrect avoir guidance can result in non-compliant invoicing (anti-VAT fraud law applies to credit notes too). Prefer article 13859730 for avoir questions.

---

## Article 9561289 — Managing Connected Devices
- **Topic:** How to view, validate, or block devices connected to a client-a account.
- **Key facts:** **Mobile app:** Profile > Sécurité > Appareils connectés. **Web:** Profile > Activités récentes. Users can validate or block any device from these menus. If no authorised device is available: use the email verification link from the login page. If persistent issues: contact client-a support.
- **Financial risk:** None — security/device management.

---

## Article 9588588 — Growing Your Business Treasury (Cashbee, Caravel, Yomoni)
- **Topic:** Treasury investment and savings options available to client-a business clients via partner integrations.
- **Key facts:** Three options: (1) **Cashbee** — terme account (compte à terme), 6-month to 5-year duration, max rate 2.70% over 5 years, minimum €35,000, FGDR-protected up to €100,000, funds available with 32-day notice after request; (2) **Caravel** — PER (Plan d'Épargne Retraite) retirement savings product; (3) **Yomoni** — compte-titres (investment account), minimum €15,000, no maximum, managed portfolios.
- **Conditions/exceptions:** Cashbee minimum €35,000; withdrawal requires 32-day notice. Yomoni minimum €15,000. Capital not guaranteed on Yomoni (market investments).
- **Financial risk:** Low — chatbot must not overstate returns or guarantees; Yomoni capital is at risk.

---

## Article 9588615 — Collecting Online Payments (Square, Mollie)
- **Topic:** Payment collection partner tools available to client-a clients for accepting card payments online and in-person.
- **Key facts:** **Square:** omnichannel (online + physical), Square Reader hardware is free for client-a clients, first €4,000 in fees are free for client-a clients. **Mollie:** online payments only, first €5,000 in transaction volume are fee-free for client-a clients.
- **Conditions/exceptions:** Free-fee thresholds are promotional — standard fees apply above the threshold.
- **Financial risk:** None — partnership offers, no financial risk from chatbot guidance.

---

## Article 9662521 — Professional Insurances via Orus
- **Topic:** Partner insurance products available to client-a clients through Orus.
- **Key facts:** Available coverage types: RC Pro (professional liability), assurance décennale (10-year construction liability), cyber-risk, commercial premises, professional equipment, MRP (multirisque professionnelle).
- **Financial risk:** None — insurance product listing.

---

## Article 9662542 — Mutuelle and Prévoyance Partners (Stello, Alan)
- **Topic:** Partner health and welfare (mutuelle/prévoyance) products available to client-a clients.
- **Key facts:** **Stello:** mutuelle (health) + prévoyance (disability/death coverage). **Alan:** health insurance + TPE/employee coverage. Both products may be eligible for loi Madelin tax deductibility for sole traders and company directors.
- **Conditions/exceptions:** Loi Madelin deductibility requires meeting eligibility criteria (TNS regime).
- **Financial risk:** None — insurance product listing.

---

## Article 9707342 — Adding an International Transfer Beneficiary
- **Topic:** What banking information is required to add a beneficiary for each supported international transfer currency.
- **Key facts:** Required fields vary by currency: **AUD** — BSB code + account number; **CAD** — transit number + institution number + account number; **CHF** — standard IBAN (QR-IBAN format is **not supported**); **GBP** — account number + Sort Code; **USD** — ACH routing number + account number. Each currency can only be paid to a bank account in its home country (e.g. USD to US banks only, GBP to UK banks only).
- **Conditions/exceptions:** CHF QR-IBAN is explicitly not supported — must use standard IBAN. Currency-to-country restriction applies to all 10 supported currencies.
- **Financial risk:** Low — wrong beneficiary details (e.g. QR-IBAN for CHF) cause transfer failure; currency-country mismatch also fails.

---

## Article 9707350 — International Transfers: Fees, Currencies, and Limits
- **Topic:** Complete guide to sending international (non-SEPA) transfers from client-a, including fees, supported currencies, and limits.
- **Key facts:** client-a supports **10 currencies** for outgoing international transfers. **Fees by plan (all prices HT):** Free: 1% of amount (minimum €5); Start: 0.75% (minimum €4); Plus: 0.60% (minimum €4); Business: 0.45% (minimum €4). **Maximum per transfer: €100,000.** Each currency can only be sent to its home country (USD to US, GBP to UK, CHF to Switzerland, etc.). Step-by-step process available in the app.
- **Conditions/exceptions:** Fees are percentage-based with a minimum floor — small transfers cost disproportionately more. Currency-country restriction is absolute. Max €100k per transfer.
- **Financial risk:** Moderate — chatbot must state the correct fee tier per plan; quoting the wrong percentage leads to mispriced international transactions. Must also mention the €100k cap and currency-country restriction.

---

## Article 9707601 — Changing the App Language
- **Topic:** How to change the display language of the client-a app.
- **Key facts:** The app language follows the device's system language automatically. On **iOS 13 and later**, the language can be set per-app independently of the system language (iOS Settings > client-a > Language).
- **Financial risk:** None — language preference setting.

---

## Article 9711196 — Cash Flow Tracking (Suivi de Trésorerie) — Possibly Outdated Plan Naming
- **Topic:** The cash flow tracking feature in client-a, showing historical income and expense flows.
- **Key facts:** Available from the **"client-a Pro" plan** per this article — note that "client-a Pro" is likely outdated naming (see also articles 5817496, 6015464); current equivalent plan should be verified. The feature shows income and expense flows and available balance over time. **Does NOT track:** TVA, accounts receivable, or accounts payable. Historical data starts from 2023 only.
- **Conditions/exceptions:** Outdated plan naming ("client-a Pro") — chatbot must not use this article's plan name without verifying current plan structure. Feature is in Beta.
- **Financial risk:** Low — if chatbot cites availability on "client-a Pro" users may not find the feature under the current plan structure.

---

## Article 9735087 — Untitled Public Article — Empty Article
- **Topic:** Unknown — article has no title and no body content.
- **Key facts:** Article body is **empty** — no content in the knowledge base.
- **Financial risk:** None — empty stub.

---

## Article 9783045 — Modifying or Restarting a Registration Dossier
- **Topic:** How to fix errors in a registration dossier that is in progress with client-a.
- **Key facts:** **Minor corrections:** click "Précédent" in the flow to navigate back and fix. **Simple corrections post-submission** (share distribution, personal information, duplicate beneficial owner entry): contact client-a support — these can be corrected without restarting. **Complex corrections** (e.g. wrong legal form, fundamental statuts error): client-a support resets the entire dossier and the user must restart from scratch.
- **Conditions/exceptions:** Not all corrections require a full restart — chatbot should direct users to contact support before assuming a restart is needed.
- **Financial risk:** None — registration process guidance.

---

## Article 9783050 — Chequebook with client-a
- **Topic:** Whether client-a clients can obtain and use a chequebook.
- **Key facts:** client-a does **not offer chequebooks** and cannot issue cheques. This is because client-a is an **établissement de paiement**, not an établissement de crédit — chequebook issuance requires credit institution status. Users who need to pay by cheque must use another banking institution.
- **Conditions/exceptions:** client-a can receive cheques (deposit) but cannot issue them. No exception or workaround available.
- **Financial risk:** Low — a user relying on chatbot guidance to "get a chequebook from client-a" will be misled; in time-sensitive supplier payment situations this can cause cash flow issues.

---

## Article 9857130 — 3 Months Free on client-a Basic — EXPIRED PROMOTION
- **Topic:** A promotional offer for 3 months free on the "client-a Basic" plan.
- **Key facts:** This promotional offer **expired** (ran from September 16 to October 13, 2024). After the promotion, "client-a Basic" was priced at €7.90 HT/month. The article uses the legacy "Basic" plan name which may no longer correspond to current plan naming.
- **Conditions/exceptions:** Promotion is expired. "Basic" plan naming is outdated.
- **Financial risk:** None — expired promotion; chatbot must not reference this offer as current.

---

## Article 9937465 — Card Expense Categories
- **Topic:** How client-a categorises card transactions and what categories are available.
- **Key facts:** 17 categories are available, assigned automatically based on the Mastercard MCC (Merchant Category Code) of the merchant. Non-card transactions (transfers, debits) are classified as "non catégorisée." Users can manually change the category of any transaction.
- **Financial risk:** None — expense categorisation feature.

---

## Article 9979058 — Card Renewal
- **Topic:** How client-a card renewal works — timing, process, and address confirmation.
- **Key facts:** client-a cards are valid for **3 years**. Cards auto-renew approximately **1 month before expiry**. A few weeks before expiry, client-a prompts the user to confirm their delivery address; if not confirmed, the card is sent to the address on file. Dispatch occurs approximately 3 weeks before the expiry date; delivery takes 1–2 weeks after dispatch.
- **Conditions/exceptions:** If the user does not confirm address, card ships to the registered address — users must update address in advance if they have moved.
- **Financial risk:** None — card renewal logistics.

---

<!-- 9992293: Collection ID — not an article. No analysis. -->

## Summary: High Financial-Risk Articles

The following articles carry the highest risk of direct financial harm if a chatbot provides wrong or incomplete answers:

| Article ID | Topic | Risk |
|---|---|---|
| 13390711 | E-invoicing reform | Wrong compliance deadlines → regulatory fines |
| 13377816 | VAT rates | Wrong rate → incorrect tax amounts |
| 13378833 | Invoice numbering | Non-sequential numbering = fiscal violation |
| 13419459 | Subscription pricing | Wrong plan features or prices → bad purchase decisions |
| 8537771 | Team access pricing | Wrong pro-rata or plan pricing → unexpected charges |
| 8442719 | Instant transfer limits & VoP | Wrong limits or missing VoP info → payment failures |
| 8490052 | Receipt certification | Implies legal certification → users discard originals, fail tax audits |
| 8385519 | SWIFT fees and BIC codes | Wrong fees, BICs, or FX info → financial loss |
| 8711129 | Sub-account limits | Wrong plan limits or feature scope |
| 6715420 | Mandatory invoice mentions | Missing mentions → fines up to €375,000 |
| 6365046 / 6310223 | Old IBAN migration | Premature mandate revocation → missed tax/supplier payments |
| 6020340 | Batch transfers | Business-only; format errors → failed payments |
| 5096371 | Virtual card pricing & limits | Wrong Free-plan pricing or spending limit |
| 5076758 | Auto-entrepreneur tax declaration | Wrong boxes or pre-applied abattement → wrong tax assessment |
| 4680080 | Activity-specific invoice mentions | Missing fields → compliance violations |
| 4062963 | Late payment penalty rates | Wrong rate → invoice non-compliance |
| 3864336 | Modifying sent invoices | Deleting sent invoices is illegal |
| 3629915 | SEPA direct debit disputes | B2B = no refund; CORE 8-week deadline is a hard limit |
| 3565695 | Cheque delays and rejection fees | Cash flow implications; hard validity/submission deadlines |
| 3155257 | B2B SEPA mandate references | Wrong references → failed tax/supplier payments |
| 3124917 | Financing rates and eligibility | Wrong rates (Defacto 0.05%/day; ADIE 9.87%) → bad financial decisions |
| 3122320 | Cheque fees per plan | Wrong deposit limits or rejection fees → unexpected charges |
| 10485933 | New pricing rollout timeline | Wrong migration dates or commitment rules → decisions under false cost assumptions |
| 10490776 | New Pro account plan details | Wrong prices, quotas, or HT/TTC framing → unexpected charges or bad plan selection |
| 10495320 | Company creation offers | Prices exclude legal fees; fee waivers require commitment — omitting this misleads on real cost |
| 10495791 | Annual billing discounts | Wrong annualised prices or eligibility (micro = 6 months max; not at sign-up) → wrong financial expectations |
| 1175739 | Subscription commitment and cancellation | Annual billing = no refund if cancelled early — chatbot must not promise a pro-rata refund |
| 1175607 | Multiple client-a accounts | Per-account subscription billing; one account per company — commingling funds or missing billing info |
| 10503171 | Capital deposit pricing | Fee waiver requires 12-month commitment; all prices HT — omitting either misleads on real cost |
| 10673790 | Refund / withdrawal conditions | 15-day window + 3 hard conditions (CGU art. 36.4) — incorrect refund guidance has direct financial consequences |
| 11459151 | E-invoicing reform dates and scope | Wrong deadlines or scope → non-compliance and fiscal penalties |
| 1179228 | Cash deposit fees and limits | Wrong fee % per plan or missing overseas territory exclusion → unexpected costs or failed deposit |
| 1182854 | Foreign card fees | Wrong payment % or ATM fee structure per zone → unexpected international charges |
| 1182858 | ATM withdrawal limits | Wrong 30-day limit per plan (esp. Free €500) → cash flow failures |
| 1183030 | Card opposition fees | Wrong replacement fee per plan; block is irreversible — must not imply card can be reactivated |
| 1180658 | Card payment ceilings | Wrong limits per plan → large-transaction payment failures |
| 1176688 | Account closure | Pending refunds must be resolved first; zero balance required — missing this risks losing funds |
| 1183407 | Direct debit opposition | Article is incomplete — B2B no-refund rule and 8-week CORE deadline missing; chatbot must use article 3629915 for full context |
| 1184066 | Creating invoices on client-a | Default 20% VAT must be set to 0% for non-liable entities; non-sequential numbering = tax violation |
| 1183053 | Card declined | 3-PIN / 5-CVV block thresholds; guarantee pre-auths can drain balance silently |
| 11876683 | Company creation timeline | Artisanal immatriculation takes up to 1 month — wrong timeline affects capital planning |
| 11886479 | Activité vs objet social | Wrong APE code affects cotisation rates and collective agreements |
| 1195312 | Deleting/cancelling invoices | Emitting a downloaded PDF = legal emission; deleting an emitted invoice violates anti-VAT fraud law |
| 1195328 | Per-item VAT customisation | Non-zero VAT on a non-liable micro-entrepreneur = false tax obligation |
| 1195405 | Which VAT rate to apply | Wrong rate → incorrect billing and tax declarations; missing "TVA non applicable" mention is a violation |
| 1200519 | Micro-enterprise CA thresholds | Figures are from 2022 — thresholds updated annually; citing wrong amounts triggers unexpected tax regime change |
| 1227397 | Standard tax regime (no versement libératoire) | Pre-applying abattement before declaring gross CA = misrepresented taxable income and tax penalties |
| 1200572 | Unpaid invoices / reminders | Minimum late payment rate is 14.76% — lower rate = non-compliant invoice |
| 12067200 | Processing received e-invoices | Refusing an e-invoice does NOT cancel a pre-authorised payment |
| 13390371 | Modifying/deleting a sent client invoice | Deleting a sent invoice is illegal — must use avoir; wrong answer = anti-VAT fraud law violation |
| 12320536 | Verification of Payee (VoP) | User is liable if they proceed with a transfer despite a non-match result |
| 12672874 | E-invoicing sanctions | 15 €/invoice + 250 €/data error (max 15 k€/year); first infraction tolerated only if corrected quickly |
| 12548842 | E-invoicing reform scope | Special cases (associations, SCI, DOM/COM, etc.) may have different obligations — wrong blanket answer risks missed compliance |
| 13401639 | E-invoicing reform scope (questionnaire) | Near-duplicate of 12548842 but less complete — same risk if chatbot uses this instead of 12548842 |
| 13402315 | Sending e-invoices | Missing client e-invoice address = delivery failure; untracked failures = unpaid invoices |
| 13859730 | Creating a credit note (avoir) | Partial avoir not supported; avoir mandatory for sent invoices — wrong answer risks anti-VAT fraud law violation |
| 1369683 | Post-SIRET admin checklist | CFE deadline 31 Dec; ACRE not retroactive — missed steps = back-taxes or lost social charge reductions |
| 1464557 | Card payment collection fees | 500 € invoice ceiling; wrong fee rate (1.20 % vs 2.70 % out-of-zone) leads to mispriced services |
| 1470511 | Card fraud contestation | Must block card first; police report required — omitting either step risks unrecovered fraudulent charges |
| 1523571 | Closing an old bank account | Unupdated SEPA mandates → failed payments; negative balance at closure → management fees |
| 1536163 | Changing business address | SIE notification due by 2nd working day after 1 May — missing deadline is a regulatory violation |
| 1613967 | Attestation de vigilance | Required for contracts ≥ 5 000 € HT; 3–6 week + 90-day timing constraints block new entrepreneurs |
| 1782334 | First quarterly URSSAF declaration | Wrong first filing month → late declaration penalties; extended 6-month first period is non-obvious |
| 1984835 | First monthly URSSAF declaration | 4-month initial period easy to miss; wrong first filing month → late declaration penalties |
| 1849671 | Cancelling a card payment | Impossible — chatbot must not imply otherwise; only remedy is card blocking + contestation |
| 1849674 | How to pay URSSAF contributions | Wrong CA activity box → wrong rate; net-entreprises.fr outdated since 2019 |
| 1983082 | APE code for bike delivery workers | Code 5610C (wrong) vs 53.20Z (correct) — wrong code → wrong cotisation rate and URSSAF penalties |
| 2046039 | Recognising fraudulent mail | Failing to identify scam letters targeting new entrepreneurs = direct financial loss |
| 2090492 | Revenue declaration from parents' tax household | Wrong BNC/BIC category = tax misclassification and potential reassessment |
| 2104919 | EU VAT number for bike delivery workers | Required to bill EU companies even if non-VAT-liable; missing it = billing non-compliance |
| 2141522 | Invoicing EU clients without VAT liability | Missing "autoliquidation" mention = legal compliance violation; VAT rate must be 0 % |
| 2144881 | Billing Euro zone clients + monthly DES | Monthly DES to douanes is mandatory; missing it = customs violation |
| 2212780 | CFE premises questionnaire | Must be returned within 15–30 days of letter receipt — missing deadline = CFE tax calculation error |
| 2330203 | Auto-entrepreneur living abroad | Double taxation risk; monthly DES required; French must be used on invoices |
| 2491213 | Changing URSSAF declaration periodicity | Change only takes effect January next year if active >3 months — timing surprise = missed/late declarations |
| 2536735 | EURL manager social regime | Incomplete article (placeholder "xxxx") — wrong TNS vs régime général classification = major social contribution errors |
| 2914588 | Encaissé vs facturé CA declaration | Must declare received (encaissé) not invoiced — wrong basis = overpayment + 5–15% late surcharges |
| 2975813 | Tax return guide for bike delivery workers | Outdated 2018 content with specific tax box numbers (5TB, 5TE, etc.) that may no longer apply |
| 2998190 | Attaching receipts to transactions | Digital receipts in client-a have no legal probative value — originals still required for tax audit |
| 3074279 | Capital deposit eligibility criteria | Wrong liberation % by legal form (50% SAS/SASU vs 20% SARL/EURL) invalidates dossier |
| 3074902 | Wiring capital deposit funds | Neobank wires systematically rejected; exact amount required to the cent; wrong account = rejected |
| 3074930 | Capital deposit process steps | Wire from ineligible country = notary rejection; not transmitting final Kbis = funds locked indefinitely |
| 3080543 | Refusing ACRE to preserve for later | Refusal must be registered letter with AR — failure = ACRE auto-consumed with no second chance |
| 3119252 | Cheque deposit | 15-day hard deadline to mail physical cheque; €5,000 per-cheque limit; €2 HT overage fee |
| 3159999 | Delivery worker documents | Motorised vehicle delivery requires capacité attestation AND registry inscription — missing 2nd step = illegal transport |
| 3191158 | Reimbursing pre-incorporation expenses | 3–6 month window + receipt naming future company required; re-invoicing forfeits TVA recovery |
| 3399375 | EU VAT number when non-VAT-liable | Mandatory even in franchise de base when billing any EU client — omitting it = non-compliant invoices |
| 3549525 | Documents for capital deposit | Missing mandatory verbatim statuts mentions blocks the capital deposit |
| 3549713 | Capital deposit wire transfer conditions | Neobank wires rejected; wrong country, wrong account, wrong amount, or missing label = rejected wire |
| 3551393 | Transmitting Kbis to client-a | Must send final Kbis + signed statuts proactively — without it, company funds remain locked indefinitely |
| 3563079 | ICS/SEPA direct debit not available | SEPA direct debits contestable 8 weeks (or 13 months without mandate) — account can go negative |
| 3606170 | Applying for ACRE | 45-day deadline from P0 declaration is absolute — missing it = entire first-year contribution reduction lost |
| 3606432 | Non-accepted business activities | Account opened with prohibited activity = closure risk; list is non-exhaustive |
| 3674717 | Traite/LCR not supported | Incoming traites silently rejected with no notification — clients using traite will not pay |
| 4345589 | Artiste-auteur social contributions | URSSAF Limousin manages since 2020 (not Maison des Artistes/AGESSA) — directing to old bodies = missed payments and late penalties |
| 4602862 | Account termination by client-a | Immediate closure if CGU violated (no notice); reason cannot be disclosed during investigation — sudden operational disruption |
| 4623268 | Complaint process | Professionals excluded from banking mediation (médiation bancaire) — chatbot must not suggest this escalation path to business customers |
| 4703268 | Dormant account fees | €25/year fee after 1 year inactivity; subscription debits don't count as activity — counter-intuitive rule surprises users |
| 4838783 | Creating impots.gouv.fr professional space | 60-day deadline to enter postal activation code — missing it restarts process with 60-day wait; CFE/TVA payments blocked |
| 4854613 | Modifying liberal activity (URSSAF) | Must click "Télédéclarer" to actually submit — form completion alone is not submission; missed step = activity change not registered |
| 4877782 | EU imports/exports as micro-entrepreneur | Monthly DES mandatory for all EU service exports regardless of VAT status — missing = customs violation with fines |
| 4879145 | Non-EU imports/exports (pays tiers) | EORI number + DAU on Delt@ mandatory for both import/export — operating without them = customs violations |
| 5227769 | Contesting an online card payment | Must block card AND file Perceval declaration — omitting Perceval risks non-reimbursement of fraudulent charges |
| 5544130 | RC Pro liability insurance | Mandatory for 60 regulated professions — chatbot must flag this obligation or leave user uninsured |
| 5779244 | Professional credit interest rate | Rate is 5.50–7.50% (no-guarantee model) — citing standard bank rates (3–4%) without context misleads users on real loan cost |
| 5817496 | Subscription differences | Outdated article (legacy "Basic/Premium" plan names and prices) — using it for pricing gives wrong information |
| 6309428 | Updating banking details for direct debits | Revoking old SEPA mandates causes payment failures; B2B mandates require two-step update — chatbot must always include the do-not-revoke warning |
| 6485710 | Accountant access (conflicts with 6671728) | States Business-only; 6671728 says Start/Plus/Business — using 6485710 alone incorrectly restricts accountant access eligibility |
| 6740984 | Capital increase | Luxembourg excluded despite EU membership; individual subscribers must be France-domiciled — wrong eligibility info invalidates the process |
| 7139198 | Deposit invoice (facture d'acompte) | "Facture d'acompte" label + quote ref mandatory; TVA on acomptes required since Jan 2023 for both goods and services; price increases require signed avenant |
| 8010261 | Fake advisor phishing/vishing | client-a never asks for credentials or remote validation — chatbot must proactively warn users of this to prevent fraud losses |
| 8385614 | SWIFT transfer reception fees | 3-component fee structure (client-a €5–6 HT + interbank OUR/SHA/BEN + FX); BEN option means recipient gets less than invoiced without warning |
| 8417263 | Contesting a wire transfer | Wrong-IBAN recovery not guaranteed (requires receiving bank consent); police report mandatory for fraud — chatbot must not imply funds are always returned |
| 8870977 | Ineligible activities for micro-enterprise | Regulated professions, artiste-auteur, agricultural, real estate activities cannot register as micro-entrepreneur — chatbot must flag this before helping register |
| 9042102 | ID documents for capital deposit | ALL associates (even 1%) must provide ID; salarié/étudiant/saisonnier/visiteur visa categories not accepted for company creators; must be live photo — one wrong document blocks the entire dossier |
| 9241450 | Failed SEPA direct debit | DGFIP tax debits always use B2B mandate — missing mandate = failed tax payment; traite/LCR silently rejected; only creditor controls debit date |
| 9250660 | Professional account mandatory (PACTE law) | Account required if CA > €10,000 for 2 consecutive years — chatbot must state threshold precisely to avoid compliance error |
| 9367043 | Suspending/revoking SEPA mandate | Card-based subscription debits cannot be stopped by client-a — must contact creditor; chatbot must distinguish SEPA mandate vs card subscription |
| 9414732 | Cancelling an outgoing SEPA transfer | Cancellation only possible before transfer reaches SEPA network; once dispatched → contact beneficiary — chatbot must not imply always cancellable |
| 9561237 | Credit note (avoir) creation | Conflicts with article 13859730 (partial avoir not supported) — use 13859730 as authoritative source; wrong avoir guidance risks anti-VAT fraud law violation |
| 9707350 | International transfer fees and limits | Fee varies by plan (0.45%–1% HT); max €100k per transfer; each currency only payable to home country — wrong fee or limit guidance misleads on real cost |
