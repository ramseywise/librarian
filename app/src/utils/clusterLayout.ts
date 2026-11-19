import type { Edge } from "@xyflow/react";
import { neighbours } from "./graphView";
import type { XY } from "./layout";

/**
 * A page's level, laid out as clusters: the page in the middle, its top related pages either side
 * of it, and behind each of those the pages reached through it. Every card has one parent, so the
 * neighbourhood reads as a few named groups, where the similarity layout gave 25 cards with every
 * link between them drawn.
 */

type Link = { source: string; target: string; data?: { relationship?: string } };

/** Related pages that get a cluster of their own; the rest sit in the cluster they link into. */
export const MAX_HEADS = 8;

/**
 * A card's box by its hops from the anchor: the page itself largest, then its related pages, then
 * theirs, then chips. Cards here are a title in type that shrinks with the hops and no summary,
 * so the level fits at a zoom where the first two hops can be read. `.wiki-node--d*` sets these
 * widths and heights.
 */
const CARD_SIZES = [
  { w: 230, h: 100 },
  { w: 176, h: 76 },
  { w: 146, h: 52 },
  { w: 104, h: 42 },
];
export const cardSize = (depth: number) => CARD_SIZES[Math.min(depth, CARD_SIZES.length - 1)];

const ROW_GAP = 10;
const CLUSTER_GAP = 22;
const COL_GAP = 40;
/** Half the room kept clear in the middle for the open page's card. */
const ANCHOR_HALF = 215;

function adjacency(ids: Set<string>, edges: Link[]): Map<string, string[]> {
  const out = new Map<string, string[]>();
  const add = (a: string, b: string) => {
    const list = out.get(a);
    if (list) list.push(b);
    else out.set(a, [b]);
  };
  for (const e of edges) {
    if (e.source === e.target || !ids.has(e.source) || !ids.has(e.target)) continue;
    add(e.source, e.target);
    add(e.target, e.source);
  }
  return out;
}

/**
 * Child → parent for every page in `ids` but the anchor. The anchor's best `maxHeads` neighbours
 * (typed See Also links first) head a cluster each; every other page joins the page it links to
 * that is nearest the anchor, the one with fewest children so far when several are, so one hub
 * can't take the whole neighbourhood.
 *
 * `tiers` are edge sets in order of trust: a later tier (semantic edges, which land seconds after
 * the wikilinks) only places what the earlier ones left, so it never moves a card. `hints` names
 * the page a click revealed each page from, for one no edge reaches. Whatever is still left hangs
 * off the anchor.
 */
export function clusterTree(
  anchor: string,
  ids: Set<string>,
  tiers: Link[][],
  degree: Map<string, number>,
  hints?: Map<string, string>,
  maxHeads = MAX_HEADS,
): Map<string, string> {
  const parent = new Map<string, string>();
  const kids = new Map<string, number>();
  const assign = (child: string, to: string) => {
    parent.set(child, to);
    kids.set(to, (kids.get(to) ?? 0) + 1);
  };
  const rank = (a: string, b: string) => (degree.get(b) ?? 0) - (degree.get(a) ?? 0) || a.localeCompare(b);
  const free = (id: string) => id !== anchor && !parent.has(id);

  tiers.forEach((edges, tier) => {
    const within = edges.filter((e) => ids.has(e.source) && ids.has(e.target));
    const adj = adjacency(ids, within);
    const direct = neighbours(anchor, within, degree, Infinity).filter(free);
    let frontier = tier === 0 ? direct.slice(0, maxHeads) : [...parent.keys()];
    if (tier === 0) for (const h of frontier) assign(h, anchor);

    for (;;) {
      const reached = new Map<string, string[]>();
      for (const from of frontier) {
        for (const to of adj.get(from) ?? []) {
          if (!free(to)) continue;
          const list = reached.get(to);
          if (list) list.push(from);
          else reached.set(to, [from]);
        }
      }
      if (reached.size === 0) {
        // Linked to the anchor and to nothing placed: a cluster of its own after all.
        const rest = direct.filter(free);
        if (rest.length === 0) break;
        for (const h of rest) assign(h, anchor);
        frontier = rest;
        continue;
      }
      const next = [...reached.keys()].sort(rank);
      for (const id of next) {
        const from = reached.get(id)!;
        assign(id, from.reduce((best, p) => ((kids.get(p) ?? 0) < (kids.get(best) ?? 0) ? p : best)));
      }
      frontier = next;
    }
  });

  let placed = true;
  while (placed && hints) {
    placed = false;
    for (const id of ids) {
      const from = hints.get(id);
      if (!free(id) || !from || (from !== anchor && !parent.has(from))) continue;
      assign(id, from);
      placed = true;
    }
  }
  for (const id of [...ids].filter(free).sort(rank)) assign(id, anchor);
  return parent;
}

