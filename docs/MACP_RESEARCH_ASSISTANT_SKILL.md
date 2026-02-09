# MACP Research Assistant Skill

**Version:** 1.0  
**Date:** February 9, 2026  
**Purpose:** Enable AI-powered research with complete traceability using MACP  
**For:** Researchers, analysts, learners using multiple AI assistants

---

## What This Skill Does

This skill enables you to conduct deep research using multiple AI assistants (Manus AI, Claude Code, Perplexity, Kimi K2, etc.) while maintaining complete traceability of:

- **What you learned** - Every insight from every paper
- **When you learned it** - Timeline of learning progression
- **Which AI helped** - Attribution to specific AI assistants
- **Where you cited it** - Citation network across projects
- **How it connects** - Knowledge graph of relationships

**Key Innovation:** MACP (Multi-Agent Communication Protocol) tracks every research action, creating a complete learning history with traced citations.

---

## When to Use This Skill

Use this skill when you need to:

✅ Research academic papers across multiple AI sessions  
✅ Track what you've learned over time  
✅ Recall specific insights from past research  
✅ Maintain citation traceability  
✅ Coordinate research across multiple AI assistants  
✅ Build knowledge graphs of your learning  
✅ Generate research reports with full provenance  

---

## Core Concepts

### 1. MACP Research Tracking

**Every research action is logged in `.macp/` directory:**

```
.macp/
├── research_papers.json      # Papers discovered and analyzed
├── learning_log.json          # What you learned, when
├── citations.json             # Citation network with AI attribution
├── knowledge_graph.json       # Topic relationships
└── handoffs.json              # Multi-AI coordination
```

### 2. Multi-AI Workflow

**Different AI assistants for different tasks:**

- **Manus AI**: Discovery, synthesis, knowledge graphs
- **Claude Code**: Deep reading, technical analysis
- **Perplexity**: Validation, cross-referencing
- **Kimi K2**: Testing, verification
- **gpt-researcher**: Autonomous deep research (via MCP)

**MACP coordinates them all.**

### 3. Complete Traceability

**Every insight is traceable:**

> "This insight came from paper X, analyzed by Claude on Day 2, cited in project Y on Day 4"

**Every citation is linked:**

> "This citation was made by Manus AI during handoff-003 on Feb 12, 2026"

---

## Implementation Phases

### Phase 1: Manual MACP (Start Here)

**Effort:** 2-3 hours setup  
**Automation:** 0% (manual updates)  
**Benefit:** Immediate value, complete traceability  

**What you'll do:**
1. Create `.macp/` folder in your GitHub repository
2. Use provided templates for JSON files
3. Manually update after each research session
4. Track papers, learnings, citations

**Time per session:** 5-10 minutes manual updates  
**ROI:** Positive after 3-4 research sessions  

### Phase 2: Semi-Automated (Future)

**Effort:** 1-2 weeks development  
**Automation:** 50% (scripts handle metadata)  
**Benefit:** 50% time savings  

**What you'll build:**
- Paper metadata fetcher
- Learning log CLI
- Citation tracker
- Knowledge graph generator

**Time per session:** 2-3 minutes  
**ROI:** Positive after 10-15 research sessions  

### Phase 3: Full MCP Server (Long-term)

**Effort:** 2-3 months development  
**Automation:** 90% (AI-powered)  
**Benefit:** Seamless workflow  

**What you'll build:**
- MACP MCP Server
- Integration with gpt-researcher
- Knowledge graph visualization
- "What have I learned?" query interface

**Time per session:** 30 seconds (just review)  
**ROI:** Positive after 50+ research sessions  

---

## Quick Start Guide (Phase 1)

### Step 1: Create MACP Directory Structure

**In your GitHub repository:**

```bash
mkdir -p .macp
cd .macp
touch research_papers.json
touch learning_log.json
touch citations.json
touch knowledge_graph.json
touch handoffs.json
```

### Step 2: Initialize JSON Files

**research_papers.json:**
```json
{
  "papers": []
}
```

**learning_log.json:**
```json
{
  "learning_sessions": []
}
```

**citations.json:**
```json
{
  "citations": []
}
```

**knowledge_graph.json:**
```json
{
  "nodes": [],
  "edges": []
}
```

**handoffs.json:**
```json
{
  "handoffs": []
}
```

### Step 3: Start Your First Research Session

