// ---------------------------------------------------------------------------
// LineItemEditor — self-contained line item table registered as a custom
// component. The agent emits { "component": "LineItemEditor" } in the
// updateComponents array. It reads /productOptions from the data model,
// manages rows in local state, and writes /form/lineItems back on every change
// so the submit button context can read the current rows.
// ---------------------------------------------------------------------------

import { useA2UIComponent } from "@a2ui/react";
import { memo, useCallback, useContext, useEffect, useRef, useState, type ChangeEvent } from "react";
import { createPortal } from "react-dom";
import { OnActionContext } from "../core/contexts";

type LineRow = {
  productId: string;
  description: string;
  quantity: string;
  unitPrice: string;
  productName: string;
};

const VAT_RATE = 0.25;

function calcRowTotal(row: LineRow): number {
  const qty = parseFloat(row.quantity) || 0;
  const price = parseFloat(row.unitPrice) || 0;
  return qty * price;
}

function fmtDKK(amount: number): string {
  return amount.toLocaleString("da-DK", { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + " DKK";
}

// Inline combobox for selecting / creating a product inside a line item row.
function ProductCombobox({
  value, productOptions, surfaceId, nodeId, onChange,
}: {
  value: string;
  productOptions: Array<{ label: string; value: string; unitPrice?: string }>;
  surfaceId: string;
  nodeId: string;
  onChange: (productId: string) => void;
}) {
  const onAction = useContext(OnActionContext);
  const inputRef = useRef<HTMLInputElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [dropPos, setDropPos] = useState({ top: 0, left: 0, width: 0 });

  const currentLabel = productOptions.find((p) => p.value === value)?.label ?? "";

  const updatePos = useCallback(() => {
    if (inputRef.current) {
      const r = inputRef.current.getBoundingClientRect();
      setDropPos({ top: r.bottom + 2, left: r.left, width: r.width });
    }
  }, []);

  const openDropdown = useCallback(() => { updatePos(); setOpen(true); setQuery(""); }, [updatePos]);

  useEffect(() => {
    if (!open) return;
    window.addEventListener("scroll", updatePos, true);
    window.addEventListener("resize", updatePos);
    return () => { window.removeEventListener("scroll", updatePos, true); window.removeEventListener("resize", updatePos); };
  }, [open, updatePos]);

  useEffect(() => {
    if (!open) return;
    const handler = (e: MouseEvent) => {
      if (!inputRef.current?.contains(e.target as Node) && !dropdownRef.current?.contains(e.target as Node)) {
        setOpen(false); setQuery("");
      }
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, [open]);

  const filtered = query ? productOptions.filter((p) => p.label.toLowerCase().includes(query.toLowerCase())) : productOptions;
  const exactMatch = productOptions.some((p) => p.label.toLowerCase() === query.toLowerCase());

  const handleSelect = useCallback((id: string) => { onChange(id); setOpen(false); setQuery(""); }, [onChange]);

  const handleCreate = useCallback(() => {
    if (onAction && query) {
      onAction({ userAction: { name: "create_product", sourceComponentId: nodeId, surfaceId, context: { name: query } } });
    }
    setOpen(false); setQuery("");
  }, [onAction, query, nodeId, surfaceId]);

  const inputCls = "w-full rounded border border-slate-200 bg-slate-50 px-2 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-blue-400 focus:bg-white";

  const dropdown = open ? createPortal(
    <div ref={dropdownRef} style={{ position: "fixed", top: dropPos.top, left: dropPos.left, width: dropPos.width, zIndex: 9999 }}
      className="max-h-52 overflow-y-auto rounded-lg border border-slate-200 bg-white shadow-lg">
      {filtered.length === 0 && <div className="px-3 py-2 text-sm text-slate-400">No products found.</div>}
      {filtered.map((p) => (
        <div key={p.value} className="px-3 py-2 text-sm cursor-pointer hover:bg-slate-100"
          onMouseDown={(e) => { e.preventDefault(); handleSelect(p.value); }}>{p.label}</div>
      ))}
      {query && !exactMatch && (
        <>
          <div className="border-t border-slate-100" />
          <div className="px-3 py-2 text-sm cursor-pointer hover:bg-slate-50 text-slate-600 flex items-center gap-2"
            onMouseDown={(e) => { e.preventDefault(); handleCreate(); }}>
            <span className="text-slate-400 text-base leading-none">⊕</span> Create &quot;{query}&quot;
          </div>
        </>
      )}
    </div>, document.body
  ) : null;

  return (
    <div className="relative w-full">
      <input ref={inputRef} type="text" autoComplete="off" placeholder="Select item"
        className={inputCls + " pr-6"}
        value={open ? query : currentLabel}
        onChange={(e) => { setQuery(e.target.value); if (!open) openDropdown(); }}
        onFocus={openDropdown}
      />
      <span className="pointer-events-none absolute right-2 top-1/2 -translate-y-1/2 text-slate-400 text-xs">▾</span>
      {dropdown}
    </div>
  );
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export const LineItemEditor = memo(function LineItemEditor2({ node, surfaceId }: { node: any; surfaceId: string }) {
  const { getValue, setValue } = useA2UIComponent(node, surfaceId);

  // Resolve product options from data model (same JSON-string trick as ChoicePicker)
  const resolvedRaw = getValue("/productOptions");
  const productOptions: Array<{ label: string; value: string; unitPrice?: string }> =
    (() => {
      if (Array.isArray(resolvedRaw)) return resolvedRaw;
      if (typeof resolvedRaw === "string") {
        try { return JSON.parse(resolvedRaw); } catch { return []; }
      }
      return [];
    })();

  const productMap = new Map(productOptions.map((p) => [p.value, p]));

  const [rows, setRows] = useState<LineRow[]>(() => {
    // Seed from pre-populated /form/lineItems when editing an existing invoice.
    const raw = getValue("/form/lineItems");
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const items: any[] = (() => {
      if (Array.isArray(raw) && raw.length > 0) return raw;
      if (typeof raw === "string") {
        try { const p = JSON.parse(raw); if (Array.isArray(p) && p.length > 0) return p; } catch {}
      }
      return [];
    })();
    if (items.length === 0) return [{ productId: "", description: "", quantity: "1", unitPrice: "", productName: "" }];
    return items.map((item) => ({
      productId: String(item.productId ?? ""),
      description: String(item.description ?? ""),
      quantity: String(item.quantity ?? "1"),
      unitPrice: String(item.unitPrice ?? ""),
      productName: String(item.productName ?? ""),
    }));
  });

  // Write rows back to data model so submit context binding /form/lineItems works.
  const writeBack = useCallback((updated: LineRow[]) => {
    const items = updated.map((r, i) => ({
      productId: r.productId,
      productName: r.productName,
      description: r.description,
      quantity: r.quantity,
      unitPrice: r.unitPrice,
      index: i,
    }));
    setValue("/form/lineItems", items);
  }, [setValue]);

  // Once productOptions load, resolve productNames for any pre-seeded rows that
  // have a productId but no name yet (options arrive async via $fetch).
  const namesResolvedRef = useRef(false);
  useEffect(() => {
    if (namesResolvedRef.current || productOptions.length === 0) return;
    namesResolvedRef.current = true;
    setRows((prev) => {
      const next = prev.map((r) => {
        if (!r.productId || r.productName) return r;
        const p = productMap.get(r.productId);
        return p ? { ...r, productName: p.label, unitPrice: r.unitPrice || String(p.unitPrice ?? "") } : r;
      });
      writeBack(next);
      return next;
    });
  }, [productOptions.length, productMap, writeBack]);

  // When the agent sets /form/pendingProductId (and optionally /form/pendingQuantity),
  // fill the first empty row or add a new row. Clear both pending values afterward.
  const pendingRaw = getValue("/form/pendingProductId");
  const pendingId = typeof pendingRaw === "string" ? pendingRaw : "";
  const pendingQtyRaw = getValue("/form/pendingQuantity");
  const pendingQty = typeof pendingQtyRaw === "number"
    ? String(pendingQtyRaw)
    : (typeof pendingQtyRaw === "string" && pendingQtyRaw ? pendingQtyRaw : "1");
  // Track productId:quantity so the same product re-applied with different quantity (or
  // after a clear) is not skipped.
  const appliedRef = useRef<string>("");
  useEffect(() => {
    const key = `${pendingId}:${pendingQty}`;
    if (!pendingId || appliedRef.current === key) return;
    const p = productMap.get(pendingId);
    if (!p) return;
    appliedRef.current = key;
    setRows((prev) => {
      const emptyIdx = prev.findIndex((r) => !r.productId);
      let next: LineRow[];
      const newRow: LineRow = { productId: p.value, productName: p.label, description: "", quantity: pendingQty, unitPrice: p.unitPrice ? String(p.unitPrice) : "" };
      if (emptyIdx >= 0) {
        // Fill the existing empty row
        next = prev.map((r, i) => i === emptyIdx ? { ...r, ...newRow } : r);
      } else {
        // All rows have products — append a new row
        next = [...prev, newRow];
      }
      setTimeout(() => {
        setValue("/form/pendingProductId", "");
        setValue("/form/pendingQuantity", "");
      }, 0);
      writeBack(next);
      return next;
    });
  }, [pendingId, pendingQty, productMap, setValue, writeBack]);

  const updateRow = useCallback((idx: number, field: keyof LineRow, val: string) => {
    setRows((prev) => {
      const next = prev.map((r, i) => {
        if (i !== idx) return r;
        const updated = { ...r, [field]: val };
        if (field === "productId") {
          const p = productMap.get(val);
          updated.unitPrice = p?.unitPrice ? String(p.unitPrice) : "";
          updated.productName = p?.label ?? "";
        }
        return updated;
      });
      writeBack(next);
      return next;
    });
  }, [productMap, writeBack]);

  const addRow = useCallback(() => {
    setRows((prev) => {
      const next = [...prev, { productId: "", description: "", quantity: "1", unitPrice: "", productName: "" }];
      writeBack(next);
      return next;
    });
  }, [writeBack]);

  const removeRow = useCallback((idx: number) => {
    setRows((prev) => {
      const next = prev.filter((_, i) => i !== idx);
      writeBack(next);
      return next;
    });
  }, [writeBack]);

  const totalExclVAT = rows.reduce((sum, r) => sum + calcRowTotal(r), 0);
  const vat = totalExclVAT * VAT_RATE;
  const totalInclVAT = totalExclVAT + vat;

  const inputCls = "w-full rounded border border-slate-200 bg-slate-50 px-2 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-blue-400 focus:bg-white";

  return (
    <div className="w-full mt-4">
      {/* Column headers */}
      <div className="grid grid-cols-[2fr_2fr_80px_100px_90px_28px] gap-2 px-1 pb-1 text-xs font-semibold text-slate-500 border-b border-slate-200">
        <span>Item</span>
        <span>Description</span>
        <span className="text-right">Quantity</span>
        <span className="text-right">Unit price</span>
        <span className="text-right">Total</span>
        <span />
      </div>

      {/* Rows */}
      {rows.map((row, idx) => (
        <div key={idx} className="grid grid-cols-[2fr_2fr_80px_100px_90px_28px] gap-2 items-center py-2 border-b border-slate-100">
          <ProductCombobox
            value={row.productId}
            productOptions={productOptions}
            surfaceId={surfaceId}
            nodeId={node.id}
            onChange={(productId) => updateRow(idx, "productId", productId)}
          />
          <input
            type="text"
            placeholder="Optional description"
            className={inputCls}
            value={row.description}
            onChange={(e: ChangeEvent<HTMLInputElement>) => updateRow(idx, "description", e.target.value)}
          />
          <input
            type="number"
            min={1}
            className={inputCls + " text-right"}
            value={row.quantity}
            onChange={(e: ChangeEvent<HTMLInputElement>) => updateRow(idx, "quantity", e.target.value)}
          />
          <input
            type="text"
            placeholder="Unit price"
            className={inputCls + " text-right"}
            value={row.unitPrice}
            onChange={(e: ChangeEvent<HTMLInputElement>) => updateRow(idx, "unitPrice", e.target.value)}
          />
          <span className="text-sm text-slate-700 text-right pr-1 tabular-nums">
            {calcRowTotal(row) > 0 ? fmtDKK(calcRowTotal(row)) : "0.00 DKK"}
          </span>
          <button
            onClick={() => removeRow(idx)}
            className="text-slate-300 hover:text-red-400 text-base leading-none flex items-center justify-center"
            title="Remove"
          >✕</button>
        </div>
      ))}

      {/* Add line */}
      <button
        onClick={addRow}
        className="mt-3 flex items-center gap-1.5 text-sm text-blue-600 hover:text-blue-800 font-medium"
      >
        <span className="text-base leading-none">⊕</span> Add line
      </button>

      {/* Totals */}
      <div className="mt-4 pt-4 border-t border-slate-200 flex justify-end">
        <div className="w-64 space-y-1 text-sm">
          <div className="flex justify-between text-slate-500">
            <span>Total excluding VAT</span>
            <span className="tabular-nums">{fmtDKK(totalExclVAT)}</span>
          </div>
          <div className="flex justify-between text-slate-500">
            <span>VAT (25%)</span>
            <span className="tabular-nums">{fmtDKK(vat)}</span>
          </div>
          <div className="flex justify-between font-semibold text-slate-800 border-t border-slate-200 pt-1 mt-1">
            <span>Total including VAT</span>
            <span className="tabular-nums">{fmtDKK(totalInclVAT)}</span>
          </div>
        </div>
      </div>
    </div>
  );
});
