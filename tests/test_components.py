"""
Unit tests for core components
Run with: python -m pytest tests/
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.document_processor import DocumentProcessor
from src.language_detector import LanguageDetector
from src.chunker import Chunker
from src.validator import Validator, Deduplicator


def test_language_detector():
    """Test language detection"""
    # English
    english_text = "This is an English document. It contains several sentences."
    assert LanguageDetector.detect_language(english_text) == 'english'
    
    # Mixed with Devanagari
    hindi_text = "यह एक हिंदी दस्तावेज़ है। इसमें कई वाक्य हैं।"
    lang = LanguageDetector.detect_language(hindi_text)
    assert lang in ['hindi', 'devanagari']
    
    print("✓ Language detection tests passed")


def test_chunker():
    """Test text chunking"""
    text = """
    This is a test document. It contains multiple sentences.
    Each sentence should be processed carefully.
    The chunker should preserve semantic meaning.
    """
    
    chunks = Chunker.chunk_text(text, chunk_size=100, chunk_overlap=20)
    assert len(chunks) > 0, "Should create at least one chunk"
    assert all(isinstance(c, tuple) and len(c) == 2 for c in chunks), "Chunks should be tuples"
    
    print(f"✓ Chunker created {len(chunks)} chunks")


def test_validator():
    """Test validation"""
    # Valid Q&A
    valid, error = Validator.validate_qa_pair(
        "What is machine learning?",
        "Machine learning is a subset of artificial intelligence that enables systems to learn from data.",
        'english'
    )
    assert valid, f"Should be valid: {error}"
    
    # Invalid - too short
    valid, error = Validator.validate_qa_pair(
        "What?",
        "Short",
        'english'
    )
    assert not valid, "Should reject short Q&A"
    
    # Invalid - empty
    valid, error = Validator.validate_qa_pair("", "", 'english')
    assert not valid, "Should reject empty Q&A"
    
    print("✓ Validator tests passed")


def test_deduplicator():
    """Test deduplication"""
    qa_pairs = [
        {"question": "What is machine learning?", "answer": "ML is..."},
        {"question": "What is machine learning?", "answer": "ML is..."},  # Exact duplicate
        {"question": "How does deep learning work?", "answer": "DL uses..."},  # Different
    ]
    
    deduplicated = Deduplicator.deduplicate(qa_pairs, similarity_threshold=0.95)
    
    # Should remove one exact duplicate
    assert len(deduplicated) == 2, f"Should deduplicate exact duplicates, got {len(deduplicated)} from {len(qa_pairs)}"
    
    print(f"✓ Deduplicator reduced {len(qa_pairs)} -> {len(deduplicated)} pairs")


def test_document_text_extraction():
    """Test text file extraction"""
    test_file = "input/sample.txt"
    
    if os.path.exists(test_file):
        text, lang_hint = DocumentProcessor.extract_text(test_file)
        assert len(text) > 100, "Should extract substantial text"
        assert 'AI' in text or 'machine' in text, "Should contain expected content"
        print(f"✓ Extracted {len(text)} characters from TXT")
    else:
        print("⊘ Sample file not found, skipping extraction test")


if __name__ == '__main__':
    print("Running component tests...\n")
    
    try:
        test_language_detector()
        test_chunker()
        test_validator()
        test_deduplicator()
        test_document_text_extraction()
        
        print("\n" + "="*50)
        print("All tests passed! ✓")
        print("="*50)
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
