# ADK Agent: Product Card with A2UI v0.8

## Full Agent Code

```python
# product_card_agent/agent.py

import json
from google.adk.agents.llm_agent import Agent

A2UI_INSTRUCTION = """
You are a shopping assistant that displays product information as rich UI.

Your final output MUST be an A2UI v0.8 UI JSON response.

Rules:
1. Separate conversational text and JSON with: ---a2ui_JSON---
2. First part: your brief conversational response
3. Second part: a single JSON array of A2UI messages in this exact order:
   a. One or more `surfaceUpdate` messages defining all components
   b. One `beginRendering` message (always last)
4. Use the flat adjacency list model — components are a flat array with ID references, NOT nested
5. Always include an `action` on every Button component
6. JSON MUST be valid A2UI v0.8

When showing a product, always include:
- A Card container wrapping the product content
- An Image for the product photo
- A Text component for the product name (variant: h3)
- A Text component for the price (variant: body)
- A Button with label "Add to Cart" and action type "event"
"""


def get_product(product_id: str) -> str:
    """Fetch product details by ID."""
    products = {
        "p001": {
            "id": "p001",
            "name": "Wireless Noise-Cancelling Headphones",
            "price": "$149.99",
            "image_url": "https://example.com/images/headphones.jpg",
        },
    }
    product = products.get(product_id, products["p001"])
    return json.dumps(product)


root_agent = Agent(
    model="gemini-2.5-flash",
    name="product_card_agent",
    description="Displays product details as a rich A2UI product card with an Add to Cart button.",
    instruction=A2UI_INSTRUCTION,
    tools=[get_product],
)
```

## Example A2UI v0.8 JSON Output

```json
[
  {
    "surfaceUpdate": {
      "surfaceId": "product-surface",
      "components": [
        {
          "id": "root-col",
          "component": { "Column": { "children": ["product-card"], "align": "center" } }
        },
        {
          "id": "product-card",
          "component": { "Card": { "child": "card-content" } }
        },
        {
          "id": "card-content",
          "component": { "Column": { "children": ["product-image", "product-name", "product-price", "add-to-cart-btn"] } }
        },
        {
          "id": "product-image",
          "component": { "Image": { "src": { "literalString": "https://example.com/images/headphones.jpg" }, "fit": "cover" } }
        },
        {
          "id": "product-name",
          "component": { "Text": { "text": { "literalString": "Wireless Noise-Cancelling Headphones" }, "variant": "h3" } }
        },
        {
          "id": "product-price",
          "component": { "Text": { "text": { "literalString": "$149.99" }, "variant": "body" } }
        },
        {
          "id": "add-to-cart-btn",
          "component": { "Button": { "child": "add-to-cart-label", "variant": "primary", "action": { "type": "event", "name": "addToCart" } } }
        },
        {
          "id": "add-to-cart-label",
          "component": { "Text": { "text": { "literalString": "Add to Cart" } } }
        }
      ]
    }
  },
  {
    "beginRendering": {
      "surfaceId": "product-surface",
      "root": "root-col"
    }
  }
]
```

---

Key design points applied from the A2UI skill:
- **Flat adjacency list** - all 8 components are siblings in the array; nesting is expressed only through ID references
- **`beginRendering` comes last** - component definitions must precede it or the client shows a blank screen
- **Button always has `action`** - required by the spec so the client knows what event to fire on click
- **Text label for Button** - the Button's `child` points to a separate `Text` component ID (not an inline string)
