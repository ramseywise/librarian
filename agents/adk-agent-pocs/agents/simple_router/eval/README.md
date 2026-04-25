# simple_router — Eval

## Running evals

```bash
# From the repo root — run all four suites:
make -C agents/simple_router eval

# Individual suites:
make -C agents/simple_router eval-routing
make -C agents/simple_router eval-response
make -C agents/simple_router eval-behavior
make -C agents/simple_router eval-error

# Run specific cases (comma-separated eval IDs):
make -C agents/simple_router eval-routing CASES=follow_up_shortcut_fires,static_route_guard_releases_next_turn
make -C agents/simple_router eval-response CASES=out_of_scope_expense_decline
make -C agents/simple_router eval-behavior CASES=behavior_oos_decline_danish
```

Or call `adk eval` directly (equivalent to the Makefile targets):

```bash
adk eval agents/simple_router \
  agents/simple_router/eval/routing_evalset.json \
  --config_file_path agents/simple_router/eval/routing_eval_config.json \
  --print_detailed_results
```

---

## Eval suites

| Suite | File | Metric | Threshold | Cases |
|-------|------|--------|-----------|-------|
| Routing | `routing_evalset.json` | `tool_trajectory_avg_score` | 1.0 | 30 |
| Response | `response_evalset.json` | `final_response_match_v2` | 1.0 | 14 |
| Behavior | `behavior_evalset.json` | `rubric_based_final_response_quality_v1` | 0.8 | 8 |
| Error | `error_evalset.json` | `rubric_based_final_response_quality_v1` | 0.8 | 3 |

---

## Routing evalset (30 cases)

Covers single-domain routing, multi-domain orchestration, cross-turn state, follow-up bypass, static routing guard, and out-of-scope fallback.

| Case | What it tests |
|------|---------------|
| `single_domain_invoice` | Basic invoice routing → `invoice_agent` |
| `single_domain_support` | Basic how-to routing → `support_agent` |
| `multi_domain_orchestrator` | Invoice + how-to composite → `orchestrator_agent` |
| `out_of_scope_to_receptionist` | Unknown domain → `receptionist_agent` |
| `cross_turn_invoice_id` | ID stated in turn 1 resolved from session facts in turn 2 |
| `how_to_with_invoice_vocab` | HOW-TO gate fires over invoice vocabulary → `support_agent` |
| `greeting_then_invoice` | Conversational opener then invoice request — correct routing after greeting |
| `follow_up_shortcut_fires` | Pre-seeded follow-up state + bare ID → shortcut bypasses router LLM |
| `follow_up_shortcut_fires_support_agent` | Same shortcut path for `support_agent` |
| `follow_up_long_message_bypasses_shortcut` | Long message with follow-up state → shortcut falls through, LLM routes |
| `follow_up_new_request_content_classifier` | New request while follow-up registered → LLM classifies by content |
| `topic_change_bypasses_follow_up` | New request after follow-up signal → routes by content, not follow-up |
| `greeting_then_follow_up_invoice_id` | Greeting → invoice agent asks for ID → bare ID follow-up → resolved |
| `static_route_howto_gate_over_invoice_vocab` | Static routing: how-to gate fires over invoice vocabulary |
| `static_route_keyword_scoring_invoice` | Static routing: high-confidence keyword match → `invoice_agent` |
| `static_route_wrong_agent_reroutes_to_support` | Static routing: wrong-domain reroute via `signal_reroute` |
| `static_route_guard_releases_next_turn` | Re-route guard (`router:static_bypass`) clears after one turn |
| `out_of_scope_expense_to_receptionist` | Expense/OOS keyword → `receptionist_agent` |
| `oos_fires_before_follow_up_shortcut` | OOS shortcut takes priority over follow-up state |
| `oos_recovery_after_decline` | Normal request after OOS decline routes correctly |
| `oos_false_positive_recovery` | In-scope request containing an OOS keyword routes to correct domain |
| `wrong_routing_recovery` | Expert calls `signal_reroute` → router re-classifies on next turn |
| `invoice_agent_declines_credit_note` | Invoice agent receives out-of-domain request (credit note) |
| `invoice_howto_invoice_no_escalation` | Invoice how-to question stays in `support_agent`, no bounce |
| `invoice_then_howto_no_bounce` | Invoice turn then how-to turn — no agent ping-pong |
| `orchestrator_separator_also` | "also" separator triggers `orchestrator_agent` |
| `orchestrator_separator_comma` | Comma separator triggers `orchestrator_agent` |
| `validate_invoice_routing` | Validate request → `invoice_agent` |
| `update_invoice_routing` | Update request → `invoice_agent` |
| `facts_field_answer_no_refetch` | Session facts injected → agent answers field question without re-fetching |

