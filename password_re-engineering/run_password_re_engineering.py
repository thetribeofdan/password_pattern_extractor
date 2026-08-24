"""Command center for the password re-engineering passes."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PASS_1 = ROOT / "pass_1/run_pass_1.py"
PASS_2 = ROOT / "pass_2/run_pass_2.py"
TARGET_BUILDER_MODULE = "target_builder.generate_review"
COMPILE_TRAINING_DATA = ROOT.parent / "compile_training_data.py"
DEFAULT_INPUT = ROOT.parent / "output/structured"
DEFAULT_PASS_1_OUTPUT_DIR = ROOT / "pass_1/output"
DEFAULT_PASS_2_OUTPUT_DIR = ROOT / "pass_2/output"
DEFAULT_REVIEWS_DIR = ROOT.parent / "target_builder/reviews"


def run_stage(script: Path, arguments: list[str]) -> None:
    command = [sys.executable, str(script), *arguments]
    print(f"\n{'=' * 60}\nRunning: {' '.join(command)}\n{'=' * 60}")
    try:
        subprocess.run(command, check=True, cwd=ROOT.parent)
    except subprocess.CalledProcessError:
        raise SystemExit(f"[!] Password re-engineering stopped at {script}") from None


def run_module(module: str, arguments: list[str]) -> None:
    command = [sys.executable, "-m", module, *arguments]
    print(f"\n{'=' * 60}\nRunning: {' '.join(command)}\n{'=' * 60}")
    try:
        subprocess.run(command, check=True, cwd=ROOT.parent)
    except subprocess.CalledProcessError:
        raise SystemExit(f"[!] Password re-engineering stopped at {module}") from None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--pass-1-output-dir", type=Path, default=DEFAULT_PASS_1_OUTPUT_DIR)
    parser.add_argument("--pass-2-output-dir", type=Path, default=DEFAULT_PASS_2_OUTPUT_DIR)
    parser.add_argument("--reviews-dir", type=Path, default=DEFAULT_REVIEWS_DIR)
    parser.add_argument("--pass-1-prompt", type=str)
    parser.add_argument("--pass-2-prompt", type=str)
    parser.add_argument("--skip-pass-1", action="store_true")
    parser.add_argument("--skip-review-build", action="store_true")
    parser.add_argument("--skip-training-compile", action="store_true")
    parser.add_argument("--no-auto-approve", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    if not args.skip_pass_1:
        pass_1_arguments = [
            "--input", str(args.input),
            "--output-dir", str(args.pass_1_output_dir),
        ]
        if args.pass_1_prompt:
            pass_1_arguments.extend(["--system-prompt", args.pass_1_prompt])
        if args.overwrite:
            pass_1_arguments.append("--overwrite")
        run_stage(PASS_1, pass_1_arguments)

    pass_2_arguments = [
        "--input", str(args.pass_1_output_dir),
        "--output-dir", str(args.pass_2_output_dir),
    ]
    if args.pass_2_prompt:
        pass_2_arguments.extend(["--system-prompt", args.pass_2_prompt])
    if args.overwrite:
        pass_2_arguments.append("--overwrite")
    run_stage(PASS_2, pass_2_arguments)

    if not args.skip_review_build:
        review_arguments = [
            "--pass1-dir", str(args.pass_1_output_dir),
            "--pass2-dir", str(args.pass_2_output_dir),
            "--output-dir", str(args.reviews_dir),
        ]
        if args.overwrite:
            review_arguments.append("--overwrite")
        run_module(TARGET_BUILDER_MODULE, review_arguments)

    if not args.skip_training_compile:
        compile_arguments = ["--reviews-dir", str(args.reviews_dir)]
        if args.no_auto_approve:
            compile_arguments.append("--no-auto-approve")
        run_stage(COMPILE_TRAINING_DATA, compile_arguments)

    print("\n[+] Password re-engineering completed successfully.")


if __name__ == "__main__":
    main()
