from __future__ import annotations

from typing import Any


VALID_CONFIDENCE = {"high", "medium", "low"}


def _get_confidence(item: dict[str, Any]) -> str:
    """Return a valid confidence value."""
    confidence = item.get("confidence", "low")

    if confidence not in VALID_CONFIDENCE:
        return "low"

    return confidence


def _add_unique(target: list[str], value: Any) -> None:
    """Add a non-empty value without creating duplicates."""
    if value is None:
        return

    value = str(value).strip()

    if value and value not in target:
        target.append(value)


def map_numbers(
    extracted: dict[str, Any],
    semantic_analysis: dict[str, Any],
) -> dict[str, list[str]]:
    """
    Build a proposed list of important password numbers.

    Numbers are collected from:
    1. Numbers identified directly by the password extractor.
    2. Numeric values identified as meaningful by Pass 1.

    The function does not attempt to determine the real-world meaning
    of a number. That interpretation is provided by Pass 1.
    """

    important_numbers: list[str] = []

    extracted_numbers = extracted.get("numbers", [])
    possible_dates = semantic_analysis.get("possible_dates", [])
    semantic_summary = semantic_analysis.get("semantic_summary", {})

    # ---------------------------------------------------------
    # 1. Numbers directly extracted from the password
    # ---------------------------------------------------------
    for number in extracted_numbers:
        _add_unique(important_numbers, number)

    # ---------------------------------------------------------
    # 2. Numbers identified by Pass 1 as meaningful dates/years
    # ---------------------------------------------------------
    for item in possible_dates:
        if not isinstance(item, dict):
            continue

        value = item.get("value")
        confidence = _get_confidence(item)

        # Only include values that Pass 1 considers at least plausible.
        if confidence in {"high", "medium", "low"}:
            _add_unique(important_numbers, value)

    # ---------------------------------------------------------
    # 3. Optional semantic numeric concepts
    # ---------------------------------------------------------
    primary_concepts = semantic_summary.get("primary_concepts", [])
    secondary_concepts = semantic_summary.get("secondary_concepts", [])

    for concept in primary_concepts + secondary_concepts:
        if isinstance(concept, (int, float)):
            _add_unique(important_numbers, concept)

        elif isinstance(concept, str) and any(char.isdigit() for char in concept):
            # Preserve concepts containing numeric information.
            _add_unique(important_numbers, concept)

    return {
        "important_numbers": important_numbers
    }
