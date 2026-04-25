---
name: invoice-skill
description: >-
  Create, view, list, edit, approve, and summarize invoices. Use this skill for any
  request involving invoice operations including creating new invoices, checking invoice
  status, editing draft invoices, approving invoices, and getting invoice summaries or
  dashboards.
metadata:
  adk_additional_tools:
    - list_invoices
    - get_invoice
    - get_invoice_summary
    - create_invoice
    - edit_invoice
---

# Invoice Operations

## Tools available

- `list_invoices` — list invoices with optional filtering by state, date, customer
- `get_invoice` — fetch details of a specific invoice by ID
- `get_invoice_summary` — dashboard stats grouped by state (draft, approved, paid,
  overdue)
- `create_invoice` — create a new invoice
- `edit_invoice` — update details of a draft OR approve an invoice by changing its state

## Functional Rules

1. **Single-step form.** Show the Detail Surface — Create Form so the user can select
   a customer, add line items, and click **Approve**. When the form is submitted, call
   `create_invoice` directly — no Confirm Surface needed.

2. **VAT is automatic.** Never pass tax or gross amount values — the API calculates
   them. Default currency is DKK. Default state is `"approved"` — omit `state` unless
   the user explicitly wants a draft.

3. **State management.**
   - **Editing:** Only invoices in `draft` state can have their fields updated.
   - **Approving:** If the user says "approve this," call `edit_invoice` with
     `state: "approved"`.
   - **Locked invoices:** If already approved or paid, explain: "This invoice is locked
     for legal compliance. To correct it, a credit note is required."

4. **Bridge after completion.**
   - After creating or approving: "Done — want me to send that invoice by email?"
   - After summarising: "Your dashboard is up to date. Should we follow up on any
     overdue invoices?"

---

## UI Rendering Specifications

These are technical rendering requirements. Follow them exactly whenever a tool is
called or a UI event is received.

### Detail Surface — Create Form (`surfaceId: "detail"`)

Emit when the user wants to create an invoice — including on a `create_invoice` UI event.
The browser fetches customer and product options automatically — do **not** call
`list_products` before showing this form.

**Customer name resolution (before showing the form):** If the user mentioned a customer
name, call `list_customers` with a name filter **before** emitting the form:
- **One match** → use that ID as `customerId` in the initial `updateDataModel`.
- **Multiple matches** → show the form with `customerId: ""` (do NOT pre-select any match) and ask the user to pick in chat (e.g. "I found 2 customers matching 'Peter'. Which one would you like?"). When they respond with their choice, call `list_customers` again with the exact chosen name (tool responses are pruned between turns — you cannot reuse the prior result), then emit a targeted `updateDataModel` for the already-open form to set the `customerId`.
- **No match** → ask if they want to create the customer first; if yes, load customer-skill.
- **No name given** → set `customerId: ""` (user picks in the form).

---

**SETTING THE CUSTOMER WHILE THE FORM IS ALREADY OPEN (chat messages like "set customer to X", "use Lars Hansen", "sæt Lars Hansen", "change customer"):**

When the create form is already visible and the user mentions a customer in chat, follow these steps **in order** — do NOT skip step 2:

1. Call `list_customers` with the mentioned name to find the customer ID.
2. **Immediately after** `list_customers` returns, emit the targeted data update below — this is MANDATORY. No prose before the JSON.
3. Confirm briefly in chat after the JSON (1 sentence).

Output format (the delimiter on its own line, then the JSON array):

```
---a2ui_JSON---
[
  { "version": "v0.9", "updateDataModel": { "surfaceId": "detail", "path": "/form/customerId", "value": "<resolved customer id>" } }
]
```

Do NOT re-emit `createSurface` or `updateComponents` — only the single `updateDataModel` above.
Tool responses are pruned between turns — never reuse a customer ID from a previous turn; always re-call `list_customers`.

---

**ADDING OR SETTING A PRODUCT / LINE ITEM WHILE THE FORM IS ALREADY OPEN (chat messages like "add Konsulentydelser", "add 2 units of X", "set product to X", "change item to Y"):**

When the create form is already visible and the user mentions a product in chat:

