---
name: insights-skill
description: >-
  Financial insights and analytics. Use this skill for revenue overviews, KPI
  dashboards, monthly revenue trends, top customers by revenue, overdue and aging
  reports, product performance analysis, trend analysis, and outlier / anomaly
  detection. Also use it when the user asks what insights, reports, or analyses are
  available. Ad-hoc questions: "how is revenue looking?", "who owes me money?", "which
  products sell best?", "is revenue trending up?", "show me unusual months", "what can
  you show me?".
metadata:
  adk_additional_tools:
    - get_insight_monthly_revenue
    - get_insight_top_customers
---

# Insights & Analytics

## How It Works

All insight panels are **self-fetching React components** — they pull their own data
from the Billy API. Your job is simply to:

1. Identify which panel(s) the user wants.
2. Emit one **surface** per panel. Each surface has its own data model, so panels with
   different years fetch independently.

You do **not** need to fetch, aggregate, or push data. Components handle that.

---

## Surface ID Rules

| Surface ID                  | Purpose                                                                                   |
| --------------------------- | ----------------------------------------------------------------------------------------- |
| `"main"`                    | The primary panel — always overwrite, never delete                                        |
| `"suggestions"`             | DashboardSuggestions chips — set once on the initial dashboard, persists across responses |
| `"panel_1"`, `"panel_2"`, … | Extra panels for side-by-side comparison — delete after use                               |

**Never emit `deleteSurface` for `"main"` or `"suggestions"`.** Whenever your response
uses only `"main"` (i.e. any single-panel response, including after a comparison AND
after the initial dashboard), emit `deleteSurface` for every `"panel_*"` surface that
may exist (`"panel_1"`, `"panel_2"`, etc.). Always include these deletes even if you are
unsure whether the surface was created — a delete for a non-existent surface is
harmless.

---

## Functional Rules

1. **One surface per panel.** Every panel you emit gets its own `surfaceId` with its own
   `createSurface` + `updateDataModel` + `updateComponents` triple. This ensures that
   two panels showing different years actually fetch different data.

2. **ALWAYS emit a surface — this is mandatory.** Every insight response MUST include a
   `---a2ui_JSON---` block. Text-only responses are a failure.

3. **Fiscal year / month.** Default to the current year (2026). Include
   `{ "year": 2026 }` in each panel's `updateDataModel`. When the user asks for a
   specific month (e.g. "last month", "March", "income in February"), also include
   `"month": <1–12>` in the data model for `RevenueSummary`. The component will filter
   data to that month and show "Mar 2026" in the period badge instead of just "2026".

4. **Labels — always translate.** Every `updateDataModel` MUST include a `labels` object
   with all panel titles and structural UI strings translated into the user's language.
   Omitting labels causes the UI to fall back to English.

   ```json
   "labels": {
     "rev_title":           "Revenue Overview",
     "pipe_title":          "Invoice Pipeline",
     "chart_title":         "Monthly Revenue",
     "chart_invoiced":      "Invoiced",
     "chart_paid":          "Paid",
     "chart_footer":        "Amounts excl. VAT",
     "top_title":           "Top Customers",
     "top_subtitle":        "by revenue",
     "top_leg_paid":        "Paid",
     "top_leg_invoiced":    "Invoiced",
     "top_leg_outstanding": "Outstanding",
     "top_paid":            "✓ paid",
     "top_nodata":          "No data",
     "aging_title":         "Aging Report",
     "aging_as_of":         "as of",
     "aging_overdue_label": "Overdue",
     "aging_col_invoice":   "Invoice",
     "aging_col_customer":  "Customer",
     "aging_col_due":       "Due date",
     "aging_col_amount":    "Amount",
     "aging_inv":           "inv.",
     "aging_empty":         "No outstanding invoices",
     "cust_kpi_invoiced":   "Invoiced",
     "cust_kpi_collected":  "Collected",
     "cust_kpi_outstanding":"Outstanding",
     "cust_kpi_overdue":    "Overdue",
     "cust_open_invoices":  "Open invoices",
     "cust_all_paid":       "✓ All invoices paid",
     "cust_last":           "Last:",
     "cust_loading":        "Loading…",
     "cust_overdue":        "overdue",
     "prod_title":          "Product Revenue",
     "prod_excl_vat":       "excl. VAT",
     "prod_qty":            "qty",
     "prod_nodata":         "No data",
     "sugg_heading":        "Explore further"
   }
   ```

   Only include the keys relevant to the panels you are emitting.

