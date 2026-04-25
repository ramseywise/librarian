// ---------------------------------------------------------------------------
// InvoiceStatusChart — segmented bar with colored stat tiles (self-fetching)
// ---------------------------------------------------------------------------

import { useA2UIComponent } from "@a2ui/react";
import { memo, useEffect, useState } from "react";
import { BILLY_REST_BASE } from "../core/fetch-resolver";
import { fmtInsightAmt, fmtFull, insightLabel } from "./helpers";

type StatusSegment = { label: string; count: number; amount: number };
type InvoiceStatusData = { fiscalYear: number; currency: string; segments: StatusSegment[] };

const SEG_CONFIG = [
  { bar: "#94a3b8", tile: "bg-slate-100",   num: "text-slate-700",   badge: "bg-slate-200 text-slate-600"  },
  { bar: "#60a5fa", tile: "bg-blue-50",     num: "text-blue-700",    badge: "bg-blue-100 text-blue-600"    },
  { bar: "#34d399", tile: "bg-emerald-50",  num: "text-emerald-700", badge: "bg-emerald-100 text-emerald-600" },
  { bar: "#f87171", tile: "bg-rose-50",     num: "text-rose-700",    badge: "bg-rose-100 text-rose-600"    },
];

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export const InvoiceStatusChart = memo(function InvoiceStatusChartInner({ node, surfaceId }: { node: any; surfaceId: string }) {
  const { getValue } = useA2UIComponent(node, surfaceId);
  const label = (key: string) => insightLabel(getValue, key);
  const yearParam = getValue("/year") as number | string | undefined;
  const [data, setData] = useState<InvoiceStatusData | null>(null);

  useEffect(() => {
    const qs = yearParam ? `?fiscal_year=${yearParam}` : "";
    fetch(`${BILLY_REST_BASE}/insights/invoice-status${qs}`)
      .then(r => r.ok ? r.json() : null)
      .then((d: InvoiceStatusData | null) => { if (d) setData(d); })
      .catch(() => {});
  }, [yearParam]);

  const fiscalYear = data?.fiscalYear;
  const currency = data?.currency ?? "DKK";
  const segments = data?.segments ?? [];
  const total = segments.reduce((s, seg) => s + seg.amount, 0);

  return (
    <div className="w-full space-y-5">
      <div className="flex items-center justify-between">
        <h2 className="text-base font-semibold text-slate-900 tracking-tight">{label("pipe_title")}</h2>
        <span className="text-xs font-medium text-slate-400 bg-slate-100 rounded-full px-2.5 py-1">{fiscalYear}</span>
      </div>

      {/* Segmented bar */}
      <div className="flex rounded-xl overflow-hidden h-8 gap-0.5">
        {segments.map((seg, i) => {
          const pct = total > 0 ? (seg.amount / total) * 100 : 0;
          const cfg = SEG_CONFIG[i % SEG_CONFIG.length];
          return pct > 0 ? (
            <div
              key={i}
              style={{ width: `${pct}%`, background: cfg.bar }}
              title={`${seg.label}: ${fmtFull(seg.amount)} ${currency} (${pct.toFixed(1)}%)`}
              className="flex items-center justify-center transition-all"
            >
              {pct > 12 && <span className="text-white text-[10px] font-bold mix-blend-overlay">{pct.toFixed(0)}%</span>}
            </div>
          ) : null;
        })}
      </div>

      {/* Stat tiles */}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        {segments.map((seg, i) => {
          const cfg = SEG_CONFIG[i % SEG_CONFIG.length];
          const pct = total > 0 ? (seg.amount / total) * 100 : 0;
          return (
            <div key={i} className={`rounded-xl p-3.5 ${cfg.tile}`}>
              <div className={`inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-bold mb-2 ${cfg.badge}`}>
                {pct.toFixed(0)}%
              </div>
              <p className="text-[11px] font-medium text-slate-500 mb-1">{seg.label}</p>
              <p className={`text-xl font-black tabular-nums leading-none ${cfg.num}`}>{fmtInsightAmt(seg.amount)}</p>
              <p className="text-[10px] text-slate-400 mt-0.5">{seg.count} inv · {currency}</p>
            </div>
          );
        })}
      </div>
    </div>
  );
});