1. Call `list_products` to find the product ID.
2. Emit a targeted `updateDataModel` — do **NOT** re-emit `createSurface` or `updateComponents`:

```
---a2ui_JSON---
[
  { "version": "v0.9", "updateDataModel": { "surfaceId": "detail", "path": "/form/pendingProductId", "value": "<product id>" } },
  { "version": "v0.9", "updateDataModel": { "surfaceId": "detail", "path": "/form/pendingQuantity", "value": <quantity as number, default 1> } }
]
```

Always emit **both** messages — `pendingProductId` AND `pendingQuantity`. Use the quantity the user mentioned, or `1` if none given. The browser fills the row and clears both values automatically.

---

**Translation:** Translate every `literalString` value to the user's detected language.

**Message order:** `deleteSurface` for `"panel_1"` → `deleteSurface` for `"panel_2"` → `deleteSurface` for `"main"` → `createSurface` → `updateDataModel` → `updateComponents`

**`updateDataModel`:** surfaceId `"detail"`, path `"/"`, value — set `customerId` to the
resolved ID if known, otherwise `""`:

```json
{
  "form": {
    "customerId": "<resolved id or empty string>",
    "dueDate": "",
    "lineItems": []
  },
  "customerOptions": { "$fetch": "/customers" },
  "productOptions": { "$fetch": "/products" }
}
```

Components (v0.9 flat format):

- `root`: `Column` children `["form-title", "header-row", "line-editor", "actions-row"]`
- `form-title`: `Text` text `{ "literalString": "New Invoice" }` variant `h2`
- `header-row`: `Row` children `["left-col", "right-col"]`
- `left-col`: `Column` children `["customer-field"]` weight `1`
- `customer-field`: `ChoicePicker` options `{ "path": "/customerOptions" }` selections `{ "path": "/form/customerId" }` maxAllowedSelections `1` label `{ "literalString": "Customer" }` onCreateAction `"create_customer"`
- `right-col`: `Column` children `["entry-date-field", "due-date-field"]` weight `1`
- `entry-date-field`: `DatePicker` label `{ "literalString": "Date" }` *(custom component — interactive date picker with calendar popup; label on left, value on right)*
- `due-date-field`: `DueDatePicker` value `{ "path": "/form/dueDate" }` label `{ "literalString": "Due date" }` *(custom component — renders Net preset selector with On receipt / Net 15/30/60/90 and a custom "Net… X days" spinner; calculates and writes the ISO due date automatically; label on left, picker on right)*
- `line-editor`: `LineItemEditor` *(custom component — renders editable line item rows with Add/remove, Description column, calculated totals incl. VAT; reads `/productOptions`, writes to `/form/lineItems` automatically)*
- `actions-row`: `Row` children `["submit-btn", "cancel-btn"]`
- `submit-btn`: `Button` child `"submit-label"` action `{ "type": "event", "name": "submit_invoice_form", "context": [{"key":"customerId","value":{"path":"/form/customerId"}},{"key":"dueDate","value":{"path":"/form/dueDate"}},{"key":"lineItems","value":{"path":"/form/lineItems"}}] }`
- `submit-label`: `Text` text `{ "literalString": "Approve" }`
- `cancel-btn`: `Button` child `"cancel-label"` action `{ "type": "event", "name": "cancel_invoice" }`
- `cancel-label`: `Text` text `{ "literalString": "Cancel" }`

`createSurface`: surfaceId `"detail"`, catalogId `"https://a2ui.org/catalog/basic/v0.8/catalog.json"`.

**UI events:**

- `submit_invoice_form` — the context contains `customerId`, `dueDate`, and `lineItems`
  (written by the `LineItemEditor`). Validate: customer selected and at least one line
  item with a product. If invalid, reply in chat. If valid: emit `deleteSurface` for
  `"detail"`, then call `create_invoice` directly with `customerId`, `dueDate`, and the
  line items (each needing `productId`, `quantity`, `unitPrice`). On success confirm in
  chat ("Done — want me to send that invoice by email?"). Do **not** show the Confirm
  Surface.

