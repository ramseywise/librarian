import { isValidElement, memo, useRef, useState, type ReactNode } from "react";
import ReactMarkdown, { type Components } from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import "katex/dist/katex.min.css";
import "./courses.css";

/** Resolve a relative href/src against a lesson id ("course/module/dir/lesson"). */
function resolveRelative(lessonId: string, href: string): string {
  const parts = lessonId.split("/").slice(0, -1);
  for (const seg of decodeURIComponent(href).split("/")) {
    if (seg === "..") parts.pop();
    else if (seg && seg !== ".") parts.push(seg);
  }
  return parts.join("/");
}

const isExternal = (url: string) => /^[a-z][a-z0-9+.-]*:/i.test(url);

function textOf(node: ReactNode): string {
  if (typeof node === "string" || typeof node === "number") return String(node);
  if (Array.isArray(node)) return node.map(textOf).join("");
  if (isValidElement<{ children?: ReactNode }>(node)) return textOf(node.props.children);
  return "";
}

/** GitHub-style heading anchor, so `[x](#some-heading)` links in lessons resolve. */
const headingId = (children: ReactNode) =>
  textOf(children).toLowerCase().trim().replace(/[^\w\s-]/g, "").replace(/\s+/g, "-");

const heading = (Tag: "h1" | "h2" | "h3" | "h4") =>
  ({ children }: { children?: ReactNode }) => <Tag id={headingId(children)}>{children}</Tag>;

interface Props {
  body: string;
  lessonId: string;
  onOpenLesson: (id: string) => void;
  onOpenConcept: (pageId: string) => void;
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

function MarkdownInner({ body, lessonId, onOpenLesson, onOpenConcept }: Props) {
  const components: Components = {
    h1: heading("h1"),
    h2: heading("h2"),
    h3: heading("h3"),
    h4: heading("h4"),
    pre: ({ children }) => <CodeBlock>{children}</CodeBlock>,
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
          <a href={href} onClick={(e) => {
            e.preventDefault();
            document.getElementById(href.slice(1))?.scrollIntoView({ behavior: "smooth" });
          }}>{children}</a>
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
    img: ({ src = "", alt }) => {
      const url = typeof src === "string" && !isExternal(src) && !src.startsWith("/")
        ? `/api/courses/files/${resolveRelative(lessonId, src)}`
        : String(src);
      return <img src={url} alt={alt ?? ""} loading="lazy" />;
    },
    table: ({ children }) => <div className="lp-table"><table>{children}</table></div>,
  };

  return (
    <ReactMarkdown remarkPlugins={[remarkGfm, remarkMath]} rehypePlugins={[rehypeKatex]} components={components}>
      {body}
    </ReactMarkdown>
  );
}

export const Markdown = memo(MarkdownInner);
