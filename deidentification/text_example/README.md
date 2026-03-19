# Text De-identification Example Using Presidio

This sample shows how to de-identify text by removing or replacing personally identifiable information (PII) using [Presidio](https://microsoft.github.io/presidio/) and [Hugging Face](https://huggingface.co/) models.

## Installation

### Prerequisites

- Python 3.8 or higher
- [uv](https://docs.astral.sh/uv/) package manager

### Setup with uv

1. **Install dependencies**

   ```bash
   uv pip install -e .
   ```

2. **Install with all optional dependencies** (recommended)

   ```bash
   uv pip install -e ".[all]"
   ```

   This includes:
   - `[stanza]` – Stanza NLP engine for advanced NER
   - `[spacy-hf]` – Hugging Face pipeline integration with spaCy
   - `[dev]` – Development tools (pytest, black, ruff)

3. **Install specific extras** (if preferred)

   ```bash
   # For Stanza model support
   uv pip install -e ".[stanza]"
   
   # For spaCy Hugging Face pipelines
   uv pip install -e ".[spacy-hf]"
   ```

### Model Setup

Depending on which NER model you choose, download the required NLP models:

**spaCy model:**
```bash
python -m spacy download en_core_web_lg
```

**Stanza model:**
```bash
python -c "import stanza; stanza.download('en')"
```

**Hugging Face model** (Stanford De-identifier):
```bash
python download_hf_deidentifier_model.py
```

## Usage

### 1. Download Hugging Face De-identification Model

Pre-download the Stanford de-identifier model to ensure it's available at runtime:

```bash
python download_hf_deidentifier_model.py
```

This script downloads and caches:
- Stanford De-identifier tokenizer
- Stanford De-identifier model for named entity recognition (NER)

### 2. Anonymize Text

Run the anonymizer with your choice of NER model:

```bash
python anonymize_text.py -m <model_choice> -f <input_file>
```

**Options:**
- `-m, --model`: NER model to use (`spacy`, `stanza`, or `hugging_face`)
- `-f, --file`: Path to the input text file to de-identify

**Examples:**

```bash
# Using spaCy
python anonymize_text.py -m spacy -f sample_text.txt -o sample_text_anonymized.txt

# Using Stanza
python anonymize_text.py -m stanza -f sample_text.txt -o sample_text_anonymized.txt

# Using Hugging Face Stanford De-identifier
python anonymize_text.py -m hugging_face -f sample_text.txt -o sample_text_anonymized.txt
```

## Important Notes

⚠️ **Please carefully review the anonymized output before using for any purpose.** The de-identification process may not catch all sensitive information. Manual review is recommended for clinical data.

### Model Comparison

| Model | Speed | Accuracy | Setup |
|-------|-------|----------|-------|
| spaCy | Fast | Good | Simple (smallest download) |
| Stanza | Slower | Very Good | Moderate (larger download) |
| Hugging Face | Moderate | Excellent | Moderate (some models specialized for medical text) |

### Supported Entity Types

The Stanford De-identifier recognizes:
- `PERSON` – Person names
- `LOCATION` – Geographic locations
- `ORGANIZATION` – Organization/facility names
- `PHONE_NUMBER` – Phone numbers
- `EMAIL` – Email addresses
- `DATE_TIME` – Dates and times
- `AGE` – Patient age
- `ID` – Identification numbers
- And other medical entities (PATIENT, STAFF, HOSPITAL, etc.)

### Customization

You can customize the anonymization behavior by modifying the `operator_config` in `anonymize_text.py`. For example, to keep dates instead of replacing them:

```python
operator_config = {
    "DATE_TIME": OperatorConfig("keep"),
    "AGE": OperatorConfig("keep")
}
```

## Converting Word Documents

To convert Word documents (.docx) to markdown before processing:

```bash
pandoc -f docx -t markdown -o output.md input.docx
```

## Project Structure

```
text_example/
├── pyproject.toml                      # Project configuration
├── README.md                           # This file
├── download_hf_deidentifier_model.py   # Download HF models
└── anonymize_text.py                   # Main de-identification script
```

## License & Disclaimer

This project is licensed under the MIT License. **No warranty is provided.** This software is provided "AS IS" without any guarantees of accuracy, completeness, or fitness for any particular purpose.

⚠️ **Clinical Use Warning**: This tool is intended for research and educational purposes only. Do not use in production without thorough testing and validation. Always review de-identified output manually before using sensitive data.

See the [LICENSE](../../../LICENSE) file for details.
