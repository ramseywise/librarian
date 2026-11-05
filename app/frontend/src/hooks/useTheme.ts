import { useSyncExternalStore } from "react";
import { currentTheme, subscribeTheme, type Theme } from "../utils/theme";

export function useTheme(): Theme {
  return useSyncExternalStore(subscribeTheme, currentTheme);
}
