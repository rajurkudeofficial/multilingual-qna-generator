"""
Validation and quality control
"""

import logging
import re
from typing import List, Dict, Any, Tuple

logger = logging.getLogger(__name__)


class Validator:
    """Validate Q&A pairs"""
    
    MIN_QUESTION_LENGTH = 10
    MAX_QUESTION_LENGTH = 500
    MIN_ANSWER_LENGTH = 20
    MAX_ANSWER_LENGTH = 2000
    
    @staticmethod
    def validate_qa_pair(
        question: str,
        answer: str,
        language: str = 'english'
    ) -> Tuple[bool, str]:
        """
        Validate a single Q&A pair
        
        Args:
            question: Question text
            answer: Answer text
            language: 'english', 'hindi', or 'marathi'
        
        Returns:
            (is_valid, error_message)
        """
        # Check emptiness
        if not question or not question.strip():
            return False, "Question is empty"
        
        if not answer or not answer.strip():
            return False, "Answer is empty"
        
        # Check length
        if len(question) < Validator.MIN_QUESTION_LENGTH:
            return False, f"Question too short (min {Validator.MIN_QUESTION_LENGTH} chars)"
        
        if len(question) > Validator.MAX_QUESTION_LENGTH:
            return False, f"Question too long (max {Validator.MAX_QUESTION_LENGTH} chars)"
        
        if len(answer) < Validator.MIN_ANSWER_LENGTH:
            return False, f"Answer too short (min {Validator.MIN_ANSWER_LENGTH} chars)"
        
        if len(answer) > Validator.MAX_ANSWER_LENGTH:
            return False, f"Answer too long (max {Validator.MAX_ANSWER_LENGTH} chars)"
        
        # Check for JSON/code artifacts
        if Validator._has_json_artifacts(question) or Validator._has_json_artifacts(answer):
            return False, "Question/answer contains JSON/code artifacts"
        
        # Language-specific validation
        if language == 'hindi':
            if not Validator._contains_devanagari(question):
                return False, "Hindi question missing Devanagari script"
            if not Validator._contains_devanagari(answer):
                return False, "Hindi answer missing Devanagari script"
        
        elif language == 'marathi':
            if not Validator._contains_devanagari(question):
                return False, "Marathi question missing Devanagari script"
            if not Validator._contains_devanagari(answer):
                return False, "Marathi answer missing Devanagari script"
        
        elif language == 'english':
            if not Validator._is_mostly_latin(question):
                return False, "English question missing Latin script"
            if not Validator._is_mostly_latin(answer):
                return False, "English answer missing Latin script"
        
        return True, ""
    
    @staticmethod
    def _has_json_artifacts(text: str) -> bool:
        """Check for JSON/code artifacts in text"""
        json_markers = ['{', '}', '[', ']', 'json', '```', 'def ', 'class ', 'import ']
        count = sum(1 for marker in json_markers if marker in text.lower())
        return count >= 3  # Multiple markers suggest code/JSON
    
    @staticmethod
    def _contains_devanagari(text: str) -> bool:
        """Check if text contains Devanagari characters"""
        devanagari_range = range(0x0900, 0x0950)
        return any(ord(c) in devanagari_range for c in text)
    
    @staticmethod
    def _is_mostly_latin(text: str) -> bool:
        """Check if text is mostly Latin characters"""
        latin_count = sum(1 for c in text if ord(c) < 256)
        return latin_count > len(text) * 0.7
    
    @staticmethod
    def validate_qa_list(
        qa_pairs: List[Dict[str, str]],
        language: str = 'english'
    ) -> Tuple[List[Dict[str, str]], List[str]]:
        """
        Validate list of Q&A pairs
        
        Args:
            qa_pairs: List of Q&A dicts
            language: Target language
        
        Returns:
            (valid_pairs, validation_messages)
        """
        valid_pairs = []
        messages = []
        
        for i, pair in enumerate(qa_pairs):
            is_valid, error = Validator.validate_qa_pair(
                pair.get('question', ''),
                pair.get('answer', ''),
                language
            )
            
            if is_valid:
                valid_pairs.append(pair)
            else:
                messages.append(f"Pair {i+1}: {error}")
        
        return valid_pairs, messages


class Deduplicator:
    """Remove duplicate and near-duplicate questions"""
    
    @staticmethod
    def deduplicate(
        qa_pairs: List[Dict[str, str]],
        similarity_threshold: float = 0.85
    ) -> List[Dict[str, str]]:
        """
        Remove duplicate questions using simple similarity
        
        Args:
            qa_pairs: List of Q&A pairs
            similarity_threshold: Threshold for considering two questions similar
        
        Returns:
            Deduplicated list
        """
        if not qa_pairs or len(qa_pairs) <= 1:
            return qa_pairs
        
        unique_pairs = []
        
        for current_pair in qa_pairs:
            current_q = current_pair['question'].lower()
            
            # Check similarity with existing questions
            is_duplicate = False
            for existing_pair in unique_pairs:
                existing_q = existing_pair['question'].lower()
                similarity = Deduplicator._similarity(current_q, existing_q)
                
                if similarity >= similarity_threshold:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_pairs.append(current_pair)
        
        logger.info(f"Deduplicated {len(qa_pairs)} -> {len(unique_pairs)} pairs")
        return unique_pairs
    
    @staticmethod
    def _similarity(text1: str, text2: str) -> float:
        """
        Simple similarity based on common words
        
        Args:
            text1: First text
            text2: Second text
        
        Returns:
            Similarity score 0-1
        """
        # Split into words
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0.0
        
        # Jaccard similarity
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0
