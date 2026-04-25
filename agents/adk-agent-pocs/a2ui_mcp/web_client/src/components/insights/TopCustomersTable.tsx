// ---------------------------------------------------------------------------
// TopCustomersTable — avatar initials + revenue progress bars (self-fetching)
// ---------------------------------------------------------------------------

import { useA2UIComponent } from "@a2ui/react";
import { memo, useEffect, useState } from "react";
import { BILLY_REST_BASE } from "../core/fetch-resolver";
import { fmtInsightAmt, insightLabel, RANK_MEDALS, AVATAR_COLORS } from "./helpers";

type CustomerRankRow = { rank: number; name: string; invoiced: number; paid: number; outstanding: number };
type TopCustomersData = { currency: string; rows: CustomerRankRow[] };

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export const TopCustomersTable = memo(function TopCustomersTableInner({ node, surfaceId }: { node: any; surfaceId: string }) {
  const { getValue } = useA2UIComponent(node, surfaceId);
  const label = (key: string) => insightLabel(getValue, key);
  const yearParam = getValue("/year") as number | string | undefined;
  const [data, setData] = useState<TopCustomersData | null>(null);

  useEffect(() => {
    const qs = yearParam ? `?fiscal_year=${yearParam}` : "";
    fetch(`${BILLY_REST_BASE}/insights/top-customers${qs}`)
      .then(r => r.ok ? r.json() : null)
      .then((d: TopCustomersData | null) => { if (d) setData(d); })
      .catch(() => {});
  }, [yearParam]);

  const currency = data?.currency ?? "DKK";
  const rows = data?.rows ?? [];
  const maxInvoiced = rows.reduce((m, r) => Math.max(m, r.invoiced), 0) || 1;

  return (
    <div className="w-full space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-base font-semibold text-slate-900 tracking-tight">{label("top_title")}</h2>
        <span className="text-xs text-slate-400">{label("top_subtitle")} · {currency}</span>
      </div>

      <div className="flex flex-col divide-y divide-slate-100">
        {rows.map((row, i) => {
          const initials = row.name.split(/\s+/).slice(0, 2).map(w => w[0]?.toUpperCase() ?? "").join("");
          const avatarCls = AVATAR_COLORS[i % AVATAR_COLORS.length];
          const barPct = (row.invoiced / maxInvoiced) * 100;
          const paidPct = row.invoiced > 0 ? (row.paid / row.invoiced) * 100 : 0;
          return (
            <div key={row.rank} className="flex items-center gap-3 py-3 group">
              {/* Avatar */}
              <div className={`w-9 h-9 rounded-full flex items-center justify-center text-xs font-bold shrink-0 ${avatarCls}`}>
                {initials || "?"}
              </div>
              {/* Name + bar */}
              <div className="flex-1 min-w-0">
                <div className="flex items-baseline justify-between mb-1">
                  <span className="text-sm font-semibold text-slate-800 truncate">
                    {RANK_MEDALS[row.rank] ?? ""} {row.name}
                  </span>
                  <span className="text-sm font-bold tabular-nums text-slate-700 ml-2 shrink-0">
                    {fmtInsightAmt(row.invoiced)}
                    <span className="text-xs font-normal text-slate-400 ml-1">{currency}</span>
                  </span>
                </div>
                {/* Stacked bar: paid portion + remaining */}
                <div className="h-2 rounded-full bg-slate-100 overflow-hidden">
                  <div className="h-full flex">
                    <div className="bg-emerald-400 rounded-full transition-all" style={{ width: `${barPct * paidPct / 100}%` }} />
                    <div className="bg-indigo-300 rounded-full transition-all" style={{ width: `${barPct * (1 - paidPct / 100)}%` }} />
                  </div>
                </div>
              </div>
              {/* Outstanding badge */}
              <div className="shrink-0 text-right w-20">
                {row.outstanding > 0 ? (
                  <span className="inline-block bg-amber-100 text-amber-700 rounded-lg px-2 py-1 text-xs font-bold">
                    {fmtInsightAmt(row.outstanding)}
                  </span>
                ) : (
                  <span className="text-xs text-emerald-500 font-medium">{label("top_paid")}</span>
                )}
              </div>
            </div>
          );
        })}
        {rows.length === 0 && (
          <p className="py-6 text-center text-sm text-slate-400">{label("top_nodata")}</p>
        )}
      </div>

      {/* Legend */}
      <div className="flex items-center gap-4 text-[11px] text-slate-400 pt-1">
        <span className="flex items-center gap-1"><span className="inline-block w-2.5 h-2.5 rounded-sm bg-emerald-400" /> {label("top_leg_paid")}</span>
        <span className="flex items-center gap-1"><span className="inline-block w-2.5 h-2.5 rounded-sm bg-indigo-300" /> {label("top_leg_invoiced")}</span>
        <span className="flex items-center gap-1"><span className="inline-block w-2.5 h-2.5 rounded-sm bg-amber-100 border border-amber-300" /> {label("top_leg_outstanding")}</span>
      </div>
    </div>
  );
});
