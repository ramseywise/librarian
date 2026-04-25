import type { ComponentType } from "react";
import { RevenueSummary } from "./RevenueSummary";
import { InvoiceStatusChart } from "./InvoiceStatusChart";
import { RevenueChart } from "./RevenueChart";
import { TopCustomersTable } from "./TopCustomersTable";
import { AgingReport } from "./AgingReport";
import { CustomerInsightCard } from "./CustomerInsightCard";
import { ProductRevenueTable } from "./ProductRevenueTable";
import { DashboardSuggestions } from "./DashboardSuggestions";

export {
  RevenueSummary,
  InvoiceStatusChart,
  RevenueChart,
  TopCustomersTable,
  AgingReport,
  CustomerInsightCard,
  ProductRevenueTable,
  DashboardSuggestions,
};

export const components: Array<{ name: string; component: ComponentType<any> }> = [
  { name: "RevenueSummary",      component: RevenueSummary },
  { name: "InvoiceStatusChart",  component: InvoiceStatusChart },
  { name: "RevenueChart",        component: RevenueChart },
  { name: "TopCustomersTable",   component: TopCustomersTable },
  { name: "AgingReport",         component: AgingReport },
  { name: "CustomerInsightCard", component: CustomerInsightCard },
  { name: "ProductRevenueTable", component: ProductRevenueTable },
  { name: "DashboardSuggestions",component: DashboardSuggestions },
];