5. **Narrate key findings.** Add 1–2 sentences of prose before the delimiter.

6. **Bridge.** End with a relevant follow-up suggestion:
   - After aging report: "Want me to draft reminder emails for the overdue invoices?"
   - After top customers: "Want to see the open invoices for [top customer]?"
   - After revenue summary: "Should I create an invoice to help close this month's gap?"

7. **Amount formatting.** All amounts are excl. VAT. Always mention the currency (DKK by
   default).

8. **Insight discovery.** When the user asks what insights, analyses, or reports are
   available (e.g. "what can you show me?", "what insights do you have?", "what kind of
   analysis can you do?"):
   - Introduce the six categories as a markdown list with **clickable links** — each bold
     label must be `[**Label**](<query>)` where `query` is the chat message sent on click:
     ```
     - [**Revenue**](<Revenue overview>) — high-level summaries of your income and collections
     - [**Invoice pipeline**](<Invoice pipeline>) — a breakdown of draft, sent, and overdue invoices
     - [**Customer insights**](<Top customers>) — rankings of your top customers and individual balance summaries
     - [**Payment tracking**](<Who owes me money?>) — aging reports showing who owes you money and for how long
     - [**Product performance**](<Which products sell best?>) — analysis of which products generate the most revenue
     - [**Trend & anomaly detection**](<Is revenue trending up?>) — growth comparisons (YoY/MoM) and unusual revenue spikes
     ```
   - Emit `DashboardSuggestions` on `"suggestions"` using **exactly** the suggestions
     array in the example below — do not substitute, reorder, or omit any item.
   - Also emit `RevenueSummary` on `"main"` as a useful default so the screen is not
     empty.

   ```
   Here is everything I can analyse for you — click any item or use the shortcuts below:
   ---a2ui_JSON---
   [
     { "version": "v0.9", "deleteSurface": { "surfaceId": "panel_1" } },
     { "version": "v0.9", "deleteSurface": { "surfaceId": "panel_2" } },
     { "version": "v0.9", "createSurface": { "surfaceId": "main", "catalogId": "https://a2ui.org/catalog/basic/v0.8/catalog.json" } },
     { "version": "v0.9", "updateDataModel": { "surfaceId": "main", "path": "/", "value": { "year": 2026, "labels": { "rev_title": "Revenue Overview" } } } },
     { "version": "v0.9", "updateComponents": { "surfaceId": "main", "components": [{ "id": "root", "component": "RevenueSummary" }] } },
     { "version": "v0.9", "createSurface": { "surfaceId": "suggestions", "catalogId": "https://a2ui.org/catalog/basic/v0.8/catalog.json" } },
     { "version": "v0.9", "updateDataModel": { "surfaceId": "suggestions", "path": "/", "value": {
       "suggestions": [
         "Revenue overview",
         "Invoice pipeline",
         "Monthly revenue 2026",
         "Top customers",
         "Who owes me money?",
         "Which products sell best?",
         "Show Acme's balance",
         "Is revenue trending up?",
         "Compare 2025 vs 2026",
         "Any unusual months?"
       ],
       "labels": { "sugg_heading": "Available analyses" }
     } } },
     { "version": "v0.9", "updateComponents": { "surfaceId": "suggestions", "components": [
       { "id": "root", "component": "DashboardSuggestions" }
     ] } }
   ]
   ```

9. **Trend analysis.** When the user asks about trends, growth, decline, or
   year-over-year / MoM comparisons:

   **Step 1 — fetch data (mandatory).** Call `get_insight_monthly_revenue` for each year
   involved. Do NOT skip this step.

   **Step 2 — compute & write the analysis (mandatory).** You MUST write the findings as
   prose BEFORE the `---a2ui_JSON---` delimiter. A text-only response without numbers is
   a failure. Include:
   - **Single year:** each non-zero month's invoiced amount, the MoM change in %, and
     which month had the peak. Example: "Revenue climbed steadily — 18,400 DKK in
     January, +31% to 24,200 DKK in February, then 22,200 DKK in March. April is the
     strongest month so far at 37,800 DKK."
   - **Two years (YoY):** average monthly invoiced for each year (non-zero months only),
     YoY % change, peak month per year, and same-period comparison ("Through April 2026
     you have invoiced X DKK vs Y DKK over the same 4 months in 2025 — tracking Z%
     ahead").

   **Step 3 — emit the chart.** Emit `RevenueChart` on `"main"` for the newer year. Emit
   `RevenueChart` on `"panel_1"` for the older year (YoY only).

   Bridge: "Want me to break this down by customer or product?"

   **Side-by-side is MANDATORY whenever two years are involved.** Any of the following
   MUST produce two panels — `RevenueChart` on `"main"` for the newer year and
   `RevenueChart` on `"panel_1"` for the older year. Never collapse a two-year request
   into a single panel or a text-only response:
   - "compare 2025 and 2026"
   - "how does it compare to last year" (current year on `"main"`, previous year on
     `"panel_1"`)
   - "and one for 2025 as well" / "show 2025 too" (user already sees one year — add the
     other as `"panel_1"`, keep the existing year on `"main"`)
   - "show revenue for 2025 and 2026"

10. **Outlier / anomaly analysis.** When the user asks about anomalies, spikes, unusual
    months, or outliers:

    **Step 1 — fetch data (mandatory).** Call `get_insight_monthly_revenue` to get the
    12-month series. Do NOT skip this step.

    **Step 2 — compute & write the analysis (mandatory).** You MUST write the findings
    as prose BEFORE the `---a2ui_JSON---` delimiter. A response without named months and
    numbers is a failure.

- Compute the mean invoiced amount across non-zero months.
- Flag any month where invoiced > mean × 1.5 (high outlier) or invoiced < mean × 0.5
  (low outlier).
- Optionally call `get_insight_top_customers` if you need to explain what drove a spike.
- Name every outlier explicitly: "The monthly average is 21,000 DKK. April stands out at
  37,800 DKK — 1.8× the average. January was below average at 9,400 DKK."
- If no outliers exist, say so: "Revenue is fairly consistent — no month deviates more
  than 50% from the 21,000 DKK average."

**Step 3 — emit the chart.** Emit `RevenueChart` on `"main"` so the bars make the spike
visible.

Bridge: "Want me to drill into a specific month or customer?"

---

## Output Format

### Single panel

Always emit `deleteSurface` for `panel_1` and `panel_2` before the `createSurface` for
`main`.

```
Your revenue overview for 2026 is ready.
---a2ui_JSON---
[
  { "version": "v0.9", "deleteSurface": { "surfaceId": "panel_1" } },
  { "version": "v0.9", "deleteSurface": { "surfaceId": "panel_2" } },
  { "version": "v0.9", "createSurface": { "surfaceId": "main", "catalogId": "https://a2ui.org/catalog/basic/v0.8/catalog.json" } },
  { "version": "v0.9", "updateDataModel": { "surfaceId": "main", "path": "/", "value": { "year": 2026, "labels": { "rev_title": "Revenue Overview" } } } },
  { "version": "v0.9", "updateComponents": { "surfaceId": "main", "components": [
    { "id": "root", "component": "RevenueSummary" }
  ] } }
]
```

### Initial dashboard (triggered by "show me a dashboard")

Emit `RevenueSummary` on `"main"`, `InvoiceStatusChart` on `"panel_1"`, and
`DashboardSuggestions` on `"suggestions"`. Each surface is independent.

Vary the suggestions each time — rotate in trend and outlier options so the user
discovers them. Example pools to draw from (pick 5–6 per dashboard):

- "Who owes me money?", "Show top customers", "Monthly revenue 2026", "Which products
  sell best?", "Show Acme's balance", "Show monthly revenue for 2025"
- "Is revenue trending up?", "Any unusual months?", "Compare 2025 vs 2026", "Which month
  had the highest revenue?", "Show revenue trend for 2025"

```
Here is your accounting overview for 2026.
---a2ui_JSON---
[
  { "version": "v0.9", "createSurface": { "surfaceId": "main", "catalogId": "https://a2ui.org/catalog/basic/v0.8/catalog.json" } },
  { "version": "v0.9", "updateDataModel": { "surfaceId": "main", "path": "/", "value": {
    "year": 2026,
    "labels": { "rev_title": "Revenue Overview" }
  } } },
  { "version": "v0.9", "updateComponents": { "surfaceId": "main", "components": [
    { "id": "root", "component": "RevenueSummary" }
  ] } },

  { "version": "v0.9", "createSurface": { "surfaceId": "panel_1", "catalogId": "https://a2ui.org/catalog/basic/v0.8/catalog.json" } },
  { "version": "v0.9", "updateDataModel": { "surfaceId": "panel_1", "path": "/", "value": {
    "year": 2026,
    "labels": { "pipe_title": "Invoice Pipeline" }
  } } },
  { "version": "v0.9", "updateComponents": { "surfaceId": "panel_1", "components": [
    { "id": "root", "component": "InvoiceStatusChart" }
  ] } },

  { "version": "v0.9", "createSurface": { "surfaceId": "suggestions", "catalogId": "https://a2ui.org/catalog/basic/v0.8/catalog.json" } },
  { "version": "v0.9", "updateDataModel": { "surfaceId": "suggestions", "path": "/", "value": {
    "suggestions": ["Who owes me money?", "Show top customers", "Monthly revenue 2026", "Is revenue trending up?", "Any unusual months?", "Which products sell best?"],
    "labels": { "sugg_heading": "Explore further" }
  } } },
  { "version": "v0.9", "updateComponents": { "surfaceId": "suggestions", "components": [
    { "id": "root", "component": "DashboardSuggestions" }
  ] } }
]
```

### Side-by-side comparison (e.g. "compare 2025 and 2026")

Use `"main"` for the first panel, `"panel_1"` for the second. Each has its own year.

```
Here are the revenue summaries for 2025 and 2026 side by side.
---a2ui_JSON---
[
  { "version": "v0.9", "createSurface": { "surfaceId": "main", "catalogId": "https://a2ui.org/catalog/basic/v0.8/catalog.json" } },
  { "version": "v0.9", "updateDataModel": { "surfaceId": "main", "path": "/", "value": {
    "year": 2026,
    "labels": { "rev_title": "Revenue Overview 2026" }
  } } },
  { "version": "v0.9", "updateComponents": { "surfaceId": "main", "components": [
    { "id": "root", "component": "RevenueSummary" }
  ] } },

  { "version": "v0.9", "createSurface": { "surfaceId": "panel_1", "catalogId": "https://a2ui.org/catalog/basic/v0.8/catalog.json" } },
  { "version": "v0.9", "updateDataModel": { "surfaceId": "panel_1", "path": "/", "value": {
    "year": 2025,
    "labels": { "rev_title": "Revenue Overview 2025" }
  } } },
  { "version": "v0.9", "updateComponents": { "surfaceId": "panel_1", "components": [
    { "id": "root", "component": "RevenueSummary" }
  ] } }
]
```

### Trend side-by-side (e.g. "how does it compare to last year", "show 2025 as well", "compare revenue trends")

Always two `RevenueChart` panels — newer year on `"main"`, older year on `"panel_1"`.
Never collapse to one panel.

```
Here are the monthly revenue trends for 2025 and 2026 side by side.
---a2ui_JSON---
[
  { "version": "v0.9", "createSurface": { "surfaceId": "main", "catalogId": "https://a2ui.org/catalog/basic/v0.8/catalog.json" } },
  { "version": "v0.9", "updateDataModel": { "surfaceId": "main", "path": "/", "value": {
    "year": 2026,
    "labels": { "chart_title": "Monthly Revenue Trend 2026", "chart_invoiced": "Invoiced", "chart_paid": "Paid", "chart_footer": "Amounts excl. VAT" }
  } } },
  { "version": "v0.9", "updateComponents": { "surfaceId": "main", "components": [
    { "id": "root", "component": "RevenueChart" }
  ] } },

  { "version": "v0.9", "createSurface": { "surfaceId": "panel_1", "catalogId": "https://a2ui.org/catalog/basic/v0.8/catalog.json" } },
  { "version": "v0.9", "updateDataModel": { "surfaceId": "panel_1", "path": "/", "value": {
    "year": 2025,
    "labels": { "chart_title": "Monthly Revenue Trend 2025", "chart_invoiced": "Invoiced", "chart_paid": "Paid", "chart_footer": "Amounts excl. VAT" }
  } } },
  { "version": "v0.9", "updateComponents": { "surfaceId": "panel_1", "components": [
    { "id": "root", "component": "RevenueChart" }
  ] } }
]
```

### Aging / Overdue report (no year)

```
Here are your overdue invoices.
---a2ui_JSON---
[
  { "version": "v0.9", "deleteSurface": { "surfaceId": "panel_1" } },
  { "version": "v0.9", "deleteSurface": { "surfaceId": "panel_2" } },
  { "version": "v0.9", "createSurface": { "surfaceId": "main", "catalogId": "https://a2ui.org/catalog/basic/v0.8/catalog.json" } },
  { "version": "v0.9", "updateDataModel": { "surfaceId": "main", "path": "/", "value": {
    "labels": { "aging_title": "Aging Report", "aging_overdue_label": "Overdue" }
  } } },
  { "version": "v0.9", "updateComponents": { "surfaceId": "main", "components": [
    { "id": "root", "component": "AgingReport" }
  ] } }
]
```

### Customer summary by name

```
Here is the summary for Acme A/S.
---a2ui_JSON---
[
  { "version": "v0.9", "deleteSurface": { "surfaceId": "panel_1" } },
  { "version": "v0.9", "deleteSurface": { "surfaceId": "panel_2" } },
  { "version": "v0.9", "createSurface": { "surfaceId": "main", "catalogId": "https://a2ui.org/catalog/basic/v0.8/catalog.json" } },
  { "version": "v0.9", "updateDataModel": { "surfaceId": "main", "path": "/", "value": {
    "contactName": "Acme", "year": 2026,
    "labels": { "cust_kpi_invoiced": "Invoiced", "cust_kpi_collected": "Collected", "cust_kpi_outstanding": "Outstanding", "cust_kpi_overdue": "Overdue", "cust_open_invoices": "Open invoices" }
  } } },
  { "version": "v0.9", "updateComponents": { "surfaceId": "main", "components": [
    { "id": "root", "component": "CustomerInsightCard" }
  ] } }
]
```

---

## Panel Reference

| Panel             | Component name                                | Trigger keywords                                                                      |
| ----------------- | --------------------------------------------- | ------------------------------------------------------------------------------------- |
| Revenue KPI Cards | `RevenueSummary`                              | "revenue overview", "KPI", "how is revenue"                                           |
| Invoice Pipeline  | `InvoiceStatusChart`                          | "invoice breakdown", "invoice pipeline", "invoice status"                             |
| Monthly Revenue   | `RevenueChart`                                | "monthly revenue", "revenue by month"                                                 |
| Top Customers     | `TopCustomersTable`                           | "top customers", "biggest customers"                                                  |
| Aging / Overdue   | `AgingReport`                                 | "who owes me", "overdue", "aging report"                                              |
| Customer Summary  | `CustomerInsightCard`                         | "summary for Acme", "what does Acme owe"                                              |
| Product Revenue   | `ProductRevenueTable`                         | "products", "best selling", "revenue by product"                                      |
| Query suggestions | `DashboardSuggestions`                        | Initial dashboard only — surface `"suggestions"`                                      |
| Trend Analysis    | `RevenueChart` (+ optional side-by-side)      | "trend", "trending", "growing", "declining", "year over year", "YoY", "MoM", "growth" |
| Outlier / Anomaly | `RevenueChart` + optional `TopCustomersTable` | "outlier", "anomaly", "unusual", "spike", "anomalous", "what's weird"                 |

### Data model fields per panel

| Panel                                                                    | Accepted fields                                                       |
| ------------------------------------------------------------------------ | --------------------------------------------------------------------- |
| RevenueSummary                                                           | `year` (int), `month` (int 1–12, optional — for monthly breakdown)    |
| InvoiceStatusChart, RevenueChart, TopCustomersTable, ProductRevenueTable | `year` (int)                                                          |
| AgingReport                                                              | `contactId` (str) or `contactName` (str) — optional filter            |
| CustomerInsightCard                                                      | `contactId` (str) **or** `contactName` (str) — required; `year` (int) |
| DashboardSuggestions                                                     | `suggestions` (JSON array of strings)                                 |
| All panels                                                               | `labels` (object) — translated UI strings                             |
