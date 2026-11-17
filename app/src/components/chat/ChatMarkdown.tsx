import { memo, useMemo } from "react";
import ReactMarkdown, { type Components } from "react-markdown";
import remarkGfm from "remark-gfm";
import type { StaleMap } from "../../hooks/useCitationStatus";
import { CitationChip } from "./CitationChip";
import { CITATION_ATTR, remarkCitations } from "./remarkCitations";

interface Props {
  content: string;
  /** Page ids cited but not read; their chips render as warnings. */
  ungrounded?: string[];
  /** Cited pages that changed or went away after the answer; their chips say so. */
  stale?: StaleMap;
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
const NOT_STALE: StaleMap = {};

// Assistant message body. No raw HTML (react-markdown escapes it by default) and no
// math. Partial input while streaming is fine: an unclosed fence renders as a code block
// running to the end of the text until the closing fence arrives.
export const ChatMarkdown = memo(function ChatMarkdown({
  content,
  ungrounded = EMPTY,
  stale = NOT_STALE,
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
            <CitationChip
              id={id}
              ungrounded={ungroundedSet.has(id)}
              stale={stale[id]}
              onOpenPage={onOpenPage}
            />
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
            {...(external ? { target: "_blank", rel: "noreferrer" } : {})}
          >
            {children}
          </a>
        );
      },
      table(all) {
        const props = withoutNode(all);
        return (
          <div className="chat-table-wrap">
            <table {...props} />
          </div>
        );
      },
    };
  }, [ungrounded, stale, onOpenPage]);

  return (
    <div className="chat-markdown">
      <ReactMarkdown remarkPlugins={remarkPlugins} components={components}>
        {content}
      </ReactMarkdown>
    </div>
  );
});
