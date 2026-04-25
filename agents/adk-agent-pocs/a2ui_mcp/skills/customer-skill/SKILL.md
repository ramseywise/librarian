---
name: customer-skill
description: >-
  Manage customers and contacts. Use this skill for creating new customers, listing
  existing customers, updating customer details (name, address, phone, email, CVR
  number), and looking up customer IDs.
metadata:
  adk_additional_tools:
    - list_customers
    - create_customer
    - edit_customer
---

# Customer Operations

## Tools available

- `list_customers` — list all active customers; pass a name search term to narrow
  results when looking for a specific customer
- `create_customer` — add a new customer (requires name, type, and country)
- `edit_customer` — update an existing customer's details

## Functional Rules

1. **Distinguish company vs person.** Use `type: "company"` for businesses,
   `type: "person"` for individuals. Danish CVR numbers must be exactly 8 digits — strip
   any prefix (e.g. "DK") before passing to the tool.

2. **Name matching when no exact match is found.** This rule applies to **lookup and
   edit** operations only — NOT when the user's intent is to create a new customer. For
   create intent, go directly to the UI Rendering Specifications — show the create form
   immediately. For lookup/edit: always call `list_customers` with the user's input as
   the search term. Then apply:
   - **Multiple partial matches**: list them and ask which one the user means.
   - **Likely typo or nickname**: suggest the close variant.
   - **No plausible match**: say the customer wasn't found and ask whether to create a
     new one.

3. **The create form is the confirmation.** When the user submits via the UI form, call
   `create_customer` directly — no additional chat prompt needed. For non-UI flows,
   summarise name, type, country, and CVR if applicable before calling
   `create_customer`.

4. **Updating email via the form.** The `submit_edit_customer` event includes `email`
   directly — pass it to `edit_customer` as the `email` parameter. If
   `send_invoice_by_email` later fails with "No contact person found", call
   `list_customers` to verify the contact person is linked and has an email set.

5. **Parse addresses.** Use the Danish format:
   `[Street] [Number], [Floor/Side], [Zip] [City]`. Split into `street`, `city`, and
   `zipcode` before passing to the tool. If any piece is missing, ask for it rather than
   submitting an incomplete record.

6. **Bridge after completion.**
   - After creating: "Done! [Name] is in your contacts — ready to work on that invoice?"
   - After listing/finding: "I found [Name] — would you like to see their recent
     invoices?"

---

## UI Rendering Specifications

These are technical rendering requirements. Follow them exactly whenever a tool is
called or a UI event is received.

### Detail Surface — Create Form (`surfaceId: "detail"`)

Emit when the user wants to create a customer, **before** calling any tool. Do NOT call
`list_customers` first. If the user already provided a name, pre-populate `/form/name`.

**Message order:** `deleteSurface` for `"panel_1"` → `deleteSurface` for `"panel_2"` → `deleteSurface` for `"main"` → `createSurface` → `updateDataModel` → `updateComponents`

`createSurface`: surfaceId `"detail"`, catalogId `"https://a2ui.org/catalog/basic/v0.8/catalog.json"`.

`updateDataModel`: surfaceId `"detail"`, path `"/"`, value — translate every label to the user's detected language (default English if unsure):
```json
{
  "mode": "create",
  "form": { "name": "", "type": "company", "country": "DK", "registrationNo": "", "phone": "", "email": "", "street": "", "city": "", "zipcode": "" },
  "labels": {
    "title_edit": "Edit contact",
    "title_create": "New contact",
    "submit_edit": "Save changes",
    "submit_create": "Create contact",
    "tab_company": "Company",
    "tab_individual": "Individual",
    "company_name": "Company name *",
    "company_name_placeholder": "Company name",
    "country": "Country *",
    "tax_id": "Tax ID",
    "cvr_placeholder": "CVR number",
    "phone": "Phone",
    "contact_person": "Contact person",
    "email": "Email",
    "first_name": "First name *",
    "first_name_placeholder": "First name",
    "last_name": "Last name",
    "last_name_placeholder": "Last name",
    "address": "Address",
    "street_placeholder": "Street",
    "zip_placeholder": "ZIP",
    "city_placeholder": "City",
    "cancel": "Cancel"
  }
}
```
If the user provided a name, set `form.name` to it.

`updateComponents` (copy exactly):
```json
{
  "version": "v0.9",
  "updateComponents": {
    "surfaceId": "detail",
    "components": [
      { "id": "root", "component": "CustomerForm" }
    ]
  }
}
```

**UI events:**

