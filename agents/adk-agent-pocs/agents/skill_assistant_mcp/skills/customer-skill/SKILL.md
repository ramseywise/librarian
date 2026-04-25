---
name: customer-skill
description: >
  Manage customers and contacts. Use this skill for creating new customers,
  listing existing customers, updating customer details (name, address, phone,
  email, CVR number), and looking up customer IDs.
---

# Customer Operations

## Tools available
- `list_customers` — list all active customers; pass a name search term to narrow results when looking for a specific customer
- `create_customer` — add a new customer (requires name, type, and country)
- `edit_customer` — update an existing customer's details

## Rules

1. **Distinguish company vs person.** Use `type: "company"` for businesses,
   `type: "person"` for individuals. Danish CVR numbers must be exactly 8 digits —
   strip any prefix (e.g. "DK") before passing to the tool.

2. **Name matching when no exact match is found.**
   Always call `list_customers` with the user's input as the search term to let
   the API handle initial filtering. Then apply:
   - **Multiple partial matches** (e.g. "Dan Rasmussen" and "Dan Beinthin" both
     start with "Dan"): list them and ask which one the user means.
   - **Likely typo or nickname** (e.g. user typed "dan", candidate is "Danny" or
     "Daniel"): suggest the close variant.
   - **No plausible match** (e.g. user typed "dan", closest is "Lars Hansen"):
     do NOT suggest unrelated names. Simply say the customer wasn't found and ask
     whether to create a new one.

3. **Confirm before creating.** Summarise name, type, country, and CVR if applicable,
   then ask "Create this customer?" before calling `create_customer`.

4. **Updating email requires `contact_person_id`.** Call `list_customers` first to
   find the correct record; pass both `contact_person_id` and `email` to `edit_customer`.
   If `send_invoice_by_email` later fails with "No contact person found", call
   `list_customers` to verify the contact person is linked and has an email set.

5. **Parse addresses.** Use the Danish format: `[Street] [Number], [Floor/Side], [Zip] [City]`.
   Split into `street`, `city`, and `zipcode` before passing to the tool. If any
   piece is missing, ask for it rather than submitting an incomplete record.

6. **Bridge after completion.**
   - After creating: "Done! [Name] is in your contacts — ready to work on that invoice?"
   - After listing/finding: "I found [Name] — would you like to see their recent invoices?"
