from __future__ import annotations

from typing import Any


def _add_unique(target: list[str], value: Any) -> None:
    """Add a non-empty pattern without creating duplicates."""
    if not isinstance(value, str):
        return

    value = value.strip()

    if value and value not in target:
        target.append(value)


def map_patterns(
    extracted: dict[str, Any],
) -> dict[str, list[str]]:
    """
    Build the proposed password construction patterns.

    The pattern extractor is the authoritative source for this field.
    No new patterns are inferred here.
    """

    likely_patterns: list[str] = []

    pattern = extracted.get("pattern")

    if pattern:
        _add_unique(likely_patterns, pattern)

    return {
        "likely_patterns": likely_patterns
    }
