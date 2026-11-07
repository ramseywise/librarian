import type { GlossaryTerm } from "../../types";

/** The slice of hast this file walks; avoids a dependency on @types/hast. */
interface HastNode {
  type: string;
  tagName?: string;
  value?: string;
  properties?: Record<string, unknown>;
  children?: HastNode[];
}

/** Rendered by the `gloss-term` entry in Markdown's components; the sanitiser strips it from raw HTML. */
export const GLOSS_TAG = "gloss-term";

const HEADING = /^h[1-6]$/;
/** Text in these is code, a label or a link of its own. A collapsed `details` would hide a section's one mark. */
const SKIP = new Set(["a", "button", "code", "details", "kbd", "math", "pre", "samp", "script", "style", "summary", "svg"]);
/** One capital matches any case; two or more mean an acronym. Same rule as librarian/courses/glossary.py. */
const EXACT_CASE_CAPITALS = 2;

interface Form {
  term: GlossaryTerm;
  exact: boolean;
  text: string;
}

const escapeRegExp = (s: string) => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");

function matcher(terms: GlossaryTerm[]): { pattern: RegExp; forms: Map<string, Form[]> } | null {
  const forms = new Map<string, Form[]>();
  for (const term of terms) {
    for (const text of [term.label, ...term.aliases]) {
      if (!text) continue;
      const exact = (text.match(/\p{Lu}/gu)?.length ?? 0) >= EXACT_CASE_CAPITALS;
      const key = text.toLowerCase();
      forms.set(key, [...(forms.get(key) ?? []), { term, exact, text }]);
    }
  }
  if (!forms.size) return null;
  const alternatives = [...forms.keys()].sort((a, b) => b.length - a.length).map(escapeRegExp);
  return { pattern: new RegExp(`(?<![\\p{L}\\p{N}_])(?:${alternatives.join("|")})(?![\\p{L}\\p{N}_])`, "giu"), forms };
}

/**
 * Rehype plugin: wrap the first mention of each glossary term in each section. A section starts at
 * any heading. Runs after the sanitiser, so its element can't be forged from a lesson's raw HTML,
 * and before KaTeX, whose math is still `code` here and so skipped.
 */
export function rehypeGlossary({ terms }: { terms: GlossaryTerm[] }) {
  const compiled = matcher(terms);
  return (tree: HastNode) => {
    if (!compiled) return;
    const { pattern, forms } = compiled;
    let seen = new Set<string>();

    /** A text node as text and term nodes, or null when it has no unseen term. */
    const split = (value: string): HastNode[] | null => {
      const out: HastNode[] = [];
      let at = 0;
      pattern.lastIndex = 0;
      for (let m = pattern.exec(value); m; m = pattern.exec(value)) {
        const candidates = forms.get(m[0].toLowerCase()) ?? [];
        const form = candidates.find((f) => (!f.exact || f.text === m[0]) && !seen.has(f.term.id));
        if (!form) continue;
        seen.add(form.term.id);
        if (m.index > at) out.push({ type: "text", value: value.slice(at, m.index) });
        out.push({
          type: "element",
          tagName: GLOSS_TAG,
          properties: { dataLabel: form.term.label, dataDef: form.term.def },
          children: [{ type: "text", value: m[0] }],
        });
        at = m.index + m[0].length;
        pattern.lastIndex = at;
      }
      if (!out.length) return null;
      if (at < value.length) out.push({ type: "text", value: value.slice(at) });
      return out;
    };

    const walk = (node: HastNode) => {
      const children = node.children;
      if (!children) return;
      for (let i = 0; i < children.length; i++) {
        const child = children[i];
        if (child.type === "text") {
          const parts = split(child.value ?? "");
          if (parts) {
            children.splice(i, 1, ...parts);
            i += parts.length - 1;
          }
        } else if (child.type === "element") {
          const tag = child.tagName ?? "";
          if (HEADING.test(tag)) seen = new Set();
          else if (!SKIP.has(tag)) walk(child);
        }
      }
    };
    walk(tree);
  };
}
