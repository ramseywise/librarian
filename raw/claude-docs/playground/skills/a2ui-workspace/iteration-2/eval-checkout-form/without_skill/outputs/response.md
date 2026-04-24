# A2UI v0.8 Multi-Step Checkout Form

Below is a complete A2UI v0.8 surface definition for a multi-step checkout form with data binding.

```json
{
  "a2ui": "0.8",
  "surface": {
    "id": "checkout-form",
    "title": "Checkout",
    "data": {
      "email": "",
      "shippingMethod": null,
      "orderTotal": 99.99,
      "currency": "USD"
    },
    "layout": {
      "type": "stack",
      "direction": "vertical",
      "spacing": "md",
      "children": [
        {
          "type": "TextField",
          "id": "email-field",
          "label": "Email Address",
          "placeholder": "you@example.com",
          "inputType": "email",
          "bind": "email",
          "required": true,
          "validation": {
            "pattern": "^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$",
            "errorMessage": "Please enter a valid email address"
          }
        },
        {
          "type": "MultipleChoice",
          "id": "shipping-method",
          "label": "Shipping Method",
          "bind": "shippingMethod",
          "required": true,
          "options": [
            { "value": "standard",  "label": "Standard Shipping",  "description": "5-7 business days", "price": 0.00 },
            { "value": "express",   "label": "Express Shipping",   "description": "2-3 business days", "price": 9.99 },
            { "value": "overnight", "label": "Overnight Shipping", "description": "Next business day",  "price": 24.99 }
          ],
          "selectionMode": "single"
        },
        {
          "type": "Card",
          "id": "order-summary",
          "title": "Order Summary",
          "children": [
            { "type": "Text", "id": "summary-email-label",    "content": "Email" },
            { "type": "Text", "id": "summary-email-value",    "bind": "email",           "fallback": "Not provided" },
            { "type": "Text", "id": "summary-shipping-label", "content": "Shipping Method" },
            { "type": "Text", "id": "summary-shipping-value", "bind": "shippingMethod",  "transform": "shippingMethodLabel", "fallback": "Not selected" },
            { "type": "Text", "id": "summary-total-label",    "content": "Order Total" },
            { "type": "Text", "id": "summary-total-value",    "expression": "formatCurrency(orderTotal + shippingCost(shippingMethod), currency)" }
          ]
        },
        {
          "type": "Button",
          "id": "submit-button",
          "label": "Place Order",
          "variant": "primary",
          "action": { "type": "submit", "validate": true, "target": "checkout-form" },
          "disabled": { "expression": "email == '' || shippingMethod == null" }
        }
      ]
    },
    "transforms": {
      "shippingMethodLabel": {
        "standard": "Standard Shipping (5-7 days)",
        "express": "Express Shipping (2-3 days)",
        "overnight": "Overnight Shipping (Next day)"
      }
    },
    "functions": {
      "shippingCost": { "standard": 0.00, "express": 9.99, "overnight": 24.99 },
      "formatCurrency": "{{value | currency: currencyCode}}"
    }
  }
}
```

## Key Design Decisions

### Data Model

The top-level `data` block defines the form state that all components share through two-way binding.

### Data Binding (`bind`)

The `bind` key establishes a two-way binding to the named field in `data`.

### MultipleChoice

`selectionMode: "single"` ensures only one shipping tier is active at a time.

### Summary Card — reactive expressions

- The email display uses a plain `bind` with a `fallback` for the empty state.
- The shipping display uses a `bind` plus a `transform` to convert the raw value into a human-readable label.
- The order total uses an `expression` that calls `shippingCost(shippingMethod)` and `formatCurrency(...)`.

### Submit Button

The Button's `disabled.expression` prevents submission until both required fields are filled.
