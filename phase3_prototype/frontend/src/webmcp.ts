/**
 * MACP Research Assistant — WebMCP Tool Registration
 * ====================================================
 * Registers `search_papers` and `analyze_paper` as WebMCP tools
 * so that browser-based AI agents (e.g., Chrome 146+ with Prompt API)
 * can discover and invoke them.
 *
 * Uses the `navigator.modelContext.provideContext` API (Chrome 146+).
 *
 * Author: RNA (Claude Code)
 * Date: February 19, 2026
 */

const API_BASE = import.meta.env.VITE_API_BASE ?? "http://localhost:8000";

// Callback to update React state from outside the component
type StateCallback = (data: unknown) => void;
let onSearchResults: StateCallback | null = null;
let onAnalysisResult: StateCallback | null = null;

/**
 * Allow the React app to register callbacks for state updates.
 */
export function registerCallbacks(
  searchCb: StateCallback,
  analysisCb: StateCallback
) {
  onSearchResults = searchCb;
  onAnalysisResult = analysisCb;
}

/**
 * Tool definitions for WebMCP registration.
 */
const tools = [
  {
    name: "search_papers",
    description:
      "Searches for research papers on arXiv and Hugging Face. Returns a list of papers with titles, authors, abstracts, and arXiv IDs.",
    inputSchema: {
      type: "object",
      properties: {
        query: {
          type: "string",
          description:
            "The search query (e.g., 'multi-agent systems', 'LLM reasoning')",
        },
        limit: {
          type: "integer",
          description: "Maximum number of results to return (default: 10)",
          default: 10,
        },
      },
      required: ["query"],
    },
    async execute(input: { query: string; limit?: number }) {
      const res = await fetch(`${API_BASE}/search`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: input.query,
          limit: input.limit || 10,
          source: "hysts",
        }),
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Search failed");
      }

      const data = await res.json();

      // Update the UI state if callback is registered
      if (onSearchResults) {
        onSearchResults(data.results);
      }

      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(data.results, null, 2),
          },
        ],
      };
    },
  },
  {
    name: "analyze_paper",
    description:
      "Analyzes a given research paper using an AI model. Returns a structured analysis with summary, key insights, methodology, research gaps, and strength score.",
    inputSchema: {
      type: "object",
      properties: {
        paper_id: {
          type: "string",
          description:
            "The arXiv ID of the paper (e.g., '2501.12345' or 'arxiv:2501.12345')",
        },
        provider: {
          type: "string",
          description:
            "The LLM provider to use: 'gemini' (free), 'anthropic', or 'openai'",
          default: "gemini",
        },
        api_key: {
          type: "string",
          description:
            "Optional API key for the provider (BYOK). Leave empty to use server-side env var.",
        },
      },
      required: ["paper_id"],
    },
    async execute(input: {
      paper_id: string;
      provider?: string;
      api_key?: string;
    }) {
      const body: Record<string, string> = {
        paper_id: input.paper_id,
        provider: input.provider || "gemini",
      };
      if (input.api_key) body.api_key = input.api_key;

      const res = await fetch(`${API_BASE}/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Analysis failed");
      }

      const data = await res.json();

      // Update the UI state if callback is registered
      if (onAnalysisResult) {
        onAnalysisResult({ paperId: data.paper_id, analysis: data.analysis });
      }

      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(data.analysis, null, 2),
          },
        ],
      };
    },
  },
];

/**
 * Register tools with the WebMCP API if available.
 *
 * Chrome 146+ exposes `navigator.modelContext.provideContext()`
 * for registering tools that browser-based AI agents can discover.
 */
export async function registerWebMCPTools(): Promise<boolean> {
  // Check if the WebMCP API is available
  const nav = navigator as unknown as {
    modelContext?: {
      provideContext: (config: {
        tools: typeof tools;
      }) => Promise<void>;
    };
  };

  if (!nav.modelContext?.provideContext) {
    console.log(
      "[WebMCP] navigator.modelContext.provideContext not available.",
      "This is expected if not running in Chrome 146+ with Prompt API enabled."
    );
    return false;
  }

  try {
    await nav.modelContext.provideContext({ tools });
    console.log(
      "[WebMCP] Successfully registered 2 tools: search_papers, analyze_paper"
    );
    return true;
  } catch (err) {
    console.error("[WebMCP] Failed to register tools:", err);
    return false;
  }
}

/**
 * Expose tools for manual invocation from DevTools console.
 *
 * Usage in Chrome DevTools:
 *   await window.macpTools.search_papers({ query: "multi-agent" })
 *   await window.macpTools.analyze_paper({ paper_id: "2501.12345" })
 */
declare global {
  interface Window {
    macpTools: {
      search_papers: typeof tools[0]["execute"];
      analyze_paper: typeof tools[1]["execute"];
    };
  }
}

window.macpTools = {
  search_papers: tools[0].execute,
  analyze_paper: tools[1].execute,
};
