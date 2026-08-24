from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from target_builder.candidate_builder import build_candidate
from target_builder.reviewer_export import (
    build_review_record,
    export_review_record,
    parse_review_status,
)


CHUNK_PATTERN = "original_chunk_*.json"


def load_json_array(
    path: str | Path,
    *,
    collection_key: str | None = None,
) -> list[dict[str, Any]]:
    """Load one JSON object or an array of objects as a list of records."""
    path = Path(path)

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if isinstance(data, dict):
        if collection_key in data:
            data = data[collection_key]
        else:
            data = [data]

    if not isinstance(data, list):
        raise ValueError(f"{path} must contain a JSON object or array.")

    if not all(isinstance(item, dict) for item in data):
        raise ValueError(f"{path} must contain only JSON objects.")

    return data


def load_pass1_records(path: str | Path) -> list[dict[str, Any]]:
    """Load a Pass 1 array or its chunked ``records`` wrapper."""
    return load_json_array(path, collection_key="records")


def load_pass2_records(path: str | Path) -> list[dict[str, Any]]:
    """Load a Pass 2 array or its chunked ``personas`` wrapper."""
    return load_json_array(path, collection_key="personas")


def chunk_file_pairs(
    pass1_dir: str | Path,
    pass2_dir: str | Path,
) -> list[tuple[Path, Path]]:
    """Return same-named Pass 1 and Pass 2 chunk files."""
    pass1_dir = Path(pass1_dir)
    pass2_dir = Path(pass2_dir)

    if not pass1_dir.is_dir():
        raise FileNotFoundError(f"Pass 1 directory not found: {pass1_dir}")

    if not pass2_dir.is_dir():
        raise FileNotFoundError(f"Pass 2 directory not found: {pass2_dir}")

    pass1_files = {
        path.name: path
        for path in pass1_dir.glob(CHUNK_PATTERN)
        if path.is_file()
    }
    pass2_files = {
        path.name: path
        for path in pass2_dir.glob(CHUNK_PATTERN)
        if path.is_file()
    }

    if not pass1_files:
        raise FileNotFoundError(
            f"No Pass 1 chunk files matching {CHUNK_PATTERN!r} found in {pass1_dir}"
        )

    if not pass2_files:
        raise FileNotFoundError(
            f"No Pass 2 chunk files matching {CHUNK_PATTERN!r} found in {pass2_dir}"
        )

    missing_pass2 = sorted(set(pass1_files) - set(pass2_files))
    missing_pass1 = sorted(set(pass2_files) - set(pass1_files))

    if missing_pass2 or missing_pass1:
        details: list[str] = []

        if missing_pass2:
            details.append(f"missing Pass 2: {', '.join(missing_pass2)}")

        if missing_pass1:
            details.append(f"missing Pass 1: {', '.join(missing_pass1)}")

        raise ValueError("Chunk files do not form matching pairs (" + "; ".join(details) + ").")

    return [
        (pass1_files[name], pass2_files[name])
        for name in sorted(pass1_files)
    ]


def _get_pass1_password(record: dict[str, Any], position: int) -> str:
    password = record.get("password")

    if not isinstance(password, str) or not password:
        raise ValueError(
            f"Pass 1 record {position} is missing a non-empty 'password' value."
        )

    return password


def _get_persona_and_password(
    record: dict[str, Any],
    position: int,
) -> tuple[dict[str, Any], str]:
    persona = record.get("persona")

    if not isinstance(persona, dict):
        raise ValueError(
            f"Pass 2 record {position} is missing a valid 'persona' object."
        )

    attributes = persona.get("attributes")

    if not isinstance(attributes, dict):
        raise ValueError(
            f"Pass 2 record {position} is missing a valid persona.attributes object."
        )

    password = persona.get("password")

    if not isinstance(password, str) or not password:
        password = attributes.get("password")

    if not isinstance(password, str) or not password:
        raise ValueError(
            f"Pass 2 record {position} is missing a non-empty persona password."
        )

    return persona, password


