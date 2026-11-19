import type { AtlasSector, RingGeometry } from "../../utils/atlas";
import type { AtlasPageInfo } from "./atlasText";
import { gapText } from "./atlasText";

export const TOOLTIP_W = 300;

export function hideTip(tip: HTMLElement | null): void {
  if (tip) tip.hidden = true;
}

export function tipLine(cls: string, text: string): HTMLDivElement {
  const div = document.createElement("div");
  div.className = cls;
  div.textContent = text;
  return div;
}

export function fillTip(
  tip: HTMLElement,
  page: AtlasPageInfo | undefined,
  sector: AtlasSector,
  links: number,
  untaught: boolean,
): void {
  const meta = `${sector.label} · ${links} ${links === 1 ? "link" : "links"}`;
  tip.replaceChildren(
    tipLine("atlas-tip-title", page?.title ?? ""),
    tipLine("atlas-tip-summary", page?.summary ?? ""),
    tipLine("atlas-tip-meta", untaught ? `${meta} · not yet in a lesson` : meta),
  );
  tip.hidden = false;
}

export function fillSectorTip(tip: HTMLElement, sector: AtlasSector, gaps: number | null): void {
  const count = `${sector.pageIds.length} pages`;
  tip.replaceChildren(
    tipLine("atlas-tip-title", sector.label),
    tipLine("atlas-tip-meta", `${gaps ? `${count} · ${gapText(gaps)}` : count} · click to open the best linked`),
  );
  tip.hidden = false;
}

/** Beside the pointer, on the side with room. Uses a transform, so it doesn't trigger layout. */
export function moveTip(tip: HTMLElement, x: number, y: number, g: RingGeometry): void {
  const left = x + 16 + TOOLTIP_W > g.width ? x - TOOLTIP_W - 16 : x + 16;
  const top = y > g.height - 150 ? y - 130 : y + 14;
  tip.style.transform = `translate(${Math.max(4, left)}px, ${Math.max(4, top)}px)`;
}
