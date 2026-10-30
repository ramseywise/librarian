import { memo, useMemo, useRef, useState, type ReactNode } from "react";
import ReactMarkdown, { type Components, type Options } from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import rehypeRaw from "rehype-raw";
import rehypeSanitize from "rehype-sanitize";
import rehypeKatex from "rehype-katex";
import "katex/dist/katex.min.css";
import "./courses.css";
import { CLOBBER_PREFIX, assetUrl, headingId, isExternal, resolveRelative, sanitizeSchema } from "./markdownUtils";

interface Props {
  body: string;
  lessonId: string;
  onOpenLesson: (id: string) => void;
  onOpenConcept: (pageId: string) => void;
}

// Module-scope component types: a new function per render would remount every heading,
// detaching the nodes LessonView's TOC IntersectionObserver is watching.
type HeadingProps = { children?: ReactNode };
const H1 = ({ children }: HeadingProps) => <h1 id={headingId(children)}>{children}</h1>;
const H2 = ({ children }: HeadingProps) => <h2 id={headingId(children)}>{children}</h2>;
const H3 = ({ children }: HeadingProps) => <h3 id={headingId(children)}>{children}</h3>;
const H4 = ({ children }: HeadingProps) => <h4 id={headingId(children)}>{children}</h4>;

const Pre = ({ children }: { children?: ReactNode }) => <CodeBlock>{children}</CodeBlock>;
const Table = ({ children }: { children?: ReactNode }) => (
  <div className="lp-table"><table>{children}</table></div>
);

const remarkPlugins: Options["remarkPlugins"] = [remarkGfm, remarkMath];
// Order matters: parse raw HTML, sanitise it, then render math (KaTeX output is trusted).
const rehypePlugins: Options["rehypePlugins"] = [rehypeRaw, [rehypeSanitize, sanitizeSchema], rehypeKatex];

/** In-page anchor; raw-HTML ids are prefixed by the sanitiser, so try that form too. */
function scrollToAnchor(id: string) {
  const el = document.getElementById(id) ?? document.getElementById(CLOBBER_PREFIX + id);
  el?.scrollIntoView({ behavior: "smooth" });
}

function CodeBlock({ children }: { children?: ReactNode }) {
  const ref = useRef<HTMLPreElement>(null);
  const [copied, setCopied] = useState(false);
  const copy = () => {
    const text = ref.current?.innerText ?? "";
    navigator.clipboard?.writeText(text).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 1200);
    });
  };
  return (
    <div className="lp-code">
      <button className="lp-copy" onClick={copy}>{copied ? "Copied" : "Copy"}</button>
      <pre ref={ref}>{children}</pre>
    </div>
  );
}

function buildComponents(
  lessonId: string,
  onOpenLesson: (id: string) => void,
  onOpenConcept: (pageId: string) => void,
): Components {
  return {
    h1: H1,
    h2: H2,
    h3: H3,
    h4: H4,
    pre: Pre,
    table: Table,
    a: ({ href = "", children }) => {
      if (href.startsWith("#wiki:")) {
        const pageId = href.slice("#wiki:".length);
        return (
          <a href={href} className="lp-wikilink" title="Open in the wiki graph"
            onClick={(e) => { e.preventDefault(); onOpenConcept(pageId); }}>
            {children}
          </a>
        );
      }
      if (href.startsWith("#")) {
        return (
          <a href={href} onClick={(e) => { e.preventDefault(); scrollToAnchor(href.slice(1)); }}>{children}</a>
        );
      }
      if (isExternal(href)) {
        return <a href={href} target="_blank" rel="noreferrer">{children}</a>;
      }
      const [path] = href.split("#");
      if (path.endsWith(".md")) {
        const target = resolveRelative(lessonId, path).replace(/\.md$/, "");
        return (
          <a href={`#/courses/${target}`} onClick={(e) => { e.preventDefault(); onOpenLesson(target); }}>
            {children}
          </a>
        );
      }
      // Relative link to something not imported (PDF, vendored repo, script).
      return <span className="lp-deadlink" title={`Not imported into librarian: ${href}`}>{children}</span>;
    },
    // Covers markdown images and raw-HTML <img> alike (rehype-raw runs first).
    img: ({ src, alt, width, height, title }) => (
      <img src={assetUrl(lessonId, typeof src === "string" ? src : "")} alt={alt ?? ""}
        width={width} height={height} title={title} loading="lazy" />
    ),
  };
}

function MarkdownInner({ body, lessonId, onOpenLesson, onOpenConcept }: Props) {
  const components = useMemo(
    () => buildComponents(lessonId, onOpenLesson, onOpenConcept),
    [lessonId, onOpenLesson, onOpenConcept],
  );
  return (
    <ReactMarkdown remarkPlugins={remarkPlugins} rehypePlugins={rehypePlugins} components={components}>
      {body}
    </ReactMarkdown>
  );
}

export const Markdown = memo(MarkdownInner);
