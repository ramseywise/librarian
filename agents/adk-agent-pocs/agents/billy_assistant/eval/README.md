# Billy Assistant — Eval

## Running evals

```bash
# From the repo root — run all three suites:
make -C agents/billy_assistant eval

# Individual suites:
make -C agents/billy_assistant eval-routing
make -C agents/billy_assistant eval-behavior
make -C agents/billy_assistant eval-error

# Run specific cases (comma-separated eval IDs):
make -C agents/billy_assistant eval-routing CASES=my_case
make -C agents/billy_assistant eval-behavior CASES=my_case
```

Or call `adk eval` directly:

```bash
adk eval agents/billy_assistant \
  agents/billy_assistant/eval/routing_evalset.json \
  --config_file_path agents/billy_assistant/eval/routing_eval_config.json \
  --print_detailed_results
```

---

## Eval suites

| Suite    | File                      | Metric                                  | Threshold | Cases |
| -------- | ------------------------- | --------------------------------------- | --------- | ----- |
| Routing  | `routing_evalset.json`    | `tool_trajectory_avg_score`             | 1.0       | 7     |
| Response | `response_evalset.json`   | `final_response_match_v2`               | 1.0       | 1     |
| Behavior | `behavior_evalset.json`   | `rubric_based_final_response_quality_v1`| 0.8       | 4     |
| Error    | `error_evalset.json`      | `rubric_based_final_response_quality_v1`| 0.8       | 6     |

---

## Routing evalset

Covers single-domain routing to each subagent, support-vs-action disambiguation, and out-of-domain fallback.

| Case | What it tests |
| ---- | ------------- |
| `how_to_upload_invoice_routes_to_support` | How-to question with invoice vocab routes directly to `support_agent`, not `invoice_agent` |
| `create_invoice_routes_to_invoice_agent` | Explicit create action routes to `invoice_agent` |
| `list_customers_routes_to_customer_agent` | List action routes to `customer_agent` |
| `add_product_routes_to_product_agent` | Product catalog action routes to `product_agent` |
| `send_invoice_email_routes_to_email_agent` | Email send action routes to `email_agent` |
| `invite_user_routes_to_invitation_agent` | User invitation routes to `invitation_agent` |
| `how_to_approve_invoice_routes_to_support` | How-to question with invoice vocab routes to `support_agent`, not `invoice_agent` |

---

## Response evalset

Semantic response matching for near-deterministic outputs. Threshold 1.0 (LLM judge).

| Case | What it tests |
| ---- | ------------- |
| `invite_no_email_asks_for_email` | Invite with no email elicits a response that asks specifically for an email address |

---

## Behavior evalset

Rubric-based behavioral compliance tests. Threshold 0.8.

| Case | What it tests |
| ---- | ------------- |
| `how_to_add_customer_goes_to_support` | How-to question routes to support and returns guidance, not a create action (`support_over_action_for_how_to`) |
| `list_products_action_goes_to_product_agent` | Concrete list action is fulfilled by the domain agent, not support docs (`action_agent_for_operations`) |
| `out_of_domain_politely_declined` | Clearly out-of-domain request is declined politely with explanation of what Billy can help with (`out_of_domain_handled_gracefully`) |
| `invoice_detail_no_hallucination` | Invoice detail response matches mock tool data — amounts, dates, statuses are not invented (`no_hallucination`) |

---

## Error evalset

Robustness tests for missing information, confirmation gates, and failed operations. Threshold 0.8.

| Case | What it tests |
| ---- | ------------- |
| `create_invoice_no_customer_asks_clarification` | Bare "create an invoice" with no customer triggers a specific clarifying question (`asks_for_missing_info`) |
| `invite_no_email_asks_clarification` | Invite request with no email address triggers a request for the email (`asks_for_missing_info`) |
| `create_customer_confirmation_required` | Create customer with full details asks for confirmation before writing (`confirmation_before_write`) |
| `create_invoice_unknown_customer_error_communicated` | Invoice for a customer not in the system triggers a lookup, finds nothing, and offers to create the customer now (`error_communicated_clearly`) |
| `create_invoice_unknown_product_error_communicated` | Invoice for a product name not in the system triggers a lookup, finds nothing, and offers to create the product now (`error_communicated_clearly`) |
| `send_draft_invoice_error_communicated` | Sending a draft invoice (2024-003) communicates the draft/approval constraint clearly (`error_communicated_clearly`) |

---

## Tool assertion design

ADK trajectory matching compares on **both name and args** (`actual.args == expected.args`). Tools that accept free-text from the model have unpredictable args across runs and cannot be used for exact assertions.

Only assert on tools with fully predictable args (e.g. `get_invoice(invoice_id="10")` where the ID is user-supplied).

For routing correctness, `intermediate_responses` records which sub-agent responded — this is the primary routing signal.

---

## Adding new cases

1. Add a new entry to the appropriate `*_evalset.json` under `eval_cases`.
2. Set `invocation_id` values sequentially within a conversation (`inv_1`, `inv_2`, …).
3. In `intermediate_data.tool_uses`, list only tools with predictable args.
4. Specify the expected sub-agent in `intermediate_data.intermediate_responses`.
5. Leave `final_response.parts[0].text` as `""` when you only care about routing or behavior.
6. Add the case ID and description to the relevant table in this README.
7. Run the targeted case before the full suite: `make eval-routing CASES=my_new_case`.

### Evalset entry schema

```json
{
  "eval_id": "my_case_id",
  "conversation": [
    {
      "invocation_id": "inv_1",
      "user_content": {
        "parts": [{ "text": "user message here" }]
      },
      "final_response": {
        "role": "model",
        "parts": [{ "text": "" }]
      },
      "intermediate_data": {
        "tool_uses": [],
        "intermediate_responses": [
          ["expected_subagent_name", [{ "text": "" }]]
        ]
      }
    }
  ],
  "session_input": {
    "app_name": "billy_assistant",
    "user_id": "eval_user",
    "state": {}
  }
}
```
