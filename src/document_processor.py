"""
Document processing - Extract text from PDF, DOCX, TXT
"""

import logging
from pathlib import Path
from typing import Optional, Tuple
import re

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Handle document extraction from various formats"""
    
    SUPPORTED_FORMATS = {'.pdf', '.docx', '.txt'}
    
    @staticmethod
    def extract_text(file_path: str) -> Tuple[str, str]:
        """
        Extract text from document.
        Returns: (text, language_hint)
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Document not found: {file_path}")
        
        if path.suffix.lower() not in DocumentProcessor.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported format: {path.suffix}")
        
        if path.suffix.lower() == '.pdf':
            return DocumentProcessor._extract_pdf(str(path))
        elif path.suffix.lower() == '.docx':
            return DocumentProcessor._extract_docx(str(path))
        elif path.suffix.lower() == '.txt':
            return DocumentProcessor._extract_txt(str(path))
        
        raise ValueError(f"Unknown format: {path.suffix}")
    
    @staticmethod
    def _extract_pdf(file_path: str) -> Tuple[str, str]:
        """Extract text from PDF"""
        try:
            import PyPDF2
        except ImportError:
            raise ImportError("PyPDF2 not installed. Install with: pip install PyPDF2")
        
        text_parts = []
        
        try:
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                
                if not reader.pages:
                    raise ValueError("PDF has no extractable pages")
                
                for page_num, page in enumerate(reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text_parts.append(page_text)
                    except Exception as e:
                        logger.warning(f"Failed to extract page {page_num + 1}: {e}")
                        continue
            
            if not text_parts:
                raise ValueError("No text could be extracted from PDF")
            
            text = '\n'.join(text_parts)
            logger.info(f"Extracted {len(text)} characters from PDF")
            return text, 'unknown'
        
        except Exception as e:
            raise RuntimeError(f"PDF extraction failed: {e}")
    
    @staticmethod
    def _extract_docx(file_path: str) -> Tuple[str, str]:
        """Extract text from DOCX"""
        try:
            from docx import Document
        except ImportError:
            raise ImportError("python-docx not installed. Install with: pip install python-docx")
        
        try:
            doc = Document(file_path)
            
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            
            if not paragraphs:
                raise ValueError("DOCX has no extractable text")
            
            text = '\n'.join(paragraphs)
            logger.info(f"Extracted {len(text)} characters from DOCX")
            return text, 'unknown'
        
        except Exception as e:
            raise RuntimeError(f"DOCX extraction failed: {e}")
    
    @staticmethod
    def _extract_txt(file_path: str) -> Tuple[str, str]:
        """Extract text from TXT"""
        try:
            # Try UTF-8 first
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
        except UnicodeDecodeError:
            # Fall back to other encodings
            for encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        text = f.read()
                    logger.warning(f"Text file decoded with {encoding} encoding")
                    break
                except:
                    continue
            else:
                raise RuntimeError("Could not decode text file with any standard encoding")
        
        if not text.strip():
            raise ValueError("TXT file is empty")
        
        logger.info(f"Extracted {len(text)} characters from TXT")
        return text, 'unknown'
    
    @staticmethod
    def normalize_text(text: str) -> str:
        """
        Basic text normalization
        - Remove excessive whitespace
        - Fix line breaks
        """
        # Replace multiple spaces with single space
        text = re.sub(r' +', ' ', text)
        
        # Replace multiple newlines with double newline
        text = re.sub(r'\n\n+', '\n\n', text)
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text
