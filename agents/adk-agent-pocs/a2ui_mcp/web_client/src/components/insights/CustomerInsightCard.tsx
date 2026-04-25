// ---------------------------------------------------------------------------
// CustomerInsightCard — single-customer KPI + open invoices (self-fetching)
// ---------------------------------------------------------------------------

import { useA2UIComponent } from "@a2ui/react";
import { memo, useEffect, useState } from "react";
import { BILLY_REST_BASE } from "../core/fetch-resolver";
import { fmtInsightAmt, insightLabel } from "./helpers";

type OpenInvoice = { invoiceNo: string; date: string; dueDate: string; amount: number; balance: number };
type CustomerSummaryData = {
  currency: string; fiscalYear: number; contactId: string; customerName: string;
  invoiced: number; paid: number; outstanding: number; overdue: number;
  invoiceCount: number; lastInvoiceDate: string; openInvoices: OpenInvoice[];
};

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export const CustomerInsightCard = memo(function CustomerInsightCardInner({ node, surfaceId }: { node: any; surfaceId: string }) {
  const { getValue } = useA2UIComponent(node, surfaceId);
  const label = (key: string) => insightLabel(getValue, key);
  const contactId   = getValue("/contactId")   as string | undefined;
  const contactName = getValue("/contactName") as string | undefined;
  const yearParam   = getValue("/year")        as number | string | undefined;
  const [data, setData] = useState<CustomerSummaryData | null>(null);

  useEffect(() => {
    const qs = new URLSearchParams();
    if (contactId)   qs.set("contact_id",   contactId);
    if (contactName) qs.set("contact_name", contactName);
    if (yearParam)   qs.set("fiscal_year",  String(yearParam));
    const q = qs.toString() ? `?${qs}` : "";
    fetch(`${BILLY_REST_BASE}/insights/customer-summary${q}`)
      .then(r => r.ok ? r.json() : null)
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      .then((d: CustomerSummaryData | null) => { if (d && !("error" in (d as any))) setData(d); })
      .catch(() => {});
  }, [contactId, contactName, yearParam]);

  if (!data) return <p className="py-6 text-center text-sm text-slate-400">{label("cust_loading")}</p>;

  const currency = data.currency;
  const kpis = [
    { label: label("cust_kpi_invoiced"),    value: data.invoiced,    color: "text-slate-800" },
    { label: label("cust_kpi_collected"),   value: data.paid,        color: "text-emerald-600" },
    { label: label("cust_kpi_outstanding"), value: data.outstanding, color: "text-indigo-600" },
    { label: label("cust_kpi_overdue"),     value: data.overdue,     color: data.overdue > 0 ? "text-red-600" : "text-slate-400" },
  ];

  return (
    <div className="w-full space-y-5">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-base font-semibold text-slate-900">{data.customerName}</h2>
          <p className="text-xs text-slate-400 mt-0.5">
            {data.invoiceCount} invoice{data.invoiceCount !== 1 ? "s" : ""} · {data.fiscalYear}
            {data.lastInvoiceDate && ` · Last: ${data.lastInvoiceDate}`}
          </p>
        </div>
        <span className="text-xs font-medium text-slate-500 bg-slate-100 rounded-full px-2.5 py-1">{currency}</span>
      </div>

      {/* KPI row */}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        {kpis.map(k => (
          <div key={k.label} className="bg-slate-50 rounded-xl p-3 border border-slate-100">
            <p className="text-[11px] text-slate-400 uppercase tracking-wide mb-1">{k.label}</p>
            <p className={`text-lg font-bold tabular-nums ${k.color}`}>{fmtInsightAmt(k.value)}</p>
          </div>
        ))}
      </div>

      {/* Open invoices */}
      {data.openInvoices.length > 0 && (
        <div>
          <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">{label("cust_open_invoices")}</h3>
          <div className="flex flex-col divide-y divide-slate-100 rounded-xl border border-slate-100 overflow-hidden">
            {data.openInvoices.map(inv => {
              const overdueDays = inv.dueDate
                ? Math.max(0, Math.floor((Date.now() - new Date(inv.dueDate).getTime()) / 86_400_000))
                : 0;
              const isOverdue = overdueDays > 0;
              return (
                <div key={inv.invoiceNo} className="flex items-center justify-between px-3 py-2.5 bg-white text-sm">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs text-slate-500">{inv.invoiceNo}</span>
                    {isOverdue && (
                      <span className="text-[10px] font-semibold bg-red-100 text-red-600 rounded px-1.5 py-0.5">
                        {overdueDays}d {label("cust_overdue")}
                      </span>
                    )}
                  </div>
                  <div className="text-right">
                    <span className="font-semibold text-slate-800">{fmtInsightAmt(inv.balance)}</span>
                    <span className="text-xs text-slate-400 ml-1">{currency}</span>
                    {inv.dueDate && <p className="text-[10px] text-slate-400">due {inv.dueDate}</p>}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
      {data.openInvoices.length === 0 && data.outstanding === 0 && (
        <p className="text-sm text-emerald-600 font-medium text-center py-2">{label("cust_all_paid")}</p>
      )}
    </div>
  );
});