---

## Response evalset (13 cases)

Verifies exact response text for cases where output is deterministic or near-deterministic. Scored with `final_response_match_v2` (LLM judge, threshold 1.0).

| Case | What it tests |
|------|---------------|
| `out_of_scope_expense_decline` | OOS expense request → graceful decline |
| `out_of_scope_after_invoice_session` | OOS after a real invoice session — decline does not leak prior context |
| `invoice_agent_declines_credit_note` | Credit note (out of scope) → decline |
| `greeting_then_follow_up_shows_invoice` | Bare ID follow-up after invoice agent asks → shows invoice |
| `invoice_memory_after_howto_turn` | Invoice facts persist through a how-to turn |
| `exact_id_matching_456_45_4` | Model correctly distinguishes IDs 456, 45, and 4 |
| `generic_request_after_history_recall_asks_for_id` | Generic "show me an invoice" after a history turn → must ask for ID |
| `history_lists_two_invoices` | Two invoices viewed → history summary lists both |
| `history_two_invoices_after_unanswered_howto` | History question after an unanswered how-to turn → signal_follow_up called exactly once |
| `show_invoice_markdown_list` | Invoice details formatted as labelled markdown list |
| `validate_invoice_response` | Validation result formatted with issues listed and next step |
| `facts_field_answer_correct_value` | Injected session fact answered correctly without tool call |
| `follow_up_field_question_answers_concisely` | Field clarification answered concisely, not full invoice repeat |
| `oos_false_positive_decline_names_topic` | OOS decline names the disallowed topic explicitly |

---

## Behavior evalset (8 cases)

Rubric-based behavioral compliance tests through the full router pipeline. Threshold 0.8.

| Case | What it tests |
|------|---------------|
| `behavior_oos_decline_danish` | OOS decline delivered in Danish (language match) |
| `behavior_oos_decline_german` | OOS decline delivered in German (language match) |
| `behavior_orchestrator_both_domains_via_router` | Both invoice and how-to domains covered end-to-end |
| `behavior_confidentiality_via_router` | System prompt deflected gracefully mid-session |
| `behavior_oos_grounding_mid_session` | General-knowledge question refused mid-session |
| `behavior_no_stale_context_reuse` | Generic "show me an invoice" must ask for ID even when a prior invoice is in session facts |
| `behavior_bare_id_after_history_fetches_invoice` | After history turn + generic read, bare ID reply must fetch that invoice (not return history) |
| `behavior_bare_id_answers_follow_up_clarification` | Bare ID `"10"` after agent's clarifying question must show invoice 10 (not loop) |

---

## Error evalset (3 cases)

Robustness tests for incomplete requests, validation failures, and confirmation gates. Threshold 0.8.

| Case | What it tests |
|------|---------------|
| `error_validation_failure_communicated` | Validation issues are named clearly in the response |
| `error_missing_invoice_id_asks` | Agent asks for missing ID rather than guessing |
| `error_update_requires_confirmation` | Write gated behind a confirmation prompt |

---

## Tool assertion design

ADK trajectory matching compares on **both name and args** (`actual.args == expected.args`). Tools that accept free-text from the model (e.g. `get_support_steps(issue_code=...)`, `invoice_agent_helper(input=...)`) have unpredictable args across runs and cannot be used for exact assertions.

The routing evalset only asserts on tools with fully predictable args:

| Tool | Why predictable |
|------|-----------------|
| `get_conversation_context()` | No user-visible args |
| `signal_follow_up()` | No user-visible args |
| `get_invoice_details(invoice_id="N")` | ID is the user-supplied value |
| `note_invoice_id(invoice_id="N")` | ID is the user-supplied value |

For routing correctness, `intermediate_responses` records which sub-agent responded — this is the primary routing signal.

---

## Adding new cases

1. Add a new entry to the appropriate `*_evalset.json` under `eval_cases`.
2. Set `invocation_id` values sequentially within a conversation (`inv_1`, `inv_2`, …).
3. In `intermediate_data.tool_uses`, list only tools with predictable args (see table above).
4. Specify the expected sub-agent in `intermediate_data.intermediate_responses`.
5. Leave `final_response.parts[0].text` as `""` when you only care about routing or behavior (rubric scorer ignores this field).
6. Run the targeted case before the full suite: `make eval-routing CASES=my_new_case`.
