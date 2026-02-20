import { useCallback, useState } from "react";
import { mcpGraph } from "../api/client";
import type { GraphData } from "../api/types";

export function useGraph() {
  const [graphData, setGraphData] = useState<GraphData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const fetchGraph = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const res = await mcpGraph();
      const text = res.content?.[0]?.text;
      if (text) {
        setGraphData(JSON.parse(text));
      }
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to load graph");
    } finally {
      setLoading(false);
    }
  }, []);

  return { graphData, loading, error, fetchGraph };
}
