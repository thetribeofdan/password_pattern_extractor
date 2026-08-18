import json
import os
from pathlib import Path


# ==========================
# Configuration
# ==========================

RAW_DATASET_DIR = Path("training_dataset/raw")
CHUNK_OUTPUT_DIR = Path("output/chunks")
STATE_FILE = Path("state/splitter_state.json")

LINES_PER_CHUNK = 5000


# ==========================
# State Management
# ==========================

def load_state():

    if not STATE_FILE.exists():

        STATE_FILE.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        state = {
            "next_chunk_id": 0,
            "processed_files": {}
        }

        save_state(state)

        return state

    with open(
        STATE_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


def save_state(state):

    with open(
        STATE_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            state,
            f,
            indent=4
        )


# ==========================
# Dataset Discovery
# ==========================

def discover_datasets():

    RAW_DATASET_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    return sorted(
        RAW_DATASET_DIR.glob("*.txt")
    )


# ==========================
# Chunk Writer
# ==========================

def write_chunk(
    chunk_path,
    lines
):

    with open(
        chunk_path,
        "w",
        encoding="utf-8"
    ) as chunk_file:

        chunk_file.writelines(lines)


# ==========================
# Dataset Splitter
# ==========================

def split_file(
    input_file,
    output_dir,
    lines_per_chunk,
    state
):

    dataset_name = input_file.name
    dataset_prefix = input_file.stem

    processed = state["processed_files"].get(dataset_name)

    if processed and processed["status"] == "completed":

        print(f"[+] Skipping {dataset_name}")

        return

    print(f"[+] Splitting {dataset_name}")

    current_lines = []

    chunk_count = 0

    chunk_index = state["next_chunk_id"]

    with open(
        input_file,
        "r",
        encoding="utf-8",
        errors="ignore"
    ) as f:

        for line in f:

            current_lines.append(line)

            if len(current_lines) >= lines_per_chunk:

                chunk_name = (
                    f"{dataset_prefix}_chunk_"
                    f"{chunk_index:06d}.txt"
                )

                chunk_path = os.path.join(
                    output_dir,
                    chunk_name
                )

                write_chunk(
                    chunk_path,
                    current_lines
                )

                print(f"[+] Created {chunk_name}")

                current_lines = []

                chunk_index += 1

                chunk_count += 1

        # Write remaining lines

        if current_lines:

            chunk_name = (
                f"{dataset_prefix}_chunk_"
                f"{chunk_index:06d}.txt"
            )

            chunk_path = os.path.join(
                output_dir,
                chunk_name
            )

            write_chunk(
                chunk_path,
                current_lines
            )

            print(f"[+] Created {chunk_name}")

            chunk_index += 1

            chunk_count += 1

    # Update state AFTER successful split

    state["next_chunk_id"] = chunk_index

    state["processed_files"][dataset_name] = {
        "status": "completed",
        "chunks_created": chunk_count
    }

    save_state(state)

    print(
        f"[+] Finished {dataset_name} "
        f"({chunk_count} chunks)"
    )


# ==========================
# Main
# ==========================

def main():

    CHUNK_OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    state = load_state()

    datasets = discover_datasets()

    if not datasets:

        print("[!] No datasets found.")

        return

    print(
        f"[+] Found {len(datasets)} dataset(s)"
    )

    for dataset in datasets:

        split_file(
            dataset,
            CHUNK_OUTPUT_DIR,
            LINES_PER_CHUNK,
            state
        )

    print("[+] Dataset splitting complete.")


if __name__ == "__main__":

    main()
