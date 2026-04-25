// ---------------------------------------------------------------------------
// ProductRevenueTable — medal ranks + gradient bars (self-fetching)
// ---------------------------------------------------------------------------

import { useA2UIComponent } from "@a2ui/react";
import { memo, useEffect, useState } from "react";
import { BILLY_REST_BASE } from "../core/fetch-resolver";
import { fmtInsightAmt, insightLabel, RANK_MEDALS } from "./helpers";

type ProductRankRow = { rank: number; name: string; quantitySold: number; revenue: number };
type ProductRevenueData = { currency: string; rows: ProductRankRow[] };

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export const ProductRevenueTable = memo(function ProductRevenueTableInner({ node, surfaceId }: { node: any; surfaceId: string }) {
  const { getValue } = useA2UIComponent(node, surfaceId);
  const label = (key: string) => insightLabel(getValue, key);
  const yearParam = getValue("/year") as number | string | undefined;
  const [data, setData] = useState<ProductRevenueData | null>(null);

  useEffect(() => {
    const qs = yearParam ? `?fiscal_year=${yearParam}` : "";
    fetch(`${BILLY_REST_BASE}/insights/product-revenue${qs}`)
      .then(r => r.ok ? r.json() : null)
      .then((d: ProductRevenueData | null) => { if (d) setData(d); })
      .catch(() => {});
  }, [yearParam]);

  const currency = data?.currency ?? "DKK";
  const rows = data?.rows ?? [];
  const maxRevenue = rows.reduce((m, r) => Math.max(m, r.revenue), 0) || 1;

  return (
    <div className="w-full space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-base font-semibold text-slate-900 tracking-tight">{label("prod_title")}</h2>
        <span className="text-xs text-slate-400">{currency} · {label("prod_excl_vat")}</span>
      </div>

      <div className="flex flex-col gap-3">
        {rows.map((row) => {
          const barPct = (row.revenue / maxRevenue) * 100;
          const isTop3 = row.rank <= 3;
          return (
            <div key={row.rank} className={`relative rounded-xl p-4 overflow-hidden ${isTop3 ? "bg-gradient-to-r from-slate-50 to-white border border-slate-200 shadow-sm" : "bg-white border border-slate-100"}`}>
              {/* Background bar fill */}
              <div
                className="absolute inset-y-0 left-0 rounded-xl opacity-[0.06] pointer-events-none"
                style={{ width: `${barPct}%`, background: "linear-gradient(90deg, #6366f1, #8b5cf6)" }}
              />
              <div className="relative flex items-center gap-3">
                {/* Rank */}
                <div className="w-8 h-8 shrink-0 flex items-center justify-center">
                  {row.rank <= 3 ? (
                    <span className="text-xl leading-none">{RANK_MEDALS[row.rank]}</span>
                  ) : (
                    <span className="text-sm font-bold text-slate-300">#{row.rank}</span>
                  )}
                </div>
                {/* Name + bar */}
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-semibold text-slate-800 truncate mb-1.5">{row.name}</p>
                  <div className="h-2 rounded-full bg-slate-100 overflow-hidden">
                    <div
                      className="h-full rounded-full transition-all"
                      style={{ width: `${barPct}%`, background: "linear-gradient(90deg, #6366f1, #a78bfa)" }}
                    />
                  </div>
                </div>
                {/* Stats */}
                <div className="shrink-0 text-right">
                  <p className="text-base font-black tabular-nums text-slate-800 leading-tight">
                    {fmtInsightAmt(row.revenue)}
                  </p>
                  <p className="text-[10px] text-slate-400">
                    {label("prod_qty")} {row.quantitySold % 1 === 0 ? row.quantitySold : row.quantitySold.toFixed(1)}
                  </p>
                </div>
              </div>
            </div>
          );
        })}
        {rows.length === 0 && (
          <p className="py-6 text-center text-sm text-slate-400">{label("prod_nodata")}</p>
        )}
      </div>
    </div>
  );
});
