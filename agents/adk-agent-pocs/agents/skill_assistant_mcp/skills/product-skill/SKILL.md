---
name: product-skill
description: >
  Manage products and services in the product catalog. Use this skill for
  creating new products, listing active or archived products, updating product
  names, descriptions, and prices.
---

# Product Operations

## Tools available
- `list_products` — list products; set `is_archived=True` to find deactivated products
- `create_product` — add a new product or service to the catalog
- `edit_product` — update an existing product's name, description, or price

## Rules

1. **Prices are always excl. VAT.** Make this clear when confirming with the user.

2. **Required details for creation.** Ensure you have all three before calling
   `create_product`:
   - **Name**
   - **Unit price**
   - **Unit type** (e.g. "hours", "pcs", "days") — ask if not provided.

3. **Confirm before creating.** Present a summary:

   **Product:** [Name]
   **Price:** [Price] DKK (excl. VAT)
   **Unit:** [Unit]

   Then ask "Shall I add this to your catalog?" before calling `create_product`.

4. **Updating price requires `price_id`.** Call `list_products` first to find the
   product's current `price_id`; pass both `price_id` and `unit_price` to `edit_product`.

5. **Check archives before creating.** If a product can't be found in the active
   list, call `list_products` with `is_archived=True` before assuming it doesn't
   exist — it may just be deactivated.

6. **Bridge after completion.** End with a proactive follow-up:
   "Product added — want to draft an invoice using it now?"
