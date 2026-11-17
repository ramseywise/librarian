import { useEffect, useLayoutEffect, useRef, useState, type ReactNode } from "react";
import type { SlideBeat, SlideFrameData } from "./types";
import "./slides.css";
import { apiFetch } from "../../utils/api";

/** What each beat is called on the slide, and the class that gives it its hue (slides.css). */
const BEATS: Record<SlideBeat, { label: string; cls: string }> = {
  problem: { label: "The idea", cls: "sf-b-idea" },
  fundamentals: { label: "The principle", cls: "sf-b-principle" },
  practice: { label: "The application", cls: "sf-b-applied" },
  pitfalls: { label: "Pitfall", cls: "sf-b-pitfall" },
  wrap: { label: "Keep", cls: "sf-b-keep" },
};
/** The class that carries a frame's hue: its beat's, yellow for a part divider, neutral otherwise. */
export function beatClass(frame: SlideFrameData): string {
  if (frame.kind === "divider") return BEATS.problem.cls;
  return frame.kind === "slide" && frame.beat ? BEATS[frame.beat].cls : "sf-b-none";
}

/** The builder's greys (deck-spec.md, Palette): a step or card given one is de-emphasised. */
const GREYS = new Set(["94A3B8", "CBD5E1"]);
/** A slide's body starts at MAX_FIT times its drawn size, so a sparse slide fills its space, and
 * shrinks in steps until it fits, down to MIN_FIT. */
const MAX_FIT = 1.3;
const MIN_FIT = 0.55;

/** An image fetched as a blob: an `<img src>` cannot carry the bearer token. */
export function AuthedImage({ url, alt, className }: { url: string; alt: string; className: string }) {
  const [src, setSrc] = useState<string | null>(null);
  useEffect(() => {
    let cancelled = false;
    let made: string | null = null;
    setSrc(null);
    apiFetch(url)
      .then((r) => (r.ok ? r.blob() : Promise.reject(new Error(`HTTP ${r.status}`))))
      .then((blob) => {
        if (cancelled) return;
        made = URL.createObjectURL(blob);
        setSrc(made);
      })
      .catch(() => undefined);
    return () => {
      cancelled = true;
      if (made) URL.revokeObjectURL(made);
    };
  }, [url]);
  return src ? <img src={src} alt={alt} className={className} /> : <div className={`${className} ${className}--loading`} />;
}

/** The deck spec's inline markup: `**bold**` and `` `code` ``, and nothing else. */
function rich(value: unknown): ReactNode {
  const s = typeof value === "string" ? value : typeof value === "number" || typeof value === "boolean" ? String(value) : "";
  return s.split(/(\*\*.+?\*\*|`[^`]+`)/).map((piece, i) =>
    piece.startsWith("**") && piece.length > 4 ? <b key={i}>{piece.slice(2, -2)}</b>
      : piece.startsWith("`") && piece.length > 2 ? <code key={i}>{piece.slice(1, -1)}</code>
        : piece,
  );
}

type Dict = Record<string, unknown>;
const isDict = (v: unknown): v is Dict => typeof v === "object" && v !== null && !Array.isArray(v);
const list = (v: unknown): unknown[] => (Array.isArray(v) ? v : []);
const str = (v: unknown): string => (typeof v === "string" || typeof v === "number" ? String(v) : "");

function Bullets({ items }: { items: unknown }) {
  const rows = list(items);
  if (!rows.length) return null;
  return (
    <ul className="sf-list">
      {rows.map((item, i) => {
        const subs = isDict(item) ? list(item.sub) : [];
        return (
          <li key={i}>
            {rich(isDict(item) ? item.text : item)}
            {subs.length > 0 && <ul className="sf-sublist">{subs.map((s, j) => <li key={j}>{rich(s)}</li>)}</ul>}
          </li>
        );
      })}
    </ul>
  );
}

