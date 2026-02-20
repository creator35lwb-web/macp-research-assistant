// MACP Research Assistant — TypeScript Interfaces (Phase 3C)

export interface User {
  id: number;
  github_id: number;
  github_login: string;
  github_name: string;
  github_avatar_url: string;
  connected_repo: string;
  created_at: string | null;
}

export interface Paper {
  id: string;
  title: string;
  authors: string[];
  abstract: string;
  url: string;
  status: string;
  source: string;
  added_at: string | null;
}

export interface Analysis {
  id: number;
  summary: string;
  key_insights: string[];
  methodology: string;
  relevance_tags: string[];
  research_gaps: string[];
  strength_score: number;
  provenance: Record<string, string>;
  _meta?: {
    bias_disclaimer: string;
    provider: string;
    model: string;
  };
}

export interface Note {
  id: number;
  paper_id: string | null;
  content: string;
  tags: string[];
  created_at: string | null;
  updated_at: string | null;
}

export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
  stats: { papers: number; analyses: number };
}

export interface GraphNode {
  id: string;
  title: string;
  type: "paper" | "analysis";
  status?: string;
  provider?: string;
  x?: number;
  y?: number;
}

export interface GraphEdge {
  source: number | GraphNode;
  target: number | GraphNode;
  type: string;
  tag?: string;
}

export interface McpResponse {
  content: { type: string; text: string }[];
  isError: boolean;
}

export interface GitHubRepo {
  full_name: string;
  name: string;
  private: boolean;
  description: string;
}

export type ViewMode = "search" | "library" | "graph" | "notes";
