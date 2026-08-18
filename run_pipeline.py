import subprocess
import sys


PIPELINE = [
    "dataset_splitter.py",
    "run_extractor.py",
    "analytics/pattern_analyzer.py"
]


def run_stage(script):

    print(f"\n{'=' * 60}")
    print(f"Running: {script}")
    print(f"{'=' * 60}")

    result = subprocess.run(
        [sys.executable, script]
    )

    if result.returncode != 0:

        print(f"\n[!] Pipeline stopped at {script}")

        sys.exit(result.returncode)


def main():

    for script in PIPELINE:

        run_stage(script)

    print("\n[+] Pipeline completed successfully.")


if __name__ == "__main__":

    main()
