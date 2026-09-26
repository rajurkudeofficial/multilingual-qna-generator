import logging

logger = logging.getLogger(__name__)


class Translator:
    def __init__(self):
        self._m2m_tokenizer = None
        self._m2m_model = None

        logger.info("Using M2M100 translator for Hindi/Marathi translation")

    def translate_to_hindi(self, text):
        """Translate English text to Hindi."""
        if not text or not text.strip():
            return text

        return self._translate_m2m100(text, "hi")

    def translate_to_marathi(self, text):
        """Translate English text to Marathi."""
        if not text or not text.strip():
            return text

        return self._translate_m2m100(text, "mr")

    def translate_qa_pairs(self, qa_pairs, target_language):
        """
        Translate a list of Q&A pairs to the target language.

        Args:
            qa_pairs: List of dictionaries containing question and answer.
            target_language: hindi or marathi

        Returns:
            List of translated Q&A dictionaries.
        """

        translated_pairs = []

        for pair in qa_pairs:
            question = pair.get("question", "")
            answer = pair.get("answer", "")

            if target_language.lower() == "hindi":
                translated_question = self.translate_to_hindi(question)
                translated_answer = self.translate_to_hindi(answer)

            elif target_language.lower() == "marathi":
                translated_question = self.translate_to_marathi(question)
                translated_answer = self.translate_to_marathi(answer)

            else:
                logger.warning(
                    f"Unsupported target language: {target_language}"
                )
                translated_question = question
                translated_answer = answer

            translated_pairs.append({
                "question": translated_question,
                "answer": translated_answer
            })

        return translated_pairs

    def _load_m2m100(self):
        """Load M2M100 model only once."""

        if self._m2m_model is not None:
            return

        try:
            from transformers import (
                M2M100ForConditionalGeneration,
                M2M100Tokenizer
            )

            logger.info("Loading M2M100 translator for fallback")

            model_name = "facebook/m2m100_418M"

            self._m2m_tokenizer = M2M100Tokenizer.from_pretrained(
                model_name
            )

            self._m2m_model = M2M100ForConditionalGeneration.from_pretrained(
                model_name
            )

            self._m2m_model.to("cpu")
            self._m2m_model.eval()

            logger.info("M2M100 translator loaded successfully")

        except Exception as e:
            logger.error(f"Failed to load M2M100 translator: {e}")
            self._m2m_model = None
            self._m2m_tokenizer = None
            raise

    def _translate_m2m100(self, text, target_lang):
        """
        Translate English text using M2M100.

        target_lang:
            hi = Hindi
            mr = Marathi
        """

        try:
            self._load_m2m100()

            self._m2m_tokenizer.src_lang = "en"

            # Split long text into sentences
            sentences = self._split_sentences(text)

            translations = []

            for sentence in sentences:
                sentence = sentence.strip()

                if not sentence:
                    continue

                try:
                    encoded = self._m2m_tokenizer(
                        sentence,
                        return_tensors="pt",
                        truncation=True,
                        max_length=512
                    )

                    generated_tokens = self._m2m_model.generate(
                        **encoded,
                        forced_bos_token_id=self._m2m_tokenizer.get_lang_id(
                            target_lang
                        ),
                        max_length=512
                    )

                    translated = self._m2m_tokenizer.batch_decode(
                        generated_tokens,
                        skip_special_tokens=True
                    )[0]

                    if translated.strip():
                        translations.append(translated.strip())
                    else:
                        translations.append(sentence)

                except Exception as e:
                    logger.warning(
                        f"Sentence translation failed: {e}"
                    )
                    translations.append(sentence)

            result = " ".join(translations)

            return result if result.strip() else text

        except Exception as e:
            logger.error(
                f"M2M100 translation failed: {e}"
            )

            # Never crash the complete pipeline.
            # Return original English text if translation fails.
            return text

    @staticmethod
    def _split_sentences(text):
        """Simple sentence splitter."""

        import re

        sentences = re.split(
            r"(?<=[.!?])\s+",
            text.strip()
        )

        return [
            sentence.strip()
            for sentence in sentences
            if sentence.strip()
        ]