- `create_customer` — the context contains `name` (the text the user typed). Emit
  `deleteSurface` for `"main"`, then load customer-skill and show the Create Customer
  form pre-populated with that name. When the customer is created, return to this skill
  and re-emit the Detail Surface — Create Form: emit `createSurface` → `updateDataModel`
  (path `"/"`, value
  `{ "form": { "customerId": "<new customer id>", "dueDate": "", "lineItems": [] }, "customerOptions": { "$fetch": "/customers" }, "productOptions": { "$fetch": "/products" } }`)
  → `updateComponents` (same components as above). The browser will fetch fresh options
  and pre-select the new customer. Do **not** call `list_customers` or `list_products`.

- `create_product` — the context contains `name` (the text the user typed). Emit
  `deleteSurface` for `"main"`, then load product-skill and show the Create Product form
  pre-populated with that name. When the product is created, return to this skill and
  re-emit the Detail Surface — Create Form: emit `createSurface` → `updateDataModel`
  (path `"/"`, value
  `{ "form": { "customerId": "", "dueDate": "", "lineItems": [], "pendingProductId": "<new product id>" }, "customerOptions": { "$fetch": "/customers" }, "productOptions": { "$fetch": "/products" } }`)
  → `updateComponents` (same components as above). The browser will fetch fresh options
  and the `LineItemEditor` will auto-select the new product. Do **not** call
  `list_products`.

- `cancel_invoice` — emit `deleteSurface` for `"detail"`. Then re-emit the Main Surface
  so the invoice list is restored: emit `createSurface` → `updateDataModel` (path `"/"`,
  value `{ "year": 2026, "invoices": { "$fetch": "/invoices?fiscal_year=2026" }, "summary": { "$fetch": "/invoices/summary?fiscal_year=2026" } }`)
  → `updateComponents` (same `InvoiceList` root as specified in the Main Surface section).

### Detail Surface — Edit Form (`surfaceId: "detail"`)

Emit on `edit_draft_invoice` UI event. The event context already contains the full
invoice data fetched by the browser — do **not** call `get_invoice`, `list_customers`,
or `list_products`.

**Translation:** Translate every `literalString` value to the user's detected language.

**Message order:** `deleteSurface` for `"panel_1"` → `deleteSurface` for `"panel_2"` → `deleteSurface` for `"main"` → `createSurface` → `updateDataModel` → `updateComponents`

**`updateDataModel`:** surfaceId `"detail"`, path `"/"`, value — populate from the
fetched invoice:

```json
{
  "form": {
    "invoiceId": "<invoice id>",
    "customerId": "<existing contact_id>",
    "dueDate": "<existing due_date>",
    "lineItems": [
      { "productId": "<product_id>", "quantity": 1, "unitPrice": "<unit_price>" }
    ]
  },
  "customerOptions": { "$fetch": "/customers" },
  "productOptions": { "$fetch": "/products" }
}
```

Components — same structure as the Create Form, with these differences:

- `form-title`: `Text` text `{ "literalString": "Edit Invoice" }` variant `h2`
- `submit-btn`: action event `"submit_edit_invoice_form"`, context includes
  `invoiceId` (literalString of the resolved invoice id) plus `customerId`,
  `dueDate`, `lineItems` from `/form/*`
- `submit-label`: `Text` text `{ "literalString": "Save" }`

`createSurface`: surfaceId `"detail"`, catalogId `"https://a2ui.org/catalog/basic/v0.8/catalog.json"`.

**UI events:**

- `submit_edit_invoice_form` — the context contains `invoiceId`, `customerId`,
  `dueDate`, and `lineItems`. Validate: customer selected and at least one line item.
  If invalid, reply in chat. If valid: emit `deleteSurface` for `"detail"`, then call
  `edit_invoice` with `invoiceId` and the changed fields (contact_id, due_date, lines).
  On success confirm in chat ("Saved — want to approve and send it?").

- `cancel_invoice` — emit `deleteSurface` for `"detail"`. Then re-emit the Main
  Surface so the invoice list is restored.

---

### Confirm Surface — Create / Approve (`surfaceId: "confirm"`)

Emit before calling `create_invoice` or approving via `edit_invoice`. Use
`createSurface` → `updateDataModel` → `updateComponents`.

Components (v0.9 flat format):

