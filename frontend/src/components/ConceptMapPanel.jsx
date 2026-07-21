import { Download, GitBranch, Maximize2, RefreshCw, X } from "./FontAwesomeIcons";
import { useEffect, useMemo, useRef } from "react";
import { IconButton } from "./IconButton";

function cleanLabel(value, fallback = "") {
  const label = String(value ?? "").trim();
  return label || fallback;
}

function nodeId(label, namespace) {
  return `${cleanLabel(label, "Untitled")}#${namespace}`;
}

function normalizeMap(conceptMap) {
  if (!conceptMap || typeof conceptMap !== "object" || Array.isArray(conceptMap)) {
    return {};
  }

  return Object.fromEntries(
    Object.entries(conceptMap)
      .map(([parent, children]) => {
        const parentLabel = cleanLabel(parent);
        if (!parentLabel) return null;

        const childLabels = Array.isArray(children)
          ? children.map((child) => cleanLabel(child)).filter(Boolean)
          : cleanLabel(children)
            ? [cleanLabel(children)]
            : [];

        return [parentLabel, childLabels];
      })
      .filter(Boolean),
  );
}

function rootsFromMap(conceptMap) {
  const parentLabels = Object.keys(conceptMap);
  const childLabels = new Set(Object.values(conceptMap).flat());
  const roots = parentLabels.filter((label) => !childLabels.has(label));
  return roots.length ? roots : parentLabels;
}

function conceptMapsToDictionary(conceptMaps, fileName) {
  const rootId = nodeId(fileName || "Concept map", "document-root");
  const graph = { [rootId]: [] };

  conceptMaps.forEach((record, recordIndex) => {
    const conceptMap = normalizeMap(record.map);
    const mapRoots = rootsFromMap(conceptMap);
    if (!mapRoots.length) return;

    const sectionLabel = cleanLabel(record.section || record.path?.at(-1), `Section ${recordIndex + 1}`);
    const sectionId = nodeId(sectionLabel, `section-${recordIndex}`);
    graph[rootId].push(sectionId);
    graph[sectionId] = mapRoots.map((label) => nodeId(label, `map-${recordIndex}-${label}`));

    Object.entries(conceptMap).forEach(([parent, children]) => {
      graph[nodeId(parent, `map-${recordIndex}-${parent}`)] = children.map((child) => nodeId(child, `map-${recordIndex}-${child}`));
    });
  });

  return graph;
}

function hasGraphData(graphData) {
  return Object.values(graphData).some((children) => Array.isArray(children) && children.length);
}

function expandGraphToDepth(graph, maxDepth = 2) {
  const incomingNodeIds = new Set(graph.graphData.links.map((link) => (typeof link.target === "object" ? link.target.id : link.target)));
  const rootNodes = graph.graphData.nodes.filter((node) => !incomingNodeIds.has(node.id));
  const queue = rootNodes.map((node) => ({ id: node.id, depth: 0 }));
  const visited = new Set();

  graph.expandedNodes.clear();

  while (queue.length) {
    const current = queue.shift();
    if (!current || visited.has(current.id)) continue;
    visited.add(current.id);

    if (current.depth < maxDepth) {
      graph.expandedNodes.add(current.id);
    }

    const children = graph.ancestorMap[current.id]?.descendants ?? [];
    children.forEach((childId) => queue.push({ id: childId, depth: current.depth + 1 }));
  }
}

export function ConceptMapPanel({ conceptMaps = [], fileName = "", onClose }) {
  const containerIdRef = useRef(`concept-map-${crypto.randomUUID()}`);
  const graphRef = useRef(null);
  const graphData = useMemo(() => conceptMapsToDictionary(conceptMaps, fileName), [conceptMaps, fileName]);
  const hasConceptMap = hasGraphData(graphData);
  const panelTitle = `Concept Map for "${fileName || "Selected file"}"`;

  useEffect(() => {
    function handleKeyDown(event) {
      if (event.key === "Escape") {
        onClose();
      }
    }

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [onClose]);

  useEffect(() => {
    if (!hasConceptMap) return undefined;

    let isCancelled = false;

    async function renderGraph() {
      const { createInteractiveAncestorGraph } = await import("../concept_map.js");
      if (isCancelled) return;

      const graph = createInteractiveAncestorGraph(containerIdRef.current, graphData);
      graph.nodeSpacing = 235;
      graph.verticalSpacing = 74;
      graph.maxLabelLength = 18;
      graph.transition_duration = 520;
      graph.colors = {
        ...graph.colors,
        secondary: "#ffffff",
        stroke: "#111827",
        border: "#d5d9e1",
        link: "#b6b8bd",
        linkOpacity: 0.82,
        text: "#111827",
      };
      expandGraphToDepth(graph, 2);
      graph.render();
      graphRef.current = graph;
    }

    renderGraph();

    return () => {
      isCancelled = true;
      graphRef.current = null;
      const container = document.getElementById(containerIdRef.current);
      if (container) {
        container.innerHTML = "";
      }
    };
  }, [graphData, hasConceptMap]);

  function resetView() {
    const graph = graphRef.current;
    if (!graph) return;

    expandGraphToDepth(graph, 2);
    graph.render();
    graph.g?.attr("transform", null);
    graph.svg?.property("__zoom", globalThis.d3?.zoomIdentity);
  }

  function expandAll() {
    const graph = graphRef.current;
    if (!graph) return;

    graph.graphData.nodes.forEach((node) => graph.expandedNodes.add(node.id));
    graph.render();
  }

  function downloadConceptMap() {
    const blob = new Blob([JSON.stringify(conceptMaps, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `${(fileName || "concept-map").replace(/[^a-z0-9_-]+/gi, "-").replace(/^-+|-+$/g, "") || "concept-map"}.json`;
    link.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="concept-map-shell" role="dialog" aria-modal="true" aria-labelledby="concept-map-title" onClick={onClose}>
      <section className="concept-map-panel" onClick={(event) => event.stopPropagation()}>
        <header className="concept-map-titlebar">
          <h2 id="concept-map-title">{panelTitle}</h2>
          <div className="concept-map-header-actions">
            <IconButton label="Download concept map" onClick={downloadConceptMap} disabled={!hasConceptMap}>
              <Download size={18} />
            </IconButton>
            <IconButton label="Close concept map" onClick={onClose}>
              <X size={18} />
            </IconButton>
          </div>
        </header>
        <div className="concept-map-body">
          {hasConceptMap ? (
            <>
              <div className="concept-map-controls" aria-label="Concept map controls">
                <button type="button" onClick={resetView}>
                  <RefreshCw size={14} />
                  <span>Reset View</span>
                </button>
                <button type="button" onClick={expandAll}>
                  <Maximize2 size={14} />
                  <span>Expand All</span>
                </button>
              </div>
              <div id={containerIdRef.current} className="concept-map-graph" aria-label="Interactive concept map" />
            </>
          ) : (
            <div className="concept-map-empty">
              <GitBranch size={28} />
              <p>No concept map has been generated for this file yet.</p>
            </div>
          )}
        </div>
      </section>
    </div>
  );
}
