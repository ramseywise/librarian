import { useCallback, useDeferredValue, useEffect, useMemo, useRef, useState } from "react";
import { createPortal } from "react-dom";
import {
  ReactFlow,
  Background,
  Controls,
  useNodesState,
  useNodesInitialized,
  useReactFlow,
  ReactFlowProvider,
  BackgroundVariant,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";

import { Atlas, type AtlasPageInfo } from "./atlas/Atlas";
import { ClusterInset } from "./ClusterInset";
import { HopField } from "./HopField";
import { MapBar } from "./MapBar";
import { MapSearch } from "./MapSearch";
import { WikiNode, type WikiFlowNode } from "./WikiNode";
import { NodeCardContext, type NodeCard } from "./nodeCard";
import { NodeDetailPanel } from "./NodeDetailPanel";
import { FiltersPanel } from "./TagFilterPanel";
import { MapControls } from "./MapControls";
import { ConnectChips } from "./EdgeTogglePanel";
import { fitPadding, fitToCanvasShape, layoutClusterField, positionsOf } from "./wikiGraphLayout";
import { ResourceNotice } from "./ResourceNotice";
import { useCurriculum } from "../hooks/useCurriculum";
import { useGlossary } from "../hooks/useGlossary";
import { useHashRoute } from "../hooks/useHashRoute";
import { useWikiData } from "../hooks/useWikiData";
import { sectorIdOf, sectorsOf } from "../utils/atlas";
import { facetPending, facetsOf, isModuleFacet, modulesOf, rankGroupsOf, withCourseGroups } from "../utils/curriculum";
import { COMMON_TERM, RANK_WEIGHTS, rankGraph, rankedNeighbourhood, whyLinked, type RankKind } from "../utils/neighbourRank";
import { searchMap } from "../utils/glossary";
import { clusterTree, depthsOf, layoutClusters, skeletonOf, withSideHandles } from "../utils/clusterLayout";
import { growDir, hopsFrom } from "../utils/hopField";
import { applyDagreLayout, declutter, placeMissingNodes, type XY } from "../utils/layout";
import {
  applyView,
  degreeOf,
  expandBridges,
  expandFrom,
  filterPrimaryIds,
  courseOrderEdges,
  moduleEdges,
  neighbours,
  pageNeighbourhood,
  relatedGroups,
  termEdges,
  renderIds as computeRenderIds,
  visibleEdges,
  type ViewState,
} from "../utils/graphView";
import {
  ATLAS,
  DEFAULT_CAP,
  PAGE_CAP,
  levelKey,
  mapPath,
  MAX_CAP,
  parentOf,
  parseMapRoute,
  replaceRoute,
  type Grouping,
  type MapView,
} from "../utils/mapRoute";
import { useTheme } from "../hooks/useTheme";
import { topicColor } from "../theme/domains";
import "./graph.css";
import "./filter.css";
import "../theme/atlas.css";
import type { EdgeVisibility, LayoutMode, SelectedNode, WikiNodeData } from "../types";

const NODE_TYPES = { wikiNode: WikiNode };
const NO_NODES: WikiFlowNode[] = [];
const NO_IDS = new Set<string>();
const NO_CITED = new Set<string>();
/** At or past this many pages in the filter, a global view carries little: the atlas is the way in. */
const ALL_NODES_LIMIT = 1000;
const SEMANTIC_DELAY_MS = 1500;
const FIRST_NODE_MARK = "graph:first-node";
/** Flow units kept above a page's level for the bar over the canvas; it fits at about half zoom. */
/** A little longer than the `.is-moving` transition in graph.css. */
const MOVE_MS = 650;

interface WikiGraphProps {
  /** The slot under the chat, for the clusters in view and the map's controls. Without one they sit in the map's corner. */
  dock?: HTMLElement | null;
  /**
   * The side column's Reading slot. Given one, the selected page's card is read there and nodes
   * on the canvas stay compact; without one the node opens into its card in place.
   */
  reading?: HTMLElement | null;
  highlightedPages?: Set<string>;
  /** Wiki page to pan/zoom to — set when arriving from a course lesson's concept link. */
  focusPage?: string | null;
  onNodeSelect?: (node: SelectedNode | null) => void;
  /** The selected page: its node is drawn as an open card. */
  selectedId?: string | null;
  /** The question the last chat answer was for, named on the card of a page it cited. */
  lastQuery?: string;
  /** A tag on an open card toggles its filter; `activePageTags` are the ones switched on. */
  onTagClick?: (tag: string) => void;
  activePageTags?: Set<string>;
  onOpenLesson?: (lessonId: string) => void;
  /** Called once `focusPage` has been applied (node found, view fitted, node selected). */
  onFocusApplied?: () => void;
  onBrief?: (domain: string) => void;
  activeTags: Set<string>;
  onActiveTagsChange: (tags: Set<string>) => void;
}

function WikiGraphInner({
  highlightedPages,
  focusPage,
  onNodeSelect,
  selectedId = null,
  lastQuery = "",
  onTagClick,
  activePageTags,
  onOpenLesson,
  onFocusApplied,
  dock,
  reading = null,
  onBrief,
  activeTags,
  onActiveTagsChange,
}: WikiGraphProps) {
  // Semantic edges arrive in the background after first paint. Tag-shared stays off until asked
  // for: deriving them is ~42k pairs, and under a large filter they were most of the edge count.
  // Shared terms start off too: a term star per glossary term is a lot of lines on a page's level.
  // Same module and course order start off: the dock offers links against similarity only, and the
  // course's own ties are in the focused map's Map popover.
  const [edgeVis, setEdgeVis] = useState<EdgeVisibility>({
    wikilink: true,
    semantic: true,
    module: false,
    term: false,
    "course-order": false,
    "tag-shared": false,
  });
  // The level of the map lives in the route. Under the courses tabs the graph stays mounted and
  // the route isn't a map route, so it keeps the level it had.
  const [route, navigate] = useHashRoute();
  const parsedView = useMemo(() => parseMapRoute(route), [route]);
  const [mapView, setMapView] = useState<MapView>(() => parsedView ?? ATLAS);
  if (parsedView && mapPath(parsedView) !== mapPath(mapView)) setMapView(parsedView);
  const onAtlas = mapView.level === "atlas";
  const {
    baseNodes,
    wikilinkEdges,
    domains,
    areas,
    tagSharedEdges,
    semanticEdges,
    fetchSemanticEdges,
    umapPositions,
    umapFailed,
    loadUmapPositions,
    connected,
    full,
    error: mapError,
    retry: retryMap,
  } = useWikiData({ tagShared: edgeVis["tag-shared"], live: !onAtlas });
  const [layout, setLayout] = useState<LayoutMode>("umap-semantic");
  const onAll = mapView.level === "all";
  const grouping: Grouping = mapView.level === "all" ? "domain" : mapView.grouping;
  const anchorId = mapView.level === "page" ? mapView.page : null;
  const [searchText, setSearchText] = useState("");
  const deferredSearch = useDeferredValue(searchText);
  /** Pages revealed by clicks since the level changed; they stay rendered. */
  const [revealed, setRevealed] = useState<Set<string>>(() => new Set());
  /** The page whose click revealed each of them: where the cluster layout hangs it. */
  const revealedFrom = useRef(new Map<string, string>());
  const [focusNodeId, setFocusNodeId] = useState<string | null>(null);
  const [loadingSemantic, setLoadingSemantic] = useState(false);
  const { fitView, fitBounds } = useReactFlow();

  const hasNodes = baseNodes.length > 0;
  const theme = useTheme();
  const { data: curriculum, error: curriculumError, retry: retryCurriculum } = useCurriculum(baseNodes, hasNodes);
  const { data: glossary, error: glossaryError, retry: retryGlossary } = useGlossary(baseNodes, hasNodes);
  const facets = useMemo(() => facetsOf(curriculum, baseNodes, glossary, areas), [curriculum, baseNodes, glossary, areas]);
  const termTitle = useMemo(() => new Map((glossary?.terms ?? []).map((t) => [t.id, t.label])), [glossary]);
  /** Pages some lesson links; the atlas draws the rest faint. Null until the curriculum is in. */
  const taught = useMemo(() => (curriculum ? new Set(Object.keys(curriculum.primaryCourse)) : null), [curriculum]);
  const pageModules = useMemo(() => modulesOf(curriculum), [curriculum]);
  const loadingUmap = !onAtlas && layout === "umap-semantic" && hasNodes && !umapPositions && !umapFailed;

  // UMAP positions are fetched once, on first use; the hook caches them. `connected` retries a
  // request that failed while the server restarted, which would otherwise stick on the fallback.
  useEffect(() => {
    if (!onAtlas && layout === "umap-semantic" && hasNodes) void loadUmapPositions();
  }, [onAtlas, layout, hasNodes, connected, loadUmapPositions]);

  // Neighbourhoods expand over wikilinks, plus semantic edges while they're shown — never over
  // tag-shared edges, whose near-cliques pulled most of the graph into every click.
  const linkEdges = useMemo(
    () => (edgeVis.semantic ? [...wikilinkEdges, ...semanticEdges] : wikilinkEdges),
    [edgeVis.semantic, wikilinkEdges, semanticEdges],
  );
  const degree = useMemo(() => degreeOf(wikilinkEdges), [wikilinkEdges]);

  // What a click pulls in: a turn each from every connection that is switched on.
  const nodeById = useMemo(() => new Map(baseNodes.map((n) => [n.id, n])), [baseNodes]);
  const reveal = useCallback(
    (id: string) => {
      const dir = nodeById.get(id)?.data.domain[0];
      const found = expandFrom(
        id,
        {
          wikilink: edgeVis.wikilink ? wikilinkEdges : undefined,
          semantic: edgeVis.semantic ? semanticEdges : undefined,
          moduleMates: edgeVis.module
            ? (p) => (pageModules.get(p) ?? []).flatMap((m) => [...(facets.get(m) ?? [])])
            : undefined,
          // Across directories only, as the shared-tag layer draws them.
          tagMates: edgeVis["tag-shared"]
            ? (p) =>
                (nodeById.get(p)?.data.tags ?? [])
                  .filter((t) => domains.includes(t))
                  .flatMap((t) => [...(facets.get(`tag:${t}`) ?? [])])
                  .filter((other) => nodeById.get(other)?.data.domain[0] !== dir)
            : undefined,
        },
        degree,
      );
      return found.length ? found : neighbours(id, wikilinkEdges, degree);
    },
    [nodeById, edgeVis, wikilinkEdges, semanticEdges, pageModules, facets, domains, degree],
  );

  // --- Level: the atlas's sectors, and the subset a focused level hands to React Flow -----
  const atlasPages = useMemo(
    () => baseNodes.map((n) => ({ id: n.id, domain: n.data.domain[0] ?? n.data.typeTag })),
    [baseNodes],
  );
  const sectors = useMemo(
    () => sectorsOf(atlasPages, degree, grouping, areas, theme),
    [atlasPages, degree, grouping, areas, theme],
  );
  const pageInfo = useMemo(
    () =>
      new Map<string, AtlasPageInfo>(
        baseNodes.map((n) => [
          n.id,
          { title: n.data.title, summary: n.data.summary, tags: n.data.tags, path: n.data.path, origins: n.data.origins, sourceCount: n.data.sourceCount },
        ]),
      ),
    [baseNodes],
  );
  const primaryIds = useMemo(() => filterPrimaryIds(baseNodes, activeTags, facets), [baseNodes, activeTags, facets]);
  const sectorId = mapView.level === "sector" || mapView.level === "page" ? mapView.sector : null;
  const sector = useMemo(() => sectors.find((s) => s.id === sectorId) ?? null, [sectors, sectorId]);
  const cap = mapView.level === "sector" || mapView.level === "page" ? mapView.cap : DEFAULT_CAP;

  // A page's level is ranked over every connection that is switched on (utils/neighbourRank), so
  // switching a kind off changes which pages it holds, not only which lines are drawn.
  const rankGroups = useMemo(() => {
    const { groups, readingOrder } = rankGroupsOf(curriculum, glossary);
    const known = groups.map((g) => ({ ...g, pages: g.pages.filter((p) => pageInfo.has(p)) }));
    return { groups: known, readingOrder };
  }, [curriculum, glossary, pageInfo]);
  const rankWeights = useMemo(() => {
    const on: Record<RankKind, boolean> = {
      typed: edgeVis.wikilink,
      link: edgeVis.wikilink,
      module: edgeVis.module,
      // Course order runs between notes, so notes are in while either is on.
      note: edgeVis.module || edgeVis["course-order"],
      term: edgeVis.term,
      course: edgeVis["course-order"],
      similar: edgeVis.semantic,
    };
    return Object.fromEntries(Object.entries(RANK_WEIGHTS).filter(([k]) => on[k as RankKind]));
  }, [edgeVis]);
  const ranking = useMemo(
    () => rankGraph({ links: wikilinkEdges, similar: semanticEdges, ...rankGroups, weights: rankWeights }),
    [wikilinkEdges, semanticEdges, rankGroups, rankWeights],
  );

  const scope = useMemo<{ ids: Set<string>; total: number; hops?: number } | null>(() => {
    if (mapView.level === "sector" && sector) {
      const ids = primaryIds ? sector.pageIds.filter((id) => primaryIds.has(id)) : sector.pageIds;
      return { ids: new Set(ids.slice(0, cap)), total: ids.length };
    }
    if (mapView.level === "page" && pageInfo.has(mapView.page)) {
      // With every kind that reaches it switched off, fall back to its links by distance.
      if (!ranking.out.get(mapView.page)?.length) return pageNeighbourhood(mapView.page, wikilinkEdges, degree, cap);
      return rankedNeighbourhood(mapView.page, ranking, cap);
    }
    return null;
  }, [mapView, sector, primaryIds, cap, pageInfo, wikilinkEdges, degree, ranking]);

  // A link can outlive what it names: an unknown or private page, a retired sector, or an "All"
  // that the filter no longer makes small enough. Nothing here says which ids exist.
  const pagesInFilter = primaryIds?.size ?? baseNodes.length;
  const facetsPending = [...activeTags].some((t) => facetPending(t, curriculum, glossary));
  // The link names a filter the panel has not taken up yet.
  const restoringTags = mapView.level === "all" && mapView.tags.some((t) => !activeTags.has(t));
  useEffect(() => {
    if (!hasNodes || parsedView === null) return;
    const bad =
      (mapView.level === "sector" && !sector) ||
      (mapView.level === "page" && (!pageInfo.has(mapView.page) || !sector)) ||
      (mapView.level === "all" && !facetsPending && !restoringTags && pagesInFilter >= ALL_NODES_LIMIT);
    if (bad) replaceRoute("/");
  }, [hasNodes, parsedView, mapView, sector, pageInfo, facetsPending, restoringTags, pagesInFilter]);

  // --- Layout: base positions (UMAP or dagre), then the filter subgraph on top ----------
  const baseLayout = useMemo<Record<string, XY> | null>(() => {
    if (!hasNodes || onAtlas) return null;
    if (layout === "umap-semantic") {
      if (umapPositions) return placeMissingNodes(baseNodes, umapPositions, wikilinkEdges);
      if (!umapFailed) return null; // still loading: render nothing rather than a pile at (0,0)
      // UMAP unavailable on the server: fall back to the hierarchy layout.
    }
    return positionsOf(applyDagreLayout(baseNodes, wikilinkEdges));
  }, [hasNodes, onAtlas, layout, umapPositions, umapFailed, baseNodes, wikilinkEdges]);

  // The filter subgraph, for "All nodes". A focused level has narrowed by the filter already.
  const filterIds = useMemo(() => {
    if (!onAll || !primaryIds) return null;
    // A module is a precise ask, so it shows its own pages. Bridges turned one with 29 into 153.
    if ([...activeTags].some(isModuleFacet)) return primaryIds;
    return expandBridges(primaryIds, linkEdges);
  }, [onAll, primaryIds, activeTags, linkEdges]);

  // Semantic layout keeps its positions under a filter (fitView zooms to the subgraph);
  // Hierarchy re-runs dagre on the subgraph so it reads as its own tree.
  const scopeIds = scope?.ids ?? null;
  const positions = useMemo(() => {
    const within = filterIds ?? scopeIds;
    if (!baseLayout || !within || layout !== "dagre") return baseLayout;
    const sub = baseNodes.filter((n) => within.has(n.id));
    // Wikilinks first so they win the one-parent-per-node choice in applyDagreLayout.
    const subEdges = linkEdges.filter((e) => within.has(e.source) && within.has(e.target));
    return { ...baseLayout, ...positionsOf(applyDagreLayout(sub, subEdges)) };
  }, [baseLayout, filterIds, scopeIds, layout, baseNodes, linkEdges]);

  // A new filter is a new view: drop the click focus so its neighbourhood doesn't linger
  // beside (and dim) the filter subgraph.
  useEffect(() => {
    setFocusNodeId(null);
  }, [activeTags]);

  // --- View: what is rendered, dimming / highlight, and the rendered edges ---------------
  const focusIds = useMemo(() => {
    if (!focusNodeId) return null;
    return new Set([focusNodeId, ...reveal(focusNodeId)]);
  }, [focusNodeId, reveal]);

  const search = useMemo(() => searchMap(deferredSearch, baseNodes, glossary), [deferredSearch, baseNodes, glossary]);

  // Arriving from a lesson highlights just that page, and a focused level then already marks it:
  // don't let that one citation dim the neighbourhood the level exists to show.
  const chatHighlight = useMemo(
    () => (highlightedPages?.size === 1 && anchorId && highlightedPages.has(anchorId) ? undefined : highlightedPages),
    [highlightedPages, anchorId],
  );

  const view = useMemo<ViewState>(
    () => ({
      chatHighlight,
      focusId: focusNodeId,
      focusIds,
      filterIds,
      activeTags,
      facets,
      anchorId,
      searchIds: search?.lit ?? null,
      openId: selectedId,
    }),
    [chatHighlight, focusNodeId, focusIds, filterIds, activeTags, facets, anchorId, search, selectedId],
  );

  const rendered = useMemo(
    () =>
      onAtlas ? NO_IDS : computeRenderIds(onAll && !filterIds, scopeIds ?? NO_IDS, revealed, view),
    [onAtlas, onAll, filterIds, scopeIds, revealed, view],
  );

  // A page's level arranged by similarity was 25 cards with every link between them. It is laid
  // out as clusters instead: the page, its top related pages, and what each of those leads to.
  // "By links" still gives the top-down tree.
  const clusters = useMemo(() => {
    if (layout !== "umap-semantic" || !anchorId || !rendered?.has(anchorId)) return null;
    const parent = clusterTree(anchorId, rendered, [wikilinkEdges, semanticEdges], degree, revealedFrom.current);
    return { positions: layoutClusters(anchorId, parent, growDir(sectors, anchorId)), skeleton: skeletonOf(parent), depth: depthsOf(anchorId, parent) };
  }, [layout, anchorId, rendered, wikilinkEdges, semanticEdges, degree, sectors]);
  const skeleton = clusters?.skeleton ?? null;
  const edgeView = useMemo<ViewState>(() => ({ ...view, skeleton }), [view, skeleton]);

  // UMAP positions overlap where pages are similar; spread just the rendered cards.
  // Dagre output never overlaps, so a dagre-laid-out filter subgraph is left alone.
  const placed = useMemo(() => {
    if (!positions || layout !== "umap-semantic") return positions;
    if (clusters) return { ...positions, ...clusters.positions };
    const spread = { ...positions, ...declutter(positions, rendered ?? baseNodes.map((n) => n.id)) };
    return scopeIds ? fitToCanvasShape(spread, scopeIds) : spread;
  }, [positions, layout, clusters, rendered, baseNodes, scopeIds]);

  const depth = clusters?.depth;
  const pageNodes = useMemo(() => {
    if (!placed || onAtlas) return NO_NODES;
    const laidOut = baseNodes
      .filter((n) => !rendered || rendered.has(n.id))
      .map((n) => ({
        ...n,
        position: placed[n.id] ?? n.position,
        data: depth ? { ...n.data, depth: depth.get(n.id) } : n.data,
      }));
    return withCourseGroups(applyView(laidOut, view), curriculum, theme);
  }, [placed, onAtlas, baseNodes, rendered, depth, view, curriculum, theme]);

  // Behind the clusters, the wiki around them: every page a point in a circle, sector by sector,
  // sized by how many links it is from the open page.
  const reach = useMemo(
    () => (clusters && anchorId ? hopsFrom(anchorId, wikilinkEdges) : null),
    [clusters, anchorId, wikilinkEdges],
  );
  const field = useMemo(() => {
    if (!clusters || !reach) return null;
    return layoutClusterField(clusters.positions, clusters.depth, reach, sectors, anchorId);
  }, [clusters, reach, sectors, anchorId]);
  const frame = field?.frame ?? null;

  const sameModule = useMemo(
    () => (edgeVis.module ? moduleEdges(pageNodes.map((n) => n.id), pageModules, degree) : []),
    [edgeVis.module, pageNodes, pageModules, degree],
  );
  const sharedTerm = useMemo(
    () => (edgeVis.term && glossary ? termEdges(pageNodes.map((n) => n.id), glossary.mentions, degree, COMMON_TERM) : []),
    [edgeVis.term, glossary, pageNodes, degree],
  );
  const notePages = useMemo(
    () => (curriculum?.courses ?? []).flatMap((c) => c.modules.map((m) => m.notes.map((n) => n.pageIds))),
    [curriculum],
  );
  const courseOrder = useMemo(
    () => (edgeVis["course-order"] ? courseOrderEdges(pageNodes.map((n) => n.id), notePages) : []),
    [edgeVis, pageNodes, notePages],
  );
  const edges = useMemo(() => {
    const shown = visibleEdges(
      {
        wikilink: wikilinkEdges,
        semantic: semanticEdges,
        tagShared: tagSharedEdges,
        module: sameModule,
        term: sharedTerm,
        courseOrder,
      },
      edgeVis,
      pageNodes,
      edgeView,
    );
    return clusters ? withSideHandles(shown, clusters.positions) : shown;
  }, [wikilinkEdges, semanticEdges, tagSharedEdges, sameModule, sharedTerm, courseOrder, edgeVis, pageNodes, edgeView, clusters]);

  // --- Sync derived nodes into React Flow state (keeps node dragging working) -----------
  // A new `positions` object means a relayout: take the new positions and refit. A new
  // filter or a new focused subset also refits, even when positions are unchanged. A new
  // `placed` (declutter re-ran because the rendered set changed) takes the new positions
  // without a refit, so revealed cards don't land on top of stale ones. Otherwise only
  // view flags changed: keep where the user dragged nodes to.
  const [nodes, setNodes, onNodesChange] = useNodesState<WikiFlowNode>([]);
  const lastPositions = useRef<Record<string, XY> | null>(null);
  const lastPlaced = useRef<Record<string, XY> | null>(null);
  const lastFrame = useRef<{ filterIds: Set<string> | null; scopeIds: Set<string> | null; onAll: boolean } | null>(null);
  const pendingFit = useRef(false);

  useEffect(() => {
    const relayout = lastPositions.current !== positions;
    lastPositions.current = positions;
    const reframe =
      lastFrame.current?.filterIds !== filterIds ||
      lastFrame.current?.scopeIds !== scopeIds ||
      lastFrame.current?.onAll !== onAll;
    lastFrame.current = { filterIds, scopeIds, onAll };
    if ((relayout || reframe) && positions) pendingFit.current = true;
    const moved = relayout || reframe || lastPlaced.current !== placed;
    lastPlaced.current = placed;
    setNodes((prev) => {
      const prevById = new Map(prev.map((n) => [n.id, n]));
      return pageNodes.map((n) => {
        const p = prevById.get(n.id);
        if (!p) return n;
        return {
          ...n,
          position: moved ? n.position : p.position,
          measured: p.measured,
          selected: p.selected,
        };
      });
    });
  }, [pageNodes, positions, placed, filterIds, scopeIds, onAll, setNodes]);

  const refit = useCallback(() => {
    const ids = filterIds;
    requestAnimationFrame(() => {
      if (ids) {
        void fitView({ nodes: [...ids].map((id) => ({ id })), padding: fitPadding(0.3), duration: 400 });
      } else if (frame) {
        // The clusters and the circle of points around them.
        void fitBounds({ x: frame.x, y: frame.y, width: frame.w, height: frame.h }, { padding: 0.03, duration: 300 });
      } else {
        void fitView({ padding: fitPadding(0.08), duration: 300 });
      }
    });
  }, [filterIds, frame, fitView, fitBounds]);
  const refitRef = useRef(refit);
  useEffect(() => {
    refitRef.current = refit;
  });
  // Cards the semantic edges place late grow the clusters without a relayout: fit again.
  const lastBounds = useRef("");
  useEffect(() => {
    const bounds = frame ? `${frame.x},${frame.y},${frame.w},${frame.h}` : "";
    if (bounds && lastBounds.current && bounds !== lastBounds.current) pendingFit.current = true;
    lastBounds.current = bounds;
    if (!pendingFit.current || !nodes.length) return;
    pendingFit.current = false;
    refit();
  }, [nodes, refit, frame]);
  // React Flow's own first fit (the `fitView` prop) runs once the cards are measured and takes in
  // the cards only: fit to the frame after it.
  const measured = useNodesInitialized();
  useEffect(() => {
    if (measured && frame) refitRef.current();
    // eslint-disable-next-line react-hooks/exhaustive-deps -- once per mount of the cards
  }, [measured]);

  // The canvas changes width when the sidebar or the chat slides: fit the level to the new room.
  const canvasRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const el = canvasRef.current;
    if (!el || typeof ResizeObserver === "undefined") return;
    let width = el.clientWidth;
    let timer: ReturnType<typeof setTimeout> | undefined;
    const observer = new ResizeObserver(() => {
      if (el.clientWidth === width) return;
      width = el.clientWidth;
      clearTimeout(timer);
      timer = setTimeout(() => refitRef.current(), 250);
    });
    observer.observe(el);
    return () => {
      observer.disconnect();
      clearTimeout(timer);
    };
  }, []);

  // --- focusPage (arriving from a lesson, or a chat citation): go to that page's level ----
  const hasRenderedNodes = nodes.length > 0;
  useEffect(() => {
    if (!focusPage || !hasNodes) return;
    const page = atlasPages.find((p) => p.id === focusPage);
    // An unknown or private page: drop the request rather than leave it pending, so it can't
    // fire later on an unrelated graph update.
    if (page) {
      navigate(
        mapPath({ level: "page", grouping, sector: sectorIdOf(page, grouping, areas), page: page.id, cap: PAGE_CAP }),
      );
    }
    onFocusApplied?.();
  }, [focusPage, hasNodes, atlasPages, grouping, areas, navigate, onFocusApplied]);

  // A new level starts clean, and a page's level opens that page's panel. Keyed on the level, not
  // on the node objects, so a graph update can't reopen a panel you closed. The cap is part of
  // no key: widening a view keeps what you clicked.
  const key = levelKey(mapView);
  const appliedLevel = useRef<string | null>(null);
  useEffect(() => {
    if (!hasNodes || appliedLevel.current === key) return;
    appliedLevel.current = key;
    setRevealed(new Set());
    revealedFrom.current = new Map();
    setFocusNodeId(null);
    setSearchText("");
    const node = anchorId ? baseNodes.find((n) => n.id === anchorId) : null;
    onNodeSelect?.(node ? { id: node.id, data: node.data } : null);
  }, [key, hasNodes, anchorId, baseNodes, onNodeSelect]);

  // From one page's level to another's, the cards that stay glide to their new places.
  // Picking a sector on the circle moves the view in on that part of it; the level itself, and
  // so the circle and the cards, stay as they are. Picking it again goes back out.
  const [focusSector, setFocusSector] = useState<string | null>(null);
  const pickSector = useCallback(
    (id: string) => {
      const arc = field?.arcs.find((a) => field.sectors[a.sector].id === id);
      if (!arc || id === focusSector) {
        setFocusSector(null);
        return refit();
      }
      setFocusSector(id);
      void fitBounds({ x: arc.box.x, y: arc.box.y, width: arc.box.w, height: arc.box.h }, { padding: 0.12, duration: 700 });
    },
    [field, focusSector, refit, fitBounds],
  );
  const [moving, setMoving] = useState(false);
  const lastLevel = useRef<string | null>(null);
  useEffect(() => {
    const first = lastLevel.current === null;
    lastLevel.current = key;
    setFocusSector(null);
    if (first || !anchorId) return;
    setMoving(true);
    const timer = setTimeout(() => setMoving(false), MOVE_MS);
    return () => clearTimeout(timer);
  }, [key, anchorId]);

  // Coming back to the atlas, the camera eases out of where you were.
  const lastFocused = useRef<{ sector: string; page?: string } | null>(null);
  const [enterFrom, setEnterFrom] = useState<{ sector: string; page?: string } | null>(null);
  useEffect(() => {
    if (mapView.level === "sector") lastFocused.current = { sector: mapView.sector };
    else if (mapView.level === "page") lastFocused.current = { sector: mapView.sector, page: mapView.page };
    else if (mapView.level === "atlas") {
      setEnterFrom(lastFocused.current);
      lastFocused.current = null;
    }
  }, [mapView]);

  // "All nodes" keeps its filter in the link. A link that changed under us (first load, or a link
  // followed from a topic page) sets the filter; after that the link follows the panel.
  const tagsInLink = useRef<string | null>(null);
  useEffect(() => {
    if (mapView.level !== "all" || parsedView === null) {
      tagsInLink.current = null;
      return;
    }
    const linked = mapPath(mapView);
    if (tagsInLink.current !== linked) {
      tagsInLink.current = linked;
      if (mapView.tags.length > 0) {
        onActiveTagsChange(new Set(mapView.tags));
        return;
      }
    }
    const path = mapPath({ level: "all", tags: [...activeTags].sort() });
    if (path !== linked) {
      tagsInLink.current = path;
      replaceRoute(path);
    }
  }, [mapView, parsedView, activeTags, onActiveTagsChange]);

  // --- Handlers ------------------------------------------------------------------------
  const handleLoadSemantic = useCallback(async () => {
    setLoadingSemantic(true);
    try {
      await fetchSemanticEdges();
    } catch {
      // Toggle stays on with no edges; the next toggle retries.
    } finally {
      setLoadingSemantic(false);
    }
  }, [fetchSemanticEdges]);

  // The first paint doesn't wait for these. Retries on reconnect while none have landed.
  const hasSemanticEdges = semanticEdges.length > 0;
  useEffect(() => {
    // The atlas draws no React Flow nodes but its cards list similar pages, so it loads them too.
    if (!(hasRenderedNodes || (onAtlas && hasNodes)) || !connected || !edgeVis.semantic || hasSemanticEdges) return;
    const timer = setTimeout(() => void handleLoadSemantic(), SEMANTIC_DELAY_MS);
    return () => clearTimeout(timer);
  }, [hasRenderedNodes, onAtlas, hasNodes, connected, edgeVis.semantic, hasSemanticEdges, handleLoadSemantic]);

  // Clicking a node focuses it and keeps its neighbours on the canvas, so the graph can be
  // walked outward click by click. Clicking it again unfocuses. In a clustered level the walk is
  // a move instead: the clicked page becomes the middle, with its own clusters around it.
  const clustered = clusters !== null;
  const handleNodeClick = useCallback(
    (_: React.MouseEvent, node: WikiFlowNode) => {
      if (clustered && node.id !== anchorId) return openPageRef.current(node.id);
      setFocusNodeId((prev) => (prev === node.id ? null : node.id));
      const found = reveal(node.id);
      for (const id of found) if (!revealedFrom.current.has(id)) revealedFrom.current.set(id, node.id);
      setRevealed((prev) => {
        const next = new Set(prev);
        next.add(node.id);
        for (const id of found) next.add(id);
        return next.size === prev.size ? prev : next;
      });
      onNodeSelect?.({ id: node.id, data: node.data as WikiNodeData });
    },
    [onNodeSelect, reveal, clustered, anchorId],
  );

  const handleResetRevealed = useCallback(() => {
    setRevealed(new Set());
    revealedFrom.current = new Map();
    setFocusNodeId(null);
  }, []);

  const openPage = useCallback(
    (pageId: string) => {
      const page = atlasPages.find((p) => p.id === pageId);
      if (!page) return;
      navigate(
        mapPath({ level: "page", grouping, sector: sectorIdOf(page, grouping, areas), page: pageId, cap: PAGE_CAP }),
      );
    },
    [atlasPages, grouping, areas, navigate],
  );

  const openPageRef = useRef(openPage);
  useEffect(() => {
    openPageRef.current = openPage;
  });
  const titleOf = useCallback((id: string) => pageInfo.get(id)?.title ?? id, [pageInfo]);

  // A page's most similar pages by embedding, best first; empty until the edges load.
  const similarOf = useMemo(() => {
    const by = new Map<string, { id: string; title: string; score: number }[]>();
    for (const e of semanticEdges) {
      const score = e.data?.score;
      if (score == null) continue;
      for (const [a, b] of [[e.source, e.target], [e.target, e.source]]) {
        const list = by.get(a) ?? [];
        list.push({ id: b, title: pageInfo.get(b)?.title ?? b, score });
        by.set(a, list);
      }
    }
    for (const list of by.values()) list.sort((x, y) => y.score - x.score);
    return (id: string) => by.get(id) ?? [];
  }, [semanticEdges, pageInfo]);

  // What an open card shows and does. Its related pages are the page's wikilinks by kind of link.
  const closeCard = useCallback(() => onNodeSelect?.(null), [onNodeSelect]);
  const nodeCard = useMemo<NodeCard>(
    () => ({
      related: (id) =>
        relatedGroups(id, wikilinkEdges, degree).map((g) => ({
          label: g.label,
          pages: g.ids.map((p) => ({ id: p, title: pageInfo.get(p)?.title ?? p })),
          more: g.more,
        })),
      why:
        mapView.level === "page"
          ? (id) =>
              id === mapView.page
                ? []
                : whyLinked(mapView.page, id, { links: wikilinkEdges, similar: semanticEdges, ...rankGroups }, (t) => termTitle.get(t) ?? t)
          : undefined,
      cited: highlightedPages ?? NO_CITED,
      lastQuery,
      activeTags: activePageTags,
      onClose: closeCard,
      onOpenPage: openPage,
      onTagClick,
      onOpenLesson,
    }),
    [wikilinkEdges, semanticEdges, degree, pageInfo, mapView, rankGroups, termTitle, highlightedPages, lastQuery, activePageTags, closeCard, openPage, onTagClick, onOpenLesson],
  );

  const handleNodeDoubleClick = useCallback(
    (_: React.MouseEvent, node: WikiFlowNode) => openPage(node.id),
    [openPage],
  );

  const openSectorLevel = useCallback(
    (id: string) => navigate(mapPath({ level: "sector", grouping, sector: id, cap: DEFAULT_CAP })),
    [navigate, grouping],
  );
  const openAtlas = useCallback(() => navigate(mapPath({ level: "atlas", grouping })), [navigate, grouping]);

  const handlePaneClick = useCallback(() => {
    setFocusNodeId(null);
    onNodeSelect?.(null);
  }, [onNodeSelect]);

  // Esc goes back one level. Not while typing; a popover handles its own Esc first.
  const backTo = parentOf(mapView);
  const escapeState = useRef({ backTo, onMap: parsedView !== null });
  useEffect(() => {
    escapeState.current = { backTo, onMap: parsedView !== null };
  });
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key !== "Escape" || e.defaultPrevented) return;
      const { backTo: to, onMap } = escapeState.current;
      const target = e.target as HTMLElement | null;
      if (!to || !onMap || target?.matches?.("input, textarea")) return;
      e.preventDefault();
      navigate(mapPath(to));
    };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [navigate]);

  const miniMapColor = useCallback(
    (n: WikiFlowNode) => n.data.groupColor ?? topicColor(n.data.domain[0], n.data.topicIndex, n.data.topicCount, theme),
    [theme],
  );

  // Navigation → first node, for anyone timing a start (see performance.getEntriesByName).
  useEffect(() => {
    if (hasRenderedNodes && !performance.getEntriesByName(FIRST_NODE_MARK).length) {
      performance.mark(FIRST_NODE_MARK);
    }
  }, [hasRenderedNodes]);

  // Before the socket opens the map runs on the atlas payload, which is enough to draw it.
  const ready = connected || (hasNodes && !full);
  const statusText = !connected
    ? hasNodes
      ? full
        ? "○ reconnecting…"
        : "● ready"
      : "○ starting server…"
    : loadingUmap
      ? "● computing layout…"
      : "● live";

  const pageCount = nodes.length;
  const shownIds = useMemo(() => pageNodes.map((n) => n.id), [pageNodes]);
  const atlasMatches = primaryIds;
  const atlasLit = useMemo(() => {
    if (search) return search.lit;
    return highlightedPages?.size ? highlightedPages : null;
  }, [search, highlightedPages]);
  const shownCount = scope?.ids.size ?? 0;
  const revealedExtra = scope ? [...revealed].filter((id) => !scope.ids.has(id)).length : 0;
  const nextCap = scope && scope.total > cap ? Math.min(cap * 2, MAX_CAP, Math.max(scope.total, cap)) : null;
  const expandCap = useCallback(() => {
    if (nextCap && (mapView.level === "sector" || mapView.level === "page")) {
      navigate(mapPath({ ...mapView, cap: nextCap }));
    }
  }, [nextCap, mapView, navigate]);
  // A sector's brief: a course area briefs on its first directory, a directory on itself.
  const briefScope = sector ? (grouping === "domain" ? areas.find((a) => a.id === sector.id)?.domains[0] ?? sector.id : sector.id) : undefined;
  const clickedPage = focusNodeId && focusNodeId !== anchorId ? focusNodeId : null;
  const allNodesAllowed = pagesInFilter < ALL_NODES_LIMIT;
  const openAll = useCallback(
    () => navigate(mapPath({ level: "all", tags: [...activeTags].sort() })),
    [navigate, activeTags],
  );

  // Offered only when the filter is small enough to draw; a disabled button is just noise.
  const allNodes = !onAll && allNodesAllowed && (
    <div className="seg">
      <button
        type="button"
        className="seg-btn"
        onClick={openAll}
        title="Every page under the current filter on one canvas"
      >
        {`All nodes (${pagesInFilter.toLocaleString("en-US")})`}
      </button>
    </div>
  );

  // Connections, arrangement and the minimap act on the page canvas. The atlas draws no lines, so
  // the bar has no Map popover there rather than disabled controls.
  const mapControls = !onAtlas && (
    <MapControls
      edgeVis={edgeVis}
      onEdgeVis={setEdgeVis}
      onLoadSemantic={handleLoadSemantic}
      loadingSemantic={loadingSemantic}
      layout={layout}
      onLayout={setLayout}
      loadingUmap={loadingUmap}
      umapFailed={umapFailed}
      miniMapColor={miniMapColor}
      withEdges={!dock}
    />
  );
  // Under the chat the connections are two chips (Links, Similar) pinned under the filters, on every level. The
  // atlas draws no lines, so there they stay in place but disabled, saying where lines are drawn.
  const connections = dock && (
    <ConnectChips
      visibility={edgeVis}
      onChange={setEdgeVis}
      onLoadSemantic={handleLoadSemantic}
      loadingSemanticEdges={loadingSemantic}
      inactive={onAtlas ? "Open a sector to draw lines" : undefined}
    />
  );
  // Under the chat the bar is the map's controls only, below the clusters in view.
  const bar = hasNodes && (
    <MapBar
      controlsOnly={!!dock}
      view={mapView}
      sectorLabel={sector?.label}
      pageTitle={anchorId ? pageInfo.get(anchorId)?.title : undefined}
      shown={scope ? shownCount : onAll ? pageCount : undefined}
      total={scope ? scope.total : onAll ? baseNodes.length : undefined}
      hops={scope?.hops}
      revealedExtra={revealedExtra}
      onResetRevealed={handleResetRevealed}
      nextCap={nextCap}
      onExpand={expandCap}
      refocus={clickedPage ? { title: `Focus on ${pageInfo.get(clickedPage)?.title ?? clickedPage}`, onClick: () => openPage(clickedPage) } : null}
      onGrouping={(g) => {
        if (g === grouping) return;
        // On a page's level the page stays open and only its clusters regroup.
        const page = anchorId ? atlasPages.find((p) => p.id === anchorId) : undefined;
        navigate(
          page
            ? mapPath({ level: "page", grouping: g, sector: sectorIdOf(page, g, areas), page: page.id, cap: PAGE_CAP })
            : mapPath({ level: "atlas", grouping: g }),
        );
      }}
      search={<MapSearch value={searchText} onChange={setSearchText} result={search} onOpenPage={openPage} />}
      filters={
        <FiltersPanel
          areas={areas}
          curriculum={curriculum}
          glossary={glossary}
          facets={facets}
          activeTags={activeTags}
          onChange={onActiveTagsChange}
          onBrief={onBrief}
          grouping={grouping}
        />
      }
      activeCount={activeTags.size}
      map={mapControls || undefined}
      connections={connections || undefined}
      onBriefSector={briefScope && onBrief ? () => onBrief(briefScope) : undefined}
      extra={allNodes || undefined}
    />
  );
  // The selected page in the Reading slot, with what the canvas card would have shown.
  const readNode = reading && !onAtlas && selectedId ? baseNodes.find((n) => n.id === selectedId) : undefined;
  const readingCard = readNode ? (
    <NodeDetailPanel
      key={readNode.id}
      nodeId={readNode.id}
      data={readNode.data}
      highlighted={nodeCard.cited.has(readNode.id)}
      lastQuery={nodeCard.lastQuery}
      onClose={nodeCard.onClose}
      onTagClick={nodeCard.onTagClick}
      activeTags={nodeCard.activeTags}
      onOpenLesson={nodeCard.onOpenLesson}
      related={nodeCard.related(readNode.id)}
      why={nodeCard.why?.(readNode.id)}
      onOpenPage={nodeCard.onOpenPage}
    />
  ) : (
    <p className="reading-empty">Click a page on the map to read it here. Double-click opens its own level.</p>
  );
  const inset = !onAtlas && (
    <ClusterInset
      sectors={sectors}
      pageIds={shownIds}
      anchorId={anchorId}
      onOpenSector={openSectorLevel}
      onOpenAtlas={openAtlas}
      around={field ? { near: field.near, far: field.far, beyond: field.beyond } : undefined}
    />
  );
  return (
    <div className="graph-root">
      <div ref={canvasRef} className={`graph-canvas${moving ? " is-moving" : ""}`}>
        {/* Connection status, shown only while it is not the normal live state */}
        {statusText !== "● live" && statusText !== "● ready" && (
          <div className={`graph-status ${ready ? "graph-status--live" : "graph-status--offline"}`}>{statusText}</div>
        )}

        {(mapError || curriculumError || glossaryError) && (
          <div className="graph-notices">
            {mapError && <ResourceNotice what="The map" error={mapError} onRetry={retryMap} />}
            {curriculumError && <ResourceNotice what="The course filters" error={curriculumError} onRetry={retryCurriculum} />}
            {glossaryError && <ResourceNotice what="The term filters" error={glossaryError} onRetry={retryGlossary} />}
          </div>
        )}

        {onAtlas ? (
          hasNodes && (
            <Atlas
              sectors={sectors}
              grouping={grouping}
              info={pageInfo}
              degree={degree}
              totalLinks={wikilinkEdges.length}
              matches={atlasMatches}
              lit={atlasLit}
              taught={taught}
              related={nodeCard.related}
              similar={similarOf}
              activeTags={activePageTags}
              onTagClick={onTagClick}
              enterFrom={enterFrom}
              reading={reading}
              links={wikilinkEdges}
            />
          )
        ) : (
          <NodeCardContext.Provider value={reading ? null : nodeCard}>
          <ReactFlow
            className="map-fade-in"
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            nodeTypes={NODE_TYPES}
            onNodeClick={handleNodeClick}
            onNodeDoubleClick={handleNodeDoubleClick}
            onPaneClick={handlePaneClick}
            fitView
            fitViewOptions={{ padding: fitPadding(0.15) }}
            onlyRenderVisibleElements
            minZoom={0.1}
            maxZoom={3}
            proOptions={{ hideAttribution: true }}
          >
            <Background variant={BackgroundVariant.Dots} color="var(--border)" gap={20} />
            <Controls className="graph-flow-controls" />
            {field && <HopField field={field} titleOf={titleOf} onOpenPage={openPage} focus={focusSector} onPickSector={pickSector} showLinks={edgeVis.wikilink} />}
          </ReactFlow>
          </NodeCardContext.Provider>
        )}

        <div className="map-corner">
          {!dock && inset}
          {!dock && bar}
        </div>
        {reading && !onAtlas && createPortal(readingCard, reading)}
        {dock &&
          createPortal(
            <>
              {inset}
              {bar}
            </>,
            dock,
          )}
      </div>
    </div>
  );
}

export function WikiGraph(props: WikiGraphProps) {
  return (
    <ReactFlowProvider>
      <WikiGraphInner {...props} />
    </ReactFlowProvider>
  );
}