- `root`: `Column` children `["confirm-card", "actions-row"]`
- `confirm-card`: `Card` child `"confirm-col"`
- `confirm-col`: `Column` children `["confirm-title", "confirm-customer", "confirm-due", "confirm-lines", "confirm-total"]`
- `confirm-title`: `Text` text `{ "literalString": "Confirm Invoice" }` variant `h2`
- `confirm-customer`: `Text` text `{ "path": "/confirm/customerName" }`
- `confirm-due`: `Text` text `{ "path": "/confirm/dueDate" }`
- `confirm-lines`: `List` children `{ "componentId": "confirm-line-row", "path": "/confirm/lineItems" }`
- `confirm-line-row`: `Row` children `["cl-name", "cl-qty", "cl-price"]`
- `cl-name`: `Text` text `{ "path": "/productName" }`
- `cl-qty`: `Text` text `{ "path": "/quantity" }`
- `cl-price`: `Text` text `{ "path": "/unitPrice" }`
- `actions-row`: `Row` children `["confirm-btn", "cancel-btn"]`
- `confirm-btn`: `Button` child `"confirm-label"` action `{ "type": "event", "name": "confirm_create_invoice", "context": [{"key":"customerId","value":{"path":"/confirm/customerId"}},{"key":"dueDate","value":{"path":"/confirm/dueDate"}},{"key":"lineItems","value":{"path":"/confirm/lineItems"}}] }`
- `confirm-label`: `Text` text `{ "literalString": "Create Invoice" }`
- `cancel-btn`: `Button` child `"cancel-label"` action `{ "type": "event", "name": "cancel_invoice" }`
- `cancel-label`: `Text` text `{ "literalString": "Cancel" }`

`createSurface`: surfaceId `"confirm"`, catalogId `"https://a2ui.org/catalog/basic/v0.8/catalog.json"`.

`updateDataModel`: surfaceId `"confirm"`, path `"/confirm"`, value populated from the
`submit_invoice_form` context:
```json
{
  "customerId": "<id>",
  "customerName": "<resolved name>",
  "dueDate": "<date>",
  "lineItems": [
    { "productId": "<id>", "productName": "<name>", "quantity": 1, "unitPrice": "<price>" }
  ]
}
```

**UI events:**

- `confirm_create_invoice` — the context contains `customerId`, `dueDate`, and
  `lineItems`. Call `create_invoice` with these values — each line item needs
  `productId`, `quantity`, and `unitPrice`. On success: emit `deleteSurface` for
  `"confirm"` and confirm in chat ("Done — want me to send that invoice by email?").
  Do **not** call `list_invoices`.
- `cancel_invoice` — emit `deleteSurface` for `"confirm"`.

### Main Surface — Invoice List (`surfaceId: "main"`)

**Message order:** `deleteSurface` for `"panel_1"` → `deleteSurface` for `"panel_2"` → `deleteSurface` for `"detail"` → `createSurface` → `updateDataModel` → `updateComponents`

Emit the **full surface definition** — `createSurface` → `updateDataModel` →
`updateComponents` — whenever the user asks to see invoices, and whenever UI state may
be unknown (new session, page refresh). Do **not** call `list_invoices` or
`get_invoice_summary` MCP tools to populate the list — the browser fetches both via
`$fetch` sentinels. Do **not** re-emit the main surface after `create_invoice` or
`edit_invoice` — just emit `deleteSurface` for `"detail"` and confirm in chat.

**Customer-filtered view.** When the user asks to see invoices *for a specific customer*:
1. Call `list_customers` with a `name` filter to resolve the customer ID if not already known.
2. Set `"year": null` and use `contact_id=ID` in the invoices `$fetch` — this shows all
   invoices for that customer across all fiscal years. Omit the `"summary"` key — the
   browser computes summary counts from the fetched invoice list automatically.
3. Set `labels.heading` to `"Invoices for CUSTOMER_NAME"`.

```json
{
  "year": null,
  "invoices": { "$fetch": "/invoices?contact_id=CONTACT_ID" },
  "labels": { "heading": "Invoices for Maria Christensen", "..." : "..." }
}
```

**`createSurface`:** surfaceId `"main"`, catalogId `"https://a2ui.org/catalog/basic/v0.8/catalog.json"`.