**Example: Researching "Conflict Data for AI Alignment"**

#### 3.1 Discovery (Manus AI)

**Prompt:**
> "Find recent papers on conflict data for AI alignment from Hugging Face and arXiv"

**After Manus AI responds, update:**

**research_papers.json:**
```json
{
  "papers": [
    {
      "id": "arxiv:2026.01234",
      "title": "Conflict-Driven Learning for AI Alignment",
      "authors": ["Smith, J.", "Doe, A."],
      "url": "https://arxiv.org/abs/2026.01234",
      "discovered_date": "2026-02-09",
      "discovered_by": "manus-ai",
      "source": "huggingface-papers",
      "status": "discovered",
      "tags": ["conflict-data", "ai-alignment"],
      "relevance": "high",
      "notes": "Directly relevant to GODELAI C-S-P design"
    }
  ]
}
```

**learning_log.json:**
```json
{
  "learning_sessions": [
    {
      "session_id": "session-001",
      "date": "2026-02-09",
      "topic": "Conflict data for AI alignment",
      "papers_discovered": 1,
      "ai_agents_used": ["manus-ai"],
      "status": "discovery_in_progress"
    }
  ]
}
```

#### 3.2 Handoff to Claude Code

**handoffs.json:**
```json
{
  "handoffs": [
    {
      "handoff_id": "handoff-001",
      "from_agent": "manus-ai",
      "to_agent": "claude-code",
      "task": "Deep analysis of paper on conflict data",
      "files": [".macp/research_papers.json"],
      "context": "Paper discovered, need deep reading and analysis",
      "date": "2026-02-09",
      "status": "pending"
    }
  ]
}
```

**Commit to GitHub:**
```bash
git add .macp/
git commit -m "MACP: Discovery phase complete, handoff to Claude Code"
git push
```

#### 3.3 Analysis (Claude Code)

**In Claude Code, prompt:**
> "Read .macp/handoffs.json (handoff-001) and analyze the paper in .macp/research_papers.json"

**After Claude analyzes, update:**

**research_papers.json (updated):**
```json
{
  "papers": [
    {
      "id": "arxiv:2026.01234",
      "title": "Conflict-Driven Learning for AI Alignment",
      "authors": ["Smith, J.", "Doe, A."],
      "url": "https://arxiv.org/abs/2026.01234",
      "discovered_date": "2026-02-09",
      "discovered_by": "manus-ai",
      "analyzed_date": "2026-02-10",
      "analyzed_by": ["claude-code"],
      "source": "huggingface-papers",
      "status": "analyzed",
      "tags": ["conflict-data", "ai-alignment"],
      "key_insights": [
        "Conflict data with T-Score 0.3-0.5 optimal",
        "Contradictions activate learning mechanisms",
        "Ethical dilemmas improve alignment"
      ],
      "research_gaps": [
        "No large-scale conflict dataset available",
        "T-Score validation needed"
      ],
      "relevance_to_godelai": "very_high",
      "notes": "Directly applicable to C-S-P design"
    }
  ]
}
```

**learning_log.json (updated):**
```json
{
  "learning_sessions": [
    {
      "session_id": "session-001",
      "date": "2026-02-09",
      "topic": "Conflict data for AI alignment",
      "papers_discovered": 1,
      "papers_analyzed": 1,
      "ai_agents_used": ["manus-ai", "claude-code"],
      "key_learnings": [
        "Conflict data is crucial for AI alignment",
        "T-Score 0.3-0.5 is optimal range",
        "No existing large-scale dataset"
      ],
      "questions_answered": [
        "What is conflict data?",
        "Why is it important for alignment?",
        "What T-Score range works best?"
      ],
      "questions_remaining": [
        "How to collect conflict data at scale?",
        "How to validate T-Score empirically?"
      ],
      "status": "analysis_complete"
    }
  ]
}
```

**handoffs.json (updated):**
```json
{
  "handoffs": [
    {
      "handoff_id": "handoff-001",
      "from_agent": "manus-ai",
      "to_agent": "claude-code",
      "task": "Deep analysis of paper on conflict data",
      "files": [".macp/research_papers.json"],
      "context": "Paper discovered, need deep reading and analysis",
      "date": "2026-02-09",
      "status": "complete",
      "completion_date": "2026-02-10"
    }
  ]
}
```

