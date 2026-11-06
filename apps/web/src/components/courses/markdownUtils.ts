import { defaultSchema, type Options as SanitizeSchema } from "rehype-sanitize";

/** Resolve a relative href/src against a lesson id ("course/module/dir/lesson"). */
export function resolveRelative(lessonId: string, href: string): string {
  const parts = lessonId.split("/").slice(0, -1);
  let decoded = href;
  try {
    decoded = decodeURIComponent(href);
  } catch {
    /* malformed escape: use as-is */
  }
  for (const seg of decoded.split("/")) {
    if (seg === "..") parts.pop();
    else if (seg && seg !== ".") parts.push(seg);
  }
  return parts.join("/");
}

export const isExternal = (url: string) => /^[a-z][a-z0-9+.-]*:/i.test(url);

/**
 * Lesson-relative asset paths are served by the API; absolute and external URLs pass
 * through. Protocol-relative `//host/x` is off-site (a tracking pixel), so it is dropped.
 */
export function assetUrl(lessonId: string, src: string): string {
  if (src.startsWith("//")) return "";
  return !src || isExternal(src) || src.startsWith("/") || src.startsWith("#")
    ? src
    : `/api/courses/files/${resolveRelative(lessonId, src)}`;
}

/** A drill's `<details>` solution block (`<details open>` too), split out so it stays hidden until asked for. */
const SOLUTION_RE = /<details(?:\s[^>]*)?>\s*(?:<summary(?:\s[^>]*)?>[\s\S]*?<\/summary>)?([\s\S]*?)<\/details>/g;
/** Fenced code blocks: a `<details>` shown as an example inside one is not the solution. */
const FENCE_RE = /^ {0,3}(`{3,}|~{3,})[^\n]*\n[\s\S]*?(?:^ {0,3}\1[ \t]*$|(?![\s\S]))/gm;

/** [before, solution, after] around the first `<details>` block outside a code fence. */
export function splitSolution(body: string): [string, string, string] | null {
  const fences = [...body.matchAll(FENCE_RE)].map((f) => [f.index, f.index + f[0].length]);
  for (const m of body.matchAll(SOLUTION_RE)) {
    if (fences.some(([a, b]) => m.index >= a && m.index < b)) continue;
    return [body.slice(0, m.index), m[1], body.slice(m.index + m[0].length)];
  }
  return null;
}

/** GitHub-style heading anchor, so `[x](#some-heading)` links in lessons resolve. */
export const slugify = (text: string) =>
  text.toLowerCase().trim().replace(/[^\w\s-]/g, "").replace(/\s+/g, "-");

/** The slice of hast this file walks; avoids a dependency on @types/hast. */
interface HastNode {
  type: string;
  tagName?: string;
  value?: string;
  properties?: Record<string, unknown>;
  children?: HastNode[];
}

const hastText = (n: HastNode): string =>
  n.type === "text" ? (n.value ?? "") : (n.children ?? []).map(hastText).join("");

/**
 * Rehype plugin: give every h1–h4 a GitHub-style id, suffixing repeats (`-1`, `-2`) the
 * way GitHub does, so the TOC (built from these ids) and `#anchor` links stay unique.
 * Runs after the sanitiser, which would otherwise prefix the ids.
 */
export function rehypeHeadingIds() {
  return (tree: HastNode) => {
    const used = new Set<string>();
    const walk = (n: HastNode) => {
      if (n.type === "element" && /^h[1-4]$/.test(n.tagName ?? "")) {
        const base = slugify(hastText(n));
        if (base) {
          let id = base;
          for (let i = 1; used.has(id); i++) id = `${base}-${i}`;
          used.add(id);
          n.properties = { ...n.properties, id };
        }
      }
      n.children?.forEach(walk);
    };
    walk(tree);
  };
}

/** Prefix rehype-sanitize puts on ids/names from lesson content (DOM-clobbering guard). */
export const CLOBBER_PREFIX = "user-content-";

const base = defaultSchema.attributes ?? {};

/**
 * Raw HTML in imported lessons (D4): the default GitHub schema (which already allows
 * img/table/details/summary/br/sup/sub, plus `align`/`width`/`height`/`alt` everywhere)
 * extended with div/span classes, a few table and figure tags, `<details open>`, and the
 * classes remark-math emits so rehype-katex (which runs after sanitize) still finds the
 * math. Scripts, `<style>`, event handlers, `style=`, and javascript: URLs stay stripped.
 */
export const sanitizeSchema: SanitizeSchema = {
  ...defaultSchema,
  tagNames: [
    ...new Set([
      ...(defaultSchema.tagNames ?? []),
      "caption", "colgroup", "col", "figure", "figcaption",
    ]),
  ],
  attributes: {
    ...base,
    div: [...(base.div ?? []), "className"],
    span: [...(base.span ?? []), "className"],
    details: [...(base.details ?? []), "open"],
    code: [["className", /^language-./, "math-inline", "math-display"]],
  },
  strip: [...(defaultSchema.strip ?? []), "style"],
};
