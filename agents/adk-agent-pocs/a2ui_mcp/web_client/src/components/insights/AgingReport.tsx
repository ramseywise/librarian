// ---------------------------------------------------------------------------
// AgingReport — heat strip summary + collapsible buckets (self-fetching)
// ---------------------------------------------------------------------------

import { useA2UIComponent } from "@a2ui/react";
import { memo, useEffect, useState } from "react";
import { BILLY_REST_BASE } from "../core/fetch-resolver";
import { fmtInsightAmt, fmtFull, insightLabel } from "./helpers";

type AgingInvoice = { invoiceNo: string; customer: string; dueDate: string; amount: number; daysOverdue: number };
type AgingBucket = { label: string; totalAmount: number; invoices: AgingInvoice[] };
type AgingReportData = { currency: string; asOf: string; buckets: AgingBucket[] };

const AGING_CFG: Record<string, { strip: string; header: string; row: string; badge: string }> = {
  "Current":    { strip: "bg-blue-400",   header: "bg-blue-50 border-blue-200 text-blue-800",   row: "bg-blue-50/60",   badge: "bg-blue-100 text-blue-700" },
  "1–30 days":  { strip: "bg-amber-400",  header: "bg-amber-50 border-amber-200 text-amber-800", row: "bg-amber-50/60",  badge: "bg-amber-100 text-amber-700" },
  "31–60 days": { strip: "bg-orange-500", header: "bg-orange-50 border-orange-200 text-orange-800", row: "bg-orange-50/60", badge: "bg-orange-100 text-orange-700" },
  "61–90 days": { strip: "bg-red-500",    header: "bg-red-50 border-red-200 text-red-800",       row: "bg-red-50/60",    badge: "bg-red-100 text-red-700" },
  "90+ days":   { strip: "bg-red-700",    header: "bg-red-100 border-red-300 text-red-900",      row: "bg-red-100/60",   badge: "bg-red-200 text-red-800" },
};
const AGING_DEFAULT = { strip: "bg-slate-400", header: "bg-slate-50 border-slate-200 text-slate-700", row: "bg-slate-50", badge: "bg-slate-100 text-slate-600" };

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export const AgingReport = memo(function AgingReportInner({ node, surfaceId }: { node: any; surfaceId: string }) {
  const { getValue } = useA2UIComponent(node, surfaceId);
  const label = (key: string) => insightLabel(getValue, key);
  const contactId   = getValue("/contactId")   as string | undefined;
  const contactName = getValue("/contactName") as string | undefined;
  const [data, setData] = useState<AgingReportData | null>(null);
  const [open, setOpen] = useState<Record<string, boolean>>({});

  useEffect(() => {
    const qs = new URLSearchParams();
    if (contactId)   qs.set("contact_id",   contactId);
    if (contactName) qs.set("contact_name", contactName);
    const q = qs.toString() ? `?${qs}` : "";
    fetch(`${BILLY_REST_BASE}/insights/aging-report${q}`)
      .then(r => r.ok ? r.json() : null)
      .then((d: AgingReportData | null) => {
        if (d) {
          setData(d);
          setOpen(Object.fromEntries(d.buckets.map(b => [b.label, b.totalAmount > 0])));
        }
      })
      .catch(() => {});
  }, [contactId, contactName]);

  const toggle = (lbl: string) => setOpen(prev => ({ ...prev, [lbl]: !prev[lbl] }));

  const currency = data?.currency ?? "DKK";
  const asOf = data?.asOf ?? "";
  const buckets = data?.buckets ?? [];
  const totalOverdue = buckets.filter(b => b.label !== "Current").reduce((s, b) => s + b.totalAmount, 0);
  const totalAll = buckets.reduce((s, b) => s + b.totalAmount, 0);

  return (
    <div className="w-full space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-base font-semibold text-slate-900 tracking-tight">{label("aging_title")}</h2>
          {asOf && <p className="text-[11px] text-slate-400 mt-0.5">{label("aging_as_of")} {asOf}</p>}
        </div>
        {totalOverdue > 0 && (
          <div className="text-right">
            <p className="text-[11px] text-slate-400">{label("aging_overdue_label")}</p>
            <p className="text-xl font-black text-rose-600 tabular-nums leading-tight">
              {fmtInsightAmt(totalOverdue)}
              <span className="text-xs font-normal text-slate-400 ml-1">{currency}</span>
            </p>
          </div>
        )}
      </div>

      {/* Heat strip */}
      {totalAll > 0 && (
        <div className="flex rounded-lg overflow-hidden h-3 gap-px">
          {buckets.map((b) => {
            const cfg = AGING_CFG[b.label] ?? AGING_DEFAULT;
            const pct = (b.totalAmount / totalAll) * 100;
            return pct > 0 ? <div key={b.label} className={`${cfg.strip} transition-all`} style={{ width: `${pct}%` }} title={`${b.label}: ${fmtFull(b.totalAmount)} ${currency}`} /> : null;
          })}
        </div>
      )}

      {/* Buckets */}
      <div className="flex flex-col gap-2">
        {buckets.map((bucket) => {
          const cfg = AGING_CFG[bucket.label] ?? AGING_DEFAULT;
          const isOpen = open[bucket.label] ?? bucket.totalAmount > 0;
          return (
            <div key={bucket.label} className={`rounded-xl border overflow-hidden ${cfg.header}`}>
              <button
                className="w-full flex items-center gap-3 px-4 py-3 text-left"
                onClick={() => toggle(bucket.label)}
              >
                <span className={`w-2.5 h-2.5 rounded-full shrink-0 ${cfg.strip}`} />
                <span className="font-semibold text-sm flex-1">{bucket.label}</span>
                <span className="text-sm font-black tabular-nums">{fmtInsightAmt(bucket.totalAmount)}</span>
                <span className="text-xs opacity-50 w-14 text-right">{bucket.invoices.length} {label("aging_inv")}</span>
                <svg className={`w-4 h-4 opacity-40 transition-transform shrink-0 ${isOpen ? "rotate-180" : ""}`} fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                  <path d="m6 9 6 6 6-6"/>
                </svg>
              </button>
              {isOpen && bucket.invoices.length > 0 && (
                <div className="border-t border-current/10">
                  <table className="w-full text-xs">
                    <thead>
                      <tr className="opacity-60 text-[11px]">
                        <th className="pl-4 py-2 text-left font-semibold">{label("aging_col_invoice")}</th>
                        <th className="px-3 py-2 text-left font-semibold">{label("aging_col_customer")}</th>
                        <th className="px-3 py-2 text-left font-semibold">{label("aging_col_due")}</th>
                        <th className="pr-4 py-2 text-right font-semibold">{label("aging_col_amount")}</th>
                      </tr>
                    </thead>
                    <tbody>
                      {bucket.invoices.map((inv, i) => (
                        <tr key={i} className={`border-t border-current/10 ${cfg.row}`}>
                          <td className="pl-4 py-2.5 font-mono font-semibold">{inv.invoiceNo}</td>
                          <td className="px-3 py-2.5 font-medium">{inv.customer}</td>
                          <td className="px-3 py-2.5">
                            {inv.dueDate}
                            {inv.daysOverdue > 0 && (
                              <span className={`ml-1.5 inline-block text-[10px] font-bold rounded px-1 ${cfg.badge}`}>{inv.daysOverdue}d</span>
                            )}
                          </td>
                          <td className="pr-4 py-2.5 text-right tabular-nums font-bold">
                            {fmtFull(inv.amount)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          );
        })}
        {buckets.length === 0 && (
          <div className="flex flex-col items-center py-8 text-slate-400">
            <svg className="w-8 h-8 mb-2 opacity-30" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24"><path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
            <p className="text-sm font-medium">{label("aging_empty")}</p>
          </div>
        )}
      </div>
    </div>
  );
});
