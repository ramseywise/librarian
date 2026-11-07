import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import "./theme/light.css";
import { installAuthFetch } from "./utils/auth";
import { initTheme } from "./utils/theme";

initTheme();
installAuthFetch();

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>
);
