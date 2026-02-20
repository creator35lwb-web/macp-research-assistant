import { useCallback, useState } from "react";
import { searchPapers, analyzePaper } from "../api/client";
import type { Analysis, Paper } from "../api/types";

export function usePapers() {
  const [papers, setPapers] = useState<Paper[]>([]);
  const [searching, setSearching] = useState(false);
  const [searchError, setSearchError] = useState("");
  const [analyses, setAnalyses] = useState<Record<string, Analysis>>({});
  const [analyzingId, setAnalyzingId] = useState<string | null>(null);
  const [analyzeError, setAnalyzeError] = useState("");

  const search = useCallback(async (query: string, limit = 10, source = "hysts") => {
    if (!query.trim()) return;
    setSearching(true);
    setSearchError("");
    setPapers([]);
    try {
      const data = await searchPapers(query, limit, source);
      setPapers(data.results || []);
    } catch (e: unknown) {
      setSearchError(e instanceof Error ? e.message : "Search failed");
    } finally {
      setSearching(false);
    }
  }, []);

  const analyze = useCallback(async (paperId: string, provider = "gemini", apiKey?: string) => {
    setAnalyzingId(paperId);
    setAnalyzeError("");
    try {
      const data = await analyzePaper(paperId, provider, apiKey);
      setAnalyses((prev) => ({ ...prev, [paperId]: data.analysis }));
    } catch (e: unknown) {
      setAnalyzeError(e instanceof Error ? e.message : "Analysis failed");
    } finally {
      setAnalyzingId(null);
    }
  }, []);

  return {
    papers, searching, searchError, search,
    analyses, analyzingId, analyzeError, analyze,
  };
}
