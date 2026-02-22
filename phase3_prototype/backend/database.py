"""
MACP Research Assistant — Database Layer (Phase 3C)
====================================================
SQLAlchemy ORM models and session management.
SQLite for local dev, PostgreSQL for production via DATABASE_URL.

Tables: users, papers, analyses, learning_sessions, citations, notes, projects, audit_log
"""

import json
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.orm import DeclarativeBase, Session, relationship, sessionmaker

from config import DATABASE_URL, MACP_DIR

# ---------------------------------------------------------------------------
# Engine & Session
# ---------------------------------------------------------------------------

# SQLite needs check_same_thread=False; PostgreSQL does not accept it
_connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, echo=False, connect_args=_connect_args)


class Base(DeclarativeBase):
    pass


SessionLocal = sessionmaker(bind=engine)


def get_db() -> Session:
    """Yield a database session (for FastAPI Depends)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables if they don't exist."""
    import os
    os.makedirs(MACP_DIR, exist_ok=True)
    Base.metadata.create_all(bind=engine)


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    github_id = Column(Integer, unique=True, nullable=False, index=True)
    github_login = Column(String(100), nullable=False)
    github_name = Column(String(200), default="")
    github_avatar_url = Column(String(500), default="")
    github_access_token = Column(Text, default="")  # Fernet-encrypted
    connected_repo = Column(String(300), default="")  # owner/repo
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_login = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    papers = relationship("Paper", back_populates="user")
    notes = relationship("Note", back_populates="user")
    projects = relationship("Project", back_populates="user")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "github_id": self.github_id,
            "github_login": self.github_login,
            "github_name": self.github_name or "",
            "github_avatar_url": self.github_avatar_url or "",
            "connected_repo": self.connected_repo or "",
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Paper(Base):
    __tablename__ = "papers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    arxiv_id = Column(String(50), unique=True, nullable=False, index=True)
    title = Column(Text, nullable=False)
    authors = Column(Text, default="[]")  # JSON array
    abstract = Column(Text, default="")
    url = Column(String(500), default="")
    source = Column(String(50), default="unknown")
    status = Column(String(20), default="discovered")
    added_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="papers")
    analyses = relationship("Analysis", back_populates="paper")
    sessions = relationship("LearningSession", back_populates="paper")
    citations = relationship("Citation", back_populates="paper")
    notes = relationship("Note", back_populates="paper")

    def to_dict(self) -> dict:
        return {
            "id": self.arxiv_id,
            "title": self.title,
            "authors": json.loads(self.authors) if self.authors else [],
            "abstract": self.abstract or "",
            "url": self.url or "",
            "status": self.status or "discovered",
            "source": self.source or "unknown",
            "added_at": self.added_at.isoformat() if self.added_at else None,
        }


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    paper_id = Column(Integer, ForeignKey("papers.id"), nullable=False)
    provider = Column(String(50), nullable=False)
    summary = Column(Text, default="")
    key_insights = Column(Text, default="[]")  # JSON array
    methodology = Column(Text, default="")
    research_gaps = Column(Text, default="[]")  # JSON array
    relevance_tags = Column(Text, default="[]")  # JSON array
    score = Column(Float, default=0)
    provenance = Column(Text, default="{}")  # JSON: model, timestamp, params
    analyzed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User")
    paper = relationship("Paper", back_populates="analyses")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "summary": self.summary or "",
            "key_insights": json.loads(self.key_insights) if self.key_insights else [],
            "methodology": self.methodology or "",
            "research_gaps": json.loads(self.research_gaps) if self.research_gaps else [],
            "relevance_tags": json.loads(self.relevance_tags) if self.relevance_tags else [],
            "strength_score": self.score or 0,
            "provenance": json.loads(self.provenance) if self.provenance else {},
            "_meta": json.loads(self.provenance) if self.provenance else {},
        }


class LearningSession(Base):
    __tablename__ = "learning_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    paper_id = Column(Integer, ForeignKey("papers.id"), nullable=False)
    insight = Column(Text, nullable=False)
    agent = Column(String(100), default="human")
    learned_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User")
    paper = relationship("Paper", back_populates="sessions")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "paper_id": self.paper.arxiv_id if self.paper else None,
            "insight": self.insight,
            "agent": self.agent,
            "learned_at": self.learned_at.isoformat() if self.learned_at else None,
        }


