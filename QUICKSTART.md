# Quick Start Guide

## 60-Second Setup

### 1. Install Dependencies (One-time setup)
```bash
pip install -r requirements.txt
```

This installs:
- Document processing: PyPDF2, python-docx
- Embeddings: sentence-transformers, faiss-cpu
- LLM: llama-cpp-python
- Translation: transformers, torch
- Utilities: numpy, requests, openpyxl

### 2. First Run (Models Auto-Download)
```bash
python main.py --input input/sample.txt
```

On first run:
- Qwen3-4B Q5_K_M model (~2.5GB) downloads automatically
- Sentence-transformers (~50MB) downloads
- M2M100 translation model (~1.5GB) downloads on first translation
- All models cached in `models/` directory for reuse

**Estimated time**: 5-15 minutes (depends on internet speed and hardware)

### 3. Check Output
```bash
ls -lh output/QnA.xlsx
open output/QnA.xlsx  # or use Excel/LibreOffice
```

## Basic Commands

### Generate Q&A (default 10 questions)
```bash
python main.py --input input/document.pdf
python main.py --input input/document.docx
python main.py --input input/document.txt
```

### Generate More Questions
```bash
python main.py --input document.pdf --num-questions 20
```

### Custom Output Location
```bash
python main.py --input document.pdf --output results/custom.xlsx
```

### Use CPU (if GPU is slow)
```bash
python main.py --input document.pdf --device cpu
```

### Lower Memory (Faster Inference)
```bash
python main.py --input document.pdf --model-type q4_k_m
```

## Troubleshooting

### Issue: "CUDA out of memory"
**Solution**: Use CPU device
```bash
python main.py --input document.pdf --device cpu
```

### Issue: Model download fails
**Solution**: Check internet connection, firewall/proxy
```bash
# Run with verbose logging
python main.py --input document.pdf --verbose
```

### Issue: Unsupported file format
**Solution**: Convert to PDF/DOCX/TXT or check file extension
```bash
# Supported: .pdf, .docx, .txt
python main.py --input document.pdf
```

## Performance Tips

| Goal | Command |
|------|---------|
| **Fastest** | `--device cuda --model-type q4_k_m --num-questions 5` |
| **Best Quality** | `--device cuda --model-type q5_k_m --num-questions 20 --top-k 5` |
| **Balanced** | `--device auto --num-questions 10` |
| **CPU Only** | `--device cpu --model-type q4_k_m` |

## Expected Performance

| Hardware | Time for 10 Q&A |
|----------|-----------------|
| GPU (RTX 3080) | 30-60 seconds |
| GPU (RTX 4090) | 20-40 seconds |
| CPU (8-core) | 2-5 minutes |
| Laptop CPU | 5-10 minutes |

## Output Format

### Excel File (QnA.xlsx)

**English Sheet**
| Questions | Answers |
|-----------|---------|
| What is AI? | AI is the simulation of human intelligence... |

**Hindi Sheet** (Devanagari script)
| Questions | Answers |
|-----------|---------|
| AI क्या है? | AI मानव बुद्धि का अनुकरण है... |

**Marathi Sheet** (Devanagari script)
| Questions | Answers |
|-----------|---------|
| AI म्हणजे काय? | AI हे मानवी बुद्धिमत्तेचे अनुरूपण आहे... |

## Advanced Options

```bash
python main.py \
  --input document.pdf \
  --output custom_output.xlsx \
  --num-questions 15 \
  --chunk-size 1024 \
  --chunk-overlap 256 \
  --top-k 5 \
  --device cuda \
  --model-type q5_k_m \
  --verbose
```

## Running Tests

### Component Tests
```bash
python tests/test_components.py
```

### Integration Tests (Without Models)
```bash
python tests/integration_test.py
```

## File Organization

```
qaml_project/
├── main.py                 # Run this: python main.py --input input/document.pdf
├── requirements.txt        # pip install -r requirements.txt
├── input/                  # Put documents here
│   ├── sample.txt
│   ├── document.pdf
│   └── document.docx
├── output/                 # Generated QnA.xlsx appears here
├── models/                 # Auto-downloaded models (auto-created, ~4GB)
├── src/                    # Source code (don't modify)
└── tests/                  # Test scripts (optional)
```

## Next Steps

1. ✓ Install dependencies
2. ✓ Run on sample document
3. ✓ Check generated Excel
4. ✓ Try your own documents
5. ✓ Adjust parameters as needed

## Getting Help

- **Verbose logging**: Add `--verbose` flag
- **Check logs**: See terminal output
- **Review README.md**: Detailed documentation
- **Inspect code**: Source code in `src/` well-commented

## Model Management

### Models Downloaded
- `models/Qwen3-4B-q5_k_m.gguf` (~2.5GB) - LLM
- Cached embedding model (~50MB) - sentence-transformers
- Cached translation model (~1.5GB) - M2M100 (on-demand)

### Clear Cache
```bash
rm -rf models/*.gguf      # Remove model files
rm ~/.cache/huggingface   # Remove HuggingFace cache
```

Models will re-download on next run.

### Change Model Quantization
```bash
# Use Q4_K_M instead of Q5_K_M (faster, lower quality)
python main.py --input document.pdf --model-type q4_k_m
```

## Output Quality

### High Quality (10-20 minutes)
```bash
python main.py --input document.pdf --num-questions 20 --top-k 5 --device cuda
```

### Standard Quality (1-2 minutes)
```bash
python main.py --input document.pdf --num-questions 10 --device cuda
```

### Fast Demo (30 seconds)
```bash
python main.py --input document.pdf --num-questions 5 --top-k 2 --model-type q4_k_m
```

## Supported Languages

### Input
- English
- Hindi
- Marathi
- Mixed (any combination)

### Output
- Always generates all three languages
- English (English text)
- Hindi (Devanagari script)
- Marathi (Devanagari script)

---

**That's it!** Run the command and enjoy multilingual Q&A generation. 🚀
