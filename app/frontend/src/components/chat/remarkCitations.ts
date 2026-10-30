import type { Root, Parent, PhrasingContent, Text } from "mdast";

// Same grammar as CITATION_RE in app/backend/agent.py, so the chips match exactly the
// ids the backend's grounding check extracts.
export const CITATION_RE = /\[page:\s*([A-Za-z0-9][A-Za-z0-9_-]*)\s*\]/g;

/** Attribute name the chip span carries; ChatMarkdown's `span` override keys on it. */
export const CITATION_ATTR = "data-page-id";

// Code spans and fences are `inlineCode` / `code` nodes with a `value`, not text
// children, so walking only `text` nodes already leaves markers inside code untouched.
// Links are skipped too: a chip inside an <a> would nest interactive elements.
const SKIP = new Set(["link", "linkReference", "inlineCode", "code", "html"]);

function citationNode(id: string): PhrasingContent {
  // An unknown node with data.hName is rendered by mdast-util-to-hast as that element.
  return {
    type: "citation",
    data: { hName: "span", hProperties: { dataPageId: id } },
    children: [{ type: "text", value: id }],
  } as unknown as PhrasingContent;
}

function splitText(value: string): PhrasingContent[] | null {
  CITATION_RE.lastIndex = 0;
  const out: PhrasingContent[] = [];
  let last = 0;
  let match: RegExpExecArray | null;
  while ((match = CITATION_RE.exec(value)) !== null) {
    if (match.index > last) out.push({ type: "text", value: value.slice(last, match.index) });
    out.push(citationNode(match[1]));
    last = match.index + match[0].length;
  }
  if (out.length === 0) return null;
  if (last < value.length) out.push({ type: "text", value: value.slice(last) });
  return out;
}

function walk(node: Parent) {
  const next: typeof node.children = [];
  for (const child of node.children) {
    // Merge adjacent text siblings first so a marker split across nodes still matches.
    const prev = next[next.length - 1];
    if (child.type === "text" && prev?.type === "text") {
      (prev as Text).value += (child as Text).value;
      continue;
    }
    next.push(child.type === "text" ? { ...child } : child);
  }
  const replaced: typeof node.children = [];
  for (const child of next) {
    if (child.type === "text") {
      const parts = splitText((child as Text).value);
      if (parts) {
        replaced.push(...(parts as typeof node.children));
        continue;
      }
    } else if ("children" in child && !SKIP.has(child.type)) {
      walk(child as Parent);
    }
    replaced.push(child);
  }
  node.children = replaced;
}

/** Remark plugin: turn `[page:<id>]` markers outside code into citation chip spans. */
export function remarkCitations() {
  return (tree: Root) => {
    walk(tree);
  };
}
