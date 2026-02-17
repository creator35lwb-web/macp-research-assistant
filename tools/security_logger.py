#!/usr/bin/env python3
"""
MACP Research Assistant - Security Logger
==========================================
Structured JSON logging for security-relevant events.
Replaces ad-hoc stderr printing with a formal audit trail.

Events logged:
- Schema validation failures
- API call errors
- Input validation failures
- Dual-use risk warnings
- Authentication events (future)
- Data purge operations

Author: RNA (Claude Code)
Date: February 17, 2026
"""

import json
import logging
import os
from datetime import datetime


# ---------------------------------------------------------------------------
# JSON Formatter
# ---------------------------------------------------------------------------

class JSONFormatter(logging.Formatter):
    """Format log records as JSON lines for structured parsing."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "event": getattr(record, "event", record.getMessage()),
            "module": record.module,
        }
        # Merge extra fields from the record
        if isinstance(record.msg, dict):
            log_entry.update(record.msg)
        elif hasattr(record, "details") and record.details:
            log_entry["details"] = record.details
        return json.dumps(log_entry, default=str)


# ---------------------------------------------------------------------------
# Logger Setup
# ---------------------------------------------------------------------------

MACP_DIR = ".macp"
SECURITY_LOG_FILE = os.path.join(MACP_DIR, "security.log")

_logger = None


def get_security_logger() -> logging.Logger:
    """Get or create the MACP_SECURITY logger with JSON file handler."""
    global _logger
    if _logger is not None:
        return _logger

    _logger = logging.getLogger("MACP_SECURITY")
    _logger.setLevel(logging.DEBUG)

    # Prevent duplicate handlers on re-import
    if not _logger.handlers:
        os.makedirs(MACP_DIR, exist_ok=True)
        file_handler = logging.FileHandler(SECURITY_LOG_FILE, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(JSONFormatter())
        _logger.addHandler(file_handler)

    return _logger


# ---------------------------------------------------------------------------
# Convenience Functions
# ---------------------------------------------------------------------------

def log_security_event(event: str, level: str = "INFO", **kwargs):
    """
    Log a security event with structured data.

    Args:
        event: Event name (e.g., "schema_validation_failed").
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        **kwargs: Additional structured data fields.
    """
    logger = get_security_logger()
    log_data = {"event": event, **kwargs}
    log_func = getattr(logger, level.lower(), logger.info)
    record = logger.makeRecord(
        name=logger.name,
        level=getattr(logging, level.upper(), logging.INFO),
        fn="",
        lno=0,
        msg=log_data,
        args=(),
        exc_info=None,
    )
    record.event = event
    logger.handle(record)


def log_validation_failure(schema_name: str, error_message: str, **kwargs):
    """Log a schema validation failure."""
    log_security_event(
        "schema_validation_failed",
        level="WARNING",
        schema=schema_name,
        error=error_message,
        **kwargs,
    )


def log_api_error(provider: str, error_message: str, **kwargs):
    """Log an external API call error."""
    log_security_event(
        "api_call_failed",
        level="ERROR",
        provider=provider,
        error=error_message,
        **kwargs,
    )


def log_input_validation_failure(field: str, error_message: str, **kwargs):
    """Log an input validation failure."""
    log_security_event(
        "input_validation_failed",
        level="WARNING",
        field=field,
        error=error_message,
        **kwargs,
    )


def log_dual_use_warning(paper_id: str, matched_keywords: list, **kwargs):
    """Log a dual-use risk warning."""
    log_security_event(
        "dual_use_warning",
        level="WARNING",
        paper_id=paper_id,
        matched_keywords=matched_keywords,
        **kwargs,
    )


def log_data_purge(dry_run: bool, files_affected: list, **kwargs):
    """Log a data purge operation."""
    log_security_event(
        "data_purge",
        level="CRITICAL" if not dry_run else "INFO",
        dry_run=dry_run,
        files_affected=files_affected,
        **kwargs,
    )
