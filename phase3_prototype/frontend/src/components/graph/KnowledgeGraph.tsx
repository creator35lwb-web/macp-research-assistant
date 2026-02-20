import { useEffect, useRef } from "react";
import type { GraphData, GraphNode } from "../../api/types";

interface KnowledgeGraphProps {
  data: GraphData;
}

export function KnowledgeGraph({ data }: KnowledgeGraphProps) {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current || !data.nodes.length) return;

    // Dynamic import of d3 to avoid SSR issues
    import("d3").then((d3) => {
      const svg = d3.select(svgRef.current);
      svg.selectAll("*").remove();

      const width = svgRef.current!.clientWidth;
      const height = svgRef.current!.clientHeight;

      const g = svg.append("g");

      // Zoom
      const zoom = d3.zoom<SVGSVGElement, unknown>()
        .scaleExtent([0.2, 4])
        .on("zoom", (event) => g.attr("transform", event.transform));
      svg.call(zoom as any);

      // Color by type
      const colorMap: Record<string, string> = {
        paper: "#3b82f6",
        analysis: "#22c55e",
      };

      // Build simulation nodes/links
      const nodes: (GraphNode & { x: number; y: number })[] = data.nodes.map((n) => ({
        ...n,
        x: width / 2 + (Math.random() - 0.5) * 200,
        y: height / 2 + (Math.random() - 0.5) * 200,
      }));

      const links = data.edges.map((e) => ({
        source: typeof e.source === "number" ? e.source : nodes.findIndex((n) => n.id === (e.source as GraphNode).id),
        target: typeof e.target === "number" ? e.target : nodes.findIndex((n) => n.id === (e.target as GraphNode).id),
        type: e.type,
      })).filter((l) => l.source >= 0 && l.target >= 0);

      const simulation = d3.forceSimulation(nodes as d3.SimulationNodeDatum[])
        .force("link", d3.forceLink(links).id((_, i) => i).distance(80))
        .force("charge", d3.forceManyBody().strength(-120))
        .force("center", d3.forceCenter(width / 2, height / 2))
        .force("collision", d3.forceCollide().radius(20));

      // Links
      const link = g.append("g")
        .selectAll("line")
        .data(links)
        .enter().append("line")
        .attr("stroke", "#3f3f46")
        .attr("stroke-width", 1)
        .attr("stroke-opacity", 0.6);

      // Nodes
      const node = g.append("g")
        .selectAll("circle")
        .data(nodes)
        .enter().append("circle")
        .attr("r", (d) => d.type === "paper" ? 8 : 5)
        .attr("fill", (d) => colorMap[d.type] || "#71717a")
        .attr("stroke", "#09090b")
        .attr("stroke-width", 1.5)
        .style("cursor", "pointer");

      // Labels
      const label = g.append("g")
        .selectAll("text")
        .data(nodes)
        .enter().append("text")
        .text((d) => d.title.length > 30 ? d.title.slice(0, 30) + "..." : d.title)
        .attr("font-size", 10)
        .attr("fill", "#a1a1aa")
        .attr("dx", 12)
        .attr("dy", 4);

      // Drag
      const drag = d3.drag<SVGCircleElement, typeof nodes[0]>()
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

      node.call(drag as any);

      simulation.on("tick", () => {
        link
          .attr("x1", (d: any) => d.source.x)
          .attr("y1", (d: any) => d.source.y)
          .attr("x2", (d: any) => d.target.x)
          .attr("y2", (d: any) => d.target.y);
        node
          .attr("cx", (d: any) => d.x)
          .attr("cy", (d: any) => d.y);
        label
          .attr("x", (d: any) => d.x)
          .attr("y", (d: any) => d.y);
      });
    });
  }, [data]);

  return (
    <div style={{ width: "100%", height: "100%", minHeight: 400 }}>
      <svg
        ref={svgRef}
        width="100%"
        height="100%"
        style={{ background: "var(--bg-primary)" }}
      />
    </div>
  );
}