class Citation(Base):
    __tablename__ = "citations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    paper_id = Column(Integer, ForeignKey("papers.id"), nullable=False)
    project = Column(String(200), nullable=False)
    context = Column(Text, default="")
    cited_by = Column(String(100), default="human")
    cited_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User")
    paper = relationship("Paper", back_populates="citations")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "paper_id": self.paper.arxiv_id if self.paper else None,
            "project": self.project,
            "context": self.context,
            "cited_by": self.cited_by,
            "cited_at": self.cited_at.isoformat() if self.cited_at else None,
        }


class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    paper_id = Column(Integer, ForeignKey("papers.id"), nullable=True)
    content = Column(Text, nullable=False)
    tags = Column(Text, default="[]")  # JSON array
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="notes")
    paper = relationship("Paper", back_populates="notes")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "paper_id": self.paper.arxiv_id if self.paper else None,
            "content": self.content,
            "tags": json.loads(self.tags) if self.tags else [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text, default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="projects")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description or "",
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    level = Column(String(20), default="INFO")
    event = Column(String(100), nullable=False)
    message = Column(Text, default="")
    source_ip = Column(String(45), default="")
    details = Column(Text, default="{}")  # JSON

    user = relationship("User")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "level": self.level,
            "event": self.event,
            "message": self.message,
            "source_ip": self.source_ip,
            "details": json.loads(self.details) if self.details else {},
        }


# ---------------------------------------------------------------------------
# Helper: log audit event
# ---------------------------------------------------------------------------

def log_audit(
    event: str,
    message: str = "",
    level: str = "INFO",
    source_ip: str = "",
    details: Optional[dict] = None,
    user_id: Optional[int] = None,
    db: Optional[Session] = None,
):
    """Write a structured audit log entry to the database and stdout (JSON for GCP Cloud Logging)."""
    from datetime import datetime, timezone

    # Structured JSON log to stdout for GCP Cloud Logging compatibility
    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "severity": level,
        "event": event,
        "message": message,
        "source_ip": source_ip or None,
        "user_id": user_id,
        "service": "macp-research-assistant",
        "version": "phase3c",
    }
    log_entry = {k: v for k, v in log_entry.items() if v is not None}
    print(json.dumps(log_entry), flush=True)

    # Also persist to database
    close_after = False
    if db is None:
        db = SessionLocal()
        close_after = True
    try:
        entry = AuditLog(
            event=event,
            message=message,
            level=level,
            source_ip=source_ip,
            user_id=user_id,
            details=json.dumps(details or {}),
        )
        db.add(entry)
        db.commit()
    finally:
        if close_after:
            db.close()


# ---------------------------------------------------------------------------
# Helper: upsert paper
# ---------------------------------------------------------------------------

def upsert_paper(db: Session, paper_dict: dict, user_id: Optional[int] = None) -> Paper:
    """Insert or update a paper from a dict (matching the old JSON format)."""
    arxiv_id = paper_dict.get("id", "")
    existing = db.query(Paper).filter(Paper.arxiv_id == arxiv_id).first()
    if existing:
        existing.title = paper_dict.get("title", existing.title)
        existing.abstract = paper_dict.get("abstract", existing.abstract)
        existing.url = paper_dict.get("url", existing.url)
        if paper_dict.get("authors"):
            existing.authors = json.dumps(paper_dict["authors"])
        if paper_dict.get("status"):
            existing.status = paper_dict["status"]
        if user_id and not existing.user_id:
            existing.user_id = user_id
        db.commit()
        return existing

    paper = Paper(
        arxiv_id=arxiv_id,
        user_id=user_id,
        title=paper_dict.get("title", ""),
        authors=json.dumps(paper_dict.get("authors", [])),
        abstract=paper_dict.get("abstract", ""),
        url=paper_dict.get("url", ""),
        source=paper_dict.get("discovered_by", paper_dict.get("source", "unknown")),
        status=paper_dict.get("status", "discovered"),
    )
    db.add(paper)
    db.commit()
    db.refresh(paper)
    return paper