def _build_persona_index(
    pass2_records: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    """Index Pass 2 personas by their exact original password."""
    personas_by_password: dict[str, dict[str, Any]] = {}

    for position, record in enumerate(pass2_records, start=1):
        persona, password = _get_persona_and_password(record, position)

        if password in personas_by_password:
            raise ValueError(
                "Pass 2 contains more than one persona for the same password."
            )

        personas_by_password[password] = persona

    return personas_by_password


def _build_extracted_record(pass1_record: dict[str, Any], password: str) -> dict[str, Any]:
    """Convert a Pass 1 observation record to extractor-compatible data."""
    observations = pass1_record.get("observations")

    if not isinstance(observations, dict):
        raise ValueError("Pass 1 record is missing a valid 'observations' object.")

    return {
        **observations,
        "password": password,
    }


def _build_semantic_analysis(pass1_record: dict[str, Any]) -> dict[str, Any]:
    """Keep Pass 1 semantic fields while excluding extractor source fields."""
    return {
        field: value
        for field, value in pass1_record.items()
        if field not in {"password", "observations"}
    }


def _build_persona_id(password: str) -> str:
    """Create a stable, opaque ID without using the password as a filename."""
    digest = hashlib.sha256(password.encode("utf-8")).hexdigest()[:16]
    return f"persona-{digest}"


def build_review_records(
    pass1_records: list[dict[str, Any]],
    pass2_records: list[dict[str, Any]],
    status: str | None = None,
) -> list[dict[str, Any]]:
    """Join Pass 1 and Pass 2 records by password and build review records."""
    personas_by_password = _build_persona_index(pass2_records)
    seen_passwords: set[str] = set()
    review_records: list[dict[str, Any]] = []

    for position, pass1_record in enumerate(pass1_records, start=1):
        password = _get_pass1_password(pass1_record, position)

        if password in seen_passwords:
            raise ValueError(
                "Pass 1 contains more than one analysis record for the same password."
            )

        seen_passwords.add(password)
        persona = personas_by_password.get(password)

        if persona is None:
            raise ValueError(
                f"Pass 1 record {position} has no matching Pass 2 persona."
            )

        extracted = _build_extracted_record(pass1_record, password)
        semantic_analysis = _build_semantic_analysis(pass1_record)
        candidate = build_candidate(
            extracted=extracted,
            semantic_analysis=semantic_analysis,
        )

        review_records.append(
            build_review_record(
                persona_id=_build_persona_id(password),
                extracted=extracted,
                semantic_analysis=semantic_analysis,
                persona=persona,
                candidate=candidate,
                status=status,
            )
        )

    unused_personas = set(personas_by_password) - seen_passwords

    if unused_personas:
        raise ValueError(
            "Pass 2 contains persona records without a matching Pass 1 analysis."
        )

    return review_records


def build_review_records_from_chunk_dirs(
    pass1_dir: str | Path,
    pass2_dir: str | Path,
    status: str | None = None,
) -> list[dict[str, Any]]:
    """Build review records from every matching Pass 1/Pass 2 chunk pair."""
    review_records: list[dict[str, Any]] = []

    for pass1_path, pass2_path in chunk_file_pairs(pass1_dir, pass2_dir):
        review_records.extend(
            build_review_records(
                pass1_records=load_pass1_records(pass1_path),
                pass2_records=load_pass2_records(pass2_path),
                status=status,
            )
        )

    persona_ids = [record["persona_id"] for record in review_records]

    if len(persona_ids) != len(set(persona_ids)):
        raise ValueError("More than one chunk produced the same review record ID.")

    return review_records


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build review records by joining Pass 1 and Pass 2 datasets."
    )

    parser.add_argument(
        "--pass1",
        type=Path,
        help="Path to one Pass 1 semantic-analysis JSON array.",
    )

    parser.add_argument(
        "--pass2",
        type=Path,
        help="Path to one Pass 2 persona JSON array.",
    )

    parser.add_argument(
        "--pass1-dir",
        type=Path,
        help=f"Directory containing Pass 1 {CHUNK_PATTERN} files.",
    )

    parser.add_argument(
        "--pass2-dir",
        type=Path,
        help=f"Directory containing Pass 2 {CHUNK_PATTERN} files.",
    )

    parser.add_argument(
        "--output-dir",
        required=True,
        type=Path,
        help="Directory where one review JSON file per matched persona is written.",
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow replacement of existing generated review files.",
    )

    review_group = parser.add_mutually_exclusive_group()

    review_group.add_argument(
        "--approve",
        action="store_true",
        help="Mark generated records as approved.",
    )

    review_group.add_argument(
        "--reject",
        action="store_true",
        help="Mark generated records as rejected.",
    )

    args = parser.parse_args()
    status = parse_review_status(
        approve=args.approve,
        reject=args.reject,
    )

    has_file_inputs = args.pass1 is not None or args.pass2 is not None
    has_directory_inputs = args.pass1_dir is not None or args.pass2_dir is not None

    if has_file_inputs == has_directory_inputs:
        parser.error(
            "Provide either --pass1 and --pass2, or --pass1-dir and --pass2-dir."
        )

    if has_file_inputs:
        if args.pass1 is None or args.pass2 is None:
            parser.error("--pass1 and --pass2 must be provided together.")

        review_records = build_review_records(
            pass1_records=load_pass1_records(args.pass1),
            pass2_records=load_pass2_records(args.pass2),
            status=status,
        )
    else:
        if args.pass1_dir is None or args.pass2_dir is None:
            parser.error("--pass1-dir and --pass2-dir must be provided together.")

        review_records = build_review_records_from_chunk_dirs(
            pass1_dir=args.pass1_dir,
            pass2_dir=args.pass2_dir,
            status=status,
        )

    output_dir = args.output_dir
    output_paths = [
        output_dir / f"{record['persona_id']}.json"
        for record in review_records
    ]
    existing_paths = [path for path in output_paths if path.exists()]

    if existing_paths and not args.overwrite:
        raise FileExistsError(
            f"{len(existing_paths)} review file(s) already exist in {output_dir}. "
            "Use --overwrite to replace them."
        )

    for record, output_path in zip(review_records, output_paths, strict=True):
        export_review_record(
            record=record,
            output_path=output_path,
        )

    print(f"Review records written: {len(review_records)}")
    print(f"Output directory: {output_dir}")
    print(f"Review status: {status}")


if __name__ == "__main__":
    main()
