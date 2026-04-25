// ---------------------------------------------------------------------------
// RevenueChart — tall bar chart with grid lines and gradient bars (self-fetching)
// ---------------------------------------------------------------------------

import { useA2UIComponent } from "@a2ui/react";
import { memo, useEffect, useState } from "react";
import { BILLY_REST_BASE } from "../core/fetch-resolver";
import { fmtInsightAmt, fmtFull, insightLabel } from "./helpers";

type MonthBar = { month: string; invoiced: number; paid: number };
type MonthlyRevenueData = { fiscalYear: number; currency: string; months: MonthBar[] };

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export const RevenueChart = memo(function RevenueChartInner({ node, surfaceId }: { node: any; surfaceId: string }) {
  const { getValue } = useA2UIComponent(node, surfaceId);
  const label = (key: string) => insightLabel(getValue, key);
  const yearParam = getValue("/year") as number | string | undefined;
  const [data, setData] = useState<MonthlyRevenueData | null>(null);

  useEffect(() => {
    const qs = yearParam ? `?fiscal_year=${yearParam}` : "";
    fetch(`${BILLY_REST_BASE}/insights/monthly-revenue${qs}`)
      .then(r => r.ok ? r.json() : null)
      .then((d: MonthlyRevenueData | null) => { if (d) setData(d); })
      .catch(() => {});
  }, [yearParam]);

  const fiscalYear = data?.fiscalYear;
  const currency = data?.currency ?? "DKK";
  const months = data?.months ?? [];
  const maxVal = months.reduce((m, mo) => Math.max(m, mo.invoiced, mo.paid), 0) || 1;
  const gridLines = [1, 0.75, 0.5, 0.25];

  return (
    <div className="w-full space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-base font-semibold text-slate-900 tracking-tight">{label("chart_title")}</h2>
        <div className="flex items-center gap-4">
          <span className="flex items-center gap-1.5 text-xs text-slate-500">
            <span className="inline-block w-3 h-3 rounded-sm" style={{ background: "linear-gradient(180deg,#6366f1,#4f46e5)" }} /> {label("chart_invoiced")}
          </span>
          <span className="flex items-center gap-1.5 text-xs text-slate-500">
            <span className="inline-block w-3 h-3 rounded-sm bg-emerald-400" /> {label("chart_paid")}
          </span>
          <span className="text-xs font-medium text-slate-400 bg-slate-100 rounded-full px-2.5 py-1">{fiscalYear}</span>
        </div>
      </div>

      {/* Chart area */}
      <div className="relative">
        {/* Grid lines */}
        <div className="absolute inset-x-0 top-0 bottom-6 pointer-events-none">
          {gridLines.map((frac) => (
            <div
              key={frac}
              className="absolute left-0 right-0 border-t border-slate-100"
              style={{ bottom: `${frac * 100}%` }}
            >
              <span className="absolute -top-2 -left-1 text-[9px] text-slate-300 pr-1 leading-none">
                {fmtInsightAmt(maxVal * frac)}
              </span>
            </div>
          ))}
        </div>

        {/* Bars */}
        <div className="flex items-end gap-1 h-52 pl-6">
          {months.map((mo, i) => {
            const invH = (mo.invoiced / maxVal) * 100;
            const paidH = (mo.paid / maxVal) * 100;
            return (
              <div key={i} className="flex flex-col items-center flex-1 min-w-0">
                <div className="flex items-end gap-0.5 w-full justify-center h-44">
                  <div
                    className="flex-1 rounded-t-md transition-all"
                    style={{ height: `${invH}%`, background: "linear-gradient(180deg, #818cf8, #4f46e5)" }}
                    title={`Invoiced: ${fmtFull(mo.invoiced)} ${currency}`}
                  />
                  <div
                    className="flex-1 rounded-t-md transition-all bg-emerald-400"
                    style={{ height: `${paidH}%` }}
                    title={`Paid: ${fmtFull(mo.paid)} ${currency}`}
                  />
                </div>
                <span className="text-[10px] text-slate-400 mt-1.5 truncate w-full text-center">{mo.month}</span>
              </div>
            );
          })}
        </div>
      </div>

      <p className="text-[11px] text-slate-400 text-right">{label("chart_footer")} · {currency}</p>
    </div>
  );
});
