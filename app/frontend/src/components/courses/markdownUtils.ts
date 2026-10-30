import { isValidElement, type ReactNode } from "react";
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

/** Lesson-relative asset paths are served by the API; absolute and external URLs pass through. */
export function assetUrl(lessonId: string, src: string): string {
  return !src || isExternal(src) || src.startsWith("/") || src.startsWith("#")
    ? src
    : `/api/courses/files/${resolveRelative(lessonId, src)}`;
}

export function textOf(node: ReactNode): string {
  if (typeof node === "string" || typeof node === "number") return String(node);
  if (Array.isArray(node)) return node.map(textOf).join("");
  if (isValidElement<{ children?: ReactNode }>(node)) return textOf(node.props.children);
  return "";
}

/** GitHub-style heading anchor, so `[x](#some-heading)` links in lessons resolve. */
export const headingId = (children: ReactNode) =>
  textOf(children).toLowerCase().trim().replace(/[^\w\s-]/g, "").replace(/\s+/g, "-");

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
