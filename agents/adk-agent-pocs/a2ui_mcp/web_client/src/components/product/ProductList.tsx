// ---------------------------------------------------------------------------
// ProductList — self-fetching product catalog with search, archive toggle,
// and table. Fires create_product and edit_product events.
// ---------------------------------------------------------------------------

import { useA2UIComponent } from "@a2ui/react";
import { memo, useCallback, useContext, useEffect, useState } from "react";
import { BILLY_REST_BASE } from "../core/fetch-resolver";
import { OnActionContext } from "../core/contexts";

const PRODUCT_LABELS_DEFAULT: Record<string, string> = {
  heading: "Products",
  newProduct: "New Product",
  toolbarLabel: "Products",
  showArchived: "Show archived",
  search: "Search...",
  colName: "Name",
  colDescription: "Description",
  colUnit: "Unit",
  colUnitPrice: "Unit price",
  noResults: "No products found.",
};

type ProductItem = {
  id: string;
  name: string;
  description: string;
  priceId: string;
  unit: string;
  unitPrice: string;
  productNo: string;
  isArchived: boolean;
};

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export const ProductList = memo(function ProductList2({ node, surfaceId }: { node: any; surfaceId: string }) {
  const onAction = useContext(OnActionContext);
  const { getValue } = useA2UIComponent(node, surfaceId);
  const label = (key: string): string => {
    const v = getValue(`/labels/${key}`);
    return typeof v === "string" && v ? v : (PRODUCT_LABELS_DEFAULT[key] ?? key);
  };
  const [products, setProducts] = useState<ProductItem[]>([]);
  const [search, setSearch] = useState("");
  const [showArchived, setShowArchived] = useState(false);

  useEffect(() => {
    fetch(`${BILLY_REST_BASE}/products?page_size=200&is_archived=${showArchived}&sort_property=name&sort_direction=ASC`)
      .then(r => r.ok ? r.json() : { products: [] })
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      .then((data: any) => {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const list: any[] = data?.products ?? [];
        setProducts(list.map((p: any) => {
          const priceEntry = p.prices?.[0];
          const price = priceEntry?.unit_price ?? 0;
          return {
            id: String(p.id ?? ""),
            name: String(p.name ?? ""),
            description: String(p.description ?? ""),
            unit: String(p.unit ?? ""),
            unitPrice: typeof price === "number" ? price.toFixed(2) : String(price),
            priceId: String(priceEntry?.id ?? ""),
            productNo: String(p.product_no ?? ""),
            isArchived: Boolean(p.is_archived),
          };
        }));
      })
      .catch(() => {});
  }, [showArchived]);

  const fireEvent = useCallback((name: string, context?: Record<string, unknown>) => {
    if (!onAction) return;
    onAction({ userAction: { name, sourceComponentId: node.id, surfaceId, context: context ?? {} } });
  }, [onAction, node.id, surfaceId]);

  const filtered = products.filter(p => {
    if (!search) return true;
    const q = search.toLowerCase();
    return p.name.toLowerCase().includes(q) || p.description.toLowerCase().includes(q);
  });

  return (
    <div className="w-full">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-slate-900">{label("heading")}</h2>
        <button
          onClick={() => fireEvent("create_product")}
          className="flex items-center gap-1.5 rounded-full bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-700 transition-colors"
        >
          <span className="text-base leading-none">⊕</span> {label("newProduct")}
        </button>
      </div>

      {/* Toolbar */}
      <div className="flex items-center gap-3 mb-3">
        <span className="text-sm font-semibold text-slate-800">{label("toolbarLabel")}</span>
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
        <label className="ml-auto flex items-center gap-2 text-sm text-slate-600 cursor-pointer select-none">
          <input
            type="checkbox"
            className="w-4 h-4 rounded border-slate-300 accent-slate-800"
            checked={showArchived}
            onChange={(e) => setShowArchived(e.target.checked)}
          />
          {label("showArchived")}
        </label>
      </div>

      {/* Table */}
      <div className="rounded-xl border border-slate-200 overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-100 bg-white">
              <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500">
                {label("colName")} <span className="text-slate-300 font-normal">↑</span>
              </th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500">{label("colDescription")}</th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500">{label("colUnit")}</th>
              <th className="px-4 py-3 text-right text-xs font-semibold text-slate-500">{label("colUnitPrice")}</th>
            </tr>
          </thead>
          <tbody>
            {filtered.length === 0 ? (
              <tr>
                <td colSpan={4} className="px-4 py-10 text-center text-sm text-slate-400">{label("noResults")}</td>
              </tr>
            ) : (
              filtered.map(p => (
                <tr
                  key={p.id}
                  className="border-b border-slate-100 last:border-0 hover:bg-slate-50 cursor-pointer"
                  onClick={() => fireEvent("edit_product", { id: p.id, name: p.name, unit: p.unit, unitPrice: p.unitPrice, priceId: p.priceId, description: p.description, productNo: p.productNo, isArchived: p.isArchived })}
                >
                  <td className="px-4 py-3 font-medium text-slate-800">{p.name}</td>
                  <td className="px-4 py-3 text-slate-500 truncate max-w-[240px]">{p.description}</td>
                  <td className="px-4 py-3 text-slate-500">{p.unit}</td>
                  <td className="px-4 py-3 text-right tabular-nums font-medium text-slate-800 whitespace-nowrap">
                    {p.unitPrice} DKK
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
