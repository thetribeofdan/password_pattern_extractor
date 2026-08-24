"""
Compile persona reviews into OpenAI fine-tuning format.

Reads persona JSON files from target_builder/reviews/ and converts them
into training examples suitable for fine-tuning a persona-aware password
reasoning model.

Output format: jsonl (one training example per line)
"""

import argparse
from copy import deepcopy
import json
import os
from pathlib import Path
from typing import Any


SYSTEM_PROMPT = """You are a persona-aware password reasoning model.

Given a synthetic persona, identify the concepts and construction patterns that are plausibly likely to influence that person's passwords.

Do not generate passwords.

Return only a JSON search-space specification containing:
- primary_tokens
- secondary_tokens
- important_numbers
- preferred_symbols
- likely_patterns

Only include attributes that are relevant to the supplied persona."""


REVIEWS_DIR = "target_builder/reviews"
OUTPUT_DIR = "training_dataset/fine-tune"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "persona_training_data.jsonl")


def load_persona_file(filepath: str) -> dict[str, Any] | None:
    """Load and parse a persona JSON file."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"[!] Error loading {filepath}: {e}")
        return None


def extract_persona_attributes(persona: dict[str, Any]) -> dict[str, Any]:
    """Extract persona attributes (excluding password field)."""
    if "persona" not in persona or "attributes" not in persona["persona"]:
        return {}

    # attrs = persona["persona"]["attributes"].copy()
    # attrs.pop("password", None)

    return persona


def extract_search_space(persona: dict[str, Any]) -> dict[str, Any]:
    """
    Extract an approved reviewed target search space.
    """
    if persona.get("review", {}).get("status") != "approved":
        return {}

    if "target_search_space" not in persona:
        return {}

    search_space = persona["target_search_space"]

    if search_space.get("reviewed"):
        return search_space["reviewed"]

    return {}


def prepare_review_for_training(
    persona: dict[str, Any],
    *,
    auto_approve: bool,
) -> tuple[bool, bool]:
    """
    Return whether a review can be compiled and whether it was updated.

    With auto-approval enabled, a proposed search space is copied to
    ``reviewed`` and marked approved. Explicitly rejected records remain
    rejected and are never changed.
    """
    review = persona.get("review")
    search_space = persona.get("target_search_space")

    if not isinstance(review, dict) or not isinstance(search_space, dict):
        return False, False

    if review.get("status") == "rejected":
        return False, False

    reviewed = search_space.get("reviewed")

    if review.get("status") == "approved" and isinstance(reviewed, dict):
        return True, False

    if not auto_approve:
        return False, False

    proposed = search_space.get("proposed")

    if not isinstance(proposed, dict):
        return False, False

    search_space["reviewed"] = deepcopy(proposed)
    review["status"] = "approved"
    if not review.get("notes"):
        review["notes"] = "Auto-approved during training-data compilation."

    return True, True


def save_persona_file(filepath: str | Path, persona: dict[str, Any]) -> None:
    """Persist an updated review record."""
    with Path(filepath).open("w", encoding="utf-8") as file:
        json.dump(persona, file, indent=2, ensure_ascii=False)


def create_training_message(persona: dict[str, Any]) -> dict[str, Any]:
    """Create a training message from a persona file."""
    attributes = extract_persona_attributes(persona)
    search_space = extract_search_space(persona)

    # Skip if we don't have both
    if not attributes or not search_space:
        return None

    return {
        "messages": [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": json.dumps({"attributes": attributes}),
            },
            {
                "role": "assistant",
                "content": json.dumps(search_space),
            },
        ]
    }


def compile_training_data(
    *,
    reviews_dir: str | Path = REVIEWS_DIR,
    output_file: str | Path = OUTPUT_FILE,
    auto_approve: bool = True,
) -> None:
    """
    Compile all persona reviews into training data.
    
    Outputs a JSONL file with one training example per line.
    """
    
    reviews_dir = Path(reviews_dir)
    output_file = Path(output_file)

    # Create output directory
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Collect all persona files
    if not reviews_dir.exists():
        print(f"[!] Reviews directory not found: {reviews_dir}")
        return
    
    persona_files = sorted(
        reviews_dir.glob("persona-*.json"),
        key=lambda p: p.name,
    )
    
    if not persona_files:
        print(f"[!] No persona files found in {reviews_dir}")
        return
    
    print(f"[+] Found {len(persona_files)} persona files")
    
    # Process each file
    training_examples = []
    skipped = 0
    auto_approved = 0
    
    for filepath in persona_files:
        persona = load_persona_file(str(filepath))
        
        if persona is None:
            skipped += 1
            continue

        can_compile, was_auto_approved = prepare_review_for_training(
            persona,
            auto_approve=auto_approve,
        )

        if not can_compile:
            print(f"[-] Skipped {filepath.name} (not approved for training)")
            skipped += 1
            continue

        if was_auto_approved:
            save_persona_file(filepath, persona)
            auto_approved += 1

        message = create_training_message(persona)
        
        if message is None:
            print(f"[-] Skipped {filepath.name} (missing attributes or search space)")
            skipped += 1
            continue
        
        training_examples.append(message)
        print(f"[+] Processed {filepath.name}")
    
    # Write output
    with output_file.open("w", encoding="utf-8") as f:
        for example in training_examples:
            f.write(json.dumps(example) + "\n")
    
    print(f"\n[+] Compiled {len(training_examples)} training examples")
    print(f"[+] Output: {output_file}")
    print(f"[*] Skipped: {skipped}")
    print(f"[*] Auto-approved: {auto_approved}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--reviews-dir",
        type=Path,
        default=Path(REVIEWS_DIR),
        help="Directory containing generated persona review JSON files.",
    )
    parser.add_argument(
        "--output-file",
        type=Path,
        default=Path(OUTPUT_FILE),
        help="Path for the compiled fine-tuning JSONL file.",
    )
    parser.add_argument(
        "--no-auto-approve",
        action="store_true",
        help="Compile only review records that are already approved and reviewed.",
    )
    args = parser.parse_args()

    compile_training_data(
        reviews_dir=args.reviews_dir,
        output_file=args.output_file,
        auto_approve=not args.no_auto_approve,
    )
