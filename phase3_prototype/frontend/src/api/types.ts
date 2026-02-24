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

export interface SectionAnalysis {
  pass: "overview" | "methodology" | "results";
  data: Record<string, unknown>;
}

export interface DeepAnalysis {
  summary: string;
  methodology_detail: string;
  key_contributions: string[];
  limitations: string[];
  future_work: string[];
  strength_score: number;
  relevance_tags: string[];
  research_gaps: string[];
  section_analyses: SectionAnalysis[];
  _meta?: {
    bias_disclaimer: string;
    analysis_type: string;
    provider: string;
    model: string;
    passes: number;
  };
}

export interface DeepAnalysisResponse {
  paper_id: string;
  analysis_type: "deep";
  page_count: number;
  sections_extracted: number;
  analysis: DeepAnalysis;
}

export interface DivergencePoint {
  topic: string;
  positions: Record<string, string>;
  resolution?: string;
}

export interface Consensus {
  arxiv_id: string;
  agents_compared: string[];
  generated_at: string;
  generated_by: string;
  agreement_score: number;
  synthesized_summary: string;
  convergence_points: string[];
  divergence_points: DivergencePoint[];
  recommended_action?: string;
  bias_cross_check?: string;
  confidence_distribution?: Record<string, number>;
}

export interface ConsensusResponse {
  paper_id: string;
  consensus: Consensus;
}

export interface Agent {
  agent_id: string;
  name: string;
  model: string;
  capabilities: string[];
  strengths: string;
  cost_tier: "free" | "freemium" | "paid" | "enterprise";
  api_endpoint?: string;
  env_key?: string | null;
  registered_at: string;
  config?: Record<string, unknown>;
}

export type ViewMode = "search" | "library" | "graph" | "notes" | "agents";
