# ADK Agent: Product Card with A2UI v0.8

This guide shows how to write an ADK agent in Python that outputs A2UI v0.8 JSON for a product card UI containing an image, product name, price, and an "Add to Cart" button.

---

## Full Python Agent Code

```python
import json
from google.adk.agents.llm_agent import Agent

# A2UI instruction injected into the system prompt
A2UI_INSTRUCTION = """
You are a shopping assistant agent. When the user asks about a product,
display it as a rich UI card using the A2UI v0.8 protocol.

Your final output MUST contain two parts separated by the delimiter:
    ---a2ui_JSON---

1. A short conversational response (one or two sentences).
2. A single JSON array of A2UI v0.8 messages.

A2UI v0.8 Rules:
- Components are a FLAT list (adjacency list model) — never nest component
  objects inside each other.
- Each component entry has an "id" (string) and a "component" (object whose
  single key is the component type, e.g. "Card", "Column", "Image", "Text",
  "Button", "Row").
- Send all surfaceUpdate messages BEFORE the beginRendering message.
- Text values use  { "literalString": "..." }  or  { "path": "/..." }.
- Buttons wrap a child component; use "variant": "primary" for the main CTA.
- Images use "src" for the URL.

Required message sequence for v0.8:
  1. surfaceUpdate  (defines all components)
  2. beginRendering (tells the client which node is the root)
"""

# Helper: parse the A2UI JSON block out of the LLM response
def parse_a2ui_response(llm_output: str) -> list:
    """Split on the delimiter and return the parsed JSON array."""
    delimiter = "---a2ui_JSON---"
    if delimiter in llm_output:
        _, json_part = llm_output.split(delimiter, 1)
    else:
        json_part = llm_output
    return json.loads(json_part.strip())


# ADK Agent definition
root_agent = Agent(
    model="gemini-2.5-flash",
    name="product_card_agent",
    description="Displays product information as a rich A2UI v0.8 card UI.",
    instruction=A2UI_INSTRUCTION,
)


# Example: run the agent programmatically and parse the UI output
if __name__ == "__main__":
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService
    from google.genai import types

    APP_NAME = "product_card_demo"
    USER_ID  = "demo_user"
    SESSION_ID = "session_001"

    session_service = InMemorySessionService()
    session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )

    runner = Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=session_service,
    )

    user_message = types.Content(
        role="user",
        parts=[types.Part(text="Show me the Wireless Noise-Cancelling Headphones for $149.99.")],
    )

    print("Running agent...\n")
    for event in runner.run(
        user_id=USER_ID,
        session_id=SESSION_ID,
        new_message=user_message,
    ):
        if event.is_final_response():
            raw = event.content.parts[0].text
            print("=== Raw agent response ===")
            print(raw)
            print("\n=== Parsed A2UI messages ===")
            messages = parse_a2ui_response(raw)
            print(json.dumps(messages, indent=2))
```

---

## Example A2UI v0.8 JSON Output

```json
[
  {
    "surfaceUpdate": {
      "surfaceId": "product-card-surface",
      "components": [
        {
          "id": "root-col",
          "component": {
            "Column": {
              "children": ["product-card"],
              "align": "center"
            }
          }
        },
        {
          "id": "product-card",
          "component": {
            "Card": {
              "child": "card-content"
            }
          }
        },
        {
          "id": "card-content",
          "component": {
            "Column": {
              "children": [
                "product-image",
                "product-name",
                "product-price",
                "add-to-cart-btn"
              ],
              "align": "center"
            }
          }
        },
        {
          "id": "product-image",
          "component": {
            "Image": {
              "src": {
                "literalString": "https://example.com/images/headphones.jpg"
              },
              "fit": "contain"
            }
          }
        },
        {
          "id": "product-name",
          "component": {
            "Text": {
              "text": {
                "literalString": "Wireless Noise-Cancelling Headphones"
              },
              "variant": "h3"
            }
          }
        },
        {
          "id": "product-price",
          "component": {
            "Text": {
              "text": {
                "literalString": "$149.99"
              },
              "variant": "body"
            }
          }
        },
        {
          "id": "add-to-cart-label",
          "component": {
            "Text": {
              "text": {
                "literalString": "Add to Cart"
              }
            }
          }
        },
        {
          "id": "add-to-cart-btn",
          "component": {
            "Button": {
              "child": "add-to-cart-label",
              "variant": "primary",
              "action": {
                "type": "event",
                "name": "addToCart",
                "payload": {
                  "productId": "headphones-001"
                }
              }
            }
          }
        }
      ]
    }
  },
  {
    "beginRendering": {
      "surfaceId": "product-card-surface",
      "root": "root-col"
    }
  }
]
```

---

## Key Design Decisions

### Flat adjacency list
All components are siblings in the top-level `components` array. Parent-child relationships are expressed through ID references, never by nesting component objects.

### `beginRendering` comes last
Per v0.8 ordering rules, all `surfaceUpdate` messages must be sent before `beginRendering`. The client waits for `beginRendering` to know which node is the tree root.

### Button wraps a Text child
`Button` does not have a `label` property; instead it has a `child` pointing to another component ID. Here `add-to-cart-label` (a `Text` node) is that child.

### Literal strings for static data
Because the product details are known at generation time, `{ "literalString": "..." }` is used. For dynamic data, use `{ "path": "/product/name" }` with a `dataModelUpdate` message.

---

## Running the Agent

```bash
pip install google-adk
export GOOGLE_GENAI_USE_VERTEXAI=FALSE
export GOOGLE_API_KEY="your_gemini_api_key"

python product_card_agent.py
```

Or launch the ADK dev UI:

```bash
adk web
```

Then navigate to `http://localhost:8000` and ask: *"Show me the Wireless Noise-Cancelling Headphones for $149.99."*
