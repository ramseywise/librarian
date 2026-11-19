import { describe, expect, it } from "vitest";
import { RANK_WEIGHTS, rankFrom, rankGraph, rankedNeighbourhood, whyLinked, type RankGroup, type RankInput } from "../neighbourRank";

// a links to b and c. a and d share a note; the next note holds e. a and f share a term.
const links = [
  { source: "a", target: "b" },
  { source: "a", target: "c", data: { relationship: "prerequisite-for" } },
];
const groups: RankGroup[] = [
  { id: "module:x/m", kind: "module", pages: ["a", "d", "e"] },
  { id: "note:x/m/1", kind: "note", pages: ["a", "d"] },
  { id: "note:x/m/2", kind: "note", pages: ["e", "g"] },
  { id: "term:bm25", kind: "term", pages: ["a", "f"] },
];
const readingOrder = [["note:x/m/1", "note:x/m/2"]];
const input = (weights: RankInput["weights"]): RankInput => ({ links, groups, readingOrder, weights });
const order = (scores: Map<string, number>) => [...scores].sort(([, x], [, y]) => y - x).map(([id]) => id);

describe("rankGraph and rankFrom", () => {
  it("ranks a typed link over an untyped one, and the note-mate over the module-mate", () => {
    const ranked = order(rankFrom("a", rankGraph(input(RANK_WEIGHTS))));
    expect(ranked.indexOf("c")).toBeLessThan(ranked.indexOf("b"));
    expect(ranked.indexOf("d")).toBeLessThan(ranked.indexOf("e"));
  });

  it("drops what only a switched-off kind reaches", () => {
    const linksOnly = rankFrom("a", rankGraph(input({ typed: 1, link: 0.7 })));
    expect([...linksOnly.keys()].sort()).toEqual(["b", "c"]);
    const withTerms = rankFrom("a", rankGraph(input({ typed: 1, link: 0.7, term: 0.4 })));
    expect(withTerms.has("f")).toBe(true);
  });

  it("reaches a similar page only with similar meaning on", () => {
    const similar = [{ source: "h", target: "a" }];
    const linksOnly = { typed: 1, link: 0.7 };
    expect(rankFrom("a", rankGraph({ ...input(linksOnly), similar })).has("h")).toBe(false);
    expect(rankFrom("a", rankGraph({ ...input({ ...linksOnly, similar: 0.3 }), similar })).has("h")).toBe(true);
  });

  it("reaches the next note's pages only through course order", () => {
    const notes = { note: 0.6 };
    expect(rankFrom("a", rankGraph(input(notes))).has("g")).toBe(false);
    expect(rankFrom("a", rankGraph(input({ ...notes, course: 0.8 }))).has("g")).toBe(true);
  });

  it("skips groups of one page and terms on too many pages", () => {
    const common: RankGroup = { id: "term:the", kind: "term", pages: Array.from({ length: 81 }, (_, i) => (i ? `p${i}` : "a")) };
    const lone: RankGroup = { id: "note:x/m/3", kind: "note", pages: ["a"] };
    const g = rankGraph({ links: [], groups: [common, lone], readingOrder: [], weights: RANK_WEIGHTS });
    expect(g.groups.size).toBe(0);
  });
});

describe("rankedNeighbourhood", () => {
  it("keeps the anchor and its best pages, and counts a shared group as one step", () => {
    const g = rankGraph(input(RANK_WEIGHTS));
    const all = rankedNeighbourhood("a", g, 100);
    expect(all.ids.has("a")).toBe(true);
    expect(all.total).toBe(7);
    // g is a note away (course order), so two steps: a → note 1 … note 2 → g.
    expect(all.hops).toBe(2);
    const top = rankedNeighbourhood("a", g, 2);
    expect(top.ids).toEqual(new Set(["a", "c"]));
    expect(top.hops).toBe(1);
  });
});

describe("whyLinked", () => {
  it("names the link, the shared lesson and the shared term", () => {
    const why = whyLinked("a", "c", { links, groups, readingOrder });
    expect(why).toEqual(["prerequisite for"]);
    expect(whyLinked("a", "d", { links, groups, readingOrder })).toEqual(["same lesson"]);
    expect(whyLinked("a", "e", { links, groups, readingOrder })).toEqual(["same module", "lesson after"]);
    expect(whyLinked("a", "f", { links, groups, readingOrder }, () => "BM25")).toEqual(["shares BM25"]);
  });

  it("says when two pages are alike by meaning", () => {
    expect(whyLinked("a", "b", { links, similar: [{ source: "b", target: "a" }], groups, readingOrder })).toEqual(["linked", "similar meaning"]);
  });
});
