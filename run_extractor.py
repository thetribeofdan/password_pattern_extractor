import os
import json
from pathlib import Path
from multiprocessing import Pool, cpu_count

from pattern_extractor import extract


CHUNK_DIR = "output/chunks"
STRUCTURED_DIR = "output/structured"

os.makedirs(STRUCTURED_DIR, exist_ok=True)


def process_chunk(chunk_file):

    input_path = os.path.join(CHUNK_DIR, chunk_file)

    output_filename = (
        Path(chunk_file).stem + ".jsonl"
    )

    output_path = os.path.join(
        STRUCTURED_DIR,
        output_filename
    )

    # Safety check
    if os.path.exists(output_path):

        print(f"[+] Skipping {chunk_file} (already processed)")

        return

    processed = 0

    try:

        with open(input_path, "r", encoding="utf-8", errors="ignore") as f, \
             open(output_path, "w") as out:

            for line in f:

                password = line.strip()

                if len(password) < 4:
                    continue

                try:

                    result = extract(password)

                    out.write(json.dumps(result) + "\n")

                    processed += 1

                except Exception as e:

                    print(f"[!] Failed password: {password}")

                    continue

        print(f"[+] Finished {chunk_file} ({processed} passwords)")

    except Exception as e:

        print(f"[!] Failed processing {chunk_file}: {e}")


def get_unprocessed_chunks():

    chunk_files = sorted(os.listdir(CHUNK_DIR))

    remaining = []

    for chunk in chunk_files:

        output_file = (
            Path(chunk).stem + ".jsonl"
        )

        output_path = os.path.join(
            STRUCTURED_DIR,
            output_file
        )

        if not os.path.exists(output_path):

            remaining.append(chunk)

    return remaining


def main():

    chunk_files = get_unprocessed_chunks()

    workers = cpu_count()

    print(f"[+] Using {workers} workers")
    print(f"[+] Remaining chunks: {len(chunk_files)}")

    if not chunk_files:

        print("[+] No remaining chunks to process")

        return

    with Pool(workers) as pool:

        pool.map(process_chunk, chunk_files)

    print("[+] Extraction complete")


if __name__ == "__main__":

    main()
