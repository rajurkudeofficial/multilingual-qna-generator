"""
Main Q&A generation pipeline
"""

import logging
from typing import List, Dict, Any
import os
import math
import time

from .config import Config
from .document_processor import DocumentProcessor
from .language_detector import LanguageDetector
from .chunker import Chunker
from .embeddings import EmbeddingGenerator, VectorStore
from .qna_generator import QAGenerator
from .translator import Translator
from .validator import Validator, Deduplicator
from .excel_generator import ExcelGenerator
from .model_manager import ModelManager

logger = logging.getLogger(__name__)


class QAGenerationPipeline:
    """Main pipeline for Q&A generation"""

    def __init__(self, config: Config):
        """
        Initialize pipeline

        Args:
            config: Pipeline configuration
        """
        self.config = config
        self.text = None
        self.language_hint = None
        self.chunks = None
        self.embeddings = None
        self.vector_store = None
        self.qna_generator = None
        self.translator = None
        self.model_manager = None

    def run(self):
        """Run the complete pipeline"""

        total_start = time.perf_counter()

        try:
            logger.info("=" * 60)
            logger.info("Starting Q&A Generation Pipeline")
            logger.info("=" * 60)

            # Step 1: Extract document
            start = time.perf_counter()

            self._extract_document()

            elapsed = time.perf_counter() - start

            logger.info(
                f"[TIMING] Step 1 - Document extraction: "
                f"{elapsed:.2f}s"
            )

            # Step 2: Detect language
            start = time.perf_counter()

            self._detect_language()

            elapsed = time.perf_counter() - start

            logger.info(
                f"[TIMING] Step 2 - Language detection: "
                f"{elapsed:.2f}s"
            )

            # Step 3: Initialize models
            start = time.perf_counter()

            self._initialize_models()

            elapsed = time.perf_counter() - start

            logger.info(
                f"[TIMING] Step 3 - Model initialization: "
                f"{elapsed:.2f}s"
            )

            # Step 4: Chunk text
            start = time.perf_counter()

            self._chunk_text()

            elapsed = time.perf_counter() - start

            logger.info(
                f"[TIMING] Step 4 - Text chunking: "
                f"{elapsed:.2f}s"
            )

            # Step 5: Generate embeddings
            start = time.perf_counter()

            self._generate_embeddings()

            elapsed = time.perf_counter() - start

            logger.info(
                f"[TIMING] Step 5 - Embeddings + FAISS: "
                f"{elapsed:.2f}s"
            )

            # Step 6: Generate Q&A
            start = time.perf_counter()

            english_qa = self._generate_qa()

            elapsed = time.perf_counter() - start

            logger.info(
                f"[TIMING] Step 6 - Q&A generation: "
                f"{elapsed:.2f}s"
            )

            # Step 7: Translate to Hindi
            start = time.perf_counter()

            hindi_qa = self._translate_qa(
                english_qa,
                "hindi"
            )

            elapsed = time.perf_counter() - start

            logger.info(
                f"[TIMING] Step 7 - Hindi translation: "
                f"{elapsed:.2f}s"
            )

            # Step 8: Translate to Marathi
            start = time.perf_counter()

            marathi_qa = self._translate_qa(
                english_qa,
                "marathi"
            )

            elapsed = time.perf_counter() - start

            logger.info(
                f"[TIMING] Step 8 - Marathi translation: "
                f"{elapsed:.2f}s"
            )

            # Step 9: Validate English
            start = time.perf_counter()

            english_qa = self._validate_qa(
                english_qa,
                "english"
            )

            elapsed = time.perf_counter() - start

            logger.info(
                f"[TIMING] Step 9a - English validation: "
                f"{elapsed:.2f}s"
            )

            # Step 10: Validate Hindi
            start = time.perf_counter()

            hindi_qa = self._validate_qa(
                hindi_qa,
                "hindi"
            )

            elapsed = time.perf_counter() - start

            logger.info(
                f"[TIMING] Step 9b - Hindi validation: "
                f"{elapsed:.2f}s"
            )

            # Step 11: Validate Marathi
            start = time.perf_counter()

            marathi_qa = self._validate_qa(
                marathi_qa,
                "marathi"
            )

            elapsed = time.perf_counter() - start

            logger.info(
                f"[TIMING] Step 9c - Marathi validation: "
                f"{elapsed:.2f}s"
            )

            # Step 12: Generate Excel
            start = time.perf_counter()

            self._generate_excel(
                english_qa,
                hindi_qa,
                marathi_qa
            )

            elapsed = time.perf_counter() - start

            logger.info(
                f"[TIMING] Step 10 - Excel generation: "
                f"{elapsed:.2f}s"
            )

            # Total time
            total_elapsed = (
                time.perf_counter() - total_start
            )

            logger.info("=" * 60)
            logger.info(
                f"[TIMING] TOTAL PIPELINE TIME: "
                f"{total_elapsed:.2f}s"
            )
            logger.info("=" * 60)

            logger.info(
                "Pipeline completed successfully!"
            )

        except Exception as e:
            logger.error(
                f"Pipeline failed: {e}",
                exc_info=True
            )
            raise

    def _extract_document(self):
        """Extract text from document"""

        logger.info(
            f"Step 1: Extracting text from "
            f"{self.config.input_file}"
        )

        self.text, language_hint = (
            DocumentProcessor.extract_text(
                self.config.input_file
            )
        )

        self.text = DocumentProcessor.normalize_text(
            self.text
        )

        logger.info(
            f"  ✓ Extracted {len(self.text)} characters"
        )

    def _detect_language(self):
        """Detect input language"""

        logger.info("Step 2: Detecting language")

        self.language_hint = (
            LanguageDetector.get_language_hint(
                self.text
            )
        )

        logger.info(
            f"  ✓ Detected language: "
            f"{self.language_hint}"
        )

    def _initialize_models(self):
        """Initialize required models"""

        logger.info("Step 3: Initializing models")

        # Initialize model manager for downloads
        self.model_manager = ModelManager(
            self.config
        )

        # Ensure LLM is available
        qwen_model_path = (
            self.model_manager.ensure_model_available(
                "qwen",
                self.config.qwen_model_url,
                self.config.qwen_model_path
            )
        )

        # Initialize components
        self.qna_generator = QAGenerator(
            qwen_model_path,
            self.config.device
        )

        self.translator = Translator()

        logger.info("  ✓ Models initialized")

    def _chunk_text(self):
        """Split text into chunks"""

        logger.info(
            f"Step 4: Chunking text "
            f"(size={self.config.chunk_size}, "
            f"overlap={self.config.chunk_overlap})"
        )

        self.chunks = Chunker.chunk_text(
            self.text,
            chunk_size=self.config.chunk_size,
            chunk_overlap=self.config.chunk_overlap
        )

        logger.info(
            f"  ✓ Created {len(self.chunks)} chunks"
        )

    def _generate_embeddings(self):
        """Generate embeddings for chunks"""

        logger.info(
            "Step 5: Generating embeddings"
        )

        embedding_gen = EmbeddingGenerator(
            self.config.embedding_model_name,
            self.config.device
        )

        chunk_texts = [
            text for text, _ in self.chunks
        ]

        embeddings = embedding_gen.generate(
            chunk_texts
        )

        self.vector_store = VectorStore(
            embeddings,
            self.chunks
        )

        logger.info(
            "  ✓ Generated embeddings "
            "and built vector store"
        )

    def _generate_qa(self):
        """Generate Q&A pairs from document context"""

        logger.info(
            f"Step 6: Generating "
            f"{self.config.num_questions} Q&A pairs"
        )

        all_qa_pairs = []

        # Calculate number of batches.
        # Each batch asks the LLM for 2 Q&A pairs.
        num_batches = math.ceil(
            self.config.num_questions / 2
        )

        for i in range(num_batches):

            batch_start = time.perf_counter()

            chunk_idx = min(
                i * 2,
                len(self.chunks) - 1
            )

            chunk_text, _ = self.chunks[
                chunk_idx
            ]

            query_embedding = (
                self._get_chunk_context(
                    chunk_text
                )
            )

            related_chunks = (
                self.vector_store.retrieve(
                    query_embedding,
                    k=self.config.top_k
                )
            )

            context = self._prepare_context(
                chunk_text,
                related_chunks
            )

            qa_start = time.perf_counter()

            qa_pairs = (
                self.qna_generator.generate_qa_pairs(
                    context,
                    num_questions=2,
                    max_retries=self.config.max_retries
                )
            )

            qa_elapsed = (
                time.perf_counter() - qa_start
            )

            all_qa_pairs.extend(
                qa_pairs
            )

            batch_elapsed = (
                time.perf_counter() - batch_start
            )

            logger.info(
                f"Batch {i + 1}/{num_batches}: "
                f"generated {len(qa_pairs)} "
                f"Q&A pairs"
            )

            logger.info(
                f"[TIMING] Q&A batch {i + 1}: "
                f"{batch_elapsed:.2f}s "
                f"(LLM: {qa_elapsed:.2f}s)"
            )

        # Remove duplicate questions
        all_qa_pairs = (
            Deduplicator.deduplicate(
                all_qa_pairs,
                self.config.similarity_threshold
            )
        )

        # Keep only requested number
        all_qa_pairs = all_qa_pairs[
            :self.config.num_questions
        ]

        logger.info(
            f"✓ Generated "
            f"{len(all_qa_pairs)} Q&A pairs"
        )

        return all_qa_pairs

    def _get_chunk_context(
        self,
        chunk_text: str
    ):
        """Get embedding for chunk text"""

        embedding_gen = EmbeddingGenerator(
            self.config.embedding_model_name,
            self.config.device
        )

        embeddings = embedding_gen.generate(
            [chunk_text]
        )

        return embeddings[0]

    def _prepare_context(
        self,
        main_chunk: str,
        related_chunks: List
    ) -> str:
        """Prepare context string from chunks"""

        context_parts = [
            main_chunk
        ]

        for chunk_text, similarity, _ in related_chunks:

            if similarity > 0.5:
                context_parts.append(
                    chunk_text
                )

        return "\n\n".join(
            context_parts
        )

    def _translate_qa(
        self,
        qa_pairs: List[Dict[str, str]],
        target_lang: str
    ) -> List[Dict[str, str]]:
        """Translate Q&A pairs"""

        logger.info(
            f"Step 7: Translating to "
            f"{target_lang}"
        )

        translated = (
            self.translator.translate_qa_pairs(
                qa_pairs,
                target_lang
            )
        )

        logger.info(
            f"  ✓ Translated "
            f"{len(translated)} pairs "
            f"to {target_lang}"
        )

        return translated

    def _validate_qa(
        self,
        qa_pairs: List[Dict[str, str]],
        language: str
    ) -> List[Dict[str, str]]:
        """Validate Q&A pairs"""

        logger.info(
            f"Step 8: Validating "
            f"{language} Q&A"
        )

        valid_pairs, messages = (
            Validator.validate_qa_list(
                qa_pairs,
                language
            )
        )

        # Show validation problems in terminal
        if messages:
            for msg in messages[:5]:
                logger.warning(
                    f"  {msg}"
                )

        logger.info(
            f"  ✓ Validated "
            f"{len(valid_pairs)}/"
            f"{len(qa_pairs)} pairs"
        )

        return valid_pairs

    def _generate_excel(
        self,
        english_qa: List[Dict[str, str]],
        hindi_qa: List[Dict[str, str]],
        marathi_qa: List[Dict[str, str]]
    ):
        """Generate Excel file"""

        logger.info(
            "Step 9: Generating Excel file"
        )

        ExcelGenerator.generate(
            self.config.output_file,
            english_qa,
            hindi_qa,
            marathi_qa
        )

        logger.info(
            f"  ✓ Excel file generated: "
            f"{self.config.output_file}"
        )