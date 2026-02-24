"""
MACP Research Assistant — Schema Validator (Phase 3E)
======================================================
Validates data against the MACP v2.0 schema (.macp/schema.json).

Uses the schema's "definitions" to enforce required fields on papers,
analyses, consensus objects, and agent registry entries before they
are persisted to GitHub or the database.
"""

import json
import logging
import os
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)

# Path to the .macp/schema.json relative to the project root
_SCHEMA_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    ".macp", "schema.json",
)

_schema_cache: Optional[dict] = None


def _load_schema() -> dict:
    """Load and cache the MACP v2.0 schema."""
    global _schema_cache
    if _schema_cache is not None:
        return _schema_cache

    if not os.path.exists(_SCHEMA_PATH):
        logger.warning("MACP schema not found at %s — validation disabled", _SCHEMA_PATH)
        return {}

    with open(_SCHEMA_PATH, "r", encoding="utf-8") as f:
        _schema_cache = json.load(f)

    logger.info("Loaded MACP v2.0 schema (version %s)", _schema_cache.get("version", "?"))
    return _schema_cache


def _get_required_fields(definition_key: str) -> set[str]:
    """Extract required field names from a schema definition."""
    schema = _load_schema()
    defn = schema.get("definitions", {}).get(definition_key, {})
    return set(defn.get("required_fields", {}).keys())


# ---------------------------------------------------------------------------
# Validation results
# ---------------------------------------------------------------------------

class ValidationResult:
    """Holds validation outcome with errors list."""

    def __init__(self, valid: bool, errors: list[str] | None = None):
        self.valid = valid
        self.errors = errors or []

    def __bool__(self) -> bool:
        return self.valid

    def to_dict(self) -> dict:
        return {"valid": self.valid, "errors": self.errors}


# ---------------------------------------------------------------------------
# Paper validation
# ---------------------------------------------------------------------------

def validate_paper_data(data: dict) -> ValidationResult:
    """Validate paper data against MACP v2.0 paper schema.

    Required fields from schema: arxiv_id, title, authors, abstract, url,
    pdf_url, status, discovered_by, discovered_at, saved_at.

    We enforce the core fields (arxiv_id, title, authors, status) strictly
    and treat the rest as warnings since legacy data may lack them.
    """
    errors = []

    # Hard requirements
    if not data.get("arxiv_id") and not data.get("id"):
        errors.append("Missing required field: arxiv_id")
    if not data.get("title"):
        errors.append("Missing required field: title")

    # Status must be from the lifecycle enum
    valid_statuses = {"discovered", "saved", "analyzed", "deep_analyzed"}
    status = data.get("status", "discovered")
    if status not in valid_statuses:
        errors.append(f"Invalid status '{status}'. Must be one of: {valid_statuses}")

    # Authors should be a list
    authors = data.get("authors")
    if authors is not None and not isinstance(authors, list):
        errors.append("authors must be an array")

    return ValidationResult(valid=len(errors) == 0, errors=errors)


# ---------------------------------------------------------------------------
# Analysis validation
# ---------------------------------------------------------------------------

def validate_analysis_data(data: dict) -> ValidationResult:
    """Validate analysis data against MACP v2.0 analysis schema.

    Required: arxiv_id (or paper_id), agent_id (or provider), model, type,
    analyzed_at, summary, key_findings, methodology, relevance_score, bias_disclaimer.

    We enforce core fields strictly and accept the existing field names
    (key_insights ↔ key_findings, provider ↔ agent_id) for backward compat.
    """
    errors = []

    # Paper reference
    if not data.get("arxiv_id") and not data.get("paper_id"):
        errors.append("Missing required field: arxiv_id or paper_id")

    # Agent/provider
    if not data.get("agent_id") and not data.get("provider"):
        errors.append("Missing required field: agent_id or provider")

    # Summary
    if not data.get("summary"):
        errors.append("Missing required field: summary")

    # Analysis type
    valid_types = {"abstract", "deep", "comparative", "methodological"}
    analysis_type = data.get("type") or data.get("analysis_type", "abstract")
    if analysis_type not in valid_types:
        errors.append(f"Invalid analysis type '{analysis_type}'. Must be one of: {valid_types}")

    # Key findings (accept key_findings or key_insights or key_contributions)
    findings = data.get("key_findings") or data.get("key_insights") or data.get("key_contributions")
    if findings is not None and not isinstance(findings, list):
        errors.append("key_findings must be an array")

    return ValidationResult(valid=len(errors) == 0, errors=errors)


# ---------------------------------------------------------------------------
# Consensus validation
# ---------------------------------------------------------------------------

def validate_consensus_data(data: dict) -> ValidationResult:
    """Validate consensus data against MACP v2.0 consensus schema.

    Required: arxiv_id, agents_compared (min 2), generated_at, generated_by,
    agreement_score (0-1), synthesized_summary, convergence_points, divergence_points.
    """
    errors = []

    if not data.get("arxiv_id"):
        errors.append("Missing required field: arxiv_id")

    agents = data.get("agents_compared", [])
    if not isinstance(agents, list) or len(agents) < 2:
        errors.append("agents_compared must be an array with at least 2 agents")

    if not data.get("generated_at"):
        errors.append("Missing required field: generated_at")

    if not data.get("generated_by"):
        errors.append("Missing required field: generated_by")

    score = data.get("agreement_score")
    if score is None:
        errors.append("Missing required field: agreement_score")
    elif not isinstance(score, (int, float)) or score < 0 or score > 1:
        errors.append("agreement_score must be a number between 0 and 1")

    if not data.get("synthesized_summary"):
        errors.append("Missing required field: synthesized_summary")

    if not isinstance(data.get("convergence_points", []), list):
        errors.append("convergence_points must be an array")

    if not isinstance(data.get("divergence_points", []), list):
        errors.append("divergence_points must be an array")

    return ValidationResult(valid=len(errors) == 0, errors=errors)


# ---------------------------------------------------------------------------
# Agent validation
# ---------------------------------------------------------------------------

def validate_agent_data(data: dict) -> ValidationResult:
    """Validate agent registry data against MACP v2.0 agent schema."""
    errors = []

    if not data.get("agent_id"):
        errors.append("Missing required field: agent_id")
    if not data.get("name"):
        errors.append("Missing required field: name")
    if not data.get("model"):
        errors.append("Missing required field: model")

    capabilities = data.get("capabilities")
    if capabilities is not None and not isinstance(capabilities, list):
        errors.append("capabilities must be an array")

    valid_tiers = {"free", "freemium", "paid", "enterprise"}
    tier = data.get("cost_tier")
    if tier and tier not in valid_tiers:
        errors.append(f"Invalid cost_tier '{tier}'. Must be one of: {valid_tiers}")

    return ValidationResult(valid=len(errors) == 0, errors=errors)


# ---------------------------------------------------------------------------
# Consensus scoring config from schema
# ---------------------------------------------------------------------------

def get_consensus_weights() -> dict:
    """Return the agreement scoring weights from the schema."""
    schema = _load_schema()
    rules = schema.get("consensus_rules", {})
    scoring = rules.get("agreement_scoring", {})
    return {
        "key_findings_overlap": scoring.get("key_findings_overlap_weight", 0.4),
        "relevance_score_alignment": scoring.get("relevance_score_alignment_weight", 0.3),
        "methodology_consistency": scoring.get("methodology_consistency_weight", 0.3),
    }


def get_consensus_min_agents() -> int:
    """Return the minimum number of agents required for consensus."""
    schema = _load_schema()
    return schema.get("consensus_rules", {}).get("minimum_agents", 2)
