import type { ComponentType } from "react";
import { ControlledMultipleChoice } from "./ControlledMultipleChoice";
import { DatePicker } from "./DatePicker";
import { DueDatePicker } from "./DueDatePicker";

export { ControlledMultipleChoice, DatePicker, DueDatePicker };

export const components: Array<{ name: string; component: ComponentType<any> }> = [
  { name: "MultipleChoice", component: ControlledMultipleChoice },
  { name: "DatePicker", component: DatePicker },
  { name: "DueDatePicker", component: DueDatePicker },
];
