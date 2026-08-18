from __future__ import annotations

from typing import Any

from .token_mapper import map_tokens
from .number_mapper import map_numbers
from .symbol_mapper import map_symbols
from .pattern_mapper import map_patterns


def build_candidate(
    extracted: dict[str, Any],
    semantic_analysis: dict[str, Any],
) -> dict[str, Any]:
    """
    Build a proposed target search space from:

    - password extractor output
    - Pass 1 semantic analysis

    Individual mapping decisions are delegated to the
    specialised mapper modules.
    """

    token_result = map_tokens(
        extracted=extracted,
        semantic_analysis=semantic_analysis,
    )

    number_result = map_numbers(
        extracted=extracted,
        semantic_analysis=semantic_analysis,
    )

    symbol_result = map_symbols(
        extracted=extracted,
        semantic_analysis=semantic_analysis,
    )

    pattern_result = map_patterns(
        extracted=extracted,
    )

    return {
        **token_result,
        **number_result,
        **symbol_result,
        **pattern_result,
    }