/** Code with its comment lines dimmed. No more than that: the slide's own `**bold**` is not valid in code. */
function Code({ code, lang }: { code: unknown; lang?: unknown }) {
  const lines = str(code).replace(/\n$/, "").split("\n");
  return (
    <pre className="sf-code">
      {str(lang) && <span className="sf-code-lang">{str(lang)}</span>}
      {lines.map((line, i) => (
        <span key={i} className={/^\s*(#|\/\/|--)/.test(line) ? "sf-code-comment" : undefined}>{line}{"\n"}</span>
      ))}
    </pre>
  );
}

/** A card of a `compare` or `cards` slide, or the aside of a `bullets` slide: title, then whichever of
 * body, bullets and code it has, then its tag. */
function CardBody({ card }: { card: Dict }) {
  return (
    <>
      {str(card.title) && <h4>{rich(card.title)}</h4>}
      {str(card.body) && <p>{rich(card.body)}</p>}
      <Bullets items={card.bullets} />
      {str(card.code) && <Code code={card.code} lang={card.lang} />}
      {str(card.tag) && <span className="sf-tag">{rich(card.tag)}</span>}
    </>
  );
}

function Body({ layout, body, title }: { layout: string; body: Dict; title: string }) {
  switch (layout) {
    case "statement":
      return (
        <>
          <p className="sf-statement">{rich(body.statement)}</p>
          {str(body.attribution) && <span className="sf-attrib">{rich(body.attribution)}</span>}
        </>
      );
    case "flow": {
      const steps = list(body.steps);
      return (
        <>
          <div className="sf-flow">
            {steps.map((step, i) => {
              const accent = isDict(step) ? str(step.accent).toUpperCase() : "";
              const last = i === steps.length - 1 && body.end_accent !== false;
              return (
                <div key={i} className={`sf-step${last ? " sf-step--accent" : ""}${GREYS.has(accent) ? " sf-step--dim" : ""}`}>
                  <b>{rich(isDict(step) ? step.label : step)}</b>
                  {isDict(step) && str(step.sub) && <small>{rich(step.sub)}</small>}
                </div>
              );
            })}
          </div>
          {str(body.loop) && <span className="sf-loop">↺ {rich(body.loop)}</span>}
          {str(body.caption) && <span className="sf-lead">{rich(body.caption)}</span>}
          <Bullets items={body.bullets} />
        </>
      );
    }
    case "steps":
      return (
        <div className="sf-steps-wrap">
          {str(body.axis) && <span className="sf-axis">{rich(body.axis)}</span>}
          <ol className="sf-steps">
            {list(body.steps).map((step, i) => (
              <li key={i}>
                <span className="sf-step-n">{isDict(step) && str(step.n) ? str(step.n) : i + 1}</span>
                <div>
                  <b>{rich(isDict(step) ? step.title : step)}</b>
                  {isDict(step) && str(step.text) && <span>{rich(step.text)}</span>}
                </div>
              </li>
            ))}
          </ol>
        </div>
      );
    case "code": {
      const side = list(body.bullets).length > 0;
      return (
        <div className={side ? "sf-split sf-split--code" : "sf-single"}>
          <Code code={body.code} lang={body.lang} />
          <Bullets items={body.bullets} />
        </div>
      );
    }
    case "table": {
      const marked = new Set(list(body.highlight).map(Number));
      return (
        <table className={`sf-table${body.bold_first === false ? "" : " sf-table--lead"}`}>
          <thead><tr>{list(body.header).map((h, i) => <th key={i}>{rich(h)}</th>)}</tr></thead>
          <tbody>
            {list(body.rows).map((row, i) => (
              <tr key={i} className={marked.has(i) ? "sf-row--hit" : undefined}>
                {list(row).map((cell, j) => <td key={j}>{rich(cell)}</td>)}
              </tr>
            ))}
          </tbody>
        </table>
      );
    }
    case "compare": {
      const win = str(body.emphasis) || "right";
      return (
        <div className="sf-compare">
          {(["left", "right"] as const).map((side) => (
            <div key={side} className={`sf-col${win === side ? " sf-col--win" : ""}`}>
              {isDict(body[side]) && <CardBody card={body[side]} />}
            </div>
          ))}
        </div>
      );
    }
    case "cards": {
      const cards = list(body.cards).filter(isDict);
      const cols = cards.length <= 4 ? cards.length : 3;
      return (
        <div className="sf-cards" style={{ gridTemplateColumns: `repeat(${cols || 1}, minmax(0, 1fr))` }}>
          {cards.map((card, i) => (
            <div key={i} className={`sf-card${str(card.accent) && !GREYS.has(str(card.accent).toUpperCase()) ? " sf-card--accent" : ""}`}>
              <CardBody card={card} />
            </div>
          ))}
        </div>
      );
    }
    case "image": {
      const side = list(body.bullets).length > 0;
      return (
        <div className={side ? "sf-split sf-split--image" : "sf-single"}>
          <figure className="sf-figure">
            {str(body.image)
              ? <AuthedImage url={str(body.image)} alt={str(body.caption) || title} className="sf-img" />
              : <div className="sf-img sf-img--loading" />}
            {str(body.caption) && <figcaption>{rich(body.caption)}</figcaption>}
          </figure>
          <Bullets items={body.bullets} />
        </div>
      );
    }
    default: {
      // `bullets`, and any layout this renderer does not know: its bullets are still worth showing.
      const aside = isDict(body.aside) ? body.aside : null;
      return (
        <div className={aside ? "sf-split sf-split--aside" : "sf-single"}>
          <Bullets items={body.bullets} />
          {aside && <div className="sf-card sf-aside"><CardBody card={aside} /></div>}
        </div>
      );
    }
  }
}

/** One slide, drawn from the deck's yaml at 16:9. It scales as a unit with its width, and its body text
 * is sized to fill the slide without running over. `courseColor` tints the title slide. */
export function SlideFrame({ frame, total, courseColor }: { frame: SlideFrameData; total: number; courseColor?: string }) {
  const body = useRef<HTMLDivElement>(null);
  useLayoutEffect(() => {
    const el = body.current;
    if (!el) return;
    let k = MAX_FIT;
    el.style.setProperty("--k", String(k));
    const wide = (sel: string) => [...el.querySelectorAll<HTMLElement>(sel)].filter((e) => e.scrollWidth > e.clientWidth + 1);
    while ((el.scrollHeight > el.clientHeight + 1 || wide(".sf-step b").length > 0) && k > MIN_FIT) {
      k -= 0.05;
      el.style.setProperty("--k", k.toFixed(2));
    }
    // A long line of code shrinks its own block, not the text beside it.
    for (const code of el.querySelectorAll<HTMLElement>(".sf-code")) {
      let kc = 1;
      code.style.setProperty("--kc", "1");
      while (code.scrollWidth > code.clientWidth + 1 && kc > MIN_FIT) {
        kc -= 0.05;
        code.style.setProperty("--kc", kc.toFixed(2));
      }
    }
  }, [frame]);

  if (frame.kind === "title") {
    return (
      <div className="sf sf-title" style={courseColor ? ({ "--course": courseColor } as React.CSSProperties) : undefined}>
        <div className="sf-in sf-title-in">
          <div className="sf-title-left">
            <h2>{rich(frame.title)}</h2>
            {frame.subtitle && <p className="sf-title-sub">{rich(frame.subtitle)}</p>}
            {frame.tagline && <p className="sf-title-tag">{rich(frame.tagline)}</p>}
            <span className="sf-title-ref">{[frame.byline, frame.reference].filter(Boolean).join(" · ")}</span>
          </div>
          <ol className="sf-agenda-list">
            {frame.agenda.map((part) => (
              <li key={part.n}>
                <span className="sf-agenda-n">{part.n}</span>
                <div><b>{rich(part.title)}</b>{part.summary && <span>{rich(part.summary)}</span>}</div>
              </li>
            ))}
          </ol>
        </div>
      </div>
    );
  }

  if (frame.kind === "divider") {
    const topics = frame.summary.split("·").map((t) => t.trim()).filter(Boolean);
    return (
      <div className="sf sf-b-idea">
        <div className="sf-in sf-divider">
          <div className="sf-divider-left">
            <span className="sf-divider-of">Part {frame.part.n} of {frame.part.of}</span>
            <span className="sf-divider-n">{frame.part.n}</span>
          </div>
          <div className="sf-divider-right">
            <h2>{rich(frame.title)}</h2>
            {topics.length > 0 && (
              <>
                <div className="sf-label">In this part</div>
                <ul className="sf-list">{topics.map((t, i) => <li key={i}>{rich(t)}</li>)}</ul>
              </>
            )}
            <div className="sf-ticks" aria-hidden="true">
              {Array.from({ length: frame.part.of }, (_, i) => <i key={i} className={i + 1 === frame.part.n ? "on" : undefined} />)}
            </div>
          </div>
        </div>
      </div>
    );
  }

  const beat = frame.beat ? BEATS[frame.beat] : null;
  const where = frame.part.n === null ? frame.part.title : `${frame.part.n} ${frame.part.title}`;
  return (
    <div className={`sf ${beat?.cls ?? "sf-b-none"}`} data-layout={frame.layout}>
      <div className="sf-in sf-slide">
        <div className="sf-head">
          {beat && <span className="sf-beat">{beat.label}</span>}
          {frame.kicker && frame.kicker.toLowerCase() !== beat?.label.toLowerCase() && <span className="sf-kicker">{rich(frame.kicker)}</span>}
          <span className="sf-where">{where} · {frame.n} / {total}</span>
        </div>
        <div className={`sf-body sf-body--${frame.layout}`} ref={body}>
          <h3 className="sf-h">{rich(frame.title)}</h3>
          {frame.lead && <span className="sf-lead">{rich(frame.lead)}</span>}
          <Body layout={frame.layout} body={frame.body} title={frame.title} />
        </div>
        {frame.takeaway && <div className="sf-take"><span>Takeaway</span><div>{rich(frame.takeaway)}</div></div>}
      </div>
    </div>
  );
}
