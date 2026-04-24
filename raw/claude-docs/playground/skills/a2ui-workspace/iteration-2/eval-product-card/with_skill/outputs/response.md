# ADK Agent: Product Card with A2UI v0.8

## Full Agent Code

**`product_card_agent/agent.py`**
```python
import json
from google.adk.agents.llm_agent import Agent

A2UI_INSTRUCTION = """
You are a product display agent. When asked to show a product, output an A2UI v0.8
UI JSON response that renders a product card.

Rules:
1. Separate any conversational text and the JSON with: ---a2ui_JSON---
2. First part: a brief conversational response (one sentence is fine).
3. Second part: a single JSON array of A2UI v0.8 messages.
4. The messages MUST follow this order:
   a. One or more `surfaceUpdate` messages defining all components.
   b. One `beginRendering` message last (required to trigger rendering).
5. Use the flat adjacency list model — never nest components inside each other.
6. All text values use { "literalString": "..." } unless bound to data.

The product card must include:
- A Card container as the top-level card wrapper.
- An Image component showing the product image.
- A Text component (variant "h3") showing the product name.
- A Text component (variant "body") showing the formatted price.
- A Button (variant "primary") with an inner Text label "Add to Cart".
"""

def get_product(product_id: str) -> str:
    """Return product details as JSON for the given product ID."""
    catalog = {
        "prod-001": {
            "id": "prod-001",
            "name": "Wireless Noise-Cancelling Headphones",
            "price": "$249.99",
            "image_url": "https://example.com/images/headphones.jpg",
        },
    }
    product = catalog.get(product_id)
    if not product:
        return json.dumps({"error": f"Product '{product_id}' not found."})
    return json.dumps(product)

root_agent = Agent(
    model="gemini-2.5-flash",
    name="product_card_agent",
    description="Displays product cards as rich A2UI v0.8 UI.",
    instruction=A2UI_INSTRUCTION,
    tools=[get_product],
)
```

**`product_card_agent/main.py`**
```python
import json
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part
from product_card_agent.agent import root_agent

SESSION_ID = "test-session"
USER_ID = "test-user"
APP_NAME = "product_card_agent"

def parse_a2ui_response(llm_output: str) -> list:
    delimiter = "---a2ui_JSON---"
    if delimiter in llm_output:
        _, json_part = llm_output.split(delimiter, 1)
    else:
        json_part = llm_output
    return json.loads(json_part.strip())

def main():
    session_service = InMemorySessionService()
    session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
    runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)
    user_message = Content(role="user", parts=[Part(text="Show me the product card for prod-001.")])

    full_text = ""
    for event in runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=user_message):
        if event.is_final_response() and event.content:
            for part in event.content.parts:
                if part.text:
                    full_text += part.text

    messages = parse_a2ui_response(full_text)
    print(json.dumps(messages, indent=2))

if __name__ == "__main__":
    main()
```

---

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
          "component": { "Image": { "src": { "literalString": "https://example.com/images/headphones.jpg" }, "fit": "contain" } }
        },
        {
          "id": "product-name",
          "component": { "Text": { "text": { "literalString": "Wireless Noise-Cancelling Headphones" }, "variant": "h3" } }
        },
        {
          "id": "product-price",
          "component": { "Text": { "text": { "literalString": "$249.99" }, "variant": "body" } }
        },
        {
          "id": "add-to-cart-btn",
          "component": { "Button": { "child": "add-to-cart-label", "variant": "primary" } }
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

## Key Design Points

1. **Flat adjacency list** — every component is a separate entry referenced by ID. No nesting.
2. **`beginRendering` must come last** — all `surfaceUpdate` component definitions must precede it. Missing this is the most common cause of a blank screen.
3. **`Button` requires a child component** — in v0.8, `Button.child` points to another component ID (here a `Text`) rather than an inline string.
4. **`literalString` for static values** — since values come from the tool result, they are embedded as literals. If using a live data model, use `{ "path": "/product/name" }` instead.
5. **Delimiter-based parsing** — the `---a2ui_JSON---` delimiter lets the LLM include a natural-language sentence alongside the JSON, keeping the agent conversational while remaining machine-parseable.
