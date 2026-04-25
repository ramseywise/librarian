import type { ComponentType } from "react";
import { InvoiceList } from "./InvoiceList";
import { LineItemEditor } from "./LineItemEditor";

export { InvoiceList, LineItemEditor };

export const components: Array<{ name: string; component: ComponentType<any> }> = [
  { name: "InvoiceList", component: InvoiceList },
  { name: "LineItemEditor", component: LineItemEditor },
];