/** Hops from the anchor along the tree: 0 for the anchor, 1 for a cluster's head. */
export function depthsOf(anchor: string, parent: Map<string, string>): Map<string, number> {
  const out = new Map([[anchor, 0]]);
  const of = (id: string): number => {
    const known = out.get(id);
    if (known !== undefined) return known;
    const d = of(parent.get(id) ?? anchor) + 1;
    out.set(id, d);
    return d;
  };
  for (const id of parent.keys()) of(id);
  return out;
}

/**
 * Positions for a cluster tree: the anchor's card centred on the origin, clusters split left and
 * right so the two sides are about as tall, one column per hop with smaller cards further out,
 * each parent level with the middle of its children. Cards never overlap, so nothing is
 * decluttered afterwards. With `grow` every cluster runs that one way (1 right, -1 left), for a
 * page that sits at one side of what is drawn round it.
 */
export function layoutClusters(anchor: string, parent: Map<string, string>, grow: -1 | 0 | 1 = 0): Record<string, XY> {
  const children = new Map<string, string[]>();
  for (const [child, to] of parent) {
    const list = children.get(to);
    if (list) list.push(child);
    else children.set(to, [child]);
  }
  /** Height of a page's card or of the stack of its children's blocks, whichever is taller. */
  const block = new Map<string, number>();
  const stack = (id: string) =>
    (children.get(id) ?? []).reduce((sum, c, i) => sum + (i ? ROW_GAP : 0) + block.get(c)!, 0);
  const measure = (id: string, depth: number): number => {
    for (const c of children.get(id) ?? []) measure(c, depth + 1);
    const h = Math.max(cardSize(depth).h, stack(id));
    block.set(id, h);
    return h;
  };

  const sides: { heads: string[]; height: number }[] = [
    { heads: [], height: 0 },
    { heads: [], height: 0 },
  ];
  for (const head of children.get(anchor) ?? []) {
    const side = !grow && sides[1].height < sides[0].height ? sides[1] : sides[0];
    side.heads.push(head);
    side.height += measure(head, 1);
  }

  const centre = cardSize(0);
  const out: Record<string, XY> = { [anchor]: { x: -centre.w / 2, y: -centre.h / 2 } };
  const place = (id: string, depth: number, reach: number, top: number, dir: 1 | -1) => {
    const { w, h } = cardSize(depth);
    const height = block.get(id)!;
    out[id] = { x: dir === 1 ? reach : -reach - w, y: top + (height - h) / 2 };
    let at = top + (height - stack(id)) / 2;
    for (const c of children.get(id) ?? []) {
      place(c, depth + 1, reach + w + COL_GAP, at, dir);
      at += block.get(c)! + ROW_GAP;
    }
  };
  sides.forEach((side, i) => {
    const total = side.height + Math.max(0, side.heads.length - 1) * CLUSTER_GAP;
    let at = -total / 2;
    for (const head of side.heads) {
      place(head, 1, ANCHOR_HALF + COL_GAP, at, grow || (i === 0 ? 1 : -1));
      at += block.get(head)! + CLUSTER_GAP;
    }
  });
  return out;
}

const pairKey = (a: string, b: string) => (a < b ? `${a}|${b}` : `${b}|${a}`);

/** The parent–child pairs of a tree, as the keys `ViewState.skeleton` holds. */
export function skeletonOf(parent: Map<string, string>): Set<string> {
  return new Set([...parent].map(([child, to]) => pairKey(child, to)));
}

/**
 * Clusters run sideways, so an edge between columns leaves and enters by the cards' sides (the
 * `sr`/`sl`/`tl`/`tr` handles of WikiNode). An edge within a column keeps top and bottom.
 */
export function withSideHandles<E extends Edge>(edges: E[], positions: Record<string, XY>): E[] {
  return edges.map((e) => {
    const from = positions[e.source];
    const to = positions[e.target];
    if (!from || !to || Math.abs(to.x - from.x) < cardSize(Infinity).w / 2) return e;
    return to.x > from.x
      ? { ...e, sourceHandle: "sr", targetHandle: "tl" }
      : { ...e, sourceHandle: "sl", targetHandle: "tr" };
  });
}