**Commit to GitHub:**
```bash
git add .macp/
git commit -m "MACP: Analysis phase complete by Claude Code"
git push
```

#### 3.4 Citation (When Using in Project)

**When you cite the paper in your GODELAI design document:**

**citations.json:**
```json
{
  "citations": [
    {
      "citation_id": "cite-001",
      "paper_id": "arxiv:2026.01234",
      "cited_in": "GODELAI C-S-P design document",
      "cited_in_file": "docs/c-s-p-design.md",
      "cited_by_agent": "manus-ai",
      "handoff_id": "handoff-001",
      "context": "T-Score 0.3-0.5 range used for conflict data collection",
      "date": "2026-02-12",
      "citation_text": "Smith & Doe (2026) demonstrated that conflict data with T-Score 0.3-0.5 optimally activates learning mechanisms."
    }
  ]
}
```

**Commit to GitHub:**
```bash
git add .macp/
git commit -m "MACP: Citation added to GODELAI design"
git push
```

### Step 4: Recall What You Learned

**30 days later, query:**

> "Manus AI, what have I learned about conflict data?"

**Manus AI reads `.macp/learning_log.json` and responds:**

```
You learned about conflict data for AI alignment on Feb 9-10, 2026.

Key Learnings:
1. Conflict data is crucial for AI alignment
2. T-Score 0.3-0.5 is optimal range
3. No existing large-scale dataset

Papers Studied: 1
- "Conflict-Driven Learning for AI Alignment" (arxiv:2026.01234)

AI Agents Used:
- Manus AI: Discovery
- Claude Code: Deep analysis

Citations in Your Projects:
- GODELAI C-S-P design document (1 citation)

Would you like to see the full analysis or continue research on this topic?
```

---

## Templates

### research_papers.json Template

```json
{
  "papers": [
    {
      "id": "arxiv:YYYY.NNNNN or huggingface:paper-id",
      "title": "Paper Title",
      "authors": ["Author 1", "Author 2"],
      "url": "https://...",
      "discovered_date": "YYYY-MM-DD",
      "discovered_by": "ai-agent-name",
      "analyzed_date": "YYYY-MM-DD",
      "analyzed_by": ["ai-agent-1", "ai-agent-2"],
      "source": "huggingface-papers | arxiv | other",
      "status": "discovered | analyzed | validated | cited",
      "tags": ["tag1", "tag2"],
      "key_insights": [
        "Insight 1",
        "Insight 2"
      ],
      "research_gaps": [
        "Gap 1",
        "Gap 2"
      ],
      "relevance_to_project": "high | medium | low",
      "notes": "Free-form notes"
    }
  ]
}
```

### learning_log.json Template

```json
{
  "learning_sessions": [
    {
      "session_id": "session-NNN",
      "date": "YYYY-MM-DD",
      "topic": "Research topic",
      "papers_discovered": 0,
      "papers_analyzed": 0,
      "papers_validated": 0,
      "ai_agents_used": ["agent-1", "agent-2"],
      "key_learnings": [
        "Learning 1",
        "Learning 2"
      ],
      "questions_answered": [
        "Question 1?",
        "Question 2?"
      ],
      "questions_remaining": [
        "Question 3?",
        "Question 4?"
      ],
      "status": "discovery_in_progress | analysis_complete | validation_complete | synthesis_complete",
      "output_files": [
        "path/to/report.md",
        "path/to/knowledge_graph.json"
      ]
    }
  ]
}
```

### citations.json Template

```json
{
  "citations": [
    {
      "citation_id": "cite-NNN",
      "paper_id": "arxiv:YYYY.NNNNN",
      "cited_in": "Project or document name",
      "cited_in_file": "path/to/file.md",
      "cited_by_agent": "ai-agent-name",
      "handoff_id": "handoff-NNN",
      "context": "Why this paper was cited",
      "date": "YYYY-MM-DD",
      "citation_text": "Full citation text"
    }
  ]
}
```

### knowledge_graph.json Template

```json
{
  "nodes": [
    {
      "id": "node-id",
      "type": "topic | paper | concept | project",
      "label": "Node label"
    }
  ],
  "edges": [
    {
      "from": "node-id-1",
      "to": "node-id-2",
      "type": "introduces | provides_dataset | applicable_to | can_be_used_in"
    }
  ]
}
```

