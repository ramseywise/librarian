// ---------------------------------------------------------------------------
// InvoiceList — full invoice list with summary cards, search bar, and table.
// A single custom component emitted as the main surface root. Reads /invoices
// and /summary from the data model; manages local filter/search state; fires
// view_invoice and create_invoice events via OnActionContext.
// ---------------------------------------------------------------------------

import { useA2UIComponent } from "@a2ui/react";
import { memo, useCallback, useContext, useState } from "react";
import { BILLY_REST_BASE } from "../core/fetch-resolver";
import { OnActionContext } from "../core/contexts";

type InvoiceItem = {
  id: string;
  invoiceNo: string;
  customerName: string;
  entryDate: string;
  dueDate: string;
  amount: string;
  grossAmount: string;
  state: string;
  description: string;
  isPaid: boolean;
};

type FilterKey = "all" | "draft" | "approved" | "overdue" | "unpaid" | "paid";

const SUMMARY_CARD_CONFIG: Array<{
  key: FilterKey;
  labelKey: string;
  defaultLabel: string;
  badgeColor: string;
  textColor: string;
}> = [
  { key: "all",      labelKey: "card_all",      defaultLabel: "All invoices", badgeColor: "bg-blue-500",   textColor: "text-slate-700" },
  { key: "draft",    labelKey: "card_draft",    defaultLabel: "Draft",        badgeColor: "bg-blue-300",   textColor: "text-blue-400" },
  { key: "overdue",  labelKey: "card_overdue",  defaultLabel: "Overdue",      badgeColor: "bg-red-400",    textColor: "text-red-500" },
  { key: "unpaid",   labelKey: "card_unpaid",   defaultLabel: "Unpaid",       badgeColor: "bg-yellow-400", textColor: "text-yellow-500" },
  { key: "paid",     labelKey: "card_paid",     defaultLabel: "Paid",         badgeColor: "bg-green-500",  textColor: "text-green-600" },
];

const INVOICE_LABELS_DEFAULT: Record<string, string> = {
  heading:          "Invoices",
  createInvoice:    "Create Invoice",
  summary:          "Summary",
  card_all:         "All invoices",
  card_draft:       "Draft",
  card_overdue:     "Overdue",
  card_unpaid:      "Unpaid",
  card_paid:        "Paid",
  search:           "Search...",
  fiscalYear:       "Fiscal Year",
  colNumber:        "Number",
  colDate:          "Date",
  colDue:           "Due",
  colCustomer:      "Customer",
  colDescription:   "Description",
  colExclVat:       "Excl. VAT",
  noResults:        "No invoices found.",
  // Detail view labels
  invCustomer:      "Customer",
  invTitle:         "Invoice",
  invNo:            "Invoice no.",
  invDate:          "Invoice date",
  invDueDate:       "Due date",
  invColDesc:       "Description",
  invColQty:        "Qty",
  invColUnitPrice:  "Unit price",
  invColPrice:      "Price",
  invExclVat:       "Total excl. VAT",
  invVat:           "VAT (25%)",
  invInclVat:       "Total incl. VAT",
};

const STATE_DOT: Record<string, string> = {
  draft:    "bg-slate-300",
  approved: "bg-yellow-400",
  paid:     "bg-green-500",
  overdue:  "bg-red-500",
};

