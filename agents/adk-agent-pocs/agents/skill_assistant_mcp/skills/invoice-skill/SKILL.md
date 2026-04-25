---
name: invoice-skill
description: >
  Create, view, list, edit, approve, and summarize invoices. Use this skill
  for any request involving invoice operations including creating new invoices,
  checking invoice status, editing draft invoices, approving invoices, and
  getting invoice summaries or dashboards.
---

# Invoice Operations

## Tools available
- `list_invoices` — list invoices with optional filtering by state, date, customer
- `get_invoice` — fetch details of a specific invoice by ID
- `get_invoice_summary` — dashboard stats grouped by state (draft, approved, paid, overdue)
- `create_invoice` — create a new invoice
- `edit_invoice` — update details of a draft OR approve an invoice by changing its state

## Rules

1. **Resolve names to IDs first.** Call `list_customers` and `list_products` in
   parallel to find IDs when the user mentions a customer or product by name.

2. **Confirm before creating or approving.** Present a structured summary:

   **Customer:** [Name] (ID: [ID])
   | Product | Qty | Unit price | Total |
   |:--------|----:|-----------:|------:|
   | [Name]  | [N] |  [Price] DKK | [Subtotal] DKK |

   **Subtotal (excl. VAT):** [Amount] DKK
   **VAT (25%):** [VAT] DKK
   **Total (incl. VAT):** [Gross] DKK
   **Due date:** [Date]

   Then ask "Does this look correct?" before calling `create_invoice`.

3. **VAT is automatic.** Never pass tax or gross amount values — the API
   calculates them from `unitPrice × quantity`. Default currency is DKK.
   Line item keys are camelCase: `productId`, `unitPrice`, `quantity`, `description`.

4. **State management.**
   - **Editing:** Only invoices in `draft` state can have their fields updated.
   - **Approving:** If the user says "approve this," call `edit_invoice` with
     `state: "approved"`.
   - **Locked invoices:** If already approved or paid, explain: "This invoice is
     locked for legal compliance. To correct it, a credit note is required."

5. **Bridge after completion.**
   - After creating or approving: "Done — want me to send that invoice by email?"
   - After summarising: "Your dashboard is up to date. Should we follow up on
     any overdue invoices?"
