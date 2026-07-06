Tier 1 — Core happy path (do these first)

"Show me all open invoices" — exercises list_invoices + routing
"What's my invoice summary for this year?" — get_invoice_summary + insight
"Who are my top customers?" — get_insight_top_customers
"Show me my expenses by category" — get_expenses_by_category
Tier 2 — Financial intelligence (the interesting stuff)

"What's my cash flow looking like?" — get_cashflow_forecast
"How's my gross margin?" — get_gross_margin + get_net_margin
"What's my runway?" — get_runway_estimate
"Are there any anomalies in my books?" — detect_anomaly
"Which invoices are overdue?" — get_insight_aging_report
Tier 3 — Multi-turn + cross-domain

Ask about a customer, then drill into their invoices
Ask a vague question ("how's business?") and see if it synthesizes across tools
Ask something it can't do ("send an invoice to John") and check the fallback message
Tier 4 — Support KB

"How do I set up VAT?" — hits support_search / fetch_support_knowledge