type InvoiceDetail = {
  id: string;
  invoice_no: string;
  contact_id: string;
  customer_name: string;
  entry_date: string;
  due_date: string;
  state: string;
  amount: number;
  tax: number;
  gross_amount: number;
  currency: string;
  payment_terms: string | null;
  lines: Array<{
    id: string;
    product_id: string;
    description: string;
    quantity: number;
    unit_price: number;
    unit: string;
    amount: number;
    tax: number;
  }>;
};

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export const InvoiceList = memo(function InvoiceList2({ node, surfaceId }: { node: any; surfaceId: string }) {
  const { getValue } = useA2UIComponent(node, surfaceId);
  const onAction = useContext(OnActionContext);
  const label = (key: string): string => {
    const v = getValue(`/labels/${key}`);
    return typeof v === "string" && v ? v : (INVOICE_LABELS_DEFAULT[key] ?? key);
  };

  const [viewingInvoice, setViewingInvoice] = useState<InvoiceDetail | null>(null);
  const [loadingInvoice, setLoadingInvoice] = useState(false);

  const openInvoice = useCallback(async (id: string) => {
    setLoadingInvoice(true);
    try {
      const res = await fetch(`${BILLY_REST_BASE}/invoices/${id}`);
      if (res.ok) setViewingInvoice(await res.json() as InvoiceDetail);
    } finally {
      setLoadingInvoice(false);
    }
  }, []);

  const editDraftInvoice = useCallback(async (id: string) => {
    if (!onAction) return;
    setLoadingInvoice(true);
    try {
      const res = await fetch(`${BILLY_REST_BASE}/invoices/${id}`);
      if (!res.ok) return;
      const inv = await res.json() as InvoiceDetail;
      const lineItems = (inv.lines ?? []).map(l => ({
        productId: l.product_id ?? "",
        quantity: l.quantity,
        unitPrice: l.unit_price,
      }));
      onAction({
        userAction: {
          name: "edit_draft_invoice",
          sourceComponentId: node.id,
          surfaceId,
          context: {
            invoiceId: inv.id,
            customerId: inv.contact_id ?? "",
            dueDate: inv.due_date ?? "",
            lineItems,
          },
        },
      });
    } finally {
      setLoadingInvoice(false);
    }
  }, [onAction, node.id, surfaceId]);

  // Parse invoices array from the JSON-serialised data model value.
  const rawInvoices = getValue("/invoices");
  const invoices: InvoiceItem[] = (() => {
    if (Array.isArray(rawInvoices)) return rawInvoices as InvoiceItem[];
    if (typeof rawInvoices === "string") {
      try { return JSON.parse(rawInvoices) as InvoiceItem[]; } catch { return []; }
    }
    return [];
  })();

  const [activeFilter, setActiveFilter] = useState<FilterKey>("all");
  const [search, setSearch] = useState("");

  const today = new Date().toISOString().split("T")[0];
  // year: null means "all years" (e.g. customer-filtered view spanning multiple years)
  const yearParam = getValue("/year") as number | null | undefined;
  const fiscalYearStr = yearParam ? String(yearParam) : null;

  // Restrict to the requested fiscal year when set; null shows all years.
  const yearInvoices = fiscalYearStr
    ? invoices.filter(inv => inv.entryDate.startsWith(fiscalYearStr))
    : invoices;

  // Compute summary from the displayed invoice set so cards always match the list.
  type SummaryBucket = { count: number; amount: number };
  const computedSummary = yearInvoices.reduce<Record<string, SummaryBucket>>(
    (acc, inv) => {
      const amt = parseFloat(inv.amount) || 0;
      acc.all.count++; acc.all.amount += amt;
      if (inv.state === "draft") { acc.draft.count++; acc.draft.amount += amt; }
      else if (inv.state === "paid" || inv.isPaid) { acc.paid.count++; acc.paid.amount += amt; }
      else if (inv.dueDate && inv.dueDate < today) { acc.overdue.count++; acc.overdue.amount += amt; }
      else { acc.unpaid.count++; acc.unpaid.amount += amt; }
      return acc;
    },
    { all: { count: 0, amount: 0 }, draft: { count: 0, amount: 0 }, overdue: { count: 0, amount: 0 }, unpaid: { count: 0, amount: 0 }, paid: { count: 0, amount: 0 } }
  );

  const getCount = (key: string): number => computedSummary[key]?.count ?? 0;
  const getAmount = (key: string): string => (computedSummary[key]?.amount ?? 0).toFixed(2);

  const filtered = yearInvoices.filter((inv) => {
    if (activeFilter === "draft"    && inv.state !== "draft") return false;
    if (activeFilter === "approved" && inv.state !== "approved") return false;
    if (activeFilter === "paid"     && inv.state !== "paid" && !inv.isPaid) return false;
    if (activeFilter === "unpaid"   && (inv.state === "draft" || inv.state === "paid" || inv.isPaid)) return false;
    if (activeFilter === "overdue"  && !(inv.dueDate && inv.dueDate < today && inv.state !== "paid" && !inv.isPaid)) return false;
    if (search) {
      const q = search.toLowerCase();
      return inv.invoiceNo.toLowerCase().includes(q) ||
             inv.customerName.toLowerCase().includes(q) ||
             inv.description.toLowerCase().includes(q);
    }
    return true;
  });

  const fireEvent = useCallback((name: string, context?: Record<string, unknown>) => {
    if (!onAction) return;
    onAction({ userAction: { name, sourceComponentId: node.id, surfaceId, context: context ?? {} } });
  }, [onAction, node.id, surfaceId]);

  const fmtDate = (d: string) => {
    if (!d || d === "undefined" || d === "null") return "";
    const [y, m, dd] = d.split("-");
    return y && m && dd ? `${m}/${dd}/${y}` : d;
  };

  const fmtAmt = (s: string) =>
    (parseFloat(s) || 0).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });

  const fmtStatAmt = (key: string) => {
    const n = parseFloat(getAmount(key)) || 0;
    return n >= 1000
      ? Math.round(n).toLocaleString("en-US")
      : Math.round(n).toString();
  };

  const dotCls = (inv: InvoiceItem) => {
    if (inv.state === "paid" || inv.isPaid) return "bg-green-500";
    if (inv.dueDate && inv.dueDate < today) return "bg-red-500";
    return STATE_DOT[inv.state] ?? "bg-slate-300";
  };

  const activeCardKey = SUMMARY_CARD_CONFIG.find(c => c.key === activeFilter)?.labelKey ?? "card_all";
  const activeLabel = label(activeCardKey);

  const fmtCurrency = (n: number, cur: string) =>
    n.toLocaleString("da-DK", { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + " " + cur;

  if (loadingInvoice) {
    return (
      <div className="flex items-center justify-center h-48 text-slate-400 text-sm">Loading…</div>
    );
  }

  if (viewingInvoice) {
    const inv = viewingInvoice;
    const fmtD = (d: string) => {
      if (!d) return "";
      const [y, m, dd] = d.split("-");
      return y && m && dd ? `${parseInt(m)}/${parseInt(dd)}/${y}` : d;
    };
    const stateBadge: Record<string, string> = {
      draft: "bg-slate-100 text-slate-600",
      approved: "bg-yellow-100 text-yellow-700",
      paid: "bg-green-100 text-green-700",
      overdue: "bg-red-100 text-red-700",
    };
    return (
      <div className="w-full">
        {/* Back nav */}
        <button
          onClick={() => setViewingInvoice(null)}
          className="flex items-center gap-1.5 text-sm text-slate-500 hover:text-slate-800 mb-6 transition-colors"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
            <path d="M15 18l-6-6 6-6"/>
          </svg>
          {label("heading")}
        </button>

        {/* Invoice document */}
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm px-10 py-10 max-w-3xl">
          {/* Top header */}
          <div className="flex justify-between items-start mb-10">
            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-400 mb-1">{label("invCustomer")}</p>
              <p className="text-lg font-semibold text-slate-900">{inv.customer_name}</p>
            </div>
            <div className="text-right">
              <span className={`inline-block px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wide ${stateBadge[inv.state] ?? "bg-slate-100 text-slate-600"}`}>
                {inv.state}
              </span>
            </div>
          </div>

          {/* Invoice title row */}
          <div className="flex justify-between items-end border-b border-slate-100 pb-6 mb-6">
            <div>
              <p className="text-4xl font-light text-slate-300 tracking-tight">{label("invTitle")}</p>
            </div>
            <div className="grid grid-cols-3 gap-6 text-right text-sm">
              <div>
                <p className="text-xs text-slate-400 mb-0.5">{label("invNo")}</p>
                <p className="font-semibold text-slate-800">#{inv.invoice_no}</p>
              </div>
              <div>
                <p className="text-xs text-slate-400 mb-0.5">{label("invDate")}</p>
                <p className="font-semibold text-slate-800">{fmtD(inv.entry_date)}</p>
              </div>
              <div>
                <p className="text-xs text-slate-400 mb-0.5">{label("invDueDate")}</p>
                <p className="font-semibold text-slate-800">{fmtD(inv.due_date)}</p>
              </div>
            </div>
          </div>

          {/* Line items */}
          <table className="w-full text-sm mb-6">
            <thead>
              <tr className="border-b border-slate-100">
                <th className="pb-2 text-left text-xs font-semibold text-slate-400 uppercase tracking-wide">{label("invColDesc")}</th>
                <th className="pb-2 text-right text-xs font-semibold text-slate-400 uppercase tracking-wide">{label("invColQty")}</th>
                <th className="pb-2 text-right text-xs font-semibold text-slate-400 uppercase tracking-wide">{label("invColUnitPrice")}</th>
                <th className="pb-2 text-right text-xs font-semibold text-slate-400 uppercase tracking-wide">{label("invColPrice")}</th>
              </tr>
            </thead>
            <tbody>
              {(inv.lines ?? []).map((line) => (
                <tr key={line.id} className="border-b border-slate-50">
                  <td className="py-3 text-slate-800 font-medium">{line.description || "—"}</td>
                  <td className="py-3 text-right text-slate-600 tabular-nums">{line.quantity}</td>
                  <td className="py-3 text-right text-slate-600 tabular-nums">{fmtCurrency(line.unit_price, inv.currency)}</td>
                  <td className="py-3 text-right font-medium text-slate-800 tabular-nums">{fmtCurrency(line.amount, inv.currency)}</td>
                </tr>
              ))}
            </tbody>
          </table>

          {/* Totals */}
          <div className="flex justify-end">
            <div className="w-64 space-y-1.5 text-sm">
              <div className="flex justify-between text-slate-600">
                <span>{label("invExclVat")}</span>
                <span className="tabular-nums">{fmtCurrency(inv.amount, inv.currency)}</span>
              </div>
              <div className="flex justify-between text-slate-600">
                <span>{label("invVat")}</span>
                <span className="tabular-nums">{fmtCurrency(inv.tax, inv.currency)}</span>
              </div>
              <div className="flex justify-between font-bold text-slate-900 border-t border-slate-200 pt-2 mt-2">
                <span>{label("invInclVat")}</span>
                <span className="tabular-nums">{fmtCurrency(inv.gross_amount, inv.currency)}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-slate-900">{label("heading")}</h2>
        <div className="flex items-center gap-2">
          <button
            onClick={() => fireEvent("create_invoice")}
            className="flex items-center gap-1.5 rounded-full bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-700 transition-colors"
          >
            <span className="text-base leading-none">⊕</span> {label("createInvoice")}
          </button>
        </div>
      </div>

      {/* Summary cards */}
      <p className="text-xs font-semibold uppercase tracking-wide text-slate-400 mb-3">{label("summary")}</p>
      <div className="grid grid-cols-5 gap-3 mb-6">
        {SUMMARY_CARD_CONFIG.map(({ key, labelKey, badgeColor, textColor }) => (
          <button
            key={key}
            onClick={() => setActiveFilter(key)}
            className={[
              "text-left rounded-xl border p-4 transition-all",
              activeFilter === key
                ? "border-blue-500 ring-2 ring-blue-200 bg-white shadow-sm"
                : "border-slate-200 bg-white hover:border-slate-300 hover:shadow-sm",
            ].join(" ")}
          >
            <div className="flex items-center gap-2 mb-3">
              <span className={`inline-flex items-center justify-center min-w-[1.25rem] h-5 rounded-full px-1.5 text-xs font-semibold text-white ${badgeColor}`}>
                {getCount(key)}
              </span>
              <span className={`text-sm font-medium ${textColor}`}>{label(labelKey)}</span>
            </div>
            <p className="text-2xl font-bold text-slate-900 tabular-nums leading-tight">
              {fmtStatAmt(key)}{" "}
              <span className="text-sm font-normal text-slate-400">DKK</span>
            </p>
          </button>
        ))}
      </div>

      {/* Toolbar */}
      <div className="flex items-center gap-3 mb-3">
        <span className="text-sm font-semibold text-slate-800">{activeLabel}</span>
        <span className="inline-flex items-center justify-center min-w-[1.25rem] h-5 rounded-full bg-slate-100 px-1.5 text-xs font-medium text-slate-600">
          {filtered.length}
        </span>
        <div className="flex items-center gap-2 rounded-full border border-slate-200 bg-white px-3 py-1.5 w-48">
          <svg className="w-3.5 h-3.5 text-slate-400 shrink-0" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
            <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
          </svg>
          <input
            type="text"
            placeholder={label("search")}
            className="flex-1 min-w-0 text-sm bg-transparent outline-none text-slate-700 placeholder:text-slate-400"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <div className="ml-auto flex items-center gap-1.5 rounded-full border border-slate-200 px-3 py-1.5 text-sm text-slate-600 select-none">
          <svg className="w-3.5 h-3.5 text-slate-400 shrink-0" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
            <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
            <line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>
          </svg>
          {label("fiscalYear")}{yearParam ? `: ${yearParam}` : ""}
        </div>
      </div>

      {/* Table */}
      <div className="rounded-xl border border-slate-200 overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-100 bg-white">
              <th className="w-8 pl-4 py-3" />
              <th className="px-3 py-3 text-left text-xs font-semibold text-slate-500">{label("colNumber")}</th>
              <th className="px-3 py-3 text-left text-xs font-semibold text-slate-500">
                {label("colDate")} <span className="text-slate-300 font-normal">↓</span>
              </th>
              <th className="px-3 py-3 text-left text-xs font-semibold text-slate-500">{label("colDue")}</th>
              <th className="px-3 py-3 text-left text-xs font-semibold text-slate-500">{label("colCustomer")}</th>
              <th className="px-3 py-3 text-left text-xs font-semibold text-slate-500">{label("colDescription")}</th>
              <th className="px-3 py-3 text-right text-xs font-semibold text-slate-500 whitespace-nowrap">{label("colExclVat")}</th>
              <th className="w-10 pr-3 py-3" />
            </tr>
          </thead>
          <tbody>
            {filtered.length === 0 ? (
              <tr>
                <td colSpan={8} className="px-4 py-10 text-center text-sm text-slate-400">{label("noResults")}</td>
              </tr>
            ) : (
              filtered.map((inv) => (
                <tr
                  key={inv.id}
                  className="border-b border-slate-100 last:border-0 hover:bg-slate-50 cursor-pointer"
                  onClick={() => inv.state === "draft" ? editDraftInvoice(inv.id) : openInvoice(inv.id)}
                >
                  <td className="pl-4 py-3">
                    <span className={`inline-block w-2.5 h-2.5 rounded-full ${dotCls(inv)}`} />
                  </td>
                  <td className="px-3 py-3 font-medium text-slate-800 whitespace-nowrap">#{inv.invoiceNo}</td>
                  <td className="px-3 py-3 text-slate-600 whitespace-nowrap">{fmtDate(inv.entryDate)}</td>
                  <td className="px-3 py-3 text-slate-600 whitespace-nowrap">{fmtDate(inv.dueDate)}</td>
                  <td className="px-3 py-3 text-slate-700">{inv.customerName}</td>
                  <td className="px-3 py-3 text-slate-500 truncate max-w-[200px]">{inv.description}</td>
                  <td className="px-3 py-3 text-right font-medium text-slate-800 tabular-nums whitespace-nowrap">
                    {fmtAmt(inv.amount)} DKK
                  </td>
                  <td className="pr-3 py-3">
                    <button
                      className="text-slate-300 hover:text-slate-500 font-bold text-base px-1"
                      onClick={(e) => { e.stopPropagation(); }}
                      title="More actions"
                    >···</button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
});
