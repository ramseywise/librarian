// ---------------------------------------------------------------------------
// Billy REST base URL — used for $fetch resolution in updateDataModel.
// Override via VITE_BILLY_REST_URL environment variable.
// ---------------------------------------------------------------------------

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export const BILLY_REST_BASE: string = ((import.meta as any).env?.VITE_BILLY_REST_URL as string | undefined) ?? "http://127.0.0.1:8766";

// ---------------------------------------------------------------------------
// $fetch resolution — intercepts { "$fetch": "/path" } sentinels in
// updateDataModel values and replaces them with data fetched from the Billy
// REST API before the batch is passed to processMessages.
// ---------------------------------------------------------------------------

import type { V09Message } from "./v09-to-v08";

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function transformCustomerOptions(data: any): Array<{ label: string; value: string }> {
  const list: any[] = Array.isArray(data) ? data : (data?.customers ?? []);
  return list.map((c: any) => ({ label: String(c.name ?? ""), value: String(c.id ?? "") }));
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function transformProductOptions(data: any): Array<{ label: string; value: string; unitPrice: number }> {
  const list: any[] = Array.isArray(data) ? data : (data?.products ?? []);
  return list.map((p: any) => {
    const price: number = p.prices?.[0]?.unit_price ?? 0;
    return { label: `${p.name} (${price} DKK)`, value: String(p.id ?? ""), unitPrice: price };
  });
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function transformInvoices(data: any): Array<Record<string, unknown>> {
  const list: any[] = Array.isArray(data) ? data : (data?.invoices ?? []);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const fmtAmt = (v: any) => typeof v === "number" ? v.toFixed(2) : String(v ?? "0.00");
  return list.map((i: any) => ({
    id: String(i.id ?? ""),
    invoiceNo: String(i.invoice_no ?? ""),
    customerName: String(i.customer_name ?? ""),
    entryDate: String(i.entry_date ?? ""),
    dueDate: String(i.due_date ?? ""),
    amount: fmtAmt(i.amount),
    grossAmount: fmtAmt(i.gross_amount),
    state: String(i.state ?? ""),
    description: String(i.line_description ?? ""),
    isPaid: Boolean(i.is_paid),
  }));
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function transformInvoiceSummary(data: any): Record<string, unknown> {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const fmtAmt = (v: any) => typeof v === "number" ? v.toFixed(2) : String(v ?? "0.00");
  return {
    all:      { count: data?.all?.count ?? 0,      amount: fmtAmt(data?.all?.amount) },
    draft:    { count: data?.draft?.count ?? 0,    amount: fmtAmt(data?.draft?.amount) },
    approved: { count: data?.approved?.count ?? 0, amount: fmtAmt(data?.approved?.amount) },
    overdue:  { count: data?.overdue?.count ?? 0,  amount: fmtAmt(data?.overdue?.amount) },
    unpaid:   { count: data?.unpaid?.count ?? 0,   amount: fmtAmt(data?.unpaid?.amount) },
    paid:     { count: data?.paid?.count ?? 0,     amount: fmtAmt(data?.paid?.amount) },
  };
}

const FETCH_TRANSFORMERS: Record<string, (data: unknown) => unknown> = {
  "/customers": transformCustomerOptions,
  "/products": transformProductOptions,
  "/invoices": transformInvoices,
  "/invoices/summary": transformInvoiceSummary,
};

export async function resolveFetches(batch: unknown[]): Promise<unknown[]> {
  return Promise.all(
    batch.map(async (msg) => {
      const m = msg as V09Message;
      if (
        !m.updateDataModel?.value ||
        typeof m.updateDataModel.value !== "object" ||
        Array.isArray(m.updateDataModel.value)
      ) {
        return msg;
      }
      const value = m.updateDataModel.value as Record<string, unknown>;
      const hasFetch = Object.values(value).some(
        (v) => v !== null && typeof v === "object" && "$fetch" in (v as object)
      );
      if (!hasFetch) return msg;

      const resolved: Record<string, unknown> = {};
      await Promise.all(
        Object.entries(value).map(async ([key, val]) => {
          if (val !== null && typeof val === "object" && "$fetch" in (val as object)) {
            const fetchPath = (val as { "$fetch": string })["$fetch"];
            const sep = fetchPath.includes("?") ? "&" : "?";
            try {
              const url = `${BILLY_REST_BASE}${fetchPath}${sep}page_size=200`;
              const res = await fetch(url);
              const data: unknown = res.ok ? await res.json() : [];
              const transformed = FETCH_TRANSFORMERS[fetchPath.split("?")[0]]?.(data) ?? data;
              console.log(`[resolveFetches] ${url} → ok:${res.ok} items:${Array.isArray(transformed) ? transformed.length : "?"}`);
              resolved[key] = transformed;
            } catch (err) {
              console.log(`[resolveFetches] ${fetchPath} FAILED:`, err);
              resolved[key] = [];
            }
          } else {
            resolved[key] = val;
          }
        })
      );
      return { ...m, updateDataModel: { ...m.updateDataModel, value: resolved } };
    })
  );
}
