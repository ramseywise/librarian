import { useTheme } from "../hooks/useTheme";
import { toggleTheme } from "../utils/theme";

export function ThemeToggle() {
  const theme = useTheme();
  const next = theme === "light" ? "dark" : "light";
  return (
    <button type="button" onClick={toggleTheme} className="pill-btn" aria-label={`Switch to ${next} theme`}>
      {next === "light" ? "Light" : "Dark"}
    </button>
  );
}
