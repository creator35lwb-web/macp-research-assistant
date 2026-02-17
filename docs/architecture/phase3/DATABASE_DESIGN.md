# Database Design — Phase 3 Architecture

**Author:** RNA (Claude Code), following L (Godel) blueprint
**Date:** 2026-02-17
**Status:** Design Document (implementation deferred to Phase 3)

---

## 1. Technology Choice

**Initial:** SQLite (embedded, zero-config, single-file)
**Migration Path:** PostgreSQL (when multi-user or cloud deployment is needed)

### Why SQLite First
- Zero infrastructure — single `.macp/macp.db` file
- Full SQL with JSON support (`json_extract()`)
- Atomic transactions replace our manual atomic write pattern
- Python `sqlite3` is in the standard library (no new dependencies)
- Easy to back up (copy one file)

### PostgreSQL Migration Path
- Use an ORM abstraction layer (`sqlite3` -> `asyncpg`/`psycopg2`)
- All queries use standard SQL (no SQLite-specific features)
- Migration script: `tools/migrate_json_to_db.py` (to be built)
- Environment variable `MACP_DATABASE_URL` switches backends

---

## 2. SQL Schema

### papers

```sql
CREATE TABLE papers (
    id TEXT PRIMARY KEY,              -- 'arxiv:XXXX.XXXXX'
    title TEXT NOT NULL,
    authors TEXT NOT NULL DEFAULT '[]', -- JSON array of strings
    abstract TEXT DEFAULT '',
    url TEXT,
    discovered_by TEXT NOT NULL,
    discovered_date DATE NOT NULL,
    status TEXT NOT NULL DEFAULT 'discovered'
        CHECK (status IN ('discovered', 'analyzing', 'analyzed', 'cited', 'validated', 'rejected')),
    insights TEXT DEFAULT '[]',       -- JSON array of strings
    meta TEXT DEFAULT '{}',           -- JSON object for extra fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_papers_status ON papers(status);
CREATE INDEX idx_papers_discovered_date ON papers(discovered_date);
```

### learning_sessions

```sql
CREATE TABLE learning_sessions (
    session_id TEXT PRIMARY KEY,
    date DATE NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    agent TEXT NOT NULL,
    summary TEXT NOT NULL,
    key_insight TEXT,
    tags TEXT DEFAULT '[]',           -- JSON array of strings
    analysis TEXT DEFAULT '{}',       -- JSON object (provider, model, methodology, etc.)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sessions_date ON learning_sessions(date);
CREATE INDEX idx_sessions_agent ON learning_sessions(agent);
```

### session_papers (junction table)

```sql
CREATE TABLE session_papers (
    session_id TEXT NOT NULL REFERENCES learning_sessions(session_id),
    paper_id TEXT NOT NULL REFERENCES papers(id),
    PRIMARY KEY (session_id, paper_id)
);
```

### citations

```sql
CREATE TABLE citations (
    citation_id TEXT PRIMARY KEY,
    paper_id TEXT NOT NULL REFERENCES papers(id),
    cited_in TEXT NOT NULL,
    context TEXT,
    cited_by TEXT NOT NULL,
    date DATE NOT NULL,
    handoff_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_citations_paper ON citations(paper_id);
CREATE INDEX idx_citations_project ON citations(cited_in);
```

### handoffs

```sql
CREATE TABLE handoffs (
    handoff_id TEXT PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    from_agent TEXT NOT NULL,
    to_agent TEXT NOT NULL,
    task_summary TEXT NOT NULL,
    completed TEXT DEFAULT '[]',      -- JSON array of strings
    pending TEXT DEFAULT '[]',        -- JSON array of strings
    knowledge_state TEXT DEFAULT '{}' -- JSON object
);

CREATE INDEX idx_handoffs_timestamp ON handoffs(timestamp);
```

### handoff_papers (junction table)

```sql
CREATE TABLE handoff_papers (
    handoff_id TEXT NOT NULL REFERENCES handoffs(handoff_id),
    paper_id TEXT NOT NULL REFERENCES papers(id),
    PRIMARY KEY (handoff_id, paper_id)
);
```

### users (for Phase 3 auth)

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    api_key_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP,
    is_active BOOLEAN DEFAULT 1
);

CREATE UNIQUE INDEX idx_users_username ON users(username);
```

---

## 3. Relationships

```
papers 1──* session_papers *──1 learning_sessions
papers 1──* citations
papers 1──* handoff_papers *──1 handoffs
users  1──* learning_sessions (future: agent -> user_id)
```

---

## 4. Migration Strategy

### JSON -> SQLite Migration Script

```python
# tools/migrate_json_to_db.py (to be implemented in Phase 3)
# 1. Read all .macp/*.json files
# 2. Create SQLite database with schema above
# 3. Insert all records with foreign key resolution
# 4. Validate record counts match
# 5. Backup original JSON files to .macp/backup/
```

### Backwards Compatibility
- Keep JSON read/write functions as fallback during migration period
- Environment variable `MACP_STORAGE=json|sqlite` to switch
- Default: `json` (current), switchable to `sqlite` when ready

---

## 5. Performance Notes

- SQLite handles up to ~100K papers with no performance issues
- Full-text search via `FTS5` extension for enhanced recall
- JSON columns use `json_extract()` for tag/insight queries
- WAL mode for concurrent read access
