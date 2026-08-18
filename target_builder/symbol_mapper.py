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


def map_symbols(
    extracted: dict[str, Any],
    semantic_analysis: dict[str, Any],
) -> dict[str, list[str]]:
    """
    Build a proposed list of preferred password symbols.

    Symbols identified directly by the password extractor are preserved.
    Semantic analysis may identify additional symbol-related information,
    particularly when a symbol participates in a reconstruction such as
    '@' -> 'a'.

    The mapper does not assume that a symbol is universally preferred.
    It only records symbols supported by the observed password evidence.
    """

    preferred_symbols: list[str] = []

    extracted_symbols = extracted.get("symbols", [])
    reconstructions = semantic_analysis.get("reconstructions", [])

    # ---------------------------------------------------------
    # 1. Preserve symbols directly observed in the password
    # ---------------------------------------------------------
    for symbol in extracted_symbols:
        _add_unique(preferred_symbols, symbol)

    # ---------------------------------------------------------
    # 2. Check semantic reconstructions for observed symbols
    #
    # Example:
    #   components: ["rib", "@", "k"]
    #   transformations: ["@ -> a"]
    #
    # We want to preserve "@" as an observed symbol.
    # ---------------------------------------------------------
    for reconstruction in reconstructions:
        if not isinstance(reconstruction, dict):
            continue

        components = reconstruction.get("components", [])

        if isinstance(components, list):
            for component in components:
                if not isinstance(component, str):
                    continue

                # If the component is not alphanumeric, treat it
                # as a potential symbol.
                if component and not component.isalnum():
                    _add_unique(preferred_symbols, component)

        # -----------------------------------------------------
        # Also inspect explicitly recorded transformations.
        # -----------------------------------------------------
        transformations = reconstruction.get("transformations", [])

        if not isinstance(transformations, list):
            continue

        for transformation in transformations:
            if not isinstance(transformation, str):
                continue

            # We deliberately do not attempt to parse arbitrary
            # transformation strings here. The extractor's symbols
            # remain the authoritative source.
            for symbol in extracted_symbols:
                if symbol in transformation:
                    _add_unique(preferred_symbols, symbol)

    return {
        "preferred_symbols": preferred_symbols
    }
