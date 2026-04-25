import type { ComponentType } from "react";
import { CustomerForm } from "./CustomerForm";
import { CustomerList } from "./CustomerList";

export { CustomerForm, CustomerList };

export const components: Array<{ name: string; component: ComponentType<any> }> = [
  { name: "CustomerForm", component: CustomerForm },
  { name: "CustomerList", component: CustomerList },
];
