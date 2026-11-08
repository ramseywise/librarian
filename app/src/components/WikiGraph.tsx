import { useCallback, useDeferredValue, useEffect, useMemo, useRef, useState } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useReactFlow,
  ReactFlowProvider,
  BackgroundVariant,
  type FitViewOptions,
  type Node,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";

import { Atlas, type AtlasPageInfo } from "./atlas/Atlas";
import { MapBar } from "./MapBar";
import { MapSearch } from "./MapSearch";
import { TermNode } from "./TermNode";
import { WikiNode, type WikiFlowNode } from "./WikiNode";
import { EdgeTogglePanel } from "./EdgeTogglePanel";
import { GraphSidebar } from "./GraphSidebar";
import { LayoutSwitcher } from "./LayoutSwitcher";
import { useCurriculum } from "../hooks/useCurriculum";
import { useGlossary } from "../hooks/useGlossary";
import { useHashRoute } from "../hooks/useHashRoute";
import { useWikiData } from "../hooks/useWikiData";
import { sectorIdOf, sectorsOf } from "../utils/atlas";
import { facetPending, facetsOf, isModuleFacet, modulesOf, withCourseGroups } from "../utils/curriculum";
import {
  isTermNodeId,
  NO_TERMS,
  searchMap,
  termIdOf,
  termLayer,
  termNodeId,
} from "../utils/glossary";
import { applyDagreLayout, declutter, placeMissingNodes, type XY } from "../utils/layout";
import {
  applyView,
  degreeOf,
  expandBridges,
  expandFrom,
  filterPrimaryIds,
  moduleEdges,
  neighbours,
  pageNeighbourhood,
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
import { domainColor } from "../theme/domains";
import { HealthStrip } from "./HealthStrip";
import "../theme/atlas.css";
import type { EdgeVisibility, LayoutMode, SelectedNode, WikiNodeData } from "../types";

const NODE_TYPES = { wikiNode: WikiNode, termNode: TermNode };
const NO_NODES: WikiFlowNode[] = [];
const NO_IDS = new Set<string>();
/** At or past this many pages in the filter, a global view carries little: the atlas is the way in. */
const ALL_NODES_LIMIT = 1000;
const MAX_STRETCH = 2.2;
const SEMANTIC_DELAY_MS = 1500;
const FIRST_NODE_MARK = "graph:first-node";

interface WikiGraphProps {
  highlightedPages?: Set<string>;
  /** Wiki page to pan/zoom to — set when arriving from a course lesson's concept link. */
  focusPage?: string | null;
  onNodeSelect?: (node: SelectedNode | null) => void;
  /** Called once `focusPage` has been applied (node found, view fitted, node selected). */
  onFocusApplied?: () => void;
  onBrief?: (domain: string) => void;
  activeTags: Set<string>;
  onActiveTagsChange: (tags: Set<string>) => void;
}

/** Fit padding that clears the status pill and level bar over the top of the canvas. */
function fitPadding(padding: number): FitViewOptions["padding"] {
  return { top: "110px", right: padding, bottom: padding, left: padding };
}

/**
 * A subset of a semantic layout keeps its wide shape, which leaves a nearly square canvas half
 * empty and cards small. Stretch it vertically: distances between pages were never exact, and
 * the same subset always gets the same shape.
 */
function fitToCanvasShape(positions: Record<string, XY>, ids: Set<string>): Record<string, XY> {
  let minY = Infinity;
  let maxY = -Infinity;
  let minX = Infinity;
  let maxX = -Infinity;
  for (const id of ids) {
    const p = positions[id];
    if (!p) continue;
    minX = Math.min(minX, p.x);
    maxX = Math.max(maxX, p.x);
    minY = Math.min(minY, p.y);
    maxY = Math.max(maxY, p.y);
  }
  const height = maxY - minY;
  if (!(height > 0)) return positions;
  const stretch = Math.min(MAX_STRETCH, Math.max(1, (maxX - minX) / height));
  if (stretch === 1) return positions;
  const out: Record<string, XY> = {};
  for (const [id, p] of Object.entries(positions)) out[id] = { x: p.x, y: minY + (p.y - minY) * stretch };
  return out;
}

function positionsOf(nodes: Node[]): Record<string, XY> {
  return Object.fromEntries(nodes.map((n) => [n.id, n.position]));
}

function WikiGraphInner({
  highlightedPages,
  focusPage,
  onNodeSelect,
  onFocusApplied,
  onBrief,
  activeTags,
  onActiveTagsChange,
}: WikiGraphProps) {
  // Semantic edges arrive in the background after first paint. Tag-shared stays off until asked
  // for: deriving them is ~42k pairs, and under a large filter they were most of the edge count.
  const [edgeVis, setEdgeVis] = useState<EdgeVisibility>({
    wikilink: true,
    semantic: true,
    module: true,
    "tag-shared": false,
    terms: true,
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
    tagSharedEdges,
    semanticEdges,
    fetchSemanticEdges,
    umapPositions,
    umapFailed,
    loadUmapPositions,
    connected,
    full,
  } = useWikiData({ tagShared: edgeVis["tag-shared"], live: !onAtlas });
  const [layout, setLayout] = useState<LayoutMode>("umap-semantic");
  const onAll = mapView.level === "all";
  const grouping: Grouping = mapView.level === "all" ? "domain" : mapView.grouping;
  const anchorId = mapView.level === "page" ? mapView.page : null;
  const [searchText, setSearchText] = useState("");
  const deferredSearch = useDeferredValue(searchText);
  /** Pages revealed by clicks since the level changed; they stay rendered. */
  const [revealed, setRevealed] = useState<Set<string>>(() => new Set());
  const [focusNodeId, setFocusNodeId] = useState<string | null>(null);
  const [loadingSemantic, setLoadingSemantic] = useState(false);
  // Narrow screens only: the control panels collapse behind one menu button.
  const [menuOpen, setMenuOpen] = useState(false);
  const menuBtnRef = useRef<HTMLButtonElement>(null);
  const { fitView } = useReactFlow();

  const hasNodes = baseNodes.length > 0;
  const theme = useTheme();
  const curriculum = useCurriculum(baseNodes, hasNodes);
  const glossary = useGlossary(baseNodes, hasNodes);
  const facets = useMemo(() => facetsOf(curriculum, baseNodes, glossary), [curriculum, baseNodes, glossary]);
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
  const curriculumPending = grouping === "course" && !curriculum;
  const sectors = useMemo(
    () => sectorsOf(atlasPages, degree, grouping, curriculum, theme),
    [atlasPages, degree, grouping, curriculum, theme],
  );
  const pageInfo = useMemo(
    () => new Map<string, AtlasPageInfo>(baseNodes.map((n) => [n.id, { title: n.data.title, summary: n.data.summary }])),
    [baseNodes],
  );
  const primaryIds = useMemo(() => filterPrimaryIds(baseNodes, activeTags, facets), [baseNodes, activeTags, facets]);
  const sectorId = mapView.level === "sector" || mapView.level === "page" ? mapView.sector : null;
  const sector = useMemo(() => sectors.find((s) => s.id === sectorId) ?? null, [sectors, sectorId]);
  const cap = mapView.level === "sector" || mapView.level === "page" ? mapView.cap : DEFAULT_CAP;

  const scope = useMemo<{ ids: Set<string>; total: number; hops?: number } | null>(() => {
    if (mapView.level === "sector" && sector) {
      const ids = primaryIds ? sector.pageIds.filter((id) => primaryIds.has(id)) : sector.pageIds;
      return { ids: new Set(ids.slice(0, cap)), total: ids.length };
    }
    if (mapView.level === "page" && pageInfo.has(mapView.page)) {
      return pageNeighbourhood(mapView.page, wikilinkEdges, degree, cap);
    }
    return null;
  }, [mapView, sector, primaryIds, cap, pageInfo, wikilinkEdges, degree]);

  // A link can outlive what it names: an unknown or private page, a retired sector, or an "All"
  // that the filter no longer makes small enough. Nothing here says which ids exist.
  const pagesInFilter = primaryIds?.size ?? baseNodes.length;
  const facetsPending = [...activeTags].some((t) => facetPending(t, curriculum, glossary));
  useEffect(() => {
    if (!hasNodes || parsedView === null) return;
    const bad =
      (mapView.level === "sector" && !curriculumPending && !sector) ||
      (mapView.level === "page" && (!pageInfo.has(mapView.page) || (!curriculumPending && !sector))) ||
      (mapView.level === "all" && !facetsPending && !restoringTags.current && pagesInFilter >= ALL_NODES_LIMIT);
    if (bad) replaceRoute("/");
  }, [hasNodes, parsedView, mapView, curriculumPending, sector, pageInfo, facetsPending, pagesInFilter]);

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
    if (isTermNodeId(focusNodeId)) {
      // A term lights the pages already here that mention it; it doesn't pull the rest in.
      const here = new Set([focusNodeId]);
      for (const id of glossary?.mentions[termIdOf(focusNodeId)] ?? []) {
        if (scopeIds?.has(id) || revealed.has(id)) here.add(id);
      }
      return here;
    }
    return new Set([focusNodeId, ...reveal(focusNodeId)]);
  }, [focusNodeId, glossary, scopeIds, revealed, reveal]);

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
    }),
    [chatHighlight, focusNodeId, focusIds, filterIds, activeTags, facets, anchorId, search],
  );

  const rendered = useMemo(
    () =>
      onAtlas ? NO_IDS : computeRenderIds(onAll && !filterIds, scopeIds ?? NO_IDS, revealed, view),
    [onAtlas, onAll, filterIds, scopeIds, revealed, view],
  );

  // UMAP positions overlap where pages are similar; spread just the rendered cards.
  // Dagre output never overlaps, so a dagre-laid-out filter subgraph is left alone.
  const placed = useMemo(() => {
    if (!positions || layout !== "umap-semantic") return positions;
    const spread = { ...positions, ...declutter(positions, rendered ?? baseNodes.map((n) => n.id)) };
    return scopeIds ? fitToCanvasShape(spread, scopeIds) : spread;
  }, [positions, layout, rendered, baseNodes, scopeIds]);

  const pageNodes = useMemo(() => {
    if (!placed || onAtlas) return NO_NODES;
    const laidOut = baseNodes
      .filter((n) => !rendered || rendered.has(n.id))
      .map((n) => ({ ...n, position: placed[n.id] ?? n.position }));
    return withCourseGroups(applyView(laidOut, view), curriculum, theme);
  }, [placed, onAtlas, baseNodes, rendered, view, curriculum, theme]);

  // Glossary terms, as a layer over a focused level. Not over "All nodes": hundreds of pages.
  const terms = useMemo(
    () =>
      glossary && edgeVis.terms && scope
        ? termLayer(pageNodes, glossary, { anchorId, focusIds, focusId: focusNodeId })
        : NO_TERMS,
    [glossary, edgeVis.terms, scope, pageNodes, anchorId, focusIds, focusNodeId],
  );
  const viewNodes = useMemo(
    () => (terms.nodes.length ? [...pageNodes, ...terms.nodes] : pageNodes),
    [pageNodes, terms],
  );

  const sameModule = useMemo(
    () => (edgeVis.module ? moduleEdges(pageNodes.map((n) => n.id), pageModules, degree) : []),
    [edgeVis.module, pageNodes, pageModules, degree],
  );
  const edges = useMemo(
    () =>
      visibleEdges(
        {
          wikilink: wikilinkEdges,
          semantic: semanticEdges,
          tagShared: tagSharedEdges,
          module: sameModule,
          mentions: terms.edges,
        },
        edgeVis,
        viewNodes,
        view,
      ),
    [wikilinkEdges, semanticEdges, tagSharedEdges, sameModule, terms, edgeVis, viewNodes, view],
  );

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
      return viewNodes.map((n) => {
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
  }, [viewNodes, positions, placed, filterIds, scopeIds, onAll, setNodes]);

  useEffect(() => {
    if (!pendingFit.current || !nodes.length) return;
    pendingFit.current = false;
    const ids = filterIds;
    requestAnimationFrame(() => {
      if (ids) {
        void fitView({ nodes: [...ids].map((id) => ({ id })), padding: fitPadding(0.3), duration: 400 });
      } else {
        void fitView({ padding: fitPadding(0.08), duration: 300 });
      }
    });
  }, [nodes, filterIds, fitView]);

  // --- focusPage (arriving from a lesson, or a chat citation): go to that page's level ----
  const hasRenderedNodes = nodes.length > 0;
  useEffect(() => {
    if (!focusPage || !hasNodes || curriculumPending) return;
    const page = atlasPages.find((p) => p.id === focusPage);
    // An unknown or private page: drop the request rather than leave it pending, so it can't
    // fire later on an unrelated graph update.
    if (page) {
      navigate(
        mapPath({ level: "page", grouping, sector: sectorIdOf(page, grouping, curriculum), page: page.id, cap: PAGE_CAP }),
      );
    }
    onFocusApplied?.();
  }, [focusPage, hasNodes, curriculumPending, atlasPages, grouping, curriculum, navigate, onFocusApplied]);

  // A new level starts clean, and a page's level opens that page's panel. Keyed on the level, not
  // on the node objects, so a graph update can't reopen a panel you closed. The cap is part of
  // no key: widening a view keeps what you clicked.
  const key = levelKey(mapView);
  const appliedLevel = useRef<string | null>(null);
  useEffect(() => {
    if (!hasNodes || appliedLevel.current === key) return;
    appliedLevel.current = key;
    setRevealed(new Set());
    setFocusNodeId(null);
    setSearchText("");
    const node = anchorId ? baseNodes.find((n) => n.id === anchorId) : null;
    onNodeSelect?.(node ? { id: node.id, data: node.data } : null);
  }, [key, hasNodes, anchorId, baseNodes, onNodeSelect]);

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

  // "All nodes" keeps its filter in the link: restore it once on load, then follow the panel.
  const restoringTags = useRef(mapView.level === "all" && mapView.tags.length > 0);
  useEffect(() => {
    if (mapView.level !== "all" || parsedView === null) return;
    if (restoringTags.current) {
      restoringTags.current = false;
      onActiveTagsChange(new Set(mapView.tags));
      return;
    }
    const tags = [...activeTags].sort();
    const path = mapPath({ level: "all", tags });
    if (path !== mapPath(mapView)) replaceRoute(path);
  }, [mapView, parsedView, activeTags, onActiveTagsChange]);

  // --- Handlers ------------------------------------------------------------------------
  const handleLoadSemantic = useCallback(async () => {
    setLoadingSemantic(true);
    try {
      await fetchSemanticEdges(0.65);
    } catch {
      // Toggle stays on with no edges; the next toggle retries.
    } finally {
      setLoadingSemantic(false);
    }
  }, [fetchSemanticEdges]);

  // The first paint doesn't wait for these. Retries on reconnect while none have landed.
  const hasSemanticEdges = semanticEdges.length > 0;
  useEffect(() => {
    if (!hasRenderedNodes || !connected || !edgeVis.semantic || hasSemanticEdges) return;
    const timer = setTimeout(() => void handleLoadSemantic(), SEMANTIC_DELAY_MS);
    return () => clearTimeout(timer);
  }, [hasRenderedNodes, connected, edgeVis.semantic, hasSemanticEdges, handleLoadSemantic]);

  // Clicking a node focuses it and keeps its neighbours on the canvas, so the graph can be
  // walked outward click by click. Clicking it again unfocuses. A term only lights its pages.
  const handleNodeClick = useCallback(
    (_: React.MouseEvent, node: WikiFlowNode) => {
      setFocusNodeId((prev) => (prev === node.id ? null : node.id));
      if (isTermNodeId(node.id)) {
        onNodeSelect?.(null);
        return;
      }
      setRevealed((prev) => {
        const next = new Set(prev);
        next.add(node.id);
        for (const id of reveal(node.id)) next.add(id);
        return next.size === prev.size ? prev : next;
      });
      onNodeSelect?.({ id: node.id, data: node.data as WikiNodeData });
    },
    [onNodeSelect, reveal],
  );

  const handleResetRevealed = useCallback(() => {
    setRevealed(new Set());
    setFocusNodeId(null);
  }, []);

  const openPage = useCallback(
    (pageId: string) => {
      const page = atlasPages.find((p) => p.id === pageId);
      if (!page) return;
      navigate(
        mapPath({ level: "page", grouping, sector: sectorIdOf(page, grouping, curriculum), page: pageId, cap: PAGE_CAP }),
      );
    },
    [atlasPages, grouping, curriculum, navigate],
  );

  const handleNodeDoubleClick = useCallback(
    (_: React.MouseEvent, node: WikiFlowNode) => {
      if (!isTermNodeId(node.id)) openPage(node.id);
    },
    [openPage],
  );

  const openSectorLevel = useCallback(
    (id: string) => navigate(mapPath({ level: "sector", grouping, sector: id, cap: DEFAULT_CAP })),
    [navigate, grouping],
  );
  const openPageLevel = useCallback(
    (id: string, page: string) => navigate(mapPath({ level: "page", grouping, sector: id, page, cap: PAGE_CAP })),
    [navigate, grouping],
  );

  const handlePaneClick = useCallback(() => {
    setFocusNodeId(null);
    onNodeSelect?.(null);
  }, [onNodeSelect]);

  // Esc goes back one level. Not while typing, and not when it's closing the narrow-screen menu.
  const backTo = parentOf(mapView);
  const termOpen = !!focusNodeId && isTermNodeId(focusNodeId);
  const escapeState = useRef({ backTo, menuOpen, onMap: parsedView !== null, termOpen });
  useEffect(() => {
    escapeState.current = { backTo, menuOpen, onMap: parsedView !== null, termOpen };
  });
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key !== "Escape" || e.defaultPrevented) return;
      const { backTo: to, menuOpen: menu, onMap, termOpen: term } = escapeState.current;
      const target = e.target as HTMLElement | null;
      if (!to || menu || !onMap || target?.matches?.("input, textarea")) return;
      e.preventDefault();
      if (term) setFocusNodeId(null);
      else navigate(mapPath(to));
    };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [navigate]);

  useEffect(() => {
    if (!menuOpen) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key !== "Escape") return;
      e.preventDefault();
      setMenuOpen(false);
      menuBtnRef.current?.focus();
    };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [menuOpen]);

  const miniMapColor = useCallback(
    (n: WikiFlowNode) => n.data.groupColor ?? domainColor(n.data.domain[0], theme),
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

  const pageCount = nodes.filter((n) => !isTermNodeId(n.id)).length;
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
  const focusedTerm =
    focusNodeId && isTermNodeId(focusNodeId)
      ? glossary?.terms.find((t) => termNodeId(t.id) === focusNodeId)
      : null;
  const clickedPage = focusNodeId && !isTermNodeId(focusNodeId) && focusNodeId !== anchorId ? focusNodeId : null;
  const allNodesAllowed = pagesInFilter < ALL_NODES_LIMIT;
  const openAll = useCallback(
    () => navigate(mapPath({ level: "all", tags: [...activeTags].sort() })),
    [navigate, activeTags],
  );

  const allNodes = !onAll && (
    <div className={`graph-all-nodes seg${onAtlas ? " graph-all-nodes--atlas" : ""}`}>
      <button
        type="button"
        className="seg-btn"
        disabled={!allNodesAllowed}
        onClick={openAll}
        title={
          allNodesAllowed
            ? "Every page under the current filter on one canvas"
            : `Filter to under ${ALL_NODES_LIMIT.toLocaleString("en-US")} pages to draw them all at once`
        }
      >
        {allNodesAllowed
          ? `All nodes (${pagesInFilter.toLocaleString("en-US")})`
          : `All nodes: filter to under ${ALL_NODES_LIMIT.toLocaleString("en-US")} (${pagesInFilter.toLocaleString("en-US")} now)`}
      </button>
    </div>
  );

  const layers = !onAtlas && (
    <>
      <EdgeTogglePanel
        visibility={edgeVis}
        onChange={setEdgeVis}
        onLoadSemantic={handleLoadSemantic}
        loadingSemanticEdges={loadingSemantic}
      />
      <LayoutSwitcher
        current={layout}
        onChange={setLayout}
        loadingUmap={loadingUmap}
        umapUnavailable={layout === "umap-semantic" && umapFailed}
      />
    </>
  );
  // Outside <ReactFlow>, inside its provider: it reads the same store. The theme's colours are
  // passed in because its CSS variables are scoped to the canvas.
  const minimap = !onAtlas && !curriculumPending && (
    <MiniMap
      nodeColor={miniMapColor}
      className="graph-minimap"
      bgColor="var(--surface)"
      maskColor="var(--minimap-mask)"
      maskStrokeColor="var(--border-pressed)"
      style={{ width: 240, height: 150 }}
      pannable
      zoomable
      ariaLabel="Minimap"
    />
  );

  return (
    <div className="graph-root">
      <GraphSidebar
        id="graph-controls"
        open={menuOpen}
        domains={domains}
        curriculum={curriculum}
        glossary={glossary}
        facets={facets}
        activeTags={activeTags}
        onChange={onActiveTagsChange}
        onBrief={onBrief}
        layers={layers || undefined}
        minimap={minimap || undefined}
      />

      <div className="graph-canvas">
        <HealthStrip />
        {/* Connection status, and how much of the wiki is on the canvas */}
        <div className={`graph-status ${ready ? "graph-status--live" : "graph-status--offline"}`}>
          {statusText}
          {hasNodes && (
            <span className="graph-status-count">
              {" "}· {onAtlas ? (primaryIds?.size ?? baseNodes.length) : pageCount} of {baseNodes.length} pages
            </span>
          )}
        </div>

        {hasNodes && (
          <MapBar
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
            onGrouping={(g) => navigate(mapPath({ level: "atlas", grouping: g }))}
            refocus={clickedPage ? { title: `Focus on ${pageInfo.get(clickedPage)?.title ?? clickedPage}`, onClick: () => openPage(clickedPage) } : null}
            search={<MapSearch value={searchText} onChange={setSearchText} result={search} onOpenPage={openPage} />}
          />
        )}

        {/* Narrow screens: one button in place of the sidebar. */}
        <button
          ref={menuBtnRef}
          type="button"
          className="graph-menu-btn"
          aria-label="Graph controls"
          aria-expanded={menuOpen}
          aria-controls="graph-controls"
          onClick={() => setMenuOpen((o) => !o)}
        >
          ☰ Controls
        </button>

        {allNodes}

        {onAtlas && curriculumPending && hasNodes && (
          <div className="map-note" role="status">
            Loading the curriculum; showing domains until it arrives.
          </div>
        )}

        {onAtlas ? (
          hasNodes && (
            <Atlas
              sectors={sectors}
              grouping={curriculumPending ? "domain" : grouping}
              info={pageInfo}
              degree={degree}
              totalLinks={wikilinkEdges.length}
              termCount={glossary?.terms.length ?? 0}
              matches={atlasMatches}
              lit={atlasLit}
              onOpenSector={openSectorLevel}
              onOpenPage={openPageLevel}
              enterFrom={enterFrom}
            />
          )
        ) : curriculumPending ? (
          <div className="map-loading">Loading the curriculum…</div>
        ) : (
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
          </ReactFlow>
        )}

        {focusedTerm && (
          <div className="term-card" role="group" aria-label={`Glossary term ${focusedTerm.label}`}>
            <div className="term-card-title">{focusedTerm.label}</div>
            <div>{focusedTerm.def}</div>
            <div className="term-card-note">
              {(focusIds?.size ?? 1) - 1} pages here mention it · {focusedTerm.mentions} in the wiki
            </div>
            <div className="term-card-actions">
              {focusedTerm.page && (
                <button type="button" className="pill-btn" onClick={() => openPage(focusedTerm.page!)}>
                  Open its page
                </button>
              )}
              <button type="button" className="pill-btn" onClick={() => setFocusNodeId(null)}>
                Close
              </button>
            </div>
          </div>
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