- `submit_create_customer` — context contains `name`, `type`, `country`, `registrationNo`,
  `phone`, `email`, `street`, `city`, `zipcode`. Call `create_customer` with these values.
  Pass `country` as `country_id`, `registrationNo` as `registration_no`, `city` as
  `city_text`, `zipcode` as `zipcode_text`. On success: emit `deleteSurface` for `"detail"`
  and confirm in chat. Do **not** call `list_customers`.
- `cancel` — emit `deleteSurface` for `"detail"`.

### Detail Surface — Edit Form (`surfaceId: "detail"`)

Emit when an `edit_customer` UI event is received. The event context contains `id`,
`name`, `type`, `country`, `email`, `phone`, `street`, `city`, `zipcode`, and
`registrationNo` — use these directly to pre-populate the form. Do **not** call
`list_customers`.

**Message order:** `deleteSurface` for `"panel_1"` → `deleteSurface` for `"panel_2"` → `deleteSurface` for `"main"` → `createSurface` → `updateDataModel` → `updateComponents`

`createSurface`: surfaceId `"detail"`, catalogId `"https://a2ui.org/catalog/basic/v0.8/catalog.json"`.

`updateDataModel`: surfaceId `"detail"`, path `"/"`, value populated from the event context — translate every label to the user's detected language (default English if unsure):
```json
{
  "mode": "edit",
  "form": {
    "id": "<context.id>",
    "name": "<context.name>",
    "type": "<context.type>",
    "country": "<context.country>",
    "registrationNo": "<context.registrationNo>",
    "phone": "<context.phone>",
    "email": "<context.email>",
    "street": "<context.street>",
    "city": "<context.city>",
    "zipcode": "<context.zipcode>"
  },
  "labels": {
    "title_edit": "Edit contact",
    "title_create": "New contact",
    "submit_edit": "Save changes",
    "submit_create": "Create contact",
    "tab_company": "Company",
    "tab_individual": "Individual",
    "company_name": "Company name *",
    "company_name_placeholder": "Company name",
    "country": "Country *",
    "tax_id": "Tax ID",
    "cvr_placeholder": "CVR number",
    "phone": "Phone",
    "contact_person": "Contact person",
    "email": "Email",
    "first_name": "First name *",
    "first_name_placeholder": "First name",
    "last_name": "Last name",
    "last_name_placeholder": "Last name",
    "address": "Address",
    "street_placeholder": "Street",
    "zip_placeholder": "ZIP",
    "city_placeholder": "City",
    "cancel": "Cancel"
  }
}
```

`updateComponents` (copy exactly):
```json
{
  "version": "v0.9",
  "updateComponents": {
    "surfaceId": "detail",
    "components": [
      { "id": "root", "component": "CustomerForm" }
    ]
  }
}
```

**UI events:**

- `submit_edit_customer` — context contains `id`, `name`, `type`, `country`,
  `registrationNo`, `phone`, `email`, `street`, `city`, `zipcode`. Call `edit_customer`
  with `contact_id` = `id`, `country_id` = `country`, `registration_no` = `registrationNo`,
  `city_text` = `city`, `zipcode_text` = `zipcode`, plus `name`, `phone`, `email`.
  On success: emit `deleteSurface` for `"detail"` and confirm in chat. Do **not** call
  `list_customers`.
- `cancel` — emit `deleteSurface` for `"detail"`.

### Main Surface — Customer List (`surfaceId: "main"`)

Emit when the user asks to see customers — **do not call `list_customers`** before showing
the UI. The `CustomerList` component fetches its own data from the REST API. Do **not**
re-emit the main surface after `create_customer` or `edit_customer` — just confirm in chat
and close the detail form.

**Message order:** `deleteSurface` for `"detail"` → `deleteSurface` for `"panel_1"` → `deleteSurface` for `"panel_2"` → `createSurface` → `updateDataModel` → `updateComponents`

**`createSurface`:** surfaceId `"main"`, catalogId `"https://a2ui.org/catalog/basic/v0.8/catalog.json"`.

**`updateDataModel`:** surfaceId `"main"`, path `"/"`, value — translate every label to
the user's detected language (default English if unsure). If the user mentioned a name
or search term, include `"search": "<term>"` to pre-filter the list:

```json
{
  "search": "",
  "labels": {
    "heading":       "Clients",
    "createContact": "Create contact",
    "toolbarLabel":  "Clients",
    "showArchived":  "Show archived",
    "search":        "Search...",
    "colName":       "Name",
    "colEmail":      "Email",
    "colPhone":      "Phone number",
    "colCountry":    "Country",
    "colCreated":    "Created date",
    "noResults":     "No clients found."
  }
}
```

**`updateComponents` (copy exactly):**

```json
{
  "version": "v0.9",
  "updateComponents": {
    "surfaceId": "main",
    "components": [
      { "id": "root", "component": "CustomerList" }
    ]
  }
}
```
