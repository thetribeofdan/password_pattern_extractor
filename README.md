# Password Pattern Extractor

A sophisticated multi-stage Python pipeline that extracts, classifies, analyzes, and understands patterns in password datasets to build semantic models of password construction.

**Purpose**: Extract actionable insights from password data by identifying structural patterns, semantic meaning, and buildable password search spaces that can inform targeted analysis and fine-tuned ML models.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Pipeline Stages](#pipeline-stages)
- [Project Structure](#project-structure)
- [Data Formats](#data-formats)
- [Modules Reference](#modules-reference)
- [Output](#output)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Overview

This project implements a complete password analysis pipeline with four main stages:

1. **Data Preparation**: Split large password datasets into manageable chunks
2. **Pattern Extraction**: Tokenize and classify password components
3. **Semantic Analysis & Target Building**: Build persona-based password search spaces
4. **Analytics**: Generate statistics and insights from discovered patterns

The system is designed to understand _how_ passwords are constructed so you can:

- Build efficient targeted searches
- Fine-tune language models on persona-password relationships
- Understand password construction patterns
- Generate synthetic persona training data

---

## ✨ Features

- ✅ **Tokenization**: Intelligently breaks passwords into meaningful components
- ✅ **Multi-class Classification**: Categorizes tokens (words, numbers, years, symbols)
- ✅ **Pattern Building**: Creates abstract password pattern templates
- ✅ **Leet Normalization**: Handles common leetspeak/obfuscation variants
- ✅ **Capitalization Detection**: Tracks case patterns and styles
- ✅ **Semantic Analysis**: Links persona attributes to password patterns
- ✅ **Target Search Space Building**: Generates candidate search spaces from personas
- ✅ **LLM Training Data**: Exports OpenAI fine-tuning format
- ✅ **Analytics & Reporting**: Generates pattern statistics and visualizations
- ✅ **Multiprocessing**: Efficient parallel processing of large datasets

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   PASSWORD PATTERN EXTRACTOR                 │
└─────────────────────────────────────────────────────────────┘

INPUT: Raw Password Files (linkedin.txt, rockyou.txt, uniques.txt)
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────┐
│ STAGE 1: DATASET SPLITTING (dataset_splitter.py)            │
│ • Chunks large files into manageable pieces                 │
│ • Maintains state for resumable processing                  │
│ Output: output/chunks/*.txt                                 │
└─────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────┐
│ STAGE 2: PATTERN EXTRACTION (run_extractor.py)              │
│ • Tokenizes passwords                                        │
│ • Classifies tokens (token, year, number, symbol)           │
│ • Builds pattern templates                                  │
│ • Detects capitalization styles                             │
│ • Normalizes leetspeak                                       │
│ Output: output/structured/*.jsonl, *.jsonl                  │
└─────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────┐
│ STAGE 3: SEMANTIC ANALYSIS & TARGET BUILDING (target_builder)
│ • Pass 1: Semantic Analysis (external/manual)               │
│ • Pass 2: Generate Personas from analysis                   │
│ • Build candidate search spaces per persona                 │
│ • Map tokens, numbers, symbols, patterns                    │
│ Output: target_builder/reviews/persona-*.json               │
└─────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────┐
│ TRAINING DATA COMPILATION (compile_training_data.py)        │
│ • Converts personas to OpenAI fine-tuning format            │
│ • System + User + Assistant message format                  │
│ Output: training_dataset/fine-tune/persona_training_data.jsonl
└─────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────┐
│ STAGE 4: ANALYTICS (analytics/pattern_analyzer.py)          │
│ • Aggregates statistics across all patterns                 │
│ • Generates distribution analysis                           │
│ • Produces reports and visualizations                       │
│ Output: output/analytics/*.txt, *.json                      │
└─────────────────────────────────────────────────────────────┘

OUTPUT: Structured datasets, personas, training data, analytics
```

---

## 🚀 Installation

### Prerequisites

- Python 3.8+
- pip (Python package manager)

### Setup

1. Clone the repository:

```bash
git clone https://github.com/yourusername/password_pattern_extractor.git
cd password_pattern_extractor
```

2. Create environment from template:

```bash
cp .env.example .env
```

3. (Optional) Create virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

4. Install dependencies (if applicable):

```bash
pip install -r requirements.txt  # (if requirements.txt is added)
```

---

## ⚡ Quick Start

### Run the Full Pipeline

```bash
python run_pipeline.py
```

This executes all stages sequentially:

1. Dataset splitting
2. Pattern extraction
3. Analytics generation

### Run Individual Stages

```bash
# Stage 1: Split datasets
python dataset_splitter.py

# Stage 2: Extract patterns
python run_extractor.py

# Stage 3: Generate analytics
python analytics/pattern_analyzer.py

# Generate training data (after persona reviews are created)
python compile_training_data.py
```

### Process Specific File

```bash
python run_extractor.py --input training_dataset/raw/linkedin.txt
```

---

## 📊 Pipeline Stages

### Stage 1: Dataset Splitting

**Purpose**: Convert raw password lists into manageable chunks for parallel processing

**Script**: `dataset_splitter.py`

**Input**:

- `training_dataset/raw/linkedin.txt`
- `training_dataset/raw/rockyou.txt`
- `training_dataset/raw/uniques.txt`

**Output**:

- `output/chunks/*.txt` (chunked password files)
- `state/splitter_state.json` (resumable state)

**Features**:

- Resumable processing (tracks state)
- Configurable chunk size
- Skip already-processed files

---

### Stage 2: Pattern Extraction

**Purpose**: Extract structural and semantic information from each password

**Script**: `run_extractor.py`

**Components**:

- **Tokenizer** (`tokenizer.py`): Breaks passwords into tokens
- **Classifier** (`classifier.py`): Tags tokens as type (token/year/number/symbol)
- **Pattern Builder** (`pattern_builder.py`): Creates pattern templates `{token}{symbol}{year}`
- **Capitalization Detector** (`capitalization.py`): Identifies case patterns
- **Leet Normalizer** (`leet_normalizer.py`): Normalizes leetspeak (1→I, 3→E, etc.)

**Input**: `output/chunks/*.txt`

**Output**: `output/structured/*.jsonl`

**Output Format**:

```json
{
  "password": "milay-ven2011",
  "tokens": ["milay", "ven"],
  "numbers": ["2011"],
  "symbols": ["-"],
  "pattern": "{token}{symbol}{token}{year}",
  "capitalization": "none; all alphabetic characters are lowercase",
  "length": 13
}
```

---

### Stage 3: Semantic Analysis & Target Building

**Purpose**: Build persona-based password search spaces

**Scripts**:

- `target_builder/generate_review.py` - Create persona reviews (manual review step)
- `target_builder/candidate_builder.py` - Orchestrate mapper modules

**Mapper Modules**:

- `target_builder/token_mapper.py` - Extract meaningful tokens
- `target_builder/number_mapper.py` - Collect important numbers
- `target_builder/symbol_mapper.py` - Identify significant symbols
- `target_builder/pattern_mapper.py` - Map likely patterns

**Output**: `target_builder/reviews/persona-*.json`

**Persona Format**:

```json
{
  "persona_id": "persona-20e38c1d704e9f53",
  "source": {
    "password": "milay-ven2011",
    "extracted": {
      /* extraction results */
    },
    "semantic_analysis": {
      /* semantic analysis */
    }
  },
  "persona": {
    "attributes": {
      "identity": {
        "name": { "value": "Milay", "confidence": "low" },
        "secondary_name_or_alias": { "value": "Ven", "confidence": "low" }
      },
      "demographics": {
        "birth_year": { "value": 2011, "confidence": "medium" }
      }
    }
  },
  "target_search_space": {
    "proposed": {
      "primary_tokens": [],
      "secondary_tokens": ["milay", "ven"],
      "important_numbers": ["2011", "year: 2011"],
      "preferred_symbols": ["-"],
      "likely_patterns": ["{token}{symbol}{token}{year}"]
    }
  }
}
```

---

### Stage 4: Training Data Compilation

**Purpose**: Convert personas into OpenAI fine-tuning format

**Script**: `compile_training_data.py`

**Input**: `target_builder/reviews/persona-*.json`

**Output**: `training_dataset/fine-tune/persona_training_data.jsonl`

**Output Format** (OpenAI fine-tuning compatible):

```json
{
  "messages": [
    {
      "role": "system",
      "content": "You are a persona-aware password reasoning model..."
    },
    {
      "role": "user",
      "content": "{\"attributes\": {\"identity\": {...}, \"demographics\": {...}}}"
    },
    {
      "role": "assistant",
      "content": "{\"primary_tokens\": [...], \"secondary_tokens\": [...], ...}"
    }
  ]
}
```

---

### Stage 5: Analytics

**Purpose**: Generate statistics and insights from extracted patterns

**Script**: `analytics/pattern_analyzer.py`

**Output**:

- `output/analytics/pattern_report.txt` - Human-readable statistics
- `output/analytics/pattern_statistics.json` - Machine-readable data

**Metrics Generated**:

- Token frequency distribution
- Password length distribution
- Pattern frequency analysis
- Capitalization style prevalence
- Number occurrence analysis

---

## 📁 Project Structure

```
password_pattern_extractor/
│
├── Core Pipeline Scripts
│   ├── run_pipeline.py              Main orchestrator (runs all stages)
│   ├── dataset_splitter.py          Stage 1: Dataset preparation
│   ├── run_extractor.py             Stage 2: Pattern extraction
│   └── compile_training_data.py     Convert personas to training format
│
├── Extraction Modules
│   ├── tokenizer.py                 Breaks passwords into tokens
│   ├── classifier.py                Classifies token types
│   ├── pattern_builder.py           Creates pattern templates
│   ├── capitalization.py            Detects case patterns
│   ├── leet_normalizer.py           Handles leetspeak
│   ├── token_reconstructor.py       Reverses normalization
│   └── pattern_extractor.py         Main extraction logic
│
├── Target Builder (Semantic Analysis)
│   ├── target_builder/
│   │   ├── candidate_builder.py     Orchestrates all mappers
│   │   ├── token_mapper.py          Maps tokens to personas
│   │   ├── number_mapper.py         Maps numbers to personas
│   │   ├── symbol_mapper.py         Maps symbols to personas
│   │   ├── pattern_mapper.py        Maps patterns to personas
│   │   ├── generate_review.py       Creates persona reviews
│   │   ├── reviewer_export.py       Exports review data
│   │   └── reviews/                 Generated persona files
│   │       └── persona-*.json       Individual persona reviews
│   │
├── Analytics
│   └── analytics/
│       └── pattern_analyzer.py      Generates statistics
│
├── Data Management
│   ├── dataset_merger.py            Combines datasets
│   └── dataset/
│       ├── docs/
│       │   └── dataset_specification.md
│       ├── examples/
│       │   └── sample_entry.json
│       └── schema/
│           └── password_dataset_schema_v1.json
│
├── Training Assets
│   └── training_assets/
│       └── substitution_map_v1.jsonl    Leet-to-normal mappings
│
├── Training Data
│   └── training_dataset/
│       ├── raw/                     Source password files
│       │   ├── linkedin.txt
│       │   ├── rockyou.txt
│       │   └── uniques.txt
│       ├── oroju/                   Organized datasets
│       └── fine-tune/
│           └── persona_training_data.jsonl
│
├── Generated Output
│   ├── output/
│   │   ├── chunks/                  Chunked password files
│   │   ├── structured/              Extracted JSONL files
│   │   └── analytics/               Statistics and reports
│   ├── state/                       Pipeline state files
│   └── *.jsonl                      Compiled datasets
│
├── Configuration
│   ├── .env                         Local environment (gitignored)
│   ├── .env.example                 Environment template
│   └── .gitignore                   Git ignore rules
│
└── Documentation
    ├── README.md                    This file
    ├── GITHUB_SETUP.md              GitHub setup guide
    └── GITHUB_CHECKLIST.md          Files to push/exclude
```

---

## 📊 Data Formats

### Password Record Format (JSONL)

Each line is a JSON object with extracted password data:

```json
{
  "password": "Example2020!",
  "tokens": ["example"],
  "numbers": ["2020"],
  "symbols": ["!"],
  "pattern": "{token}{year}{symbol}",
  "capitalization": "first-letter capital (E)",
  "length": 12
}
```

### Persona Format

Synthetic persona with attributes and predicted search space:

```json
{
  "persona": {
    "attributes": {
      "identity": { "name": { "value": "John", "confidence": "high" } },
      "demographics": {
        "birth_year": { "value": 1985, "confidence": "medium" }
      }
    }
  },
  "target_search_space": {
    "primary_tokens": ["John"],
    "secondary_tokens": [],
    "important_numbers": ["1985", "85"],
    "preferred_symbols": ["."],
    "likely_patterns": ["{token}{symbol}{year}"]
  }
}
```

### Training Data Format (JSONL)

OpenAI fine-tuning compatible format:

```json
{
  "messages": [
    {
      "role": "system",
      "content": "You are a persona-aware password reasoning model..."
    },
    { "role": "user", "content": "{\"attributes\": {...}}" },
    { "role": "assistant", "content": "{\"primary_tokens\": [...], ...}" }
  ]
}
```

---

## 🔧 Modules Reference

### Core Extraction

| Module                 | Purpose                                      |
| ---------------------- | -------------------------------------------- |
| `tokenizer.py`         | Tokenizes passwords into components          |
| `classifier.py`        | Classifies tokens (token/year/number/symbol) |
| `pattern_builder.py`   | Creates abstract pattern templates           |
| `capitalization.py`    | Analyzes capitalization patterns             |
| `leet_normalizer.py`   | Normalizes leetspeak variants                |
| `pattern_extractor.py` | Main extraction orchestrator                 |

### Target Building

| Module                 | Purpose                                |
| ---------------------- | -------------------------------------- |
| `candidate_builder.py` | Combines all mappers into search space |
| `token_mapper.py`      | Maps tokens from semantic analysis     |
| `number_mapper.py`     | Maps numbers (dates, significances)    |
| `symbol_mapper.py`     | Maps symbols from analysis             |
| `pattern_mapper.py`    | Maps likely password patterns          |

### Data Processing

| Module                     | Purpose                               |
| -------------------------- | ------------------------------------- |
| `run_extractor.py`         | Orchestrates extraction over datasets |
| `dataset_splitter.py`      | Chunks large files for processing     |
| `dataset_merger.py`        | Combines multiple datasets            |
| `compile_training_data.py` | Exports personas as training data     |

### Analytics

| Module                | Purpose                          |
| --------------------- | -------------------------------- |
| `pattern_analyzer.py` | Generates statistics and reports |

---

## 📈 Output

### Extraction Output

**Location**: `output/structured/`

JSONL files containing extracted password metadata from each chunk.

### Analytics Output

**Location**: `output/analytics/`

- `pattern_report.txt` - Human-readable statistics summary
- `pattern_statistics.json` - Machine-readable metrics

### Training Data

**Location**: `training_dataset/fine-tune/`

- `persona_training_data.jsonl` - OpenAI fine-tuning format (26 examples)

Suitable for fine-tuning language models on persona-password reasoning.

### Personas

**Location**: `target_builder/reviews/`

Individual persona files with attributes and predicted search spaces.

---

## 👨‍💻 Development

### Adding New Features

1. Follow the module structure (one responsibility per file)
2. Use type hints for clarity
3. Add docstrings to functions
4. Test with sample data before running on full datasets

### Running Tests

```bash
# (Test infrastructure to be added)
python -m pytest tests/
```

### Performance Optimization

- The pipeline supports multiprocessing (`multiprocessing.Pool`)
- Chunk processing runs in parallel by default
- Use `num_workers` config to adjust concurrency

### Extending the Pipeline

To add a new stage:

1. Create a new script following naming conventions
2. Implement input/output handling
3. Add to `PIPELINE` list in `run_pipeline.py`
4. Update documentation

---

## 📝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make changes and test thoroughly
4. Commit with clear messages: `git commit -m "Add feature: description"`
5. Push to branch: `git push origin feature/your-feature`
6. Submit a Pull Request

### Code Style

- Follow PEP 8
- Use meaningful variable names
- Include type hints
- Add docstrings to public functions

---

## 📄 Files to Include/Exclude

### ✅ Included in Repository

- All `.py` source files
- Documentation (`.md` files)
- Dataset schema and examples
- `training_assets/substitution_map_v1.jsonl`
- `.env.example`, `.gitignore`

### ❌ Excluded from Repository

- Raw password data (`training_dataset/raw/`)
- Generated output (`output/`, `*.jsonl`, `state/`)
- Generated personas (`target_builder/reviews/`)
- Python cache (`__pycache__/`, `*.pyc`)
- `.env` (use `.env.example` as template)

See `.gitignore` for complete rules.

---

## 📖 Documentation

- [GITHUB_SETUP.md](GITHUB_SETUP.md) - Detailed setup and configuration guide
- [GITHUB_CHECKLIST.md](GITHUB_CHECKLIST.md) - Files to push/exclude checklist
- [dataset/docs/dataset_specification.md](dataset/docs/dataset_specification.md) - Data schema details

---

## 🔄 Workflow Example

```bash
# 1. Setup
cp .env.example .env

# 2. Run complete pipeline
python run_pipeline.py

# 3. Review generated personas
cat target_builder/reviews/persona-*.json

# 4. Generate training data
python compile_training_data.py

# 5. Use training data
# Upload persona_training_data.jsonl to OpenAI for fine-tuning
```

---

## 📊 Dataset Information

### Input Datasets

- **LinkedIn Passwords**: Anonymized extract from LinkedIn breach
- **RockYou Passwords**: Popular password dataset
- **Uniques**: Unique passwords from combined sources

⚠️ **Note**: For ethical use only. Ensure compliance with local regulations and data protection laws.

### Processing Statistics

- Passwords processed: 26+ personas generated
- Pattern types identified: 20+
- Semantic categories: Names, numbers, symbols, patterns

---

## 🐛 Troubleshooting

### Common Issues

**Issue**: Pipeline stops at extraction stage

- **Solution**: Check `output/chunks/` exists and contains files
- Run: `python dataset_splitter.py` first

**Issue**: Import errors

- **Solution**: Ensure Python path includes project directory
- Run from project root: `cd password_pattern_extractor && python run_pipeline.py`

**Issue**: Out of memory on large datasets

- **Solution**: Reduce `CHUNK_SIZE` in configuration
- Or increase virtual memory/RAM

### Debugging

```bash
# Run individual stage with debug output
python run_extractor.py --debug

# Check pipeline state
cat state/splitter_state.json
```

---

## 📜 License

This project is provided for educational and research purposes. Ensure compliance with local laws and regulations regarding password data handling.

---

## 🙏 Acknowledgments

- Built for password security research and analysis
- Inspired by modern NLP techniques
- Uses efficient multiprocessing for scalability

---

## 📞 Support

For issues, questions, or contributions:

1. Check existing documentation
2. Review example files in `dataset/examples/`
3. Consult schema in `dataset/schema/`
4. Open an issue on GitHub

---

## 🔗 Related Resources

- [Password Security Best Practices](https://owasp.org/www-project-authentication-cheat-sheet/)
- [OpenAI Fine-tuning Documentation](https://platform.openai.com/docs/guides/fine-tuning)
- [Python Documentation](https://docs.python.org/3/)

---

**Last Updated**: August 2026  
**Project Status**: Active Development
