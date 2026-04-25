// ---------------------------------------------------------------------------
// CustomerList — self-fetching customer/client list with search, archive
// toggle, and table. Registered as a custom component; the agent emits only
// the surface structure — no data model values needed.
// ---------------------------------------------------------------------------

import { useA2UIComponent } from "@a2ui/react";
import { memo, useCallback, useContext, useEffect, useState } from "react";
import { BILLY_REST_BASE } from "../core/fetch-resolver";
import { OnActionContext } from "../core/contexts";

type CustomerItem = {
  id: string;
  name: string;
  type: string;
  email: string;
  phone: string;
  country: string;
  street: string;
  city: string;
  zipcode: string;
  registrationNo: string;
  createdTime: string;
};

const COUNTRY_NAMES: Record<string, string> = {
  DK: "Denmark", SE: "Sweden", NO: "Norway", DE: "Germany",
  GB: "United Kingdom", US: "United States", FI: "Finland", NL: "Netherlands",
  FR: "France", IT: "Italy", ES: "Spain", PL: "Poland",
};

const CUSTOMER_LABELS_DEFAULT: Record<string, string> = {
  heading:      "Clients",
  createContact: "Create contact",
  toolbarLabel: "Clients",
  showArchived: "Show archived",
  search:       "Search...",
  colName:      "Name",
  colEmail:     "Email",
  colPhone:     "Phone number",
  colCountry:   "Country",
  colCreated:   "Created date",
  noResults:    "No clients found.",
};

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export const CustomerList = memo(function CustomerList2({ node, surfaceId }: { node: any; surfaceId: string }) {
  const onAction = useContext(OnActionContext);
  const { getValue } = useA2UIComponent(node, surfaceId);
  const label = (key: string): string => {
    const v = getValue(`/labels/${key}`);
    return typeof v === "string" && v ? v : (CUSTOMER_LABELS_DEFAULT[key] ?? key);
  };
  const [customers, setCustomers] = useState<CustomerItem[]>([]);
  const initialSearch = (getValue("/search") as string | undefined) ?? "";
  const [search, setSearch] = useState(initialSearch);
  const [showArchived, setShowArchived] = useState(false);

  useEffect(() => {
    fetch(`${BILLY_REST_BASE}/customers?page_size=200&is_archived=${showArchived}&sort_property=name&sort_direction=ASC`)
      .then(r => r.ok ? r.json() : { customers: [] })
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      .then((data: any) => {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const list: any[] = data?.customers ?? [];
        setCustomers(list.map((c: any) => ({
          id: String(c.id ?? ""),
          name: String(c.name ?? ""),
          type: String(c.type ?? "company"),
          email: String(c.email ?? ""),
          phone: String(c.phone ?? ""),
          country: String(c.country ?? ""),
          street: String(c.street ?? ""),
          city: String(c.city ?? ""),
          zipcode: String(c.zipcode ?? ""),
          registrationNo: String(c.registration_no ?? ""),
          createdTime: String(c.created_time ?? ""),
        })));
      })
      .catch(() => {});
  }, [showArchived]);

  const fireEvent = useCallback((name: string, context?: Record<string, unknown>) => {
    if (!onAction) return;
    onAction({ userAction: { name, sourceComponentId: node.id, surfaceId, context: context ?? {} } });
  }, [onAction, node.id, surfaceId]);

  const filtered = customers.filter(c => {
    if (!search) return true;
    const q = search.toLowerCase();
    return c.name.toLowerCase().includes(q) ||
           c.email.toLowerCase().includes(q) ||
           c.phone.includes(q);
  });

  const fmtDate = (iso: string) => {
    if (!iso || iso === "undefined") return "";
    const d = new Date(iso);
    if (isNaN(d.getTime())) return "";
    const m = String(d.getMonth() + 1).padStart(2, "0");
    const dd = String(d.getDate()).padStart(2, "0");
    return `${m}/${dd}/${d.getFullYear()}`;
  };

  return (
    <div className="w-full">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-slate-900">{label("heading")}</h2>
        <button
          onClick={() => fireEvent("create_customer")}
          className="flex items-center gap-1.5 rounded-full bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-700 transition-colors"
        >
          <span className="text-base leading-none">⊕</span> {label("createContact")}
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
              <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500">{label("colEmail")}</th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500">{label("colPhone")}</th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500">{label("colCountry")}</th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500">{label("colCreated")}</th>
            </tr>
          </thead>
          <tbody>
            {filtered.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-4 py-10 text-center text-sm text-slate-400">{label("noResults")}</td>
              </tr>
            ) : (
              filtered.map(c => (
                <tr
                  key={c.id}
                  className="border-b border-slate-100 last:border-0 hover:bg-slate-50 cursor-pointer"
                  onClick={() => fireEvent("edit_customer", { id: c.id, name: c.name, type: c.type, country: c.country, email: c.email, phone: c.phone, street: c.street, city: c.city, zipcode: c.zipcode, registrationNo: c.registrationNo })}
                >
                  <td className="px-4 py-3 font-medium text-slate-800">{c.name}</td>
                  <td className="px-4 py-3 text-slate-500">{c.email}</td>
                  <td className="px-4 py-3 text-slate-500">{c.phone}</td>
                  <td className="px-4 py-3 text-slate-500">{COUNTRY_NAMES[c.country] ?? c.country}</td>
                  <td className="px-4 py-3 text-slate-500">{fmtDate(c.createdTime)}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
});
