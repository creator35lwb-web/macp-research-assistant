import { useEffect, useRef } from "react";
import type { GraphData, GraphNode } from "../../api/types";

interface KnowledgeGraphProps {
  data: GraphData;
}

const NODE_COLOR: Record<string, string> = {
  paper:   "#3b82f6",   // blue
  concept: "#a855f7",   // purple
  method:  "#f59e0b",   // amber
  author:  "#22c55e",   // green
  analysis:"#71717a",   // grey (legacy fallback)
};

const NODE_RADIUS: Record<string, number> = {
  paper:   10,
  concept: 6,
  method:  6,
  author:  5,
  analysis:5,
};

const LEGEND_ENTRIES = [
  { type: "paper",   label: "Paper" },
  { type: "concept", label: "Concept" },
  { type: "method",  label: "Method" },
  { type: "author",  label: "Author" },
];

export function KnowledgeGraph({ data }: KnowledgeGraphProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const tooltipRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!svgRef.current || !data.nodes.length) return;

    import("d3").then((d3) => {
      const svg = d3.select(svgRef.current);
      svg.selectAll("*").remove();

      const width = svgRef.current!.clientWidth;
      const height = svgRef.current!.clientHeight;

      const g = svg.append("g");

      // --- Zoom ---
      const zoom = d3.zoom<SVGSVGElement, unknown>()
        .scaleExtent([0.1, 6])
        .on("zoom", (event) => g.attr("transform", event.transform));
      svg.call(zoom as any);

      // --- Nodes & links ---
      const nodes: (GraphNode & { x: number; y: number })[] = data.nodes.map((n) => ({
        ...n,
        x: width / 2 + (Math.random() - 0.5) * 300,
        y: height / 2 + (Math.random() - 0.5) * 300,
      }));

      const links = data.edges.map((e) => ({
        source: typeof e.source === "number" ? e.source : nodes.findIndex((n) => n.id === (e.source as GraphNode).id),
        target: typeof e.target === "number" ? e.target : nodes.findIndex((n) => n.id === (e.target as GraphNode).id),
        type: e.type,
      })).filter((l) => l.source >= 0 && l.target >= 0);

      // Charge and distance tuned for mixed node types
      const simulation = d3.forceSimulation(nodes as d3.SimulationNodeDatum[])
        .force("link", d3.forceLink(links).id((_, i) => i).distance((l: any) => {
          const src = nodes[l.source?.index ?? l.source];
          const tgt = nodes[l.target?.index ?? l.target];
          if (src?.type === "paper" && tgt?.type === "paper") return 120;
          if (src?.type === "paper" || tgt?.type === "paper") return 70;
          return 50;
        }))
        .force("charge", d3.forceManyBody().strength(-80))
        .force("center", d3.forceCenter(width / 2, height / 2))
        .force("collision", d3.forceCollide().radius((d: any) => (NODE_RADIUS[d.type] ?? 5) + 4));

      // --- Links ---
      const linkEls = g.append("g")
        .selectAll("line")
        .data(links)
        .enter().append("line")
        .attr("stroke", (d) => d.type === "relates_to" ? "#a855f7" : "#3f3f46")
        .attr("stroke-width", (d) => d.type === "relates_to" ? 1.5 : 1)
        .attr("stroke-opacity", 0.5)
        .attr("stroke-dasharray", (d) => d.type === "relates_to" ? "4 3" : "none");

      // --- Node groups (circle + optional diamond) ---
      const nodeG = g.append("g")
        .selectAll("g")
        .data(nodes)
        .enter().append("g")
        .style("cursor", "pointer");

      // Diamond for method nodes
      const diamond = (r: number) => {
        const s = r * 1.4;
        return `M 0 ${-s} L ${s} 0 L 0 ${s} L ${-s} 0 Z`;
      };

      nodeG.each(function(d) {
        const el = d3.select(this);
        const r = NODE_RADIUS[d.type] ?? 5;
        const color = NODE_COLOR[d.type] ?? "#71717a";
        if (d.type === "method") {
          el.append("path")
            .attr("d", diamond(r))
            .attr("fill", color)
            .attr("stroke", "#09090b")
            .attr("stroke-width", 1.5);
        } else {
          el.append("circle")
            .attr("r", r)
            .attr("fill", color)
            .attr("stroke", "#09090b")
            .attr("stroke-width", 1.5);
        }
      });

      // --- Labels (paper nodes only by default) ---
      const label = g.append("g")
        .selectAll("text")
        .data(nodes)
        .enter().append("text")
        .text((d) => {
          if (d.type !== "paper") return "";
          return d.title.length > 28 ? d.title.slice(0, 28) + "…" : d.title;
        })
        .attr("font-size", 9)
        .attr("fill", "#a1a1aa")
        .attr("dx", 13)
        .attr("dy", 4)
        .style("pointer-events", "none");

      // --- Tooltip ---
      const tooltip = d3.select(tooltipRef.current);

      nodeG
        .on("mouseover", (event: MouseEvent, d: GraphNode) => {
          const connections = links.filter(
            (l: any) => l.source?.index === nodes.indexOf(d as any) || l.target?.index === nodes.indexOf(d as any)
          ).length;
          tooltip
            .style("opacity", "1")
            .style("left", `${event.offsetX + 12}px`)
            .style("top", `${event.offsetY - 8}px`)
            .html(`<strong>${d.title}</strong><br/><span>${d.type}</span> · ${connections} connections`);
        })
        .on("mousemove", (event: MouseEvent) => {
          tooltip
            .style("left", `${event.offsetX + 12}px`)
            .style("top", `${event.offsetY - 8}px`);
        })
        .on("mouseout", () => {
          tooltip.style("opacity", "0");
        });

      // --- Click: highlight connected edges ---
      nodeG.on("click", (_event: MouseEvent, d: GraphNode) => {
        const idx = nodes.indexOf(d as any);
        linkEls
          .attr("stroke-opacity", (l: any) =>
            l.source?.index === idx || l.target?.index === idx ? 1 : 0.1
          )
          .attr("stroke-width", (l: any) =>
            l.source?.index === idx || l.target?.index === idx ? 2.5 : 1
          );
        nodeG.style("opacity", (n: GraphNode) => {
          const ni = nodes.indexOf(n as any);
          if (ni === idx) return "1";
          const connected = links.some(
            (l: any) =>
              (l.source?.index === idx && l.target?.index === ni) ||
              (l.target?.index === idx && l.source?.index === ni)
          );
          return connected ? "1" : "0.2";
        });
      });

      // Double-click to reset highlighting
      svg.on("dblclick.zoom", null);
      svg.on("dblclick", () => {
        linkEls.attr("stroke-opacity", 0.5).attr("stroke-width", 1);
        nodeG.style("opacity", "1");
      });

      // --- Drag ---
      const drag = d3.drag<SVGGElement, typeof nodes[0]>()
        .on("start", (event, d) => {
          if (!event.active) simulation.alphaTarget(0.3).restart();
          (d as any).fx = d.x;
          (d as any).fy = d.y;
        })
        .on("drag", (event, d) => {
          (d as any).fx = event.x;
          (d as any).fy = event.y;
        })
        .on("end", (event, d) => {
          if (!event.active) simulation.alphaTarget(0);
          (d as any).fx = null;
          (d as any).fy = null;
        });

      nodeG.call(drag as any);

      simulation.on("tick", () => {
        linkEls
          .attr("x1", (d: any) => d.source.x)
          .attr("y1", (d: any) => d.source.y)
          .attr("x2", (d: any) => d.target.x)
          .attr("y2", (d: any) => d.target.y);
        nodeG.attr("transform", (d: any) => `translate(${d.x},${d.y})`);
        label
          .attr("x", (d: any) => d.x)
          .attr("y", (d: any) => d.y);
      });
    });
  }, [data]);

  return (
    <div style={{ width: "100%", height: "100%", minHeight: 400, position: "relative" }}>
      {/* Legend */}
      <div className="graph-legend">
        {LEGEND_ENTRIES.map(({ type, label }) => (
          <div key={type} className="graph-legend__item">
            <svg width="12" height="12" style={{ flexShrink: 0 }}>
              {type === "method" ? (
                <polygon
                  points="6,0 12,6 6,12 0,6"
                  fill={NODE_COLOR[type]}
                  stroke="#09090b"
                  strokeWidth="1"
                />
              ) : (
                <circle
                  cx="6" cy="6"
                  r={type === "paper" ? 5 : type === "author" ? 4 : 4.5}
                  fill={NODE_COLOR[type]}
                  stroke="#09090b"
                  strokeWidth="1"
                />
              )}
            </svg>
            <span>{label}</span>
          </div>
        ))}
        <div className="graph-legend__hint">Double-click to reset</div>
      </div>

      {/* Tooltip */}
      <div ref={tooltipRef} className="graph-tooltip" style={{ opacity: 0 }} />

      <svg
        ref={svgRef}
        width="100%"
        height="100%"
        style={{ background: "var(--bg-primary)" }}
      />
    </div>
  );
}
