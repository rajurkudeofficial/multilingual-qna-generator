"""
Text chunking - Split text into semantic chunks
"""

import logging
import re
from typing import List, Tuple

logger = logging.getLogger(__name__)


class Chunker:
    """Split text into meaningful chunks"""
    
    @staticmethod
    def chunk_text(
        text: str,
        chunk_size: int = 512,
        chunk_overlap: int = 128,
        use_sentences: bool = True
    ) -> List[Tuple[str, int]]:
        """
        Split text into chunks.
        Returns: List of (chunk_text, chunk_index) tuples
        
        Args:
            text: Text to chunk
            chunk_size: Target size in characters
            chunk_overlap: Overlap between chunks
            use_sentences: Try to preserve sentence boundaries
        """
        if not text or not text.strip():
            raise ValueError("Cannot chunk empty text")
        
        if use_sentences:
            return Chunker._chunk_by_sentences(text, chunk_size, chunk_overlap)
        else:
            return Chunker._chunk_by_size(text, chunk_size, chunk_overlap)
    
    @staticmethod
    def _chunk_by_sentences(
        text: str,
        chunk_size: int,
        chunk_overlap: int
    ) -> List[Tuple[str, int]]:
        """Chunk by sentence boundaries"""
        
        # Split by sentence (basic regex)
        sentence_pattern = r'(?<=[.!?])\s+(?=[A-Z\d])'
        sentences = re.split(sentence_pattern, text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            # Fallback to paragraph
            sentences = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        chunks = []
        current_chunk = ""
        chunk_index = 0
        
        for sentence in sentences:
            test_chunk = current_chunk + " " + sentence if current_chunk else sentence
            
            if len(test_chunk) > chunk_size and current_chunk:
                # Save current chunk
                chunks.append((current_chunk.strip(), chunk_index))
                chunk_index += 1
                
                # Start new chunk with overlap
                # Include some sentences from previous chunk for context
                current_chunk = sentence
            else:
                current_chunk = test_chunk
        
        # Add final chunk
        if current_chunk.strip():
            chunks.append((current_chunk.strip(), chunk_index))
        
        logger.info(f"Created {len(chunks)} chunks (sentence-based)")
        return chunks
    
    @staticmethod
    def _chunk_by_size(
        text: str,
        chunk_size: int,
        chunk_overlap: int
    ) -> List[Tuple[str, int]]:
        """Chunk by character size"""
        
        chunks = []
        start = 0
        chunk_index = 0
        
        while start < len(text):
            end = min(start + chunk_size, len(text))
            
            # Try to find a good break point (space/newline)
            if end < len(text):
                # Look back for space or newline
                for i in range(end, max(start, end - 100), -1):
                    if text[i] in ' \n':
                        end = i
                        break
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append((chunk, chunk_index))
                chunk_index += 1
            
            # Move start position (with overlap)
            start = end - chunk_overlap
            if start <= 0:
                start = end
        
        logger.info(f"Created {len(chunks)} chunks (character-based)")
        return chunks