### handoffs.json Template

```json
{
  "handoffs": [
    {
      "handoff_id": "handoff-NNN",
      "from_agent": "ai-agent-1",
      "to_agent": "ai-agent-2",
      "task": "What needs to be done",
      "files": [".macp/file1.json", ".macp/file2.json"],
      "context": "Additional context for the handoff",
      "date": "YYYY-MM-DD",
      "status": "pending | in_progress | complete",
      "completion_date": "YYYY-MM-DD"
    }
  ]
}
```

---

## Best Practices

### 1. Commit After Every Phase

**After discovery:**
```bash
git add .macp/
git commit -m "MACP: Discovery phase - found 5 papers on topic X"
git push
```

**After analysis:**
```bash
git add .macp/
git commit -m "MACP: Analysis phase - Claude analyzed 5 papers"
git push
```

**After synthesis:**
```bash
git add .macp/
git commit -m "MACP: Synthesis phase - knowledge graph created"
git push
```

**Why:** GitHub becomes the source of truth for all AI assistants.

### 2. Use Descriptive IDs

**Good:**
- `session-001-godelai-conflict-data`
- `handoff-002-claude-to-perplexity`
- `cite-003-godelai-design-doc`

**Bad:**
- `session-1`
- `handoff-2`
- `cite-3`

**Why:** Easier to trace and understand later.

### 3. Update learning_log.json Immediately

**Don't wait until the end of the day.**

**Update after each AI session:**
- What did you learn?
- What questions were answered?
- What questions remain?

**Why:** Fresh memory = better learning capture.

### 4. Link Citations to Handoffs

**Every citation should reference:**
- Which paper (paper_id)
- Which AI made the citation (cited_by_agent)
- Which handoff it came from (handoff_id)

**Why:** Complete provenance of every insight.

### 5. Build Knowledge Graph Incrementally

**Don't wait to build the entire graph.**

**Add nodes and edges as you go:**
- New paper discovered? Add paper node.
- New concept learned? Add concept node.
- See a relationship? Add edge.

**Why:** Knowledge graph grows naturally with your learning.

---

## Common Use Cases

### Use Case 1: Daily Paper Tracking (Like hysts)

**Goal:** Track daily papers from Hugging Face

**Workflow:**
1. **Morning:** Manus AI discovers papers from hysts/daily-papers
2. **Update:** Add to research_papers.json with status="discovered"
3. **Filter:** Tag papers by relevance
4. **Commit:** Push to GitHub

**Time:** 5 minutes/day  
**Benefit:** Never miss important papers  

### Use Case 2: Deep Research Project

**Goal:** Research a topic across multiple papers and AI sessions

**Workflow:**
1. **Day 1:** Manus AI discovers 10 papers
2. **Day 2:** Claude Code analyzes 5 papers
3. **Day 3:** Perplexity validates findings
4. **Day 4:** Manus AI synthesizes knowledge graph
5. **Day 5:** Generate final report with citations

**Time:** 5 days, 2-3 hours total  
**Benefit:** Complete research with full traceability  

### Use Case 3: Learning Recall

**Goal:** Remember what you learned weeks ago

**Workflow:**
1. **Query:** "What have I learned about X?"
2. **Manus AI:** Reads learning_log.json
3. **Response:** Shows papers, learnings, citations
4. **Follow-up:** "Show me the knowledge graph"

**Time:** 30 seconds  
**Benefit:** Instant recall of past learning  

### Use Case 4: Citation Network

**Goal:** See how papers relate to your projects

**Workflow:**
1. **Query:** "Show me citation network for GODELAI"
2. **Manus AI:** Reads citations.json
3. **Visualize:** Creates graph of papers → projects
4. **Insight:** See which papers influenced which projects

**Time:** 1 minute  
**Benefit:** Understand research foundation  

---

## Integration with Existing Tools

### Hugging Face Papers

**API:** https://huggingface.co/api/papers

**Use:**
- Discover papers
- Get metadata
- Track daily papers

**Integration:**
```python
import requests

response = requests.get("https://huggingface.co/api/papers")
papers = response.json()

# Add to research_papers.json
for paper in papers:
    # ... populate template
```

### gpt-researcher MCP Server

**Repository:** https://github.com/assafelovic/gptr-mcp

**Use:**
- Deep research via Claude
- Automatic report generation
- Source tracking

