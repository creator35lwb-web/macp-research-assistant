/**
 * useGraphStats — fetch graph stats on mount and persist to localStorage
 * for session continuity messaging (P4.2 / P4.5).
 */
import { useCallback, useEffect, useState } from "react";
import { mcpGraph } from "../api/client";

export interface GraphStats {
  papers: number;
  concepts: number;
  methods: number;
  connections: number;
}

export interface GraphDelta {
  papers: number;
  concepts: number;
  connections: number;
}

const STORAGE_KEY = "macp_graph_stats_last";

function loadLastStats(): GraphStats | null {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

function saveStats(stats: GraphStats) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(stats));
  } catch {
    /* ignore quota errors */
  }
}

export function useGraphStats(userId: number | undefined) {
  const [stats, setStats] = useState<GraphStats | null>(null);
  const [delta, setDelta] = useState<GraphDelta | null>(null);
  const [loading, setLoading] = useState(false);

  const fetchStats = useCallback(async () => {
    if (!userId) return;
    setLoading(true);
    try {
      const res = await mcpGraph();
      const text = res.content?.[0]?.text;
      if (!text) return;
      const data = JSON.parse(text);
      const current: GraphStats = {
        papers: data.stats?.papers ?? 0,
        concepts: data.stats?.concepts ?? 0,
        methods: data.stats?.methods ?? 0,
        connections: data.stats?.connections ?? 0,
      };
      const last = loadLastStats();
      if (last) {
        const d: GraphDelta = {
          papers: current.papers - last.papers,
          concepts: current.concepts - last.concepts,
          connections: current.connections - last.connections,
        };
        if (d.papers > 0 || d.concepts > 0 || d.connections > 0) {
          setDelta(d);
        }
      }
      setStats(current);
      saveStats(current);
    } catch {
      /* silently fail — widget is non-critical */
    } finally {
      setLoading(false);
    }
  }, [userId]);

  useEffect(() => {
    fetchStats();
  }, [fetchStats]);

  return { stats, delta, loading, refetch: fetchStats };
}
