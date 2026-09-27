# Multilingual Q&A Generator

A local AI-based Q&A generation system that accepts PDF, DOCX and TXT documents and generates context-aware Question & Answer pairs in English, Hindi and Marathi.

## Features

- PDF, DOCX and TXT document support
- Automatic language detection
- RAG-based context retrieval using FAISS
- Local Qwen3-4B Q5_K_M model for Q&A generation
- English to Hindi and Marathi translation
- Q&A validation and deduplication
- Excel output with separate English, Hindi and Marathi sheets
- Command-line interface
- Streamlit web interface
- CPU-only inference

## Requirements

- Windows
- Python 3.11
- 8 GB RAM minimum (16 GB recommended)
- Sufficient disk space for local models
- Internet connection for first-time model downloads

The Qwen GGUF model is not included in this repository because of its large file size.

## Setup

### 1. Clone the repository

```powershell
git clone https://github.com/rajurkudeofficial/multilingual-qna-generator.git
cd multilingual-qna-generator
```

### 2. Create a virtual environment

```powershell
python -m venv .venv
```

Activate it on Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. Run the Application

### Web Interface

Start the Streamlit application:

```powershell
python -m streamlit run app.py
```

Open the local URL shown in the terminal.

### Command Line

Example:

```powershell
python main.py --input input\sample.docx --output output\QnA.xlsx --num-questions 4 --device cpu --model-type q5_k_m
```

The generated Excel file will be saved at:

```text
output/QnA.xlsx
```

### 5. Downloading the Qwen model

Once you run the streamlit app,
The required model automatically started downloading at:

```text
models/Qwen3-4B-Q5_K_M.gguf
```

The Qwen GGUF model is excluded from GitHub because of its large size (approx 2.8GB).

The embedding and translation models are downloaded and cached locally when required.

## Input

Upload a PDF, DOCX or TXT document, select the required number of questions, and generate the Excel output.

## Output

`QnA.xlsx` contains three worksheets:

- English
- Hindi
- Marathi

Each worksheet contains:

| Questions | Answers |
|-----------|---------|
| Generated question | Generated answer |

## Processing Pipeline

```text
Document
   ↓
Text Extraction
   ↓
Language Detection
   ↓
Text Chunking
   ↓
Sentence Embeddings
   ↓
FAISS Retrieval
   ↓
Qwen3-4B Q5_K_M
   ↓
Q&A Generation
   ↓
Validation & Deduplication
   ↓
Hindi / Marathi Translation
   ↓
Excel Generation
```

## Project Structure

```text
Q&A-Generator/
│
├── src/
│   ├── __init__.py
│   ├── chunker.py
│   ├── config.py
│   ├── document_processor.py
│   ├── embeddings.py
│   ├── excel_generator.py
│   ├── language_detector.py
│   ├── model_manager.py
│   ├── pipeline.py
│   ├── qna_generator.py
│   ├── translator.py
│   └── validator.py
│
├── input/
├── models/
├── output/
│
├── app.py
├── main.py
├── requirements.txt
├── README.md
└── .gitignore
```

## Testing

After completing the setup, run:

```powershell
python main.py --input input\sample.docx --output output\QnA.xlsx --num-questions 4 --device cpu --model-type q5_k_m
```

Verify that `output/QnA.xlsx` is created and contains:

- English sheet
- Hindi sheet
- Marathi sheet
- Questions and Answers columns

## Important Notes

- The project is configured for CPU-based inference.
- Input documents can be placed in the `input` folder.
- Generated files are saved in the `output` folder.
- The Qwen GGUF model must be available in the `models` folder which is downloaded automatically when the pipeline is started.
- First-time execution may take longer because required models need to be downloaded and cached.
- CPU inference can take several minutes depending on document size and the number of questions.

## Windows Installation Troubleshooting

In most cases, the provided `requirements.txt` installs
`llama-cpp-python` using a prebuilt CPU wheel, so Microsoft Visual
Studio Build Tools should not be required.

However, on some Windows systems, if pip cannot use the compatible
prebuilt wheel and attempts to build `llama-cpp-python` from source,
the installation may fail with a C/C++ compiler or Microsoft Visual
C++ Build Tools error.

### If this error occurs

Install Microsoft Visual Studio Build Tools from the official Microsoft
website.

During installation, select:

- Desktop development with C++
- MSVC C++ build tools
- Windows SDK

After installation, restart the terminal and activate the virtual
environment again:

```powershell
.\.venv\Scripts\Activate.ps1
```

Then retry:
```pip install -r requirements.txt```

# Important -
Do not install Visual Studio Build Tools unless the dependency
installation actually reports a C/C++ compiler or build-tools error.

## Author

**Raj Urkude**  
B.Tech CSE (AI & ML)
