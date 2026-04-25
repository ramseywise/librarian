// ---------------------------------------------------------------------------
// RevenueSummary — hero dark card + 3 accent cards (self-fetching)
// ---------------------------------------------------------------------------

import { useA2UIComponent } from "@a2ui/react";
import { memo, useEffect, useState } from "react";
import { BILLY_REST_BASE } from "../core/fetch-resolver";
import { fmtInsightAmt, fmtFull, insightLabel } from "./helpers";

type KpiCard = { label: string; amount: number; delta: number | null };
const MONTH_NAMES = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];

type RevenueSummaryData = { fiscalYear: number; month?: number; currency: string; cards: KpiCard[] };

const CARD_ACCENTS = [
  { bg: "bg-emerald-50", border: "border-emerald-200", num: "text-emerald-700", dot: "bg-emerald-500" },
  { bg: "bg-blue-50",    border: "border-blue-200",    num: "text-blue-700",    dot: "bg-blue-500"    },
  { bg: "bg-rose-50",    border: "border-rose-200",    num: "text-rose-700",    dot: "bg-rose-500"    },
];

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export const RevenueSummary = memo(function RevenueSummaryInner({ node, surfaceId }: { node: any; surfaceId: string }) {
  const { getValue } = useA2UIComponent(node, surfaceId);
  const label = (key: string) => insightLabel(getValue, key);
  const yearParam = getValue("/year") as number | string | undefined;
  const monthParam = getValue("/month") as number | undefined;
  const [data, setData] = useState<RevenueSummaryData | null>(null);

  useEffect(() => {
    const params = new URLSearchParams();
    if (yearParam) params.set("fiscal_year", String(yearParam));
    if (monthParam) params.set("month", String(monthParam));
    const qs = params.size ? `?${params}` : "";
    fetch(`${BILLY_REST_BASE}/insights/revenue-summary${qs}`)
      .then(r => r.ok ? r.json() : null)
      .then((d: RevenueSummaryData | null) => { if (d) setData(d); })
      .catch(() => {});
  }, [yearParam, monthParam]);

  const fiscalYear = data?.fiscalYear;
  // Drive the period badge from the data model (set by agent) so it shows
  // immediately and correctly even before the fetch resolves.
  const displayYear = yearParam ?? fiscalYear;
  const periodLabel = monthParam != null && displayYear != null
    ? `${MONTH_NAMES[monthParam - 1]} ${displayYear}`
    : displayYear != null ? String(displayYear) : undefined;
  const currency = data?.currency ?? "DKK";
  const cards = data?.cards ?? [];

  const [hero, ...rest] = cards;

  return (
    <div className="w-full space-y-4">
      {/* Section header */}
      <div className="flex items-center justify-between">
        <h2 className="text-base font-semibold text-slate-900 tracking-tight">{label("rev_title")}</h2>
        <span className="text-xs font-medium text-slate-400 bg-slate-100 rounded-full px-2.5 py-1">{periodLabel}</span>
      </div>

      {/* Hero card */}
      {hero && (
        <div
          className="relative rounded-2xl overflow-hidden p-6"
          style={{ background: "linear-gradient(135deg, #1e293b 0%, #0f172a 100%)" }}
        >
          {/* decorative circle */}
          <div className="absolute -top-8 -right-8 w-40 h-40 rounded-full opacity-10" style={{ background: "radial-gradient(circle, #6366f1, transparent)" }} />
          <p className="text-xs font-medium text-slate-400 uppercase tracking-widest mb-2">{hero.label}</p>
          <p className="text-5xl font-black text-white tabular-nums leading-none">
            {fmtFull(hero.amount)}
            <span className="text-lg font-normal text-slate-400 ml-2">{currency}</span>
          </p>
          {hero.delta != null && (
            <div className={`inline-flex items-center gap-1 mt-3 rounded-full px-3 py-1 text-sm font-semibold ${hero.delta >= 0 ? "bg-emerald-500/20 text-emerald-400" : "bg-rose-500/20 text-rose-400"}`}>
              {hero.delta >= 0 ? "↑" : "↓"} {Math.abs(hero.delta).toFixed(1)}% vs {monthParam != null ? `${MONTH_NAMES[monthParam - 1]} ` : ""}{Number(displayYear) - 1}
            </div>
          )}
        </div>
      )}

      {/* Accent cards */}
      <div className="grid grid-cols-3 gap-3">
        {rest.map((card, i) => {
          const a = CARD_ACCENTS[i % CARD_ACCENTS.length];
          return (
            <div key={i} className={`rounded-xl border ${a.border} ${a.bg} p-4`}>
              <div className="flex items-center gap-1.5 mb-2">
                <span className={`w-2 h-2 rounded-full ${a.dot}`} />
                <p className="text-[11px] font-semibold text-slate-500 uppercase tracking-wide leading-none">{card.label}</p>
              </div>
              <p className={`text-2xl font-black tabular-nums leading-none ${a.num}`}>
                {fmtInsightAmt(card.amount)}
              </p>
              <p className="text-[11px] text-slate-400 mt-0.5">{currency}</p>
              {card.delta != null && (
                <p className={`text-xs mt-1.5 font-medium ${card.delta >= 0 ? "text-emerald-600" : "text-rose-500"}`}>
                  {card.delta >= 0 ? "↑" : "↓"} {Math.abs(card.delta).toFixed(1)}%
                </p>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
});
