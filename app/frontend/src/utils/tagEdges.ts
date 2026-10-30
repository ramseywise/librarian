import type { Edge, Node } from "@xyflow/react";
import type { WikiEdgeData, WikiNodeData } from "../types";

/**
 * Tag-shared edges, computed client-side (the server stopped sending them: they were
 * ~42k edges and ~10 MB of every graph_update).
 *
 * Same rule as the former server implementation in app/backend/wiki_parser.py:
 * two pages are linked when they live in different directories and share at least one
 * frontmatter tag that is a domain tag. `domains` is the payload's domain list.
 *
 * Edge ids are `ts:<a>-><b>` with a < b, so the result is deterministic.
 */
export function tagSharedEdges(
  nodes: Pick<Node<WikiNodeData>, "id" | "data">[],
  domains: Iterable<string>,
): Edge<WikiEdgeData>[] {
  const domainSet = new Set(domains);
  const dir = new Map<string, string>();
  const tagsOf = new Map<string, Set<string>>();
  const byTag = new Map<string, string[]>();

  for (const n of nodes) {
    dir.set(n.id, n.data.domain[0] ?? "");
    const tags = new Set(n.data.tags.filter((t) => domainSet.has(t)));
    tagsOf.set(n.id, tags);
    for (const t of tags) {
      const list = byTag.get(t);
      if (list) list.push(n.id);
      else byTag.set(t, [n.id]);
    }
  }

  const seen = new Set<string>();
  const edges: Edge<WikiEdgeData>[] = [];
  for (const ids of byTag.values()) {
    for (let i = 0; i < ids.length; i++) {
      for (let j = i + 1; j < ids.length; j++) {
        const [a, b] = ids[i] < ids[j] ? [ids[i], ids[j]] : [ids[j], ids[i]];
        if (dir.get(a) === dir.get(b)) continue;
        const id = `ts:${a}->${b}`;
        if (seen.has(id)) continue;
        seen.add(id);
        const ta = tagsOf.get(a)!;
        const shared = [...tagsOf.get(b)!].filter((t) => ta.has(t)).sort();
        edges.push({ id, source: a, target: b, data: { edgeType: "tag-shared", sharedTags: shared } });
      }
    }
  }
  return edges;
}
