// MACP Research Assistant — API Client (Phase 3C)
// Fetch wrapper with JWT auth (cookie-based) and error handling.

const API_BASE = import.meta.env.VITE_API_BASE ?? "http://localhost:8000";

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
    ...options,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || res.statusText);
  }

  return res.json();
}

// Auth
export const getMe = () => request<{ user: import("./types").User | null; authenticated: boolean }>("/api/auth/me");
export const logout = () => request<{ status: string }>("/api/auth/logout", { method: "POST" });

// Search
export const searchPapers = (query: string, limit = 10, source = "hysts", offset = 0) =>
  request<{ results: import("./types").Paper[]; count: number; has_more: boolean; offset: number }>("/search", {
    method: "POST",
    body: JSON.stringify({ query, limit, source, offset }),
  });

// Analyze
export const analyzePaper = (paper_id: string, provider = "gemini", api_key?: string) =>
  request<{ paper_id: string; title: string; analysis: import("./types").Analysis }>("/analyze", {
    method: "POST",
    body: JSON.stringify({ paper_id, provider, ...(api_key ? { api_key } : {}) }),
  });

// Deep Analysis (Phase 3E)
export const analyzeDeep = (paper_id: string, provider = "gemini", api_key?: string) =>
  request<import("./types").DeepAnalysisResponse>("/api/mcp/analyze-deep", {
    method: "POST",
    body: JSON.stringify({ paper_id, provider, ...(api_key ? { api_key } : {}) }),
  });

// WebMCP endpoints
export const mcpLibrary = () =>
  request<{ content: { type: string; text: string }[] }>("/api/mcp/library");

export const mcpGraph = () =>
  request<{ content: { type: string; text: string }[] }>("/api/mcp/graph");

export const mcpListNotes = () =>
  request<{ content: { type: string; text: string }[] }>("/api/mcp/notes");

export const mcpAddNote = (content: string, tags: string[] = [], paper_id?: string) =>
  request<{ content: { type: string; text: string }[] }>("/api/mcp/note", {
    method: "POST",
    body: JSON.stringify({ content, tags, ...(paper_id ? { paper_id } : {}) }),
  });

export const mcpSave = (paper_id: string) =>
  request<{ content: { type: string; text: string }[] }>("/api/mcp/save", {
    method: "POST",
    body: JSON.stringify({ paper_id }),
  });

// BYOK Validation
export const validateApiKey = (provider: string, api_key: string) =>
  request<{ valid: boolean; provider: string; model: string; error?: string }>("/api/validate-key", {
    method: "POST",
    body: JSON.stringify({ provider, api_key }),
  });

export const mcpDiscovery = () =>
  request<{ tools: unknown[]; count: number; version: string }>("/api/mcp/");

// GitHub Storage
export const githubRepos = () =>
  request<{ repos: import("./types").GitHubRepo[] }>("/api/github/repos");

export const githubConnect = (repo: string) =>
  request<{ status: string; repo: string }>("/api/github/connect", {
    method: "POST",
    body: JSON.stringify({ repo }),
  });

export const githubSync = () =>
  request<{ status: string; stats: Record<string, number> }>("/api/github/sync", { method: "POST" });

export const githubStatus = () =>
  request<{ connected: boolean; repo: string | null; manifest: unknown }>("/api/github/status");
