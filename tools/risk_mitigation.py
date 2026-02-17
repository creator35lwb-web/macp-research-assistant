#!/usr/bin/env python3
"""
MACP Research Assistant - Dual-Use Risk Mitigation
====================================================
Checks paper titles and abstracts for potentially sensitive
dual-use research topics. Logs warnings via the security logger
and prompts the user for explicit confirmation before proceeding.

Author: RNA (Claude Code)
Date: February 17, 2026
"""

import re
from typing import List

from security_logger import log_dual_use_warning

# ---------------------------------------------------------------------------
# Sensitive Keyword Registry
# ---------------------------------------------------------------------------

SENSITIVE_KEYWORDS: List[str] = [
    # Weapons
    "weapon",
    "bioweapon",
    "chemical weapon",
    "nuclear weapon",
    "autonomous weapon",
    "lethal autonomous",
    # Surveillance
    "surveillance",
    "mass surveillance",
    "facial recognition",
    "social credit",
    "tracking individuals",
    # Cyber
    "cyberattack",
    "cyber attack",
    "malware",
    "exploit development",
    "zero-day",
    "ransomware",
    # Biological
    "gain of function",
    "pathogen enhancement",
    "synthetic biology risk",
    "bioterrorism",
    # Disinformation
    "deepfake",
    "disinformation campaign",
    "propaganda generation",
    # Other dual-use
    "military targeting",
    "drone strike",
    "interrogation",
]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def check_for_sensitive_topics(text: str) -> List[str]:
    """
    Scan text for potentially sensitive dual-use keywords.

    Args:
        text: The text to check (title + abstract).

    Returns:
        List of matched keywords found in the text.
    """
    if not text:
        return []

    text_lower = text.lower()
    matched = []
    for keyword in SENSITIVE_KEYWORDS:
        # Use word-boundary matching to reduce false positives
        pattern = r"\b" + re.escape(keyword) + r"\b"
        if re.search(pattern, text_lower):
            matched.append(keyword)

    return matched


def warn_and_confirm(paper_id: str, matched_keywords: List[str]) -> bool:
    """
    Print a dual-use warning and ask for explicit confirmation.

    Args:
        paper_id: The paper's ID for logging.
        matched_keywords: List of sensitive keywords found.

    Returns:
        True if the user confirms they want to proceed, False otherwise.
    """
    # Log to security audit trail
    log_dual_use_warning(paper_id, matched_keywords)

    print()
    print("!" * 60)
    print("  [DUAL-USE WARNING]")
    print("  This paper contains potentially sensitive research topics.")
    print(f"  Matched keywords: {', '.join(matched_keywords)}")
    print()
    print("  MACP flags this for awareness, not censorship.")
    print("  You may proceed if this is legitimate research.")
    print("!" * 60)
    print()

    try:
        confirm = input("  Type 'proceed' to continue analysis: ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        confirm = ""

    return confirm == "proceed"
