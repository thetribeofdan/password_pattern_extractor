# Password Pattern Extractor

## Purpose and scope

This repository is a research pipeline for analysing **authorised** password
datasets. It extracts password structure, asks two LLM-assisted passes for
semantic and synthetic-persona reasoning, builds a reviewable search-space
specification, and compiles approved records into JSONL training data.

Use it only with data and systems you are explicitly authorised to analyse.
Do not use any output to access accounts or services without permission.

> **Sensitive-data warning**
>
> Raw passwords are retained in the structured, Pass 1, Pass 2, and review
> artefacts so that records can be joined accurately. Keep these files out of
> source control and limit access to authorised researchers.
>
> The current `compile_training_data.py` implementation has a known issue:
> `extract_persona_attributes()` returns the complete review record, so the
> generated training JSONL can include source/password fields. Do **not** upload
> the current training JSONL to a model provider until that implementation is
> corrected and the output has been audited.

## Workflow at a glance

```text
authorised raw .txt data
        |
        v
dataset_splitter.py
        |  output/chunks/<dataset>_chunk_*.txt
        v
run_extractor.py
        |  output/structured/<dataset>_chunk_*.jsonl
        v
password_re-engineering/run_password_re_engineering.py
        |
        +-- Pass 1: semantic analysis
        |     password-re-engineering/pass_1/output/original_chunk_*.json
        |
        +-- Pass 2: synthetic personas
        |     password-re-engineering/pass_2/output/original_chunk_*.json
        |
        +-- target_builder.generate_review
        |     target_builder/reviews/persona-<opaque-id>.json
        |
        `-- compile_training_data.py
              training_dataset/fine-tune/persona_training_data.jsonl
```

The filenames for the Pass 1 and Pass 2 chunks must match. Records inside a
matching pair are joined by the exact original password:

```text
Pass 1: password
Pass 2: persona.password
```

Older Pass 2 data that stores the value at `persona.attributes.password` is
also supported by the review builder.

## Prerequisites

- Python 3.10 or later
- An OpenAI API key for the Pass 1 and Pass 2 stages
- A local `.env` file created from `.env.example`

Example `.env` values:

```dotenv
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-5.6-sol
CHUNK_SIZE=25
```

The LLM stages send the selected chunk contents to the configured API and may
incur cost. Review the prompts in `password-re-engineering/pass_1/run_pass_1.py`
and `password-re-engineering/pass_2/run_pass_2.py` before use.

## 1. Core extraction pipeline

The core pipeline handles splitting, deterministic extraction, and analytics:

```powershell
python run_pipeline.py
```

It runs:

1. `dataset_splitter.py`
2. `run_extractor.py`
3. `analytics/pattern_analyzer.py`

### Outputs

| Stage | Output |
|---|---|
| Dataset splitting | `output/chunks/<dataset>_chunk_*.txt` |
| Pattern extraction | `output/structured/<dataset>_chunk_*.jsonl` |
| Analytics | `output/analytics/pattern_report.txt` and `pattern_statistics.json` |

Each structured JSONL line contains deterministic evidence such as tokens,
numbers, symbols, pattern, capitalization, length, and token positions.

## 2. Password re-engineering pipeline

Run the chunk-aware semantic, persona, review, and compilation workflow with:

```powershell
python password-re-engineering/run_password_re_engineering.py
```

The orchestrator performs these stages in order:

1. **Pass 1** reads `output/structured/original_chunk_*.jsonl` and writes
   semantic-analysis chunks.
2. **Pass 2** reads only matching `original_chunk_*.json` Pass 1 outputs and
   writes synthetic-persona chunks. Legacy result files are ignored.
3. **Review generation** pairs the two directories and writes one review JSON
   per joined record.
4. **Training-data compilation** processes the review files.

Useful orchestrator options:

```powershell
# Rebuild generated outputs intentionally.
python password-re-engineering/run_password_re_engineering.py --overwrite

# Reuse existing Pass 1 results, but continue with Pass 2 and later stages.
python password-re-engineering/run_password_re_engineering.py --skip-pass-1

# Stop after creating review records.
python password-re-engineering/run_password_re_engineering.py --skip-training-compile

