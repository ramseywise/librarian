# A2UI v0.8 Checkout Form — Message Sequence

The sequence is three messages: one `dataModelUpdate` to seed initial state, one `surfaceUpdate` to declare all components, then `beginRendering` to display.

---

### Message 1 — Seed the data model

```json
{
  "dataModelUpdate": {
    "surfaceId": "checkout-surface",
    "contents": [
      { "key": "form/email",           "valueString":  "" },
      { "key": "form/shipping",        "valueString":  "" },
      { "key": "order/subtotal",       "valueString":  "$89.99" },
      { "key": "order/shippingCost",   "valueString":  "TBD" },
      { "key": "order/total",          "valueString":  "$89.99" }
    ]
  }
}
```

---

### Message 2 — Declare all components (flat adjacency list)

```json
{
  "surfaceUpdate": {
    "surfaceId": "checkout-surface",
    "components": [
      {
        "id": "root-col",
        "component": {
          "Column": {
            "children": ["page-title","divider-top","email-section-title","email-field","divider-mid1","shipping-section-title","shipping-picker","divider-mid2","summary-section-title","summary-card","divider-bot","submit-btn"],
            "align": "stretch"
          }
        }
      },
      { "id": "page-title", "component": { "Text": { "text": { "literalString": "Checkout" }, "variant": "h2" } } },
      { "id": "divider-top",  "component": { "Divider": { "axis": "horizontal" } } },
      { "id": "email-section-title", "component": { "Text": { "text": { "literalString": "Contact Information" }, "variant": "h4" } } },
      {
        "id": "email-field",
        "component": {
          "TextField": {
            "value": { "path": "/form/email" },
            "type": "shortText",
            "label": { "literalString": "Email address" },
            "validationRegexp": "^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$"
          }
        }
      },
      { "id": "divider-mid1", "component": { "Divider": { "axis": "horizontal" } } },
      { "id": "shipping-section-title", "component": { "Text": { "text": { "literalString": "Shipping Method" }, "variant": "h4" } } },
      {
        "id": "shipping-picker",
        "component": {
          "MultipleChoice": {
            "selections": { "path": "/form/shipping" },
            "maxAllowedSelections": 1,
            "options": [
              { "id": "standard",  "label": { "literalString": "Standard (5–7 days, free)" } },
              { "id": "express",   "label": { "literalString": "Express (2–3 days, $9.99)" } },
              { "id": "overnight", "label": { "literalString": "Overnight (next day, $24.99)" } }
            ]
          }
        }
      },
      { "id": "divider-mid2", "component": { "Divider": { "axis": "horizontal" } } },
      { "id": "summary-section-title", "component": { "Text": { "text": { "literalString": "Order Summary" }, "variant": "h4" } } },
      { "id": "summary-card", "component": { "Card": { "child": "summary-inner-col" } } },
      {
        "id": "summary-inner-col",
        "component": { "Column": { "children": ["summary-row-subtotal","summary-row-shipping","summary-divider","summary-row-total"], "align": "stretch" } }
      },
      { "id": "summary-row-subtotal", "component": { "Row": { "children": ["summary-label-subtotal","summary-value-subtotal"], "justify": "spaceBetween" } } },
      { "id": "summary-label-subtotal", "component": { "Text": { "text": { "literalString": "Subtotal" }, "variant": "body" } } },
      { "id": "summary-value-subtotal", "component": { "Text": { "text": { "path": "/order/subtotal" }, "variant": "body" } } },
      { "id": "summary-row-shipping", "component": { "Row": { "children": ["summary-label-shipping","summary-value-shipping"], "justify": "spaceBetween" } } },
      { "id": "summary-label-shipping", "component": { "Text": { "text": { "literalString": "Shipping" }, "variant": "body" } } },
      { "id": "summary-value-shipping", "component": { "Text": { "text": { "path": "/order/shippingCost" }, "variant": "body" } } },
      { "id": "summary-divider", "component": { "Divider": { "axis": "horizontal" } } },
      { "id": "summary-row-total", "component": { "Row": { "children": ["summary-label-total","summary-value-total"], "justify": "spaceBetween" } } },
      { "id": "summary-label-total", "component": { "Text": { "text": { "literalString": "Total" }, "variant": "h5" } } },
      { "id": "summary-value-total", "component": { "Text": { "text": { "path": "/order/total" }, "variant": "h5" } } },
      { "id": "divider-bot", "component": { "Divider": { "axis": "horizontal" } } },
      {
        "id": "submit-btn",
        "component": {
          "Button": {
            "child": "submit-btn-label",
            "variant": "primary",
            "action": { "type": "event", "name": "checkoutSubmit" }
          }
        }
      },
      { "id": "submit-btn-label", "component": { "Text": { "text": { "literalString": "Place Order" }, "variant": "body" } } }
    ]
  }
}
```

---

### Message 3 — Begin rendering (always last in v0.8)

```json
{
  "beginRendering": {
    "surfaceId": "checkout-surface",
    "root": "root-col"
  }
}
```

---

## How the data binding works

- `email-field` writes back to `/form/email` bidirectionally as the user types.
- `shipping-picker` writes the selected option ID to `/form/shipping`.
- Summary Card Text nodes read from `/order/*` paths. Update them reactively:

```json
{
  "dataModelUpdate": {
    "surfaceId": "checkout-surface",
    "contents": [
      { "key": "order/shippingCost", "valueString": "$9.99" },
      { "key": "order/total",        "valueString": "$99.98" }
    ]
  }
}
```

## Key design notes

- Flat adjacency list — `Card` holds `summary-inner-col` by ID, not by nesting JSON.
- `MultipleChoice` uses `maxAllowedSelections: 1` to behave as a radio group.
- `Button` always includes `action` so the renderer knows what event to fire on click.
- `beginRendering` is sent last, per the v0.8 ordering rule.
