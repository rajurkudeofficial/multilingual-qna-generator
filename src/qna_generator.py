import json
import logging
import re
from typing import List, Dict, Any

from llama_cpp import Llama


logger = logging.getLogger(__name__)


class QAGenerator:
    """
    Local Q&A generator using Qwen3 GGUF through llama.cpp.

    CPU-only configuration.
    """

    def __init__(
        self,
        model_path: str,
        device: str = "cpu",
        model_type: str = "q5_k_m",
    ):
        self.model_path = model_path
        self.device = "cpu"
        self.model_type = model_type

        logger.info(f"Loading LLM from: {self.model_path}")

        self.llm = Llama(
            model_path=self.model_path,
            n_ctx=4096,
            n_threads=8,
            n_gpu_layers=0,
            verbose=False,
        )

        logger.info("LLM loaded successfully on cpu")

    # ============================================================
    # CLEAN MODEL OUTPUT
    # ============================================================

    def _clean_output(self, text: str) -> str:
        if not text:
            return ""

        text = text.strip()

        # Remove Qwen thinking section
        text = re.sub(
            r"<think>.*?</think>",
            "",
            text,
            flags=re.DOTALL | re.IGNORECASE,
        )

        # Remove common special tokens
        special_tokens = [
            "<|im_start|>",
            "<|im_end|>",
            "<|endoftext|>",
            "<|assistant|>",
            "<|user|>",
            "<|system|>",
        ]

        for token in special_tokens:
            text = text.replace(token, "")

        text = text.strip()

        # Remove markdown code fences
        text = re.sub(r"```json\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"```\s*", "", text)

        return text.strip()

    # ============================================================
    # JSON EXTRACTION
    # ============================================================

    def _extract_json_array(self, text: str):
        """
        Find the first balanced JSON array in arbitrary model output.
        """

        start = text.find("[")

        while start != -1:
            depth = 0
            in_string = False
            escape = False

            for i in range(start, len(text)):
                ch = text[i]

                if escape:
                    escape = False
                    continue

                if ch == "\\" and in_string:
                    escape = True
                    continue

                if ch == '"':
                    in_string = not in_string
                    continue

                if in_string:
                    continue

                if ch == "[":
                    depth += 1

                elif ch == "]":
                    depth -= 1

                    if depth == 0:
                        candidate = text[start:i + 1]

                        try:
                            return json.loads(candidate)
                        except Exception:
                            break

            start = text.find("[", start + 1)

        return None

    def _extract_json_objects(self, text: str):
        """
        Fallback parser:
        extracts individual {...} JSON objects.
        """

        objects = []

        starts = [m.start() for m in re.finditer(r"\{", text)]

        for start in starts:
            depth = 0
            in_string = False
            escape = False

            for i in range(start, len(text)):
                ch = text[i]

                if escape:
                    escape = False
                    continue

                if ch == "\\" and in_string:
                    escape = True
                    continue

                if ch == '"':
                    in_string = not in_string
                    continue

                if in_string:
                    continue

                if ch == "{":
                    depth += 1

                elif ch == "}":
                    depth -= 1

                    if depth == 0:
                        candidate = text[start:i + 1]

                        try:
                            obj = json.loads(candidate)

                            if isinstance(obj, dict):
                                objects.append(obj)

                        except Exception:
                            pass

                        break

        return objects

    def _parse_qa(self, raw_output: str) -> List[Dict[str, str]]:
        """
        Parse Q&A from model output.

        Supports:
        1. JSON array
        2. Individual JSON objects
        3. Markdown/code-fence wrapped JSON
        """

        cleaned = self._clean_output(raw_output)

        if not cleaned:
            return []

        # --------------------------------------------------------
        # Method 1: Direct JSON
        # --------------------------------------------------------

        try:
            data = json.loads(cleaned)

            if isinstance(data, dict):
                data = [data]

            if isinstance(data, list):
                return self._validate_pairs(data)

        except Exception:
            pass

        # --------------------------------------------------------
        # Method 2: Extract JSON array
        # --------------------------------------------------------

        data = self._extract_json_array(cleaned)

        if isinstance(data, list):
            pairs = self._validate_pairs(data)

            if pairs:
                return pairs

        # --------------------------------------------------------
        # Method 3: Extract individual objects
        # --------------------------------------------------------

        objects = self._extract_json_objects(cleaned)

        if objects:
            pairs = self._validate_pairs(objects)

            if pairs:
                return pairs

        logger.warning("Could not parse JSON from LLM response")

        # Helpful debug information
        preview = cleaned[:1000].replace("\n", " ")
        logger.warning(f"LLM output preview: {preview}")

        return []

    # ============================================================
    # VALIDATION
    # ============================================================

    def _validate_pairs(self, data: Any) -> List[Dict[str, str]]:

        if not isinstance(data, list):
            return []

        valid_pairs = []

        for item in data:

            if not isinstance(item, dict):
                continue

            question = item.get("question")
            answer = item.get("answer")

            if not isinstance(question, str):
                continue

            if not isinstance(answer, str):
                continue

            question = question.strip()
            answer = answer.strip()

            if not question or not answer:
                continue

            valid_pairs.append(
                {
                    "question": question,
                    "answer": answer,
                }
            )

        return valid_pairs

    # ============================================================
    # GENERATE
    # ============================================================

    def generate_qa_pairs(
        self,
        context: str,
        num_questions: int = 2,
        max_retries: int = 2,
    ) -> List[Dict[str, str]]:

        # --------------------------------------------------------
        # HARD CONTEXT LIMIT
        #
        # Qwen context window = 4096
        # Keep prompt + context comfortably below it.
        # --------------------------------------------------------

        max_context_chars = 5500

        if len(context) > max_context_chars:
            context = context[:max_context_chars]

        prompt = f"""<|im_start|>system
You are a question-answer generation system.

Generate exactly {num_questions} meaningful question-answer pairs
using ONLY the provided context.

Rules:
- Questions must be answerable from the context.
- Answers must be accurate and directly supported by the context.
- Do not invent information.
- Do not add explanations.
- Do not add markdown.
- Do not add commentary.
- Return ONLY valid JSON.
- Use English.
- JSON format must be exactly:

[
  {{
    "question": "Question here",
    "answer": "Answer here"
  }}
]
<|im_end|>

<|im_start|>user
Context:
{context}

Generate exactly {num_questions} question-answer pairs.
Return ONLY the JSON array.
<|im_end|>

<|im_start|>assistant
"""

        for attempt in range(1, max_retries + 1):

            try:
                logger.info(
                    f"Generating Q&A (attempt {attempt}/{max_retries})"
                )

                result = self.llm(
                    prompt,
                    max_tokens=700,
                    temperature=0.2,
                    top_p=0.9,
                    repeat_penalty=1.05,
                    stop=[
                        "<|im_end|>",
                        "<|endoftext|>",
                    ],
                )

                raw_output = result["choices"][0]["text"]

                pairs = self._parse_qa(raw_output)

                if pairs:
                    logger.info(
                        f"Successfully parsed {len(pairs)} Q&A pairs"
                    )

                    return pairs[:num_questions]

                logger.warning(
                    "LLM returned output but no valid Q&A pairs could be parsed"
                )

            except Exception as e:
                logger.error(f"Q&A generation error: {e}")

        return []