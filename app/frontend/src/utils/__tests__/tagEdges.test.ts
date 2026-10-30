import { describe, expect, it } from "vitest";
import { tagSharedEdges } from "../tagEdges";
import type { WikiNodeData } from "../../types";

const node = (id: string, dir: string, tags: string[]) => ({
  id,
  data: { domain: [dir], tags } as unknown as WikiNodeData,
});

describe("tagSharedEdges", () => {
  const domains = ["rag", "eval", "memory"];

  it("links cross-directory pages sharing a domain tag", () => {
    const edges = tagSharedEdges([node("a", "rag", ["rag", "pattern"]), node("b", "eval", ["rag"])], domains);
    expect(edges).toEqual([
      { id: "ts:a->b", source: "a", target: "b", data: { edgeType: "tag-shared", sharedTags: ["rag"] } },
    ]);
  });

  it("skips same-directory pairs", () => {
    expect(tagSharedEdges([node("a", "rag", ["rag"]), node("b", "rag", ["rag"])], domains)).toEqual([]);
  });

  it("ignores non-domain tags", () => {
    expect(tagSharedEdges([node("a", "rag", ["pattern"]), node("b", "eval", ["pattern"])], domains)).toEqual([]);
  });

  it("emits one edge per pair with all shared tags, ordered ids", () => {
    const edges = tagSharedEdges(
      [node("z", "rag", ["rag", "memory"]), node("a", "eval", ["memory", "rag"])],
      domains,
    );
    expect(edges).toHaveLength(1);
    expect(edges[0].id).toBe("ts:a->z");
    expect(edges[0].data?.sharedTags).toEqual(["memory", "rag"]);
  });
});
