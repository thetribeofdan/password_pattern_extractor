import os


def merge_jsonl_files(input_dir, output_file):

    files = os.listdir(input_dir)

    with open(output_file, "w") as out:

        for file in files:

            path = os.path.join(input_dir, file)

            with open(path, "r") as f:

                for line in f:
                    out.write(line)

    print(f"[+] Merged dataset saved to {output_file}")


if __name__ == "__main__":

    merge_jsonl_files(
        input_dir="output/structured",
        output_file="structured_dataset.jsonl"
    )