# Require pre-approved, reviewed records during compilation.
python password-re-engineering/run_password_re_engineering.py --no-auto-approve
```

`--overwrite` replaces generated Pass, review, and output files. Do not use it
when a review file contains changes you need to retain.

## 3. Pass-output formats

The chunk files are JSON objects that wrap lists of records.

### Pass 1

`password-re-engineering/pass_1/output/original_chunk_*.json`

```json
{
  "records": [
    {
      "password": "<sensitive>",
      "observations": {
        "tokens": [],
        "numbers": [],
        "symbols": [],
        "pattern": "",
        "capitalization": "",
        "length": 0
      },
      "entities": [],
      "possible_dates": [],
      "semantic_summary": {}
    }
  ]
}
```

### Pass 2

`password-re-engineering/pass_2/output/original_chunk_*.json`

```json
{
  "personas": [
    {
      "persona": {
        "password": "<sensitive>",
        "attributes": {
          "identity": {},
          "demographics": {}
        }
      }
    }
  ]
}
```

The review builder rejects missing chunk pairs, duplicate passwords within a
pair, and records that do not match across Pass 1 and Pass 2.

## 4. Review-record generation

`target_builder/generate_review.py` combines deterministic extractor evidence
with Pass 1 semantics. The Pass 2 persona is attached as reviewer context.

It produces:

- `primary_tokens` and `secondary_tokens`
- `important_numbers`
- `preferred_symbols`
- `likely_patterns`

Process existing Pass outputs without calling the LLM stages:

```powershell
python -m target_builder.generate_review `
  --pass1-dir "password-re-engineering/pass_1/output" `
  --pass2-dir "password-re-engineering/pass_2/output" `
  --output-dir "target_builder/reviews"
```

To process one Pass 1/Pass 2 file pair instead, use `--pass1` and `--pass2`.
Use `--overwrite` only when replacing existing review records is intended.

Each resulting review record contains source evidence, persona context, a
machine-generated `proposed` search space, a `reviewed` search space, and a
review status. Review IDs are deterministic opaque identifiers derived from the
joined password; passwords are not used in filenames.

## 5. Training-data compilation and approval behaviour

Compile review files directly with:

```powershell
python compile_training_data.py --reviews-dir "target_builder/reviews"
```

By default, compilation does the following for each eligible record:

1. Copies `target_search_space.proposed` to `target_search_space.reviewed`.
2. Sets `review.status` to `approved`.
3. Adds an auto-approval note when the record has no note.
4. Persists the updated review JSON and writes a JSONL training example.

Explicitly rejected records are skipped and are not changed. To disable this
automatic approval behaviour, use:

```powershell
python compile_training_data.py --no-auto-approve
```

With that flag, only records that are already both `approved` and populated in
`target_search_space.reviewed` are compiled.

The intended JSONL structure is:

```json
{
  "messages": [
    {"role": "system", "content": "..."},
    {"role": "user", "content": "{\"attributes\": {...}}"},
    {"role": "assistant", "content": "{\"primary_tokens\": [...]}"}
  ]
}
```

See the sensitive-data warning at the top of this document before using the
current compiled file.

## Project layout

```text
password_pattern_extractor/
|-- dataset_splitter.py
|-- run_extractor.py
|-- run_pipeline.py
|-- compile_training_data.py
|-- output/
|   |-- chunks/
|   |-- structured/
|   `-- analytics/
|-- password-re-engineering/
|   |-- openai_client.py
|   |-- run_password_re_engineering.py
|   |-- pass_1/
|   |   |-- run_pass_1.py
|   |   `-- output/
|   `-- pass_2/
|       |-- run_pass_2.py
|       `-- output/
|-- target_builder/
|   |-- candidate_builder.py
|   |-- token_mapper.py
|   |-- number_mapper.py
|   |-- symbol_mapper.py
|   |-- pattern_mapper.py
|   |-- generate_review.py
|   |-- reviewer_export.py
|   `-- reviews/
`-- training_dataset/
    `-- fine-tune/
```

## Verification commands

Run these after changing workflow code:

```powershell
python -m py_compile `
  target_builder/generate_review.py `
  password-re-engineering/pass_2/run_pass_2.py `
  password-re-engineering/run_password_re_engineering.py `
  compile_training_data.py

python -m target_builder.generate_review --help
python compile_training_data.py --help
python password-re-engineering/run_password_re_engineering.py --help
```

Do not treat a successful syntax check as approval to process or upload
sensitive password data.
