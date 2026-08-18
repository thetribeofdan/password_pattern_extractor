import json
from pathlib import Path
from collections import Counter


# =====================================
# Configuration
# =====================================

STRUCTURED_DIR = Path("output/structured")

OUTPUT_DIR = Path("output/analytics")

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

PATTERN_STATS_FILE = (
    OUTPUT_DIR /
    "pattern_statistics.json"
)

PATTERN_REPORT_FILE = (
    OUTPUT_DIR /
    "pattern_report.txt"
)


# =====================================
# Dataset Discovery
# =====================================

def discover_structured_chunks():

    return sorted(
        STRUCTURED_DIR.glob("*.jsonl")
    )


# =====================================
# Pattern Analysis
# =====================================

def analyze_pattern_construction():

    pattern_counter = Counter()

    total_records = 0

    structured_chunks = discover_structured_chunks()

    if not structured_chunks:

        print("[!] No structured chunks found.")

        return

    print(
        f"[+] Found {len(structured_chunks)} structured chunk(s)"
    )

    for index, chunk in enumerate(
        structured_chunks,
        start=1
    ):

        print(
            f"[{index}/{len(structured_chunks)}] "
            f"Processing {chunk.name}"
        )

        with open(
            chunk,
            "r",
            encoding="utf-8"
        ) as f:

            for line in f:

                try:

                    record = json.loads(line)

                    pattern = record.get("pattern")

                    if not pattern:
                        continue

                    pattern_counter[pattern] += 1

                    total_records += 1

                except Exception as e:

                    print(
                        f"[!] Failed parsing line "
                        f"in {chunk.name}"
                    )

                    continue

    if total_records == 0:

        print("[!] No valid password records found.")

        return

    sorted_patterns = sorted(
        pattern_counter.items(),
        key=lambda x: x[1],
        reverse=True
    )

    statistics = {

        "_metadata": {

            "structured_chunks_processed":
                len(structured_chunks),

            "total_passwords":
                total_records,

            "unique_patterns":
                len(pattern_counter)

        },

        "patterns": {}

    }

    for pattern, count in sorted_patterns:

        percentage = round(
            (count / total_records) * 100,
            4
        )

        statistics["patterns"][pattern] = {

            "count": count,

            "percentage": percentage

        }

    with open(
        PATTERN_STATS_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            statistics,
            f,
            indent=4
        )

    generate_report(
        sorted_patterns,
        total_records,
        len(structured_chunks)
    )

    print()

    print(
        f"[+] Processed "
        f"{total_records:,} passwords"
    )

    print(
        f"[+] Found "
        f"{len(pattern_counter):,} "
        f"unique patterns"
    )

    print(
        f"[+] Statistics saved to"

        f" {PATTERN_STATS_FILE}"
    )

    print(
        f"[+] Report saved to"

        f" {PATTERN_REPORT_FILE}"
    )


# =====================================
# Report Generator
# =====================================

def generate_report(

    sorted_patterns,

    total_records,

    total_chunks

):

    with open(
        PATTERN_REPORT_FILE,
        "w",
        encoding="utf-8"
    ) as report:

        report.write(
            "AI-PassGen Password Pattern Analysis Report\n"
        )

        report.write(
            "=" * 60 + "\n\n"
        )

        report.write(
            f"Structured Chunks Processed : "
            f"{total_chunks:,}\n"
        )

        report.write(
            f"Total Passwords            : "
            f"{total_records:,}\n"
        )

        report.write(
            f"Unique Patterns            : "
            f"{len(sorted_patterns):,}\n\n"
        )

        report.write(
            "Top 20 Password Construction Patterns\n"
        )

        report.write(
            "-" * 60 + "\n"
        )

        for rank, (

            pattern,

            count

        ) in enumerate(

            sorted_patterns[:20],

            start=1

        ):

            percentage = (
                count /
                total_records
            ) * 100

            report.write(

                f"{rank:>2}. "

                f"{pattern:<35}"

                f"{percentage:>8.4f}% "

                f"({count:,})\n"

            )


# =====================================
# Entry Point
# =====================================

if __name__ == "__main__":

    analyze_pattern_construction()