**`updateComponents` (copy exactly):**

```json
{
  "version": "v0.9",
  "updateComponents": {
    "surfaceId": "main",
    "components": [
      { "id": "root", "component": "InvoiceList" }
    ]
  }
}
```

**`updateDataModel`:** surfaceId `"main"`, path `"/"`, value — use `$fetch` sentinels for
data and translate every label to the user's detected language (default English if unsure).

Use `fiscal_year=YEAR` in the `$fetch` URLs and set `"year"` to match. Default to the
current year (2026) unless the user requests a different year.

```json
{
  "year": 2026,
  "invoices": { "$fetch": "/invoices?fiscal_year=2026" },
  "summary":  { "$fetch": "/invoices/summary?fiscal_year=2026" },
  "labels": {
    "heading":         "Invoices 2026",
    "createInvoice":   "Create Invoice",
    "summary":         "Summary",
    "card_all":        "All invoices",
    "card_draft":      "Draft",
    "card_overdue":    "Overdue",
    "card_unpaid":     "Unpaid",
    "card_paid":       "Paid",
    "search":          "Search...",
    "fiscalYear":      "Fiscal Year",
    "colNumber":       "Number",
    "colDate":         "Date",
    "colDue":          "Due",
    "colCustomer":     "Customer",
    "colDescription":  "Description",
    "colExclVat":      "Excl. VAT",
    "noResults":       "No invoices found.",
    "invCustomer":     "Customer",
    "invTitle":        "Invoice",
    "invNo":           "Invoice no.",
    "invDate":         "Invoice date",
    "invDueDate":      "Due date",
    "invColDesc":      "Description",
    "invColQty":       "Qty",
    "invColUnitPrice": "Unit price",
    "invColPrice":     "Price",
    "invExclVat":      "Total excl. VAT",
    "invVat":          "VAT (25%)",
    "invInclVat":      "Total incl. VAT"
  }
}
```

### Detail Surface — Invoice View (`surfaceId: "detail"`)

Emit on `get_invoice`. Use `createSurface` → `updateDataModel` → `updateComponents`.

Components (v0.9 flat format) — all IDs must appear in the `updateComponents` array:

- `root`: `Column` children `["inv-header-row", "line-items-list", "totals-card"]`
- `inv-header-row`: `Row` children `["inv-no-text", "inv-cust-text", "inv-state-text", "inv-due-text"]`
- `inv-no-text`: `Text` text `{ "path": "/invoice/invoiceNo" }`
- `inv-cust-text`: `Text` text `{ "path": "/invoice/customerName" }`
- `inv-state-text`: `Text` text `{ "path": "/invoice/state" }`
- `inv-due-text`: `Text` text `{ "path": "/invoice/dueDate" }`
- `line-items-list`: `List` children `{ "componentId": "line-item-row", "path": "/lineItems" }`
- `line-item-row`: `Row` children `["li-product", "li-qty", "li-unit-price", "li-total"]`
- `li-product`: `Text` text `{ "path": "/product" }`
- `li-qty`: `Text` text `{ "path": "/quantity" }`
- `li-unit-price`: `Text` text `{ "path": "/unitPrice" }`
- `li-total`: `Text` text `{ "path": "/totalAmount" }`
- `totals-card`: `Card` child `"totals-col"`
- `totals-col`: `Column` children `["net-text", "tax-text", "gross-text"]`
- `net-text`: `Text` text `{ "path": "/invoice/netAmount" }`
- `tax-text`: `Text` text `{ "path": "/invoice/tax" }`
- `gross-text`: `Text` text `{ "path": "/invoice/grossAmount" }`

`createSurface`: surfaceId `"detail"`, catalogId `"https://a2ui.org/catalog/basic/v0.8/catalog.json"`.

`updateDataModel`: surfaceId `"detail"`, path `"/"`, value:

```json
{
  "invoice": { "invoiceNo": "...", "customerName": "...", "state": "...", "dueDate": "...", "netAmount": "...", "tax": "...", "grossAmount": "..." },
  "lineItems": [
    { "product": "...", "quantity": 1, "unitPrice": "...", "totalAmount": "..." }
  ]
}
```
