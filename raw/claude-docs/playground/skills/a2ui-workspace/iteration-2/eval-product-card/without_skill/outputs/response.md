# ADK Agent: Product Card with A2UI v0.8 JSON

## Full Agent Code

```python
import json
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

def generate_product_card(
    product_name: str,
    price: float,
    image_url: str,
    currency: str = "USD"
) -> dict:
    """Generates A2UI v0.8 JSON for a product card UI component."""
    formatted_price = f"${price:.2f}" if currency == "USD" else f"{price:.2f} {currency}"

    a2ui_json = {
        "a2ui": "0.8",
        "type": "card",
        "id": "product-card",
        "children": [
            {
                "type": "image",
                "id": "product-image",
                "src": image_url,
                "alt": f"Image of {product_name}",
                "style": { "width": "100%", "height": "auto", "objectFit": "cover" }
            },
            {
                "type": "container",
                "id": "product-details",
                "children": [
                    {
                        "type": "text",
                        "id": "product-name",
                        "content": product_name,
                        "variant": "heading"
                    },
                    {
                        "type": "text",
                        "id": "product-price",
                        "content": formatted_price,
                        "variant": "price"
                    },
                    {
                        "type": "button",
                        "id": "add-to-cart-button",
                        "label": "Add to Cart",
                        "action": {
                            "type": "event",
                            "event": "add_to_cart",
                            "payload": { "product_name": product_name, "price": price }
                        }
                    }
                ]
            }
        ]
    }

    return {"a2ui_json": json.dumps(a2ui_json, indent=2), "raw": a2ui_json}


product_card_agent = Agent(
    name="product_card_agent",
    model="gemini-2.0-flash",
    description="An agent that generates A2UI v0.8 JSON for product card UI components.",
    instruction="""You are a UI generation agent. When a user asks you to show a product card,
call the generate_product_card tool with the appropriate product details.""",
    tools=[generate_product_card],
)
```

---

## Example A2UI v0.8 JSON Output

```json
{
  "a2ui": "0.8",
  "type": "card",
  "id": "product-card",
  "children": [
    {
      "type": "image",
      "id": "product-image",
      "src": "https://images.example.com/products/wireless-headphones.jpg",
      "alt": "Image of Wireless Headphones Pro"
    },
    {
      "type": "container",
      "id": "product-details",
      "children": [
        { "type": "text", "id": "product-name", "content": "Wireless Headphones Pro", "variant": "heading" },
        { "type": "text", "id": "product-price", "content": "$89.99", "variant": "price" },
        {
          "type": "button",
          "id": "add-to-cart-button",
          "label": "Add to Cart",
          "action": { "type": "event", "event": "add_to_cart", "payload": { "price": 89.99 } }
        }
      ]
    }
  ]
}
```
