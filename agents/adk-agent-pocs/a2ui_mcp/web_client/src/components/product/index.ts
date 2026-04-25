import type { ComponentType } from "react";
import { ProductForm } from "./ProductForm";
import { ProductList } from "./ProductList";

export { ProductForm, ProductList };

export const components: Array<{ name: string; component: ComponentType<any> }> = [
  { name: "ProductForm", component: ProductForm },
  { name: "ProductList", component: ProductList },
];
