import { memo, useMemo, type CSSProperties } from "react";
import ReactMarkdown, { type Components } from "react-markdown";
import remarkGfm from "remark-gfm";
import { CitationChip } from "./CitationChip";
import { CITATION_ATTR, remarkCitations } from "./remarkCitations";

interface Props {
  content: string;
  /** Page ids cited but not read; their chips render as warnings. */
  ungrounded?: string[];
  onOpenPage?: (id: string) => void;
}

// react-markdown passes the hast `node` to overrides; it must not reach the DOM.
function withoutNode<T extends { node?: unknown }>(props: T): Omit<T, "node"> {
  const { node, ...rest } = props;
  void node;
  return rest;
}

const remarkPlugins = [remarkGfm, remarkCitations];
const EMPTY: string[] = [];

// Assistant message body. No raw HTML (react-markdown escapes it by default) and no
// math. Partial input while streaming is fine: an unclosed fence renders as a code block
// running to the end of the text until the closing fence arrives.
export const ChatMarkdown = memo(function ChatMarkdown({
  content,
  ungrounded = EMPTY,
  onOpenPage,
}: Props) {
  const components = useMemo<Components>(() => {
    const ungroundedSet = new Set(ungrounded);
    return {
      span(all) {
        const props = withoutNode(all);
        const id = (props as Record<string, unknown>)[CITATION_ATTR];
        if (typeof id === "string") {
          return (
            <CitationChip id={id} ungrounded={ungroundedSet.has(id)} onOpenPage={onOpenPage} />
          );
        }
        return <span {...props} />;
      },
      a(all) {
        const { href, children, ...props } = withoutNode(all);
        const external = !!href && /^(https?:)?\/\//i.test(href);
        return (
          <a
            {...props}
            href={href}
            style={linkStyle}
            {...(external ? { target: "_blank", rel: "noreferrer" } : {})}
          >
            {children}
          </a>
        );
      },
      pre(all) {
        const props = withoutNode(all);
        return <pre {...props} style={preStyle} />;
      },
      table(all) {
        const props = withoutNode(all);
        return (
          <div style={{ overflowX: "auto" }}>
            <table {...props} style={tableStyle} />
          </div>
        );
      },
      th(all) {
        const props = withoutNode(all);
        return <th {...props} style={cellStyle} />;
      },
      td(all) {
        const props = withoutNode(all);
        return <td {...props} style={cellStyle} />;
      },
    };
  }, [ungrounded, onOpenPage]);

  return (
    <div style={rootStyle} className="chat-markdown">
      <style>{INLINE_CODE_CSS}</style>
      <ReactMarkdown remarkPlugins={remarkPlugins} components={components}>
        {content}
      </ReactMarkdown>
    </div>
  );
});

const rootStyle: CSSProperties = { lineHeight: 1.55, overflowWrap: "anywhere" };
const linkStyle: CSSProperties = { color: "#8fb4e8" };
const preStyle: CSSProperties = {
  background: "#0b0b0b",
  border: "1px solid #262626",
  borderRadius: 6,
  padding: "8px 10px",
  overflowX: "auto",
  fontSize: 11,
  lineHeight: 1.45,
  color: "#d6d6d6",
  whiteSpace: "pre",
};
// Inline code only; fenced code is styled through the <pre> override. A selector
// rather than a `code` override, since react-markdown does not say whether a code
// element sits inside <pre>.
const INLINE_CODE_CSS =
  ".chat-markdown :not(pre) > code { background: #232323; border-radius: 4px; padding: 1px 4px; font-size: 11px; color: #e0c08a; }" +
  " .chat-markdown p { margin: 0 0 8px; } .chat-markdown pre { margin: 6px 0 8px; }" +
  " .chat-markdown ul, .chat-markdown ol { margin: 0 0 8px; padding-left: 18px; }" +
  " .chat-markdown h1, .chat-markdown h2, .chat-markdown h3, .chat-markdown h4 { font-size: 13px; margin: 8px 0 4px; color: #e0e0e0; }" +
  " .chat-markdown > :last-child { margin-bottom: 0; }";
const tableStyle: CSSProperties = { borderCollapse: "collapse", margin: "6px 0", fontSize: 11 };
const cellStyle: CSSProperties = { border: "1px solid #2a2a2a", padding: "3px 6px", textAlign: "left" };
