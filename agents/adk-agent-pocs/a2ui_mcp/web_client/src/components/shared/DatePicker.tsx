// ---------------------------------------------------------------------------
// DatePicker — interactive date picker with calendar popup, label-left /
// value-right row layout matching DueDatePicker.
// ---------------------------------------------------------------------------

import { useA2UIComponent } from "@a2ui/react";
import { memo, useCallback, useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";

const WEEK_DAYS = ["S", "M", "T", "W", "T", "F", "S"];
const MONTH_NAMES = ["January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December"];

function calendarDays(month: number, year: number) {
  const firstDow = new Date(year, month, 1).getDay();
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const prevMonthDays = new Date(year, month, 0).getDate();
  const cells: { day: number; current: boolean }[] = [];
  for (let i = firstDow - 1; i >= 0; i--)
    cells.push({ day: prevMonthDays - i, current: false });
  for (let d = 1; d <= daysInMonth; d++)
    cells.push({ day: d, current: true });
  while (cells.length % 7 !== 0)
    cells.push({ day: cells.length - daysInMonth - firstDow + 1, current: false });
  return cells;
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export const DatePicker = memo(function DatePicker2({ node, surfaceId }: { node: any; surfaceId: string }) {
  const { resolveString, getValue, setValue } = useA2UIComponent(node, surfaceId);
  const props = node.properties ?? {};
  const fieldLabel = resolveString(props.label) ?? resolveString(props.description) ?? "Date";
  const valuePath: string | undefined =
    (props.value as { path?: string })?.path ??
    (props.text as { path?: string })?.path;

  const today = new Date();
  const [selected, setSelected] = useState<Date>(today);
  const [viewMonth, setViewMonth] = useState(today.getMonth());
  const [viewYear, setViewYear] = useState(today.getFullYear());
  const [open, setOpen] = useState(false);
  const triggerRef = useRef<HTMLDivElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const [dropPos, setDropPos] = useState({ top: 0, left: 0 });

  // Sync initial value to data model
  useEffect(() => {
    if (valuePath && !getValue(valuePath))
      setValue(valuePath, today.toISOString().split("T")[0]);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const updatePos = useCallback(() => {
    if (triggerRef.current) {
      const r = triggerRef.current.getBoundingClientRect();
      setDropPos({ top: r.bottom + 4, left: r.left });
    }
  }, []);

  useEffect(() => {
    if (!open) return;
    window.addEventListener("scroll", updatePos, true);
    window.addEventListener("resize", updatePos);
    return () => {
      window.removeEventListener("scroll", updatePos, true);
      window.removeEventListener("resize", updatePos);
    };
  }, [open, updatePos]);

  useEffect(() => {
    if (!open) return;
    const handler = (e: MouseEvent) => {
      const t = e.target as Node;
      if (!triggerRef.current?.contains(t) && !dropdownRef.current?.contains(t)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, [open]);

  const prevMonth = useCallback(() => {
    setViewMonth((m) => { if (m === 0) { setViewYear((y) => y - 1); return 11; } return m - 1; });
  }, []);
  const nextMonth = useCallback(() => {
    setViewMonth((m) => { if (m === 11) { setViewYear((y) => y + 1); return 0; } return m + 1; });
  }, []);

  const handleDay = useCallback((day: number, current: boolean) => {
    let m = viewMonth, y = viewYear;
    if (!current) {
      if (day > 15) { m--; if (m < 0) { m = 11; y--; } }
      else { m++; if (m > 11) { m = 0; y++; } }
    }
    const d = new Date(y, m, day);
    setSelected(d);
    setViewMonth(m); setViewYear(y);
    if (valuePath) setValue(valuePath, d.toISOString().split("T")[0]);
    setOpen(false);
  }, [viewMonth, viewYear, valuePath, setValue]);

  const fmt = (d: Date) => d.toLocaleDateString("en-GB", { day: "2-digit", month: "2-digit", year: "numeric" });

  const cells = calendarDays(viewMonth, viewYear);
  const isToday = (day: number, current: boolean) =>
    current && day === today.getDate() && viewMonth === today.getMonth() && viewYear === today.getFullYear();
  const isSelected = (day: number, current: boolean) =>
    current && day === selected.getDate() && viewMonth === selected.getMonth() && viewYear === selected.getFullYear();

  const CalendarIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4 text-slate-400 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>
    </svg>
  );

  const calendar = open ? createPortal(
    <div
      ref={dropdownRef}
      style={{ position: "fixed", top: dropPos.top, left: dropPos.left, zIndex: 9999 }}
      className="w-72 rounded-xl border border-slate-200 bg-white shadow-lg p-4"
    >
      {/* Navigation */}
      <div className="flex items-center justify-between mb-3 text-sm font-medium text-slate-700">
        <button className="p-1 text-slate-400 hover:text-slate-700" onMouseDown={(e) => { e.preventDefault(); prevMonth(); }}>‹</button>
        <span>{MONTH_NAMES[viewMonth]}</span>
        <button className="p-1 text-slate-400 hover:text-slate-700" onMouseDown={(e) => { e.preventDefault(); nextMonth(); }}>›</button>
        <div className="flex items-center gap-0.5">
          <button className="p-1 text-slate-400 hover:text-slate-700" onMouseDown={(e) => { e.preventDefault(); setViewYear((y) => y - 1); }}>‹</button>
          <span>{viewYear}</span>
          <button className="p-1 text-slate-400 hover:text-slate-700" onMouseDown={(e) => { e.preventDefault(); setViewYear((y) => y + 1); }}>›</button>
        </div>
      </div>
      {/* Weekday headers */}
      <div className="grid grid-cols-7 mb-1">
        {WEEK_DAYS.map((d, i) => (
          <div key={i} className="text-center text-xs text-slate-400 font-medium py-1">{d}</div>
        ))}
      </div>
      {/* Day cells */}
      <div className="grid grid-cols-7 gap-y-0.5">
        {cells.map((cell, i) => (
          <button
            key={i}
            className={[
              "mx-auto w-8 h-8 flex items-center justify-center rounded-full text-sm",
              !cell.current ? "text-slate-300" : "text-slate-700 hover:bg-slate-100",
              isSelected(cell.day, cell.current) ? "!bg-blue-600 !text-white font-semibold hover:!bg-blue-700" : "",
              isToday(cell.day, cell.current) && !isSelected(cell.day, cell.current) ? "border border-blue-400 text-blue-600" : "",
            ].join(" ")}
            onMouseDown={(e) => { e.preventDefault(); handleDay(cell.day, cell.current); }}
          >{cell.day}</button>
        ))}
      </div>
    </div>,
    document.body
  ) : null;

  const hostStyle = node.weight !== undefined ? ({ "--weight": node.weight } as React.CSSProperties) : {};

  return (
    <div className="w-full flex items-center justify-end gap-3 py-1" style={hostStyle}>
      <span className="text-sm text-slate-500 w-20 text-right whitespace-nowrap">{fieldLabel}</span>
      <div
        ref={triggerRef}
        className="w-48 flex items-center justify-between gap-2 rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-800 cursor-pointer hover:border-blue-400 focus-within:ring-2 focus-within:ring-blue-400"
        onClick={() => { updatePos(); setOpen((o) => !o); }}
      >
        <span>{fmt(selected)}</span>
        <CalendarIcon />
      </div>
      {calendar}
    </div>
  );
});
