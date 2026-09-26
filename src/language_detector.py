"""
Language detection
"""

import logging
import re
from typing import Dict, List

logger = logging.getLogger(__name__)


class LanguageDetector:
    """Detect language(s) in text"""
    
    # Devanagari script range
    DEVANAGARI_RANGE = range(0x0900, 0x0950)
    
    # Common English words
    COMMON_ENGLISH = {
        'the', 'is', 'and', 'to', 'of', 'a', 'in', 'for', 'that', 'was',
        'been', 'have', 'with', 'are', 'from', 'by', 'on', 'can', 'as',
        'or', 'be', 'this', 'at', 'it', 'an', 'will', 'would', 'could'
    }
    
    # Common Hindi words
    COMMON_HINDI = {
        'है', 'का', 'में', 'और', 'यह', 'के', 'से', 'को', 'हो', 'था',
        'एक', 'अन्य', 'या', 'लेकिन', 'भी', 'जो', 'कर', 'दे', 'ले',
        'कहा', 'नहीं', 'सब', 'तो', 'यदि', 'जा', 'लगा', 'पाए'
    }
    
    # Common Marathi words
    COMMON_MARATHI = {
        'आहे', 'का', 'मध्ये', 'आणि', 'हे', 'ना', 'से', 'ला', 'हो', 'होते',
        'एक', 'अन्य', 'किंवा', 'पण', 'ही', 'जो', 'करा', 'दे', 'घे',
        'म्हणाले', 'नाही', 'सब', 'तर', 'जर', 'जा', 'लागले'
    }
    
    @staticmethod
    def detect_script(text: str) -> Dict[str, float]:
        """
        Detect script distribution in text.
        Returns: {'english': 0.8, 'hindi': 0.15, 'marathi': 0.05}
        """
        if not text:
            return {'unknown': 1.0}
        
        english_chars = 0
        devanagari_chars = 0
        other_chars = 0
        
        for char in text:
            code = ord(char)
            if 65 <= code <= 122 or code == 32 or code == 10:  # A-Z, a-z, space, newline
                english_chars += 1
            elif code in LanguageDetector.DEVANAGARI_RANGE:
                devanagari_chars += 1
            else:
                other_chars += 1
        
        total = len(text)
        
        if total == 0:
            return {'unknown': 1.0}
        
        distribution = {
            'english': english_chars / total,
            'devanagari': devanagari_chars / total,
            'other': other_chars / total
        }
        
        return distribution
    
    @staticmethod
    def detect_language(text: str) -> str:
        """
        Detect primary language: 'english', 'hindi', 'marathi', or 'mixed'
        """
        script_dist = LanguageDetector.detect_script(text)
        
        # If significant Devanagari, analyze words
        if script_dist['devanagari'] > 0.05:
            # Could be Hindi or Marathi
            return LanguageDetector._detect_indic_language(text)
        elif script_dist['english'] > 0.7:
            return 'english'
        else:
            return 'unknown'
    
    @staticmethod
    def _detect_indic_language(text: str) -> str:
        """
        Detect between Hindi and Marathi using word patterns
        Both use Devanagari script, so we look for language-specific markers
        """
        text_lower = text.lower()
        
        # Hindi-specific markers
        hindi_markers = sum(1 for marker in ['है', 'का', 'को', 'से', 'ही'] 
                          if marker in text)
        
        # Marathi-specific markers
        marathi_markers = sum(1 for marker in ['आहे', 'ला', 'ने', 'चा', 'ची']
                            if marker in text)
        
        if marathi_markers > hindi_markers:
            return 'marathi'
        elif hindi_markers > 0:
            return 'hindi'
        else:
            return 'devanagari'  # Unknown Devanagari script
    
    @staticmethod
    def get_language_hint(text: str) -> str:
        """
        Get a language hint for the document
        Returns primary detected language
        """
        return LanguageDetector.detect_language(text)
