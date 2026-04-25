// Shared helpers for all insight components.

export function fmtInsightAmt(n: number): string {
  if (n >= 1_000_000) return (n / 1_000_000).toFixed(1) + "M";
  if (n >= 1_000) return Math.round(n / 1_000) + "k";
  return n.toLocaleString();
}

export function fmtFull(n: number): string {
  return n.toLocaleString("en-DK", { minimumFractionDigits: 0, maximumFractionDigits: 0 });
}

// ---------------------------------------------------------------------------
// INSIGHTS_LABELS_DEFAULT — English fallbacks for all insight panel labels.
// The agent overrides these by setting /labels/* in updateDataModel.
// ---------------------------------------------------------------------------

export const INSIGHTS_LABELS_DEFAULT: Record<string, string> = {
  // RevenueSummary
  rev_title:           "Revenue Overview",
  // InvoiceStatusChart
  pipe_title:          "Invoice Pipeline",
  // RevenueChart
  chart_title:         "Monthly Revenue",
  chart_invoiced:      "Invoiced",
  chart_paid:          "Paid",
  chart_footer:        "Amounts excl. VAT",
  // TopCustomersTable
  top_title:           "Top Customers",
  top_subtitle:        "by revenue",
  top_leg_paid:        "Paid",
  top_leg_invoiced:    "Invoiced",
  top_leg_outstanding: "Outstanding",
  top_paid:            "✓ paid",
  top_nodata:          "No data",
  // AgingReport
  aging_title:         "Aging Report",
  aging_as_of:         "as of",
  aging_overdue_label: "Overdue",
  aging_col_invoice:   "Invoice",
  aging_col_customer:  "Customer",
  aging_col_due:       "Due date",
  aging_col_amount:    "Amount",
  aging_inv:           "inv.",
  aging_empty:         "No outstanding invoices",
  // CustomerInsightCard
  cust_kpi_invoiced:   "Invoiced",
  cust_kpi_collected:  "Collected",
  cust_kpi_outstanding:"Outstanding",
  cust_kpi_overdue:    "Overdue",
  cust_open_invoices:  "Open invoices",
  cust_all_paid:       "✓ All invoices paid",
  cust_last:           "Last:",
  cust_loading:        "Loading…",
  cust_overdue:        "overdue",
  // ProductRevenueTable
  prod_title:          "Product Revenue",
  prod_excl_vat:       "excl. VAT",
  prod_qty:            "qty",
  prod_nodata:         "No data",
  // DashboardSuggestions
  sugg_heading:        "Explore further",
};

export function insightLabel(getValue: (path: string) => unknown, key: string): string {
  const v = getValue(`/labels/${key}`);
  return typeof v === "string" && v ? v : (INSIGHTS_LABELS_DEFAULT[key] ?? key);
}

export const RANK_MEDALS: Record<number, string> = {
  1: "🥇", 2: "🥈", 3: "🥉",
};

export const AVATAR_COLORS = [
  "bg-violet-100 text-violet-700", "bg-blue-100 text-blue-700",
  "bg-emerald-100 text-emerald-700", "bg-amber-100 text-amber-700",
  "bg-rose-100 text-rose-700", "bg-indigo-100 text-indigo-700",
];