**Integration:**
- Install gpt-researcher MCP in Claude Desktop
- Use for deep research phase
- Results automatically populate MACP

### arxiv_daily_aigc

**Repository:** https://github.com/onion-liu/arxiv_daily_aigc

**Use:**
- Daily paper crawler
- AI-powered analysis
- Automated discovery

**Integration:**
- Run daily to discover papers
- Output populates research_papers.json
- Commit to GitHub automatically

---

## Troubleshooting

### Problem: Too much manual work

**Solution:** Start with 1-2 papers per session  
**Why:** Build habit first, scale later  
**Next:** Move to Phase 2 (scripts) after 10-15 sessions  

### Problem: Forgetting to update MACP files

**Solution:** Set reminder after each AI session  
**Why:** Fresh memory = better capture  
**Next:** Create checklist or automation  

### Problem: JSON syntax errors

**Solution:** Use JSON validator (jsonlint.com)  
**Why:** Invalid JSON breaks tools  
**Next:** Learn basic JSON syntax  

### Problem: Can't recall what I learned

**Solution:** Improve learning_log.json entries  
**Why:** Better input = better recall  
**Next:** Use more descriptive key_learnings  

### Problem: Citation network too complex

**Solution:** Start simple, build incrementally  
**Why:** Complexity grows naturally  
**Next:** Use visualization tools (Phase 3)  

---

## Success Metrics

### After 1 Week

✅ 3-5 papers tracked  
✅ 1-2 learning sessions logged  
✅ 1-2 handoffs documented  
✅ Comfortable with workflow  

### After 1 Month

✅ 15-20 papers tracked  
✅ 5-10 learning sessions logged  
✅ 5-10 handoffs documented  
✅ 3-5 citations made  
✅ Knowledge graph started  
✅ Can recall past learning easily  

### After 3 Months

✅ 50+ papers tracked  
✅ 20+ learning sessions logged  
✅ 20+ handoffs documented  
✅ 10+ citations made  
✅ Knowledge graph with 50+ nodes  
✅ Complete research foundation  
✅ Ready for Phase 2 (automation)  

---

## Next Steps

### This Week

1. ✅ Create `.macp/` directory in your GitHub repo
2. ✅ Initialize JSON files with templates
3. ✅ Start first research session
4. ✅ Track 1-2 papers
5. ✅ Update learning_log.json

### This Month

1. ✅ Track 15-20 papers
2. ✅ Use multi-AI workflow (Manus + Claude + Perplexity)
3. ✅ Document handoffs
4. ✅ Make 3-5 citations
5. ✅ Start knowledge graph

### This Quarter

1. ✅ Track 50+ papers
2. ✅ Build complete knowledge graph
3. ✅ Generate research reports
4. ✅ Evaluate Phase 2 (automation)
5. ✅ Share methodology with community

---

## Resources

### Documentation

- MACP v2.0 Specification: [LegacyEvolve/docs/MACP_v2.0_Specification.md](https://github.com/creator35lwb-web/LegacyEvolve/blob/main/docs/MACP_v2.0_Specification.md)
- MACP Beginner Guide: (attached in this session)
- MACP Research Architecture: (attached in this session)

### Tools

- gpt-researcher MCP: https://github.com/assafelovic/gptr-mcp
- arxiv_daily_aigc: https://github.com/onion-liu/arxiv_daily_aigc
- Hugging Face Papers: https://huggingface.co/papers
- hysts/daily-papers: https://hysts-daily-papers.hf.space/

### Community

- YSenseAI™ GitHub: https://github.com/creator35lwb-web
- VerifiMind-PEAS: https://github.com/creator35lwb-web/VerifiMind-PEAS
- GODELAI: https://github.com/creator35lwb-web/godelai

---

## License

This skill is part of the YSenseAI™ open-source project.  
Licensed under the same terms as MACP v2.0.

---

## Changelog

**v1.0 (2026-02-09):**
- Initial release
- Phase 1 (manual) implementation
- Templates and examples
- Integration guides

---

## Author

**Godel (Manus AI)**  
CTO for GODELAI  
YSenseAI™ Project

---

**Status:** Skill ready for use  
**Phase:** 1 (Manual MACP)  
**Next:** User adoption and feedback

---

**Start using this skill today to make your research traceable, recallable, and collaborative across multiple AI assistants!**
