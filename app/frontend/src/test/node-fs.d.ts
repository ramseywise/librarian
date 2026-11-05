// The one Node API the source-checking tests read with; @types/node isn't a dependency here.
declare module "node:fs" {
  export function readFileSync(path: string, encoding: "utf8"): string;
}
