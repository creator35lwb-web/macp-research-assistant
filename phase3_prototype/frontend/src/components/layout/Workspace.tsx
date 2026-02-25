import { useCallback, useState } from "react";
import type { Note, ViewMode, DeepAnalysis, Consensus, Agent } from "../../api/types";
import { useAuth } from "../../hooks/useAuth";
import { usePapers } from "../../hooks/usePapers";
import { useGraph } from "../../hooks/useGraph";
import { useGitHub } from "../../hooks/useGitHub";
import { mcpAddNote, mcpListNotes, mcpSave, validateApiKey, analyzeDeep, generateConsensus, getAgents } from "../../api/client";
import { Sidebar } from "./Sidebar";
import { MainPanel } from "./MainPanel";
import { DetailPanel } from "./DetailPanel";
import { KnowledgeGraph } from "../graph/KnowledgeGraph";
import { ErrorBoundary } from "../common/ErrorBoundary";
import { showToast } from "../common/Toast";
import type { Paper } from "../../api/types";

export function Workspace() {
  const { user, loading: authLoading, logout, loginUrl } = useAuth();
  const {
    papers, searching, searchError, search,
    analyses, analyzingId, analyzeError, analyze,
    hasMore, loadMore, loadingMore,
    libraryPapers, libraryLoading, fetchLibrary, markSaved,
  } = usePapers();
  const { graphData, loading: graphLoading, fetchGraph } = useGraph();
  const {
    repos, connected, connectedRepo, loading: githubLoading,
    fetchStatus, fetchRepos, connect, sync,
  } = useGitHub();

  const [activeView, setActiveView] = useState<ViewMode>("search");
  const [selectedPaper, setSelectedPaper] = useState<Paper | null>(null);
  const [mobileDetailOpen, setMobileDetailOpen] = useState(false);
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);
  const [provider, setProvider] = useState("gemini");
  const [apiKey, setApiKey] = useState("");
  const [byokValidated, setByokValidated] = useState(false);
  const [byokValidating, setByokValidating] = useState(false);
  const [notes, setNotes] = useState<Note[]>([]);
  const [notesLoading, setNotesLoading] = useState(false);
  const [deepAnalyses, setDeepAnalyses] = useState<Record<string, { analysis: DeepAnalysis; pageCount: number; sectionsExtracted: number }>>({});
  const [analyzingDeep, setAnalyzingDeep] = useState(false);
  const [consensusResults, setConsensusResults] = useState<Record<string, Consensus>>({});
  const [generatingConsensus, setGeneratingConsensus] = useState(false);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [agentsLoading, setAgentsLoading] = useState(false);

  const fetchNotes = useCallback(async () => {
    setNotesLoading(true);
    try {
      const data = await mcpListNotes();
      const text = data.content?.[0]?.text;
      if (text) {
        const parsed = JSON.parse(text);
        setNotes(parsed.notes || []);
      }
    } catch {
      setNotes([]);
    } finally {
      setNotesLoading(false);
    }
  }, []);

  const fetchAgents = useCallback(async () => {
    setAgentsLoading(true);
    try {
      const data = await getAgents();
      const text = data.content?.[0]?.text;
      if (text) {
        const parsed = JSON.parse(text);
        setAgents(parsed.agents || []);
      }
    } catch {
      setAgents([]);
    } finally {
      setAgentsLoading(false);
    }
  }, []);

  // Fetch GitHub status on mount if user is logged in
  useState(() => {
    if (user) fetchStatus();
  });

  const handleSearch = (query: string, source: string) => {
    search(query, 10, source);
  };

  const handleAnalyze = (paperId: string) => {
    analyze(paperId, provider, apiKey || undefined);
  };

  const handleSave = async (paperId: string) => {
    try {
      await mcpSave(paperId);
      markSaved(paperId);
      showToast("success", "Paper saved to library");
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Failed to save paper";
      showToast("error", msg);
    }
  };

  const handleViewChange = (view: ViewMode) => {
    setActiveView(view);
    if (view === "library" && user) {
      fetchLibrary();
    }
    if (view === "notes" && user) {
      fetchNotes();
    }
    if (view === "agents") {
      fetchAgents();
    }
  };

  const handleAddNote = async (content: string, tags: string[], paperId?: string) => {
    try {
      await mcpAddNote(content, tags, paperId);
      showToast("success", "Note saved");
      fetchNotes();
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Failed to save note";
      showToast("error", msg);
    }
  };

  const handleValidateKey = async () => {
    if (!apiKey.trim()) {
      showToast("error", "Enter an API key first");
      return;
    }
    setByokValidating(true);
    try {
      const result = await validateApiKey(provider, apiKey);
      if (result.valid) {
        setByokValidated(true);
        showToast("success", `Key validated for ${result.provider} (${result.model})`);
      } else {
        setByokValidated(false);
        showToast("error", result.error || "Invalid API key");
      }
    } catch (err) {
      setByokValidated(false);
      const msg = err instanceof Error ? err.message : "Validation failed";
      showToast("error", msg);
    } finally {
      setByokValidating(false);
    }
  };

  const handleClearKey = () => {
    setApiKey("");
    setByokValidated(false);
    showToast("info", "API key cleared — using server default");
  };

  const handleProviderChange = (p: string) => {
    setProvider(p);
    setByokValidated(false);
  };

  const handleAnalyzeDeep = async (paperId: string) => {
    setAnalyzingDeep(true);
    try {
      const data = await analyzeDeep(paperId, provider, apiKey || undefined);
      setDeepAnalyses((prev) => ({
        ...prev,
        [paperId]: {
          analysis: data.analysis,
          pageCount: data.page_count,
          sectionsExtracted: data.sections_extracted,
        },
      }));
      showToast("success", "Deep analysis complete");
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Deep analysis failed";
      showToast("error", msg);
    } finally {
      setAnalyzingDeep(false);
    }
  };

  const handleGenerateConsensus = async (paperId: string) => {
    setGeneratingConsensus(true);
    try {
      const data = await generateConsensus(paperId, provider, apiKey || undefined);
      setConsensusResults((prev) => ({ ...prev, [paperId]: data.consensus }));
      showToast("success", `Consensus generated (${data.consensus.agreement_score.toFixed(0)}% agreement)`);
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Consensus generation failed";
      showToast("error", msg);
    } finally {
      setGeneratingConsensus(false);
    }
  };

  if (authLoading) {
    return <div className="workspace" style={{ placeItems: "center", display: "grid" }}>Loading...</div>;
  }

  const handleSelectPaper = (paper: Paper) => {
    setSelectedPaper(paper);
    setMobileDetailOpen(true);
  };

  const handleMobileViewChange = (view: ViewMode) => {
    handleViewChange(view);
    setMobileSidebarOpen(false);
  };

  return (
    <div className="workspace">
      {/* Mobile header — visible only on small screens */}
      <header className="mobile-header">
        <button className="mobile-menu-btn" onClick={() => setMobileSidebarOpen(!mobileSidebarOpen)}>
          <span className="mobile-menu-icon" />
        </button>
        <span className="sidebar-logo">MACP Research</span>
        {user && <img className="mobile-avatar" src={user.github_avatar_url} alt="" />}
      </header>

      {/* Mobile sidebar overlay */}
      {mobileSidebarOpen && (
        <div className="mobile-sidebar-overlay" onClick={() => setMobileSidebarOpen(false)}>
          <div className="mobile-sidebar" onClick={(e) => e.stopPropagation()}>
            <Sidebar
              user={user}
              loginUrl={loginUrl}
              onLogout={logout}
              activeView={activeView}
              onViewChange={handleMobileViewChange}
              repos={repos}
              connected={connected}
              connectedRepo={connectedRepo}
              githubLoading={githubLoading}
              onFetchRepos={fetchRepos}
              onConnect={connect}
              onSync={sync}
            />
          </div>
        </div>
      )}

      {/* Desktop sidebar */}
      <Sidebar
        user={user}
        loginUrl={loginUrl}
        onLogout={logout}
        activeView={activeView}
        onViewChange={handleViewChange}
        repos={repos}
        connected={connected}
        connectedRepo={connectedRepo}
        githubLoading={githubLoading}
        onFetchRepos={fetchRepos}
        onConnect={connect}
        onSync={sync}
      />

      <ErrorBoundary>
        {activeView === "graph" && graphData ? (
          <main className="main-panel" style={{ padding: 0 }}>
            <KnowledgeGraph data={graphData} />
          </main>
        ) : (
          <MainPanel
            view={activeView}
            papers={papers}
            libraryPapers={libraryPapers}
            libraryLoading={libraryLoading}
            searching={searching}
            searchError={searchError}
            onSearch={handleSearch}
            selectedPaper={selectedPaper}
            onSelectPaper={handleSelectPaper}
            analyses={analyses}
            analyzingId={analyzingId}
            analyzeError={analyzeError}
            onAnalyze={handleAnalyze}
            onSave={user ? handleSave : undefined}
            onAddNote={handleAddNote}
            onLoadGraph={fetchGraph}
            graphLoading={graphLoading}
            provider={provider}
            onProviderChange={handleProviderChange}
            apiKey={apiKey}
            onApiKeyChange={(k) => { setApiKey(k); setByokValidated(false); }}
            byokValidated={byokValidated}
            byokValidating={byokValidating}
            onValidateKey={handleValidateKey}
            onClearKey={handleClearKey}
            hasMore={hasMore}
            onLoadMore={() => loadMore()}
            loadingMore={loadingMore}
            notes={notes}
            notesLoading={notesLoading}
            agents={agents}
            agentsLoading={agentsLoading}
            onFetchAgents={fetchAgents}
          />
        )}
      </ErrorBoundary>

      <div className={`detail-panel-wrapper ${mobileDetailOpen && selectedPaper ? "mobile-open" : ""}`}>
        {mobileDetailOpen && selectedPaper && (
          <button className="mobile-back-btn" onClick={() => setMobileDetailOpen(false)}>
            &larr; Back to results
          </button>
        )}
        <DetailPanel
          paper={selectedPaper}
          analysis={selectedPaper ? analyses[selectedPaper.id] : undefined}
          deepAnalysis={selectedPaper ? deepAnalyses[selectedPaper.id] : undefined}
          consensus={selectedPaper ? consensusResults[selectedPaper.id] : undefined}
          onAnalyzeDeep={handleAnalyzeDeep}
          onGenerateConsensus={handleGenerateConsensus}
          analyzingDeep={analyzingDeep}
          generatingConsensus={generatingConsensus}
        />
      </div>
    </div>
  );
}
