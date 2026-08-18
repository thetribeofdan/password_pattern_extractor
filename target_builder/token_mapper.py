from __future__ import annotations

from typing import Any


VALID_CONFIDENCE = {"high", "medium", "low"}


def _get_confidence(item: dict[str, Any]) -> str:
    """Return confidence, defaulting to low when unavailable."""
    confidence = item.get("confidence", "low")

    if confidence not in VALID_CONFIDENCE:
        return "low"

    return confidence


def _normalise(value: str) -> str:
    """Normalise a token for case-insensitive comparison."""
    return value.strip().casefold()


def _add_token(
    target: list[str],
    value: Any,
) -> None:
    """Add a token if it is non-empty and not already present."""
    if not isinstance(value, str):
        return

    value = value.strip()

    if not value:
        return

    normalised = _normalise(value)

    if all(_normalise(existing) != normalised for existing in target):
        target.append(value)


def _remove_token(
    target: list[str],
    value: str,
) -> None:
    """Remove tokens matching value case-insensitively."""
    normalised = _normalise(value)

    target[:] = [
        token
        for token in target
        if _normalise(token) != normalised
    ]


def map_tokens(
    extracted: dict[str, Any],
    semantic_analysis: dict[str, Any],
) -> dict[str, list[str]]:
    """
    Build proposed primary and secondary password tokens.

    Rules:
    - Raw extracted tokens are treated as candidate secondary tokens.
    - High-confidence semantic entities become primary tokens.
    - Medium/low-confidence semantic entities become secondary tokens.
    - If a semantic entity matches a raw token case-insensitively,
      the semantic entity takes precedence.
    - Reconstructions are handled using the same confidence rules.
    - Duplicate values are removed case-insensitively.
    """

    primary_tokens: list[str] = []
    secondary_tokens: list[str] = []

    extracted_tokens = extracted.get("tokens", [])
    entities = semantic_analysis.get("entities", [])
    reconstructions = semantic_analysis.get("reconstructions", [])

    # ---------------------------------------------------------
    # 1. Raw tokens
    # ---------------------------------------------------------
    for token in extracted_tokens:
        _add_token(secondary_tokens, token)

    # ---------------------------------------------------------
    # 2. Semantic entities
    # ---------------------------------------------------------
    for entity in entities:
        if not isinstance(entity, dict):
            continue

        value = entity.get("value")
        confidence = _get_confidence(entity)

        if not isinstance(value, str) or not value.strip():
            continue

        if confidence == "high":
            # High-confidence semantic interpretation takes
            # precedence over the raw extracted token.
            _remove_token(secondary_tokens, value)
            _add_token(primary_tokens, value)

        else:
            # Medium/low confidence interpretations remain
            # secondary candidates.
            _add_token(secondary_tokens, value)

    # ---------------------------------------------------------
    # 3. Reconstructed values
    # ---------------------------------------------------------
    for reconstruction in reconstructions:
        if not isinstance(reconstruction, dict):
            continue

        value = reconstruction.get("result")
        confidence = _get_confidence(reconstruction)

        if not isinstance(value, str) or not value.strip():
            continue

        if confidence == "high":
            _remove_token(secondary_tokens, value)
            _add_token(primary_tokens, value)
        else:
            _add_token(secondary_tokens, value)

    # ---------------------------------------------------------
    # 4. Remove anything from secondary that already exists
    #    in primary.
    # ---------------------------------------------------------
    secondary_tokens = [
        token
        for token in secondary_tokens
        if all(
            _normalise(token) != _normalise(primary)
            for primary in primary_tokens
        )
    ]

    return {
        "primary_tokens": primary_tokens,
        "secondary_tokens": secondary_tokens,
    }
