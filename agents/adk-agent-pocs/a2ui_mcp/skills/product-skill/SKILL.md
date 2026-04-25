---
name: product-skill
description: >-
  Manage products and services in the product catalog. Use this skill for creating new
  products, listing active or archived products, updating product names, descriptions,
  and prices.
metadata:
  adk_additional_tools:
    - list_products
    - create_product
    - edit_product
---

# Product Operations

## Tools available

- `list_products` — list products; set `is_archived=True` to find deactivated products
- `create_product` — add a new product or service to the catalog
- `edit_product` — update an existing product's name, description, or price

## Functional Rules

1. **Prices are always excl. VAT.** Make this clear when confirming with the user.

2. **Required details for creation.** Ensure you have both before calling
   `create_product`:
   - **Name**
   - **Unit price** — always pass as a number (float/int), not a string. If the user
     types "500.50", convert it before calling the tool.

3. **The create form is the confirmation.** When the user wants to create a product
   (including when they click "New Product" in the UI), immediately emit the create form
   surface (see UI Rendering Specifications). The submit button click calls
   `create_product` directly — no additional chat prompt needed.

4. **Updating price requires `price_id`.** Call `list_products` first to find the
   product's current `price_id`; pass both `price_id` and `unit_price` to
   `edit_product`.

5. **Check archives before creating.** If a product can't be found in the active list,
   call `list_products` with `is_archived=True` before assuming it doesn't exist — it
   may just be deactivated.

6. **Bridge after completion.** End with a proactive follow-up: "Product added — want to
   draft an invoice using it now?"

---

## UI Rendering Specifications

These are technical rendering requirements. Follow them exactly whenever a tool is
called or a UI event is received.

### Detail Surface — Create Form (`surfaceId: "detail"`)

Emit when the user wants to create a product — including when a `create_product`
`[ui_event]` is received. Emit **before** calling any tool.

**Message order:** `deleteSurface` for `"panel_1"` → `deleteSurface` for `"panel_2"` → `deleteSurface` for `"main"` → `createSurface` → `updateDataModel` → `updateComponents`

`createSurface`: surfaceId `"detail"`, catalogId `"https://a2ui.org/catalog/basic/v0.8/catalog.json"`.

`updateDataModel`: surfaceId `"detail"`, path `"/"`, value — translate every label to the user's detected language (default English if unsure):
```json
{
  "mode": "create",
  "form": { "name": "", "description": "", "unitPrice": "", "productNo": "", "isArchived": false },
  "labels": {
    "title_edit": "Edit item",
    "title_create": "Create item",
    "submit_edit": "Save changes",
    "submit_create": "Create item",
    "name_label": "Name of the product or service *",
    "name_placeholder": "E.g. web design services / Acme red hammer",
    "description": "Description",
    "description_placeholder": "None",
    "description_hint": "Automatically inserted as default for new invoices",
    "unit_price": "Unit price *",
    "unit_price_placeholder": "Unit price",
    "excl_vat": "Excl. VAT",
    "sku": "SKU / Item code",
    "sku_placeholder": "None",
    "sku_hint": "Only seen by you",
    "archived": "Archived (hide from lists)",
    "cancel": "Cancel"
  }
}
```
If the user already provided a name, set `form.name` to it.

`updateComponents` (copy exactly):
```json
{
  "version": "v0.9",
  "updateComponents": {
    "surfaceId": "detail",
    "components": [
      { "id": "root", "component": "ProductForm" }
    ]
  }
}
```

**UI events:**

- `submit_create_product` — context contains `name`, `description`, `unitPrice`. Call
  `create_product` with `name`, `unit_price` (cast `unitPrice` to number), `description`.
  On success: emit `deleteSurface` for `"detail"` and confirm in chat. Do **not** call
  `list_products`.
- `cancel_product` — emit `deleteSurface` for `"detail"`.

### Detail Surface — Edit Form (`surfaceId: "detail"`)

Emit when an `edit_product` UI event is received. The event context contains `id`,
`name`, `unitPrice`, `priceId`, `description`, `productNo`, and `isArchived` — use
these directly to pre-populate the form. Do **not** call `list_products`.

**Message order:** `deleteSurface` for `"panel_1"` → `deleteSurface` for `"panel_2"` → `deleteSurface` for `"main"` → `createSurface` → `updateDataModel` → `updateComponents`

`createSurface`: surfaceId `"detail"`, catalogId `"https://a2ui.org/catalog/basic/v0.8/catalog.json"`.

`updateDataModel`: surfaceId `"detail"`, path `"/"`, value populated from the event context — translate every label to the user's detected language (default English if unsure):
```json
{
  "mode": "edit",
  "form": {
    "id": "<context.id>",
    "name": "<context.name>",
    "description": "<context.description>",
    "unitPrice": "<context.unitPrice>",
    "priceId": "<context.priceId>",
    "productNo": "<context.productNo>",
    "isArchived": "<context.isArchived>"
  },
  "labels": {
    "title_edit": "Edit item",
    "title_create": "Create item",
    "submit_edit": "Save changes",
    "submit_create": "Create item",
    "name_label": "Name of the product or service *",
    "name_placeholder": "E.g. web design services / Acme red hammer",
    "description": "Description",
    "description_placeholder": "None",
    "description_hint": "Automatically inserted as default for new invoices",
    "unit_price": "Unit price *",
    "unit_price_placeholder": "Unit price",
    "excl_vat": "Excl. VAT",
    "sku": "SKU / Item code",
    "sku_placeholder": "None",
    "sku_hint": "Only seen by you",
    "archived": "Archived (hide from lists)",
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
      { "id": "root", "component": "ProductForm" }
    ]
  }
}
```

**UI events:**

- `submit_edit_product` — context contains `id`, `priceId`, `name`, `description`,
  `unitPrice`, `productNo`, `isArchived`. Call `edit_product` with `product_id` = `id`,
  `price_id` = `priceId`, `unit_price` (cast `unitPrice` to number), `name`,
  `description`, `product_no` = `productNo`. On success: emit `deleteSurface` for
  `"detail"` and confirm in chat. Do **not** call `list_products`.
- `cancel_product` — emit `deleteSurface` for `"detail"`.

### Main Surface — Product List (`surfaceId: "main"`)

Emit when the user asks to see products — **do not call `list_products`** before showing
the UI. The `ProductList` component fetches its own data from the REST API. Do **not**
re-emit the main surface after `create_product` or `edit_product` — just confirm in chat
and close the detail form.

**Message order:** `deleteSurface` for `"panel_1"` → `deleteSurface` for `"panel_2"` → `deleteSurface` for `"detail"` → `createSurface` → `updateDataModel` → `updateComponents`

**`createSurface`:** surfaceId `"main"`, catalogId `"https://a2ui.org/catalog/basic/v0.8/catalog.json"`.

**`updateDataModel`:** surfaceId `"main"`, path `"/"`, value — translate every label to the
user's detected language (default English if unsure):

```json
{
  "labels": {
    "heading":      "Products",
    "newProduct":   "New Product",
    "toolbarLabel": "Products",
    "showArchived": "Show archived",
    "search":       "Search...",
    "colName":      "Name",
    "colDescription": "Description",
    "colUnit":      "Unit",
    "colUnitPrice": "Unit price",
    "noResults":    "No products found."
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
      { "id": "root", "component": "ProductList" }
    ]
  }
}
```

**UI events:**

- `create_product` — immediately emit the Detail Surface — Create Form above.
- `edit_product` — context contains `id`, `name`, `unitPrice`, `priceId`, `description`,
  `productNo`, `isArchived`; follow the Detail Surface — Edit Form spec above.
