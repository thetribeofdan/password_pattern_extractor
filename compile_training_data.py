"""
Compile persona reviews into OpenAI fine-tuning format.

Reads persona JSON files from target_builder/reviews/ and converts them
into training examples suitable for fine-tuning a persona-aware password
reasoning model.

Output format: jsonl (one training example per line)
"""

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

    attrs = persona["persona"]["attributes"].copy()

    return attrs


def extract_search_space(persona: dict[str, Any]) -> dict[str, Any]:
    """
    Extract the target search space.
    
    Prefers 'reviewed' if available, falls back to 'proposed'.
    """
    if "target_search_space" not in persona:
        return {}
    
    search_space = persona["target_search_space"]
    
    # Prefer reviewed version, fall back to proposed
    if search_space.get("reviewed"):
        return search_space["reviewed"]
    
    if search_space.get("proposed"):
        return search_space["proposed"]
    
    return {}


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


def compile_training_data():
    """
    Compile all persona reviews into training data.
    
    Outputs a JSONL file with one training example per line.
    """
    
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Collect all persona files
    if not os.path.exists(REVIEWS_DIR):
        print(f"[!] Reviews directory not found: {REVIEWS_DIR}")
        return
    
    persona_files = sorted(
        Path(REVIEWS_DIR).glob("persona-*.json"),
        key=lambda p: p.name,
    )
    
    if not persona_files:
        print(f"[!] No persona files found in {REVIEWS_DIR}")
        return
    
    print(f"[+] Found {len(persona_files)} persona files")
    
    # Process each file
    training_examples = []
    skipped = 0
    
    for filepath in persona_files:
        persona = load_persona_file(str(filepath))
        
        if persona is None:
            skipped += 1
            continue
        
        message = create_training_message(persona)
        
        if message is None:
            print(f"[-] Skipped {filepath.name} (missing attributes or search space)")
            skipped += 1
            continue
        
        training_examples.append(message)
        print(f"[+] Processed {filepath.name}")
    
    # Write output
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for example in training_examples:
            f.write(json.dumps(example) + "\n")
    
    print(f"\n[+] Compiled {len(training_examples)} training examples")
    print(f"[+] Output: {OUTPUT_FILE}")
    print(f"[*] Skipped: {skipped}")


if __name__ == "__main__":
    compile_training_data()
