# Authentication Design — Phase 3 Architecture

**Author:** RNA (Claude Code), following L (Godel) blueprint
**Date:** 2026-02-17
**Status:** Design Document (implementation deferred to Phase 3)

---

## 1. Strategy

**Approach:** Simple API key-based authentication
**Scope:** MCP server endpoints (Phase 3), not the local CLI

### Why API Keys (Not OAuth/JWT)
- Simplest model for programmatic access (AI agents)
- No session management needed
- Easy to generate, revoke, and rotate
- Standard pattern for developer tools (like our BYOK model)
- Can upgrade to OAuth later if web UI is added

---

## 2. User Table

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    api_key_hash TEXT NOT NULL,        -- SHA-256 hash of the API key
    api_key_prefix TEXT NOT NULL,      -- First 8 chars for identification
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP,
    is_active BOOLEAN DEFAULT 1,
    rate_limit INTEGER DEFAULT 100     -- Requests per hour
);
```

---

## 3. API Key Generation

```python
import hashlib
import secrets

def generate_api_key(username: str) -> tuple[str, str]:
    """
    Generate a new API key for a user.

    Returns:
        (plain_key, key_hash) — plain key shown once, hash stored in DB.
    """
    # Generate 32-byte random key
    raw = secrets.token_bytes(32)

    # Format: macp_{prefix}_{random}
    prefix = secrets.token_hex(4)  # 8 chars
    key_body = secrets.token_urlsafe(32)
    plain_key = f"macp_{prefix}_{key_body}"

    # Hash for storage (never store plain key)
    key_hash = hashlib.sha256(plain_key.encode()).hexdigest()

    return plain_key, key_hash, prefix
```

### Key Format
```
macp_a1b2c3d4_dGhpcyBpcyBhIHRlc3Qga2V5...
     ^^^^^^^^  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
     prefix    random body (url-safe base64)
```

- Prefix: displayed in UI for key identification (e.g., "macp_a1b2...")
- Full key: shown only once at creation, never stored in plain text

---

## 4. Authentication Flow

```
Client                          MCP Server
  |                                 |
  |  X-API-Key: macp_xxxx_yyyy     |
  |------------------------------->|
  |                                 | 1. Extract key from header
  |                                 | 2. SHA-256 hash the key
  |                                 | 3. Lookup hash in users table
  |                                 | 4. Check is_active = true
  |                                 | 5. Check rate limit
  |                                 | 6. Update last_active
  |    200 OK / 401 Unauthorized   |
  |<-------------------------------|
```

### Header
```
X-API-Key: macp_a1b2c3d4_dGhpcyBpcyBhIHRlc3Qga2V5...
```

---

## 5. CLI Key Management

```bash
# Generate a new API key
python tools/macp_cli.py auth create --username alice
# Output: Your API key (save it, shown only once): macp_a1b2c3d4_...

# List users (shows prefix only)
python tools/macp_cli.py auth list
# Output: alice  macp_a1b2...  active  created: 2026-02-17

# Revoke a key
python tools/macp_cli.py auth revoke --username alice

# Rotate a key (revoke old, generate new)
python tools/macp_cli.py auth rotate --username alice
```

---

## 6. Security Considerations

- **Never store plain API keys** — only SHA-256 hashes
- **Rate limiting** per user (configurable, default 100 req/hour)
- **Key rotation** supported without downtime
- **Audit logging** — all auth events written to security log
- **No default keys** — must be explicitly generated
- **Local CLI mode** — bypasses auth (no key needed for local usage)

---

## 7. Migration Path

### Phase 3 (Initial)
- SQLite `users` table
- API key auth for MCP server endpoints
- Local CLI continues to work without auth

### Phase 4 (If Needed)
- PostgreSQL backend
- OAuth 2.0 for web UI
- Role-based access control (admin, researcher, viewer)
- Team/organization support
