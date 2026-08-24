"""Run pass 2 against the JSON output produced by pass 1."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from openai_client import read_text, request_json, write_json


# Replace this value with the pass 2 system prompt before running the script.
SYSTEM_PROMPT = """You are assisting in an academic cybersecurity research project.

Your task is to create a list of completely fictional synthetic persona for supervised machine learning.

A clear year or date observation can be inferred to be either a birth year or an important date to the persona.

The persona exists solely as a plausible research artefact for training a persona reasoning model.

You will receive a list of structured semantic evidence extracted from a password.

Treat the supplied evidence as reasonable constraints.

Do not contradict the evidence.

USE data LEARNED from human password creation behaviour/tendencies to make reasonable personas

Do not invent details that are unrelated to the evidence.

If information cannot reasonably be inferred, leave the field null.

If an inferred information requires a new field or category, Include the new field or category

Only INCLUDE attributes that are useful.

THERE IS No requirement to populate every field.

Where multiple possibilities exist, choose the most plausible while remaining internally consistent.

A Confidence of low or medium should be considered highly to fill in a field if there isn't any contradicting evidence....i.e random years or dates included in the inference/observations can be used to fill in birth years or e highlighted as a important year for the persona...... in some cases ethnicity + gender - some relevant year based on the persona's origin/ethnicity

The resulting persona should resemble a believable person rather than a stereotype except largely eluded to.

Avoid dramatic biographies.

Do NOT explain your choices.

Return ONLY valid JSON.

Use the following json schema as a starter. You can grow this json schema where you see necessary based on the data you have available to you.

{
    "persona": {
        "attributes": {
                "identity": {
                    "name": {
                    "value": "Daniel",
                    "confidence": "high"
                        }
                    },
                "interests": {
                    "teams": {
                    "value": ["Arsenal"],
                    "confidence": "high"
                        }
                    },
                "demographics": {
                    "birth_year": {
                    "value": 1999,
                    "confidence": "medium"
                        }
                    },
            },
        "password": "given password"
    }
}"""
DEFAULT_INPUT = Path(__file__).resolve().parents[1] / "pass_1/output"
DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parent / "output"
CHUNK_PATTERN = "original_chunk_*.json"


def input_files(input_path: Path) -> list[Path]:

    if input_path.is_file():

        return [input_path]

    if input_path.is_dir():

        return sorted(input_path.glob(CHUNK_PATTERN))

    raise FileNotFoundError(f"Input file or directory not found: {input_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--system-prompt", type=str, default=SYSTEM_PROMPT)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    if args.system_prompt.startswith("PASTE YOUR"):
        raise SystemExit("Edit SYSTEM_PROMPT in run_pass_2.py or pass --system-prompt.")

    files = input_files(args.input)

    if not files:

        raise SystemExit(f"No JSON files found in {args.input}")

    for input_file in files:

        output_file = args.output_dir / f"{input_file.stem}.json"

        if output_file.exists() and not args.overwrite:

            print(f"[+] Skipping {input_file.name}; output already exists")

            continue

        result = request_json(args.system_prompt, read_text(input_file))
        write_json(output_file, result)
        print(f"[+] Pass 2 output written to {output_file}")


if __name__ == "__main__":
    main()
