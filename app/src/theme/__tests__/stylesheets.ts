import { readdirSync, readFileSync, statSync } from "node:fs";

/** Every stylesheet under a directory, read from disk (Vitest empties CSS imports under `css: false`).
 *  `dir` is an absolute path; the caller derives it from its own `import.meta.url`. */
export function stylesheets(dir: string): { file: string; css: string }[] {
  return readdirSync(dir).flatMap((name) => {
    const path = `${dir.replace(/\/$/, "")}/${name}`;
    if (statSync(path).isDirectory()) return stylesheets(path);
    return name.endsWith(".css") ? [{ file: name, css: readFileSync(path, "utf8") }] : [];
  });
}

export const withoutComments = (css: string) => css.replace(/\/\*[\s\S]*?\*\//g, "");

/** Hex colours (#rgb to #rrggbbaa) in the rules, ignoring comments. */
export const hexColours = (css: string) => withoutComments(css).match(/#[0-9a-fA-F]{3,8}\b/g) ?? [];

/** Section headers: `/* ---- Title ---- *\/` comments. */
export const sectionHeaders = (css: string) =>
  [...css.matchAll(/\/\*\s*-{3,}\s*(.+?)\s*-{3,}\s*\*\//g)].map((m) => m[1]);

export const duplicates = (items: string[]) => items.filter((x, i) => items.indexOf(x) !== i);
