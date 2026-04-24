# A2UI v0.8 Multi-Step Checkout Form

The surface is built using three messages in the required v0.8 order: `dataModelUpdate` to seed the initial state, `surfaceUpdate` to define all components, and `beginRendering` last.

### Message Sequence

```json
[
  {
    "dataModelUpdate": {
      "surfaceId": "checkout-surface",
      "contents": [
        { "key": "form/email",           "valueString":  "" },
        { "key": "form/shipping",        "valueString":  "" },
        { "key": "order/total",          "valueString":  "$128.97" },
        { "key": "order/itemCount",      "valueNumber":  3 }
      ]
    }
  },
  {
    "surfaceUpdate": {
      "surfaceId": "checkout-surface",
      "components": [
        {
          "id": "root",
          "component": {
            "Column": {
              "children": [
                "page-title", "divider-top", "email-section-label", "email-field",
                "shipping-section-label", "shipping-picker", "divider-mid",
                "order-summary-card", "divider-bottom", "submit-btn-label", "submit-btn"
              ],
              "justify": "start",
              "align": "stretch"
            }
          }
        },
        {
          "id": "page-title",
          "component": { "Text": { "text": { "literalString": "Checkout" }, "variant": "h1" } }
        },
        {
          "id": "divider-top",
          "component": { "Divider": { "axis": "horizontal" } }
        },
        {
          "id": "email-section-label",
          "component": { "Text": { "text": { "literalString": "Contact Information" }, "variant": "h3" } }
        },
        {
          "id": "email-field",
          "component": {
            "TextField": {
              "value":            { "path": "/form/email" },
              "type":             "shortText",
              "label":            { "literalString": "Email address" },
              "validationRegexp": "^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$"
            }
          }
        },
        {
          "id": "shipping-section-label",
          "component": { "Text": { "text": { "literalString": "Shipping Method" }, "variant": "h3" } }
        },
        {
          "id": "shipping-picker",
          "component": {
            "MultipleChoice": {
              "selections":           { "path": "/form/shipping" },
              "maxAllowedSelections": 1,
              "options": [
                { "id": "standard",  "label": { "literalString": "Standard (5–7 business days — free)" } },
                { "id": "express",   "label": { "literalString": "Express (2–3 business days — $9.99)" } },
                { "id": "overnight", "label": { "literalString": "Overnight (next business day — $24.99)" } }
              ]
            }
          }
        },
        {
          "id": "divider-mid",
          "component": { "Divider": { "axis": "horizontal" } }
        },
        {
          "id": "order-summary-card",
          "component": { "Card": { "child": "order-summary-col" } }
        },
        {
          "id": "order-summary-col",
          "component": {
            "Column": {
              "children": ["summary-heading", "summary-row-items", "summary-row-shipping", "summary-row-total"],
              "justify": "start", "align": "stretch"
            }
          }
        },
        {
          "id": "summary-heading",
          "component": { "Text": { "text": { "literalString": "Order Summary" }, "variant": "h4" } }
        },
        {
          "id": "summary-row-items",
          "component": { "Row": { "children": ["summary-label-items", "summary-value-items"], "justify": "space-between" } }
        },
        {
          "id": "summary-label-items",
          "component": { "Text": { "text": { "literalString": "Items" }, "variant": "body" } }
        },
        {
          "id": "summary-value-items",
          "component": { "Text": { "text": { "path": "/order/itemCount" }, "variant": "body" } }
        },
        {
          "id": "summary-row-shipping",
          "component": { "Row": { "children": ["summary-label-shipping", "summary-value-shipping"], "justify": "space-between" } }
        },
        {
          "id": "summary-label-shipping",
          "component": { "Text": { "text": { "literalString": "Shipping" }, "variant": "body" } }
        },
        {
          "id": "summary-value-shipping",
          "component": { "Text": { "text": { "path": "/form/shipping" }, "variant": "body" } }
        },
        {
          "id": "summary-row-total",
          "component": { "Row": { "children": ["summary-label-total", "summary-value-total"], "justify": "space-between" } }
        },
        {
          "id": "summary-label-total",
          "component": { "Text": { "text": { "literalString": "Order Total" }, "variant": "h5" } }
        },
        {
          "id": "summary-value-total",
          "component": { "Text": { "text": { "path": "/order/total" }, "variant": "h5" } }
        },
        {
          "id": "divider-bottom",
          "component": { "Divider": { "axis": "horizontal" } }
        },
        {
          "id": "submit-btn-label",
          "component": { "Text": { "text": { "literalString": "Place Order" }, "variant": "body" } }
        },
        {
          "id": "submit-btn",
          "component": {
            "Button": {
              "child": "submit-btn-label",
              "variant": "primary",
              "action": { "userEventName": "checkout_submitted" }
            }
          }
        }
      ]
    }
  },
  {
    "beginRendering": {
      "surfaceId": "checkout-surface",
      "root": "root"
    }
  }
]
```

---

### How It Works

**Message order (v0.8 rules followed):**

1. `dataModelUpdate` — seeds the data model with empty form state and a fixed order total before any component tries to bind against it.
2. `surfaceUpdate` — defines every component in a flat adjacency list. No nesting inside the JSON itself; parent-child relationships are declared as ID arrays (`children`) or single ID references (`child`).
3. `beginRendering` — sent last to signal the client to start rendering the surface with `root` as the entry point.

**Data binding:**

| Path | Bound to | Direction |
|------|----------|-----------|
| `/form/email` | `TextField` `value` | Bidirectional — user edits write back to the model |
| `/form/shipping` | `MultipleChoice` `selections` | Bidirectional — user selection writes back to the model |
| `/form/shipping` | Summary "Shipping" `Text` | Read-only display — auto-updates when selection changes |
| `/order/total` | Summary "Order Total" `Text` | Read-only — agent updates via `dataModelUpdate` |
| `/order/itemCount` | Summary "Items" `Text` | Read-only — set by the agent |

**Updating the total when shipping changes:**

```json
{
  "dataModelUpdate": {
    "surfaceId": "checkout-surface",
    "contents": [
      { "key": "order/total", "valueString": "$138.96" }
    ]
  }
}
```

**Component structure:**

```
root (Column)
  page-title (Text h1)
  divider-top (Divider)
  email-section-label (Text h3)
  email-field (TextField → /form/email)
  shipping-section-label (Text h3)
  shipping-picker (MultipleChoice → /form/shipping)
  divider-mid (Divider)
  order-summary-card (Card)
    order-summary-col (Column)
      summary-heading (Text h4)
      summary-row-items (Row)
        summary-label-items (Text)
        summary-value-items (Text → /order/itemCount)
      summary-row-shipping (Row)
        summary-label-shipping (Text)
        summary-value-shipping (Text → /form/shipping)
      summary-row-total (Row)
        summary-label-total (Text h5)
        summary-value-total (Text → /order/total)
  divider-bottom (Divider)
  submit-btn-label (Text)
  submit-btn (Button primary → checkout_submitted)
```
