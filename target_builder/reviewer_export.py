from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def build_review_record(
    persona_id: str,
    extracted: dict[str, Any],
    semantic_analysis: dict[str, Any],
    persona: dict[str, Any],
    candidate: dict[str, Any],
    status: str | None = None,
) -> dict[str, Any]:
    """
    Build a review record containing the source evidence,
    generated persona, proposed search space, and review state.

    status:
        None       -> not reviewed
        "approved" -> approved by reviewer
        "rejected" -> rejected by reviewer
    """

    if status not in {None, "approved", "rejected"}:
        raise ValueError(f"Invalid review status: {status}")

    return {
        "persona_id": persona_id,

        "source": {
            "password": extracted.get("password"),
            "extracted": extracted,
            "semantic_analysis": semantic_analysis,
        },

        "persona": persona,

        "target_search_space": {
            "proposed": candidate,
            "reviewed": None
        },

        "review": {
            "status": status,
            "notes": ""
        }
    }


def export_review_record(
    record: dict[str, Any],
    output_path: str | Path,
) -> None:
    """
    Write a review record as formatted JSON.
    """

    output_path = Path(output_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(
            record,
            file,
            indent=2,
            ensure_ascii=False,
        )


def parse_review_status(
    *,
    approve: bool = False,
    reject: bool = False,
) -> str | None:
    """Return a review status from already-parsed CLI flag values."""
    if approve and reject:
        raise ValueError("A record cannot be both approved and rejected.")

    if approve:
        return "approved"

    if reject:
        return "rejected"

    return None
