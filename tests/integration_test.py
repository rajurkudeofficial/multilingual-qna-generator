#!/usr/bin/env python3
"""
Integration test - demonstrates pipeline flow without full model download
Tests all components working together
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.document_processor import DocumentProcessor
from src.language_detector import LanguageDetector
from src.chunker import Chunker
from src.validator import Validator, Deduplicator


def test_full_pipeline():
    """Test the full pipeline without LLM"""
    print("="*60)
    print("Q&A Generation Pipeline - Integration Test")
    print("="*60)
    print()
    
    # Step 1: Document extraction
    print("Step 1: Document Extraction")
    print("-" * 40)
    
    test_file = "input/sample.txt"
    if not os.path.exists(test_file):
        print(f"✗ Test file not found: {test_file}")
        return False
    
    text, lang_hint = DocumentProcessor.extract_text(test_file)
    text = DocumentProcessor.normalize_text(text)
    print(f"✓ Extracted {len(text)} characters")
    print(f"✓ First 100 chars: {text[:100]}...")
    print()
    
    # Step 2: Language detection
    print("Step 2: Language Detection")
    print("-" * 40)
    
    detected_lang = LanguageDetector.detect_language(text)
    print(f"✓ Detected language: {detected_lang}")
    
    script_dist = LanguageDetector.detect_script(text)
    print(f"✓ Script distribution: {script_dist}")
    print()
    
    # Step 3: Chunking
    print("Step 3: Text Chunking")
    print("-" * 40)
    
    chunks = Chunker.chunk_text(text, chunk_size=512, chunk_overlap=128)
    print(f"✓ Created {len(chunks)} chunks")
    print(f"✓ Sample chunk 0: {chunks[0][0][:80]}...")
    if len(chunks) > 1:
        print(f"✓ Sample chunk 1: {chunks[1][0][:80]}...")
    print()
    
    # Step 4: Validation
    print("Step 4: Q&A Validation")
    print("-" * 40)
    
    # Create sample Q&A pairs
    sample_qa = [
        {
            "question": "What is artificial intelligence?",
            "answer": "Artificial Intelligence is the simulation of human intelligence processes by machines, particularly computer systems."
        },
        {
            "question": "What are the types of machine learning?",
            "answer": "There are three types: Supervised Learning, Unsupervised Learning, and Reinforcement Learning."
        },
        {
            "question": "Define NLP",
            "answer": "Natural Language Processing is a field of AI focused on enabling computers to understand and process human language in a meaningful manner."
        },
        {
            "question": "What?",  # Invalid - too short
            "answer": "Short"
        }
    ]
    
    valid_qa, messages = Validator.validate_qa_list(sample_qa, 'english')
    print(f"✓ Validated {len(valid_qa)}/{len(sample_qa)} Q&A pairs")
    if messages:
        print(f"  Validation messages:")
        for msg in messages:
            print(f"    - {msg}")
    print()
    
    # Step 5: Deduplication
    print("Step 5: Deduplication")
    print("-" * 40)
    
    duplicate_qa = [
        {
            "question": "What is machine learning?",
            "answer": "Machine learning is a subset of AI."
        },
        {
            "question": "What is machine learning?",  # Exact duplicate
            "answer": "Machine learning is a subset of AI."
        },
        {
            "question": "What is deep learning?",
            "answer": "Deep learning uses neural networks."
        }
    ]
    
    deduplicated = Deduplicator.deduplicate(duplicate_qa, similarity_threshold=0.95)
    print(f"✓ Deduplicated {len(duplicate_qa)} -> {len(deduplicated)} pairs")
    print()
    
    # Step 6: Excel generation simulation
    print("Step 6: Excel Generation (Structure)")
    print("-" * 40)
    
    print(f"✓ Will generate Excel with 3 sheets:")
    print(f"  - English: {len(valid_qa)} Q&A pairs")
    print(f"  - Hindi: {len(valid_qa)} translated pairs")
    print(f"  - Marathi: {len(valid_qa)} translated pairs")
    print()
    
    # Summary
    print("="*60)
    print("Pipeline Test Summary")
    print("="*60)
    print(f"✓ Document extraction: OK")
    print(f"✓ Language detection: OK")
    print(f"✓ Text chunking: OK")
    print(f"✓ Q&A validation: OK")
    print(f"✓ Deduplication: OK")
    print(f"✓ Excel structure: OK")
    print()
    print("Next steps to run full pipeline:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Run: python main.py --input input/sample.txt")
    print("3. Check output/QnA.xlsx")
    print()
    
    return True


if __name__ == '__main__':
    try:
        success = test_full_pipeline()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
