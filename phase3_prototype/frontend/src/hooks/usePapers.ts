import { useCallback, useRef, useState } from "react";
import { searchPapers, analyzePaper, mcpLibrary } from "../api/client";
import type { Analysis, Paper } from "../api/types";

export function usePapers() {
  const [papers, setPapers] = useState<Paper[]>([]);
  const [searching, setSearching] = useState(false);
  const [searchError, setSearchError] = useState("");
  const [analyses, setAnalyses] = useState<Record<string, Analysis>>({});
  const [analyzingId, setAnalyzingId] = useState<string | null>(null);
  const [analyzeError, setAnalyzeError] = useState("");
  const [hasMore, setHasMore] = useState(false);
  const [loadingMore, setLoadingMore] = useState(false);
  const [libraryPapers, setLibraryPapers] = useState<Paper[]>([]);
  const [libraryLoading, setLibraryLoading] = useState(false);

  // Track current query/source for loadMore
  const currentQuery = useRef("");
  const currentSource = useRef("hysts");
  const currentOffset = useRef(0);

  const search = useCallback(async (query: string, limit = 10, source = "hysts") => {
    if (!query.trim()) return;
    setSearching(true);
    setSearchError("");
    setPapers([]);
    setHasMore(false);
    currentQuery.current = query;
    currentSource.current = source;
    currentOffset.current = 0;
    try {
      const data = await searchPapers(query, limit, source, 0);
      setPapers(data.results || []);
      setHasMore(data.has_more ?? false);
      currentOffset.current = limit;
    } catch (e: unknown) {
      setSearchError(e instanceof Error ? e.message : "Search failed");
    } finally {
      setSearching(false);
    }
  }, []);

  const loadMore = useCallback(async (limit = 10) => {
    if (!currentQuery.current || loadingMore) return;
    setLoadingMore(true);
    try {
      const data = await searchPapers(
        currentQuery.current, limit, currentSource.current, currentOffset.current
      );
      setPapers((prev) => [...prev, ...(data.results || [])]);
      setHasMore(data.has_more ?? false);
      currentOffset.current += limit;
    } catch (e: unknown) {
      setSearchError(e instanceof Error ? e.message : "Load more failed");
    } finally {
      setLoadingMore(false);
    }
  }, [loadingMore]);

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

  const fetchLibrary = useCallback(async () => {
    setLibraryLoading(true);
    try {
      const data = await mcpLibrary();
      const text = data.content?.[0]?.text;
      if (text) {
        const parsed = JSON.parse(text);
        setLibraryPapers(parsed.papers || []);
      }
    } catch {
      // Library fetch may fail for guests — that's OK
      setLibraryPapers([]);
    } finally {
      setLibraryLoading(false);
    }
  }, []);

  const markSaved = useCallback((paperId: string) => {
    setPapers((prev) => prev.map((p) =>
      p.id === paperId ? { ...p, status: "saved" } : p
    ));
  }, []);

  return {
    papers, searching, searchError, search,
    analyses, analyzingId, analyzeError, analyze,
    hasMore, loadMore, loadingMore,
    libraryPapers, libraryLoading, fetchLibrary, markSaved,
  };
}